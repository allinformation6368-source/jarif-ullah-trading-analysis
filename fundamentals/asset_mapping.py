EVENT_ASSET_MAP = {
    "FOMC": ["USD", "BTC"], "Federal Reserve": ["USD", "BTC"], "ADP Employment": ["USD"], "Nonfarm Payrolls": ["USD"], "NFP": ["USD"], "Jobless Claims": ["USD"], "CPI": ["USD"], "PCE": ["USD"], "ECB": ["EUR"], "European Central Bank": ["EUR"], "Bank of England": ["GBP"], "BOE": ["GBP"], "Bank of Japan": ["JPY"], "BOJ": ["JPY"], "RBA": ["AUD"], "Bank of Canada": ["CAD"], "BOC": ["CAD"], "Crude oil": ["CAD"], "Oil": ["CAD"], "Treasury yields": ["USD", "BTC"], "USD strength": ["USD", "BTC"], "Crypto": ["BTC"], "Bitcoin": ["BTC"], "Ethereum": ["ETH"]
}

ASSET_PAIRS = {
    "USD": ["EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "USD/CAD", "BTC/USD", "ETH/USD"],
    "EUR": ["EUR/USD"],
    "GBP": ["GBP/USD"],
    "JPY": ["USD/JPY"],
    "AUD": ["AUD/USD"],
    "CAD": ["USD/CAD"],
    "BTC": ["BTC/USD"],
    "ETH": ["ETH/USD"]
}


def get_affected_assets(title):
    title_lower = title.lower()
    assets = set()
    for keyword, mapped_assets in EVENT_ASSET_MAP.items():
        if keyword.lower() in title_lower:
            assets.update(mapped_assets)
    return sorted(assets)


def get_affected_pairs(title):
    assets = get_affected_assets(title)
    pairs = set()
    for asset in assets:
        pairs.update(ASSET_PAIRS.get(asset, []))
    return sorted(pairs)
