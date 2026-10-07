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

    # MSS is the primary directional anchor.
    # If MSS is unavailable, use market structure bias.
    if bullish_mss and not bearish_mss:
        direction = 'BULLISH'
    elif bearish_mss and not bullish_mss:
        direction = 'BEARISH'
    elif structure['bias'] in ('BULLISH', 'BEARISH'):
        direction = structure['bias']
    else:
        direction = None

    # Count only the latest FVG matching the setup direction.
    if direction and fvgs:
        matching_fvgs = [
            f for f in fvgs
            if (
                direction == 'BULLISH'
                and f['type'] == 'BULLISH_FVG'
            )
            or (
                direction == 'BEARISH'
                and f['type'] == 'BEARISH_FVG'
            )
        ]

        if matching_fvgs:
            latest_fvg = matching_fvgs[-1]
            score += 1 if direction == 'BULLISH' else -1
            reasons.append(
                'Bullish FVG present'
                if direction == 'BULLISH'
                else 'Bearish FVG present'
            )

    # Count only the latest Order Block matching the setup direction.
    if direction and order_blocks:
        matching_obs = [
            o for o in order_blocks
            if (
                direction == 'BULLISH'
                and o['type'] == 'BULLISH_OB'
            )
            or (
                direction == 'BEARISH'
                and o['type'] == 'BEARISH_OB'
            )
        ]

        if matching_obs:
            latest_ob = matching_obs[-1]
            score += 1 if direction == 'BULLISH' else -1
            reasons.append(
                'Bullish order block present'
                if direction == 'BULLISH'
                else 'Bearish order block present'
            )

    if pd is not None:
        if pd['zone'] == 'DISCOUNT':
            score += 1
            reasons.append('Price in discount')
        elif pd['zone'] == 'PREMIUM':
            score -= 1
            reasons.append('Price in premium')

    # Count only the latest displacement matching the setup direction.
    if direction and displacement:
        matching_displacements = [
            d for d in displacement
            if (
                direction == 'BULLISH'
                and d['type'] == 'BULLISH'
            )
            or (
                direction == 'BEARISH'
                and d['type'] == 'BEARISH'
            )
        ]

        if matching_displacements:
            latest_displacement = matching_displacements[-1]
            score += 1 if direction == 'BULLISH' else -1
            reasons.append(
                'Bullish displacement'
                if direction == 'BULLISH'
                else 'Bearish displacement'
            )

    if score >= 4:
        signal = 'LONG'
    elif score <= -4:
        signal = 'SHORT'
    else:
        signal = 'WAIT'

    confidence = min(abs(score) * 10, 100)

    return {
        'signal': signal,
        'score': score,
        'confidence': confidence,
        'reasons': reasons
    }
