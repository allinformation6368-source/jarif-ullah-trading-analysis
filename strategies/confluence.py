def calculate_confluence(structure, sweeps, mss, fvgs, order_blocks, pd, displacement):
    score = 0
    reasons = []

    if structure['bias'] == 'BULLISH':
        score += 2
        reasons.append('Bullish market structure')
    elif structure['bias'] == 'BEARISH':
        score -= 2
        reasons.append('Bearish market structure')

    bullish_sweeps = sum(1 for s in sweeps if s['type'] == 'SSL_SWEEP')
    bearish_sweeps = sum(1 for s in sweeps if s['type'] == 'BSL_SWEEP')
    if bullish_sweeps:
        score += 1
        reasons.append('Sell-side liquidity sweep')
    if bearish_sweeps:
        score -= 1
        reasons.append('Buy-side liquidity sweep')

    bullish_mss = sum(1 for m in mss if m['type'] == 'BULLISH_MSS')
    bearish_mss = sum(1 for m in mss if m['type'] == 'BEARISH_MSS')
    if bullish_mss:
        score += 3
        reasons.append('Bullish MSS confirmed')
    if bearish_mss:
        score -= 3
        reasons.append('Bearish MSS confirmed')

    bullish_fvg = sum(1 for f in fvgs if f['type'] == 'BULLISH_FVG')
    bearish_fvg = sum(1 for f in fvgs if f['type'] == 'BEARISH_FVG')
    if bullish_fvg:
        score += 1
        reasons.append('Bullish FVG present')
    if bearish_fvg:
        score -= 1
        reasons.append('Bearish FVG present')

    bullish_ob = sum(1 for o in order_blocks if o['type'] == 'BULLISH_OB')
    bearish_ob = sum(1 for o in order_blocks if o['type'] == 'BEARISH_OB')
    if bullish_ob:
        score += 1
        reasons.append('Bullish order block present')
    if bearish_ob:
        score -= 1
        reasons.append('Bearish order block present')

    if pd is not None:
        if pd['zone'] == 'DISCOUNT':
            score += 1
            reasons.append('Price in discount')
        elif pd['zone'] == 'PREMIUM':
            score -= 1
            reasons.append('Price in premium')

    bullish_displacement = sum(1 for d in displacement if d['type'] == 'BULLISH')
    bearish_displacement = sum(1 for d in displacement if d['type'] == 'BEARISH')
    if bullish_displacement:
        score += 1
        reasons.append('Bullish displacement')
    if bearish_displacement:
        score -= 1
        reasons.append('Bearish displacement')

    if score >= 4:
        signal = 'LONG'
    elif score <= -4:
        signal = 'SHORT'
    else:
        signal = 'WAIT'

    confidence = min(abs(score) * 10, 100)
    return {'signal': signal, 'score': score, 'confidence': confidence, 'reasons': reasons}
