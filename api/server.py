import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from analysis.live_mtf import analyze_live_market
from config.risk import (
    DEFAULT_ACCOUNT_BALANCE,
    DEFAULT_RISK_PERCENT,
    validate_risk_config,
)
from config.timeframes import TRADING_MODES


HOST = "0.0.0.0"
PORT = int(os.getenv("BRAIN_API_PORT", "8000"))
MAX_REQUEST_BYTES = 1024 * 1024


def _json_response(handler, status_code, payload):
    body = json.dumps(
        payload,
        separators=(",", ":"),
        default=str,
    ).encode("utf-8")

    handler.send_response(status_code)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header(
        "Access-Control-Allow-Methods",
        "POST, OPTIONS",
    )
    handler.send_header(
        "Access-Control-Allow-Headers",
        "Content-Type",
    )
    handler.end_headers()
    handler.wfile.write(body)


def _error(reason):
    return {
        "status": "REJECTED",
        "reason": reason,
    }


def _validate_request(payload):
    if not isinstance(payload, dict):
        return "Request body must be a JSON object"

    symbol = payload.get("symbol")
    mode = payload.get("mode")

    if not isinstance(symbol, str) or not symbol.strip():
        return "Invalid symbol"

    if not isinstance(mode, str) or mode not in TRADING_MODES:
        return "Invalid mode"

    account_balance = payload.get(
        "account_balance",
        DEFAULT_ACCOUNT_BALANCE,
    )

    risk_percent = payload.get(
        "risk_percent",
        DEFAULT_RISK_PERCENT,
    )

    if isinstance(account_balance, bool):
        return "Invalid account balance"

    if isinstance(risk_percent, bool):
        return "Invalid risk percent"

    try:
        account_balance = float(account_balance)
        risk_percent = float(risk_percent)
    except (TypeError, ValueError):
        return "Invalid account balance or risk percent"

    risk_config = validate_risk_config(
        account_balance=account_balance,
        risk_percent=risk_percent,
    )

    if risk_config["status"] != "VALID":
        return risk_config["reason"]

    return None


def build_analysis_response(
    symbol,
    mode,
    analysis,
):
    return {
        "status": "VALID",
        "symbol": symbol,
        "mode": mode,
        "analysis": {
            "decision": analysis.get("decision"),
            "market_regime": analysis.get("market_regime"),
            "session": analysis.get("session"),
            "trade_plan": analysis.get("trade_plan"),
            "risk": analysis.get("risk"),
            "position_sizing": analysis.get(
                "position_sizing"
            ),
            "risk_guard": analysis.get("risk_guard"),
            "paper_order": analysis.get("paper_order"),
        },
    }


class BrainAPIHandler(BaseHTTPRequestHandler):
    server_version = "JarifUllahBrainAPI/1.0"

    def log_message(self, format, *args):
        return

    def do_OPTIONS(self):
        _json_response(
            self,
            204,
            {},
        )

    def do_GET(self):
        if self.path == "/health":
            _json_response(
                self,
                200,
                {
                    "status": "VALID",
                    "service": "brain-api",
                    "version": "1.0",
                },
            )
            return

        _json_response(
            self,
            404,
            _error("Not found"),
        )

    def do_POST(self):
        if self.path != "/api/v1/analyze":
            _json_response(
                self,
                404,
                _error("Not found"),
            )
            return

        content_length = self.headers.get(
            "Content-Length",
            "0",
        )

        try:
            content_length = int(content_length)
        except ValueError:
            _json_response(
                self,
                400,
                _error("Invalid Content-Length"),
            )
            return

        if content_length <= 0:
            _json_response(
                self,
                400,
                _error("Request body is required"),
            )
            return

        if content_length > MAX_REQUEST_BYTES:
            _json_response(
                self,
                413,
                _error("Request body too large"),
            )
            return

        raw_body = self.rfile.read(content_length)

        try:
            payload = json.loads(raw_body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            _json_response(
                self,
                400,
                _error("Invalid JSON"),
            )
            return

        validation_error = _validate_request(payload)

        if validation_error:
            _json_response(
                self,
                400,
                _error(validation_error),
            )
            return

        symbol = payload["symbol"].strip()
        mode = payload["mode"]
        account_balance = float(
            payload.get(
                "account_balance",
                DEFAULT_ACCOUNT_BALANCE,
            )
        )
        risk_percent = float(
            payload.get(
                "risk_percent",
                DEFAULT_RISK_PERCENT,
            )
        )

        try:
            result = analyze_live_market(
                symbol=symbol,
                mode=mode,
                account_balance=account_balance,
                risk_percent=risk_percent,
                outputsize=500,
                provider="twelvedata",
            )
        except Exception:
            _json_response(
                self,
                502,
                _error("Brain analysis failed"),
            )
            return

        if result.get("status") != "VALID":
            _json_response(
                self,
                502,
                _error(
                    result.get(
                        "reason",
                        "Market analysis failed",
                    )
                ),
            )
            return

        response = build_analysis_response(
            symbol=symbol,
            mode=mode,
            analysis=result["analysis"],
        )

        _json_response(
            self,
            200,
            response,
        )


def create_server(
    host=HOST,
    port=PORT,
):
    return ThreadingHTTPServer(
        (host, port),
        BrainAPIHandler,
    )


def main():
    server = create_server()

    print(
        f"Brain API listening on "
        f"http://{HOST}:{PORT}"
    )
    print(
        "POST /api/v1/analyze"
    )
    print(
        "GET  /health"
    )

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
