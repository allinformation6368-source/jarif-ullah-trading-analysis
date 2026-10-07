from analysis.mtf_confluence import calculate_mtf_confluence


aligned = {
    "5m": {"confluence": {"signal": "LONG", "score": 10}},
    "15m": {"confluence": {"signal": "LONG", "score": 10}},
    "1h": {"confluence": {"signal": "LONG", "score": 10}},
}

entry_conflict = {
    "5m": {"confluence": {"signal": "SHORT", "score": -10}},
    "15m": {"confluence": {"signal": "LONG", "score": 10}},
    "1h": {"confluence": {"signal": "LONG", "score": 10}},
}


aligned_result = calculate_mtf_confluence(aligned)
conflict_result = calculate_mtf_confluence(entry_conflict)


assert aligned_result["signal"] == "LONG"
assert aligned_result["score"] == 60
assert aligned_result["confidence"] == 100

assert conflict_result["signal"] == "LONG"
assert conflict_result["score"] == 40
assert conflict_result["confidence"] == 67

assert aligned_result["confidence"] > conflict_result["confidence"]

print("MTF ENTRY QUALITY TEST: SUCCESS")
print(
    "Aligned:",
    aligned_result["signal"],
    aligned_result["score"],
    aligned_result["confidence"],
)
print(
    "Entry conflict:",
    conflict_result["signal"],
    conflict_result["score"],
    conflict_result["confidence"],
)
