import random

MISS, HIT, SUNK = "miss", "hit", "sunk"


class Ship:
    def __init__(self, name, cells):
        self.name = name
        self.cells = frozenset(cells)
        self.hits = set()

    def is_sunk(self):
        return self.cells <= self.hits


class Board:
    """Ship and shot state. Every coordinate is a 0-based (row, col) tuple."""

    SIZE = 6
    FLEET = [("Cruiser", 3), ("Destroyer", 2), ("Submarine", 2)]

    def __init__(self):
        self.fleet = []
        self.shots = set()

    @classmethod
    def in_bounds(cls, pos):
        return 0 <= pos[0] < cls.SIZE and 0 <= pos[1] < cls.SIZE

    @property
    def ships(self):
        """All occupied cells."""
        return {cell for ship in self.fleet for cell in ship.cells}

    def place_ship(self, name, cells):
        cells = set(cells)
        if not all(self.in_bounds(c) for c in cells):
            raise ValueError(f"{name} is outside the board")
        if cells & self.ships:
            raise ValueError(f"{name} overlaps another ship")
        self.fleet.append(Ship(name, cells))

    def place_fleet_randomly(self, rng=random):
        for name, length in self.FLEET:
            while True:
                horizontal = rng.random() < 0.5
                r = rng.randrange(self.SIZE - (0 if horizontal else length - 1))
                c = rng.randrange(self.SIZE - (length - 1 if horizontal else 0))
                cells = {(r, c + i) if horizontal else (r + i, c) for i in range(length)}
                if not cells & self.ships:
                    self.place_ship(name, cells)
                    break

    def fire(self, pos):
        """Record a shot. Returns (MISS|HIT|SUNK, ship or None).

        Raises ValueError for a repeated or out-of-bounds shot.
        """
        if not self.in_bounds(pos):
            raise ValueError("outside board")
        if pos in self.shots:
            raise ValueError("already fired there")
        self.shots.add(pos)
        for ship in self.fleet:
            if pos in ship.cells:
                ship.hits.add(pos)
                return (SUNK if ship.is_sunk() else HIT), ship
        return MISS, None

    def all_sunk(self):
        return bool(self.fleet) and all(s.is_sunk() for s in self.fleet)

    def ships_afloat(self):
        return [s for s in self.fleet if not s.is_sunk()]

    def render(self, reveal):
        """Grid view. reveal=True shows ship positions (your own board)."""
        lines = ["   " + " ".join(str(c + 1) for c in range(self.SIZE))]
        for r in range(self.SIZE):
            row = []
            for c in range(self.SIZE):
                pos = (r, c)
                if pos in self.shots:
                    row.append("X" if pos in self.ships else "o")
                elif reveal and pos in self.ships:
                    row.append("S")
                else:
                    row.append(".")
            lines.append(f"{r + 1:>2} " + " ".join(row))
        return lines


def parse_coord(raw):
    """Turn user text like '2,3' (1-based) into an internal (1, 2) tuple."""
    r, c = map(int, raw.split(","))
    return (r - 1, c - 1)


def format_coord(pos):
    """Turn an internal (1, 2) tuple back into user-facing '2,3'."""
    return f"{pos[0] + 1},{pos[1] + 1}"
