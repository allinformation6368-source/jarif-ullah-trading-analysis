from data.scanner.scanner_config import SCANNER_PAIRS


class RoundRobinScanner:
    """
    Deterministic one-pair-at-a-time scanner.

    No parallel pair requests are generated here.
    """

    def __init__(self, pairs=None):
        selected = tuple(pairs or SCANNER_PAIRS)

        if len(selected) != 8:
            raise ValueError("Scanner must contain exactly 8 pairs")

        if len(set(selected)) != 8:
            raise ValueError("Scanner pairs must be unique")

        self.pairs = selected
        self.index = 0

    def next_pair(self):
        pair = self.pairs[self.index]
        self.index = (self.index + 1) % len(self.pairs)
        return pair

    def peek_pair(self):
        return self.pairs[self.index]

    def reset(self):
        self.index = 0

    def snapshot(self):
        return {
            "pairs": list(self.pairs),
            "index": self.index,
            "next_pair": self.peek_pair(),
        }
