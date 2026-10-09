import curses
import curses.textpad
import json
import os
import urllib.error
import urllib.request


API_BASE = os.getenv("BRAIN_API_URL", "http://127.0.0.1:8000")
SYMBOL = "BTC/USD"
BALANCE = 10000
RISK_PERCENT = 1.0

SCREENS = ["HOME", "ANALYSIS", "TRADES", "ACCOUNT", "SETTINGS"]
MODES = ["scalping", "intraday", "swing"]


def api_request(path, method="GET", payload=None):
    url = API_BASE.rstrip("/") + path

    try:
        data = None
        headers = {}

        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"

        request = urllib.request.Request(
            url,
            data=data,
            headers=headers,
            method=method,
        )

        with urllib.request.urlopen(request, timeout=8) as response:
            raw = response.read().decode("utf-8")
            return response.status, json.loads(raw)

    except urllib.error.HTTPError as exc:
        try:
            body = exc.read().decode("utf-8")
            return exc.code, json.loads(body)
        except Exception:
            return exc.code, {"status": "REJECTED", "reason": str(exc)}

    except Exception as exc:
        return 0, {
            "status": "REJECTED",
            "reason": f"Brain unavailable: {exc}",
        }


def health():
    status, data = api_request("/health")
    return status == 200 and data.get("status") == "VALID"


def analyze(mode):
    return api_request(
        "/api/v1/analyze",
        method="POST",
        payload={
            "symbol": SYMBOL,
            "mode": mode,
            "account_balance": BALANCE,
            "risk_percent": RISK_PERCENT,
        },
    )


def value(obj, *keys, default="--"):
    if not isinstance(obj, dict):
        return default

    for key in keys:
        item = obj.get(key)
        if item is not None:
            return item

    return default


def safe_add(stdscr, y, x, text, attr=0):
    h, w = stdscr.getmaxyx()

    if y < 0 or y >= h or x >= w:
        return

    text = str(text)
    width = max(0, w - x - 1)

    if width:
        try:
            stdscr.addnstr(y, x, text, width, attr)
        except curses.error:
            pass


def box(stdscr, top, left, bottom, right, title):
    h, w = stdscr.getmaxyx()

    top = max(0, min(top, h - 1))
    bottom = max(top, min(bottom, h - 1))
    left = max(0, min(left, w - 1))
    right = max(left, min(right, w - 1))

    try:
        curses.textpad.rectangle(
            stdscr,
            top,
            left,
            bottom,
            right,
        )
    except curses.error:
        pass

    safe_add(
        stdscr,
        top,
        left + 2,
        f" {title} ",
        curses.A_BOLD,
    )


def header(stdscr, screen, online):
    h, w = stdscr.getmaxyx()

    safe_add(
        stdscr,
        0,
        2,
        "⚡ JARIF ULLAH",
        curses.A_BOLD,
    )

    status = "● ONLINE" if online else "● OFFLINE"

    safe_add(
        stdscr,
        0,
        max(2, w - len(status) - 3),
        status,
        curses.A_BOLD,
    )

    safe_add(
        stdscr,
        1,
        2,
        "TRADING ANALYSIS",
        curses.A_BOLD,
    )

    safe_add(
        stdscr,
        3,
        2,
        f"SCREEN: {screen}",
        curses.A_BOLD,
    )

    safe_add(
        stdscr,
        4,
        2,
        "PAPER TRADING  •  SAFE MODE",
    )


def footer(stdscr):
    h, _ = stdscr.getmaxyx()

    safe_add(
        stdscr,
        h - 2,
        1,
        "[1] HOME  [2] ANALYSIS  [3] TRADES  [4] ACCOUNT  [5] SETTINGS  [R] REFRESH  [Q] EXIT",
        curses.A_BOLD,
    )

    safe_add(
        stdscr,
        h - 1,
        2,
        "Terminal UI  •  Brain/API connected read-only",
    )


def scanner_status_panel(stdscr, y, w, data, scanner_engine):
    """Render read-only scanner status; never calls a market-data provider."""
    try:
        from datetime import datetime
        from data.scanner.scanner_config import (
            SCANNER_PAIRS,
            SCANNER_START,
            SCANNER_STOP,
        )
        from data.scanner.credit_tracker import get_credit_status
        from terminal_ui.scanner_status import (
            build_scanner_status,
            format_scanner_status,
        )

        engine_status = scanner_engine.status()
        scheduler = engine_status.get("scheduler", {})

        scanner_state = scheduler.get(
            "scanner_status",
            "PAUSED",
        )

        used = int(
            scheduler.get(
                "credits_used_today",
                0,
            ) or 0
        )

        remaining = int(
            scheduler.get(
                "credits_remaining",
                800,
            ) or 0
        )

        next_pair = scheduler.get(
            "next_pair",
            SCANNER_PAIRS[0],
        )

        last_result = engine_status.get("last_result") or {}
        current_pair = last_result.get("pair", "--")

        analysis = data.get("analysis", {}) if isinstance(data, dict) else {}
        decision = value(
            analysis.get("decision"),
            "decision",
            default="WAIT",
        )

        confidence = value(
            analysis.get("decision"),
            "confidence",
            default=0,
        )

        try:
            confidence = int(float(confidence))
        except (TypeError, ValueError):
            confidence = 0

        quality = "LOW"
        if decision in ("BUY", "SELL"):
            quality = "MEDIUM"

        status = build_scanner_status(
            scanner_status=scanner_state,
            current_pair=current_pair,
            next_pair=next_pair,
            signal=decision,
            quality=quality,
            confidence=confidence,
            setup_state="--",
            credits_used=used,
            credits_remaining=remaining,
        )

        lines = format_scanner_status(status).splitlines()

        box(
            stdscr,
            y,
            2,
            min(stdscr.getmaxyx()[0] - 2, y + 9),
            max(2, w - 3),
            "SCANNER STATUS",
        )

        for offset, line in enumerate(lines[:8], start=1):
            safe_add(
                stdscr,
                y + offset,
                5,
                line[:max(1, w - 10)],
            )

    except Exception as exc:
        box(
            stdscr,
            y,
            2,
            min(stdscr.getmaxyx()[0] - 2, y + 4),
            max(2, w - 3),
            "SCANNER STATUS",
        )
        safe_add(
            stdscr,
            y + 2,
            5,
            "SCANNER STATUS UNAVAILABLE  •  READ-ONLY",
            curses.A_BOLD,
        )


def home(stdscr, mode, online, data, scanner_engine):
    h, w = stdscr.getmaxyx()

    header(stdscr, "HOME", online)

    safe_add(stdscr, 6, 2, SYMBOL, curses.A_BOLD)
    safe_add(stdscr, 6, max(2, w - 10), "PAPER", curses.A_BOLD)

    safe_add(stdscr, 8, 2, "MODE", curses.A_BOLD)

    x = 2

    for item in MODES:
        label = f"[ {item.upper()} ]"
        attr = curses.A_REVERSE if item == mode else 0
        safe_add(stdscr, 9, x, label, attr)
        x += len(label) + 2

    box(
        stdscr,
        11,
        2,
        min(h - 10, 19),
        max(2, w - 3),
        "MARKET SNAPSHOT",
    )

    analysis = data.get("analysis", {}) if isinstance(data, dict) else {}

    decision = value(
        analysis.get("decision"),
        "decision",
        default="WAIT",
    )

    signal = value(
        analysis.get("decision"),
        "signal",
        default="--",
    )

    confidence = value(
        analysis.get("decision"),
        "confidence",
        default="--",
    )

    regime = value(
        analysis.get("market_regime"),
        "regime",
        default="--",
    )

    session = value(
        analysis.get("session"),
        "session",
        default="--",
    )

    safe_add(stdscr, 13, 5, f"DECISION       {decision}", curses.A_BOLD)
    safe_add(stdscr, 14, 5, f"SIGNAL         {signal}")
    safe_add(stdscr, 15, 5, f"CONFIDENCE     {confidence}")
    safe_add(stdscr, 16, 5, f"REGIME         {regime}")
    safe_add(stdscr, 17, 5, f"SESSION        {session}")

    y = min(h - 8, 21)

    box(
        stdscr,
        y,
        2,
        min(h - 3, y + 5),
        max(2, w - 3),
        "STATUS",
    )

    if online:
        safe_add(
            stdscr,
            y + 2,
            5,
            "BRAIN ONLINE  •  READ-ONLY ANALYSIS",
            curses.A_BOLD,
        )
    else:
        safe_add(
            stdscr,
            y + 2,
            5,
            "BRAIN DISCONNECTED  •  SAFE WAIT",
            curses.A_BOLD,
        )

    scanner_y = min(h - 2, y + 6)
    scanner_status_panel(stdscr, scanner_y, w, data, scanner_engine)

    footer(stdscr)


def analysis(stdscr, mode, online, data):
    h, w = stdscr.getmaxyx()

    header(stdscr, "ANALYSIS", online)

    safe_add(stdscr, 6, 2, SYMBOL, curses.A_BOLD)
    safe_add(stdscr, 7, 2, f"MODE  {mode.upper()}")

    result = data.get("analysis", {}) if isinstance(data, dict) else {}

    box(
        stdscr,
        9,
        2,
        min(h - 12, 19),
        max(2, w - 3),
        "BRAIN ANALYSIS",
    )

    decision_data = result.get("decision") or {}

    if isinstance(decision_data, dict):
        decision = value(decision_data, "decision", default="WAIT")
        signal = value(decision_data, "signal", default="--")
        confidence = value(decision_data, "confidence", default="--")
    else:
        decision = decision_data or "WAIT"
        signal = "--"
        confidence = "--"

    regime_data = result.get("market_regime") or {}
    session_data = result.get("session") or {}

    regime = value(regime_data, "regime", default="--")
    session = value(session_data, "session", default="--")

    rows = [
        ("DECISION", decision),
        ("SIGNAL", signal),
        ("CONFIDENCE", confidence),
        ("REGIME", regime),
        ("SESSION", session),
    ]

    y = 11

    for key, val in rows:
        safe_add(stdscr, y, 5, f"{key:<14}")
        safe_add(stdscr, y, 21, val, curses.A_BOLD)
        y += 1

    y = min(h - 10, 21)

    box(
        stdscr,
        y,
        2,
        min(h - 3, y + 6),
        max(2, w - 3),
        "TRADE PLAN / RISK",
    )

    trade_plan = result.get("trade_plan") or {}
    risk = result.get("risk") or {}
    sizing = result.get("position_sizing") or {}
    guard = result.get("risk_guard") or {}

    safe_add(
        stdscr,
        y + 2,
        5,
        f"PLAN       {value(trade_plan, 'status', 'decision')}",
    )

    safe_add(
        stdscr,
        y + 3,
        5,
        f"RISK       {value(risk, 'status', 'risk', 'risk_percent')}",
    )

    safe_add(
        stdscr,
        y + 4,
        5,
        f"POSITION   {value(sizing, 'position_size', 'quantity', 'size')}",
    )

    safe_add(
        stdscr,
        y + 5,
        5,
        f"GUARD      {value(guard, 'status', 'decision', 'reason')}",
    )

    footer(stdscr)


def trades(stdscr, data, online):
    h, w = stdscr.getmaxyx()

    header(stdscr, "TRADES", online)

    result = data.get("analysis", {}) if isinstance(data, dict) else {}
    order = result.get("paper_order") or {}

    box(
        stdscr,
        7,
        2,
        min(h - 6, 17),
        max(2, w - 3),
        "PAPER TRADES",
    )

    if order:
        safe_add(
            stdscr,
            10,
            5,
            f"STATUS       {value(order, 'status')}",
            curses.A_BOLD,
        )
        safe_add(
            stdscr,
            11,
            5,
            f"SIDE         {value(order, 'side', 'direction')}",
        )
        safe_add(
            stdscr,
            12,
            5,
            f"QUANTITY     {value(order, 'quantity', 'position_size')}",
        )
    else:
        safe_add(
            stdscr,
            10,
            5,
            "NO ACTIVE PAPER TRADE",
            curses.A_BOLD,
        )
        safe_add(
            stdscr,
            11,
            5,
            "Brain has not produced an executable paper order.",
        )

    footer(stdscr)


def account(stdscr, online):
    h, w = stdscr.getmaxyx()

    header(stdscr, "ACCOUNT", online)

    box(
        stdscr,
        7,
        2,
        min(h - 7, 16),
        max(2, w - 3),
        "PAPER ACCOUNT",
    )

    rows = [
        ("BALANCE", f"{BALANCE:,.2f}"),
        ("RISK / TRADE", f"{RISK_PERCENT:.1f}%"),
        ("EXECUTION", "PAPER"),
        ("LIVE TRADING", "DISABLED"),
        ("STATUS", "SAFE"),
    ]

    y = 9

    for key, val in rows:
        safe_add(stdscr, y, 5, f"{key:<18}")
        safe_add(stdscr, y, 24, val, curses.A_BOLD)
        y += 1

    footer(stdscr)


def settings(stdscr, mode, online):
    h, w = stdscr.getmaxyx()

    header(stdscr, "SETTINGS", online)

    box(
        stdscr,
        7,
        2,
        min(h - 7, 18),
        max(2, w - 3),
        "SYSTEM SETTINGS",
    )

    rows = [
        ("MODE", mode.upper()),
        ("EXECUTION", "PAPER"),
        ("LIVE TRADING", "DISABLED"),
        ("API", API_BASE),
        ("RISK", f"{RISK_PERCENT:.1f}%"),
    ]

    y = 9

    for key, val in rows:
        safe_add(stdscr, y, 5, f"{key:<18}")
        safe_add(stdscr, y, 24, val, curses.A_BOLD)
        y += 2

    footer(stdscr)


def run(stdscr):
    curses.curs_set(0)
    stdscr.keypad(True)

    screen = 0
    mode_index = 1
    mode = MODES[mode_index]

    online = False
    data = {}

    from data.scanner.scanner_engine import ScannerEngine
    scanner_engine = ScannerEngine()

    def refresh():
        nonlocal online, data

        online = health()

        if not online:
            data = {}
            return

        status, response = analyze(mode)

        if status == 200 and response.get("status") == "VALID":
            data = response
        else:
            data = {
                "status": "REJECTED",
                "reason": response.get(
                    "reason",
                    "Brain analysis failed",
                ),
            }

    refresh()

    while True:
        stdscr.erase()

        if screen == 0:
            home(stdscr, mode, online, data, scanner_engine)
        elif screen == 1:
            analysis(stdscr, mode, online, data)
        elif screen == 2:
            trades(stdscr, data, online)
        elif screen == 3:
            account(stdscr, online)
        else:
            settings(stdscr, mode, online)

        stdscr.refresh()

        key = stdscr.getch()

        if key in (ord("q"), ord("Q")):
            break

        if key in (
            ord("1"),
            ord("2"),
            ord("3"),
            ord("4"),
            ord("5"),
        ):
            screen = int(chr(key)) - 1
            continue

        if key in (ord("r"), ord("R")):
            refresh()
            continue

        if key in (ord("m"), ord("M")):
            mode_index = (mode_index + 1) % len(MODES)
            mode = MODES[mode_index]
            refresh()
            continue

        if key == curses.KEY_LEFT:
            mode_index = (mode_index - 1) % len(MODES)
            mode = MODES[mode_index]
            refresh()
            continue

        if key == curses.KEY_RIGHT:
            mode_index = (mode_index + 1) % len(MODES)
            mode = MODES[mode_index]
            refresh()


def main():
    curses.wrapper(run)


if __name__ == "__main__":
    main()
