import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from config.settings import TWELVE_DATA_API_KEY
from data.candle_provider import normalize_candles


TWELVE_DATA_BASE_URL = "https://api.twelvedata.com"
TIME_SERIES_ENDPOINT = "/time_series"


def _build_time_series_url(
    symbol,
    interval,
    outputsize=100,
):
    params = urlencode(
        {
            "symbol": symbol,
            "interval": interval,
            "outputsize": outputsize,
        }
    )

    return f"{TWELVE_DATA_BASE_URL}{TIME_SERIES_ENDPOINT}?{params}"


def parse_twelve_data_response(response):
    if not isinstance(response, dict):
        return {
            "status": "REJECTED",
            "reason": "Invalid TwelveData response",
        }

    if response.get("status") != "ok":
        return {
            "status": "REJECTED",
            "reason": response.get(
                "message",
                "TwelveData request failed",
            ),
        }

    values = response.get("values")

    if not isinstance(values, list):
        return {
            "status": "REJECTED",
            "reason": "Missing TwelveData values",
        }

    result = normalize_candles(values)

    if result["status"] != "VALID":
        return result

    return {
        "status": "VALID",
        "candles": result["candles"],
        "meta": response.get("meta", {}),
    }


def fetch_twelve_data_candles(
    symbol,
    interval,
    outputsize=100,
    api_key=None,
    timeout=10,
):
    if not isinstance(symbol, str) or not symbol.strip():
        return {
            "status": "REJECTED",
            "reason": "Invalid symbol",
        }

    if not isinstance(interval, str) or not interval.strip():
        return {
            "status": "REJECTED",
            "reason": "Invalid interval",
        }

    if not isinstance(outputsize, int) or outputsize <= 0:
        return {
            "status": "REJECTED",
            "reason": "Invalid outputsize",
        }

    if api_key is None:
        api_key = TWELVE_DATA_API_KEY

    if not api_key:
        return {
            "status": "REJECTED",
            "reason": "TwelveData API key is not configured",
        }

    url = _build_time_series_url(
        symbol=symbol,
        interval=interval,
        outputsize=outputsize,
    )

    request = Request(
        url,
        headers={
            "Authorization": f"apikey {api_key}",
            "Accept": "application/json",
        },
    )

    try:
        with urlopen(request, timeout=timeout) as response:
            payload = json.loads(
                response.read().decode("utf-8")
            )
    except HTTPError as error:
        return {
            "status": "REJECTED",
            "reason": f"HTTP error: {error.code}",
        }
    except URLError as error:
        return {
            "status": "REJECTED",
            "reason": f"Network error: {error.reason}",
        }
    except TimeoutError:
        return {
            "status": "REJECTED",
            "reason": "Request timeout",
        }
    except json.JSONDecodeError:
        return {
            "status": "REJECTED",
            "reason": "Invalid JSON response",
        }

    return parse_twelve_data_response(payload)
