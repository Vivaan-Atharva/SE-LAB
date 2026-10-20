import random

from board import MISS, SUNK


class AI:
    """Hunt/target AI.

    Hunt mode: pick a random untried cell.
    Target mode: after a hit, try untried cells next to unsunk hits first.
    choose() is side-effect free apart from remembering the cell it picked;
    the game reports the real result back through record().
    """

    def __init__(self, size=6, rng=None):
        self.size = size
        self.rng = rng or random.Random()
        self.tried = set()
        self.open_hits = set()  # hits on ships that are not sunk yet

    def _untried(self, pos):
        r, c = pos
        return 0 <= r < self.size and 0 <= c < self.size and pos not in self.tried

    def _neighbours(self, pos):
        r, c = pos
        return [p for p in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)) if self._untried(p)]

    def candidates(self):
        """Cells the AI would consider next, best first group only."""
        near = {n for h in self.open_hits for n in self._neighbours(h)}
        if near:
            return sorted(near)
        return [(r, c) for r in range(self.size) for c in range(self.size)
                if (r, c) not in self.tried]

    def choose(self):
        """Return an untried (row, col) tuple, or None if the board is exhausted."""
        options = self.candidates()
        if not options:
            return None
        pos = self.rng.choice(options)
        self.tried.add(pos)
        return pos

    def record(self, pos, result, ship=None):
        """Feed back the real outcome of the shot at pos."""
        if result == MISS:
            return
        self.open_hits.add(pos)
        if result == SUNK and ship is not None:
            self.open_hits -= set(ship.cells)
