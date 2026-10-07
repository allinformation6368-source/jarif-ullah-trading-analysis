from strategies.market_structure import analyze_structure
from strategies.liquidity import detect_liquidity_pools
from strategies.liquidity_sweep import detect_liquidity_sweeps
from strategies.bos_mss import detect_bos_mss
from strategies.fvg import detect_fvg
from strategies.order_blocks import detect_order_blocks
from strategies.premium_discount import calculate_premium_discount
from strategies.displacement import detect_displacement
from strategies.confluence import calculate_confluence


def analyze_timeframe(candles):
    structure = analyze_structure(candles)

    liquidity = detect_liquidity_pools(
        structure["swings"]
    )

    sweeps = detect_liquidity_sweeps(
        candles,
        liquidity
    )

    mss = detect_bos_mss(
        candles,
        structure["swings"],
        sweeps
    )

    fvgs = detect_fvg(candles)

    order_blocks = detect_order_blocks(candles)

    premium_discount = calculate_premium_discount(
        candles
    )

    displacement = detect_displacement(candles)

    confluence = calculate_confluence(
        structure,
        sweeps,
        mss,
        fvgs,
        order_blocks,
        premium_discount,
        displacement
    )

    return {
        "structure": structure,
        "liquidity": liquidity,
        "sweeps": sweeps,
        "mss": mss,
        "fvgs": fvgs,
        "order_blocks": order_blocks,
        "premium_discount": premium_discount,
        "displacement": displacement,
        "confluence": confluence,
    }
