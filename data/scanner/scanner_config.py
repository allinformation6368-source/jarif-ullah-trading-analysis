from datetime import time


# Scanner-only universe.
# Global config/assets.py remains untouched.
SCANNER_PAIRS = (
    "BTC/USD",
    "ETH/USD",
    "EUR/USD",
    "GBP/USD",
    "USD/JPY",
    "USD/CHF",
    "AUD/USD",
    "USD/CAD",
)

SCANNER_START = time(6, 0)
SCANNER_STOP = time(21, 0)

PAIR_SCAN_INTERVAL_SECONDS = 72

DAILY_LIMIT = 800
PLANNED_BUDGET = 750
SAFETY_RESERVE = 50

# At 72 seconds:
# 900 minutes / 1.2 minutes = 750 pair scans/day.
TARGET_SCANS_PER_DAY = 750

# Conservative scheduler floor.
MIN_SCAN_INTERVAL_SECONDS = 72

# Prevent accidental extremely-fast polling if configuration changes.
MAX_SCAN_INTERVAL_SECONDS = 3600


def validate_scanner_config():
    assert len(SCANNER_PAIRS) == 8
    assert len(set(SCANNER_PAIRS)) == 8

    assert SCANNER_START < SCANNER_STOP

    assert PAIR_SCAN_INTERVAL_SECONDS == 72

    assert DAILY_LIMIT == 800
    assert PLANNED_BUDGET == 750
    assert SAFETY_RESERVE == 50

    assert PLANNED_BUDGET + SAFETY_RESERVE == DAILY_LIMIT

    assert TARGET_SCANS_PER_DAY == 750

    return True
