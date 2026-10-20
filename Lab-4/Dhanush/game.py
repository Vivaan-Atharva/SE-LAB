import random

from board import Board, parse_coord, format_coord, HIT, SUNK
from ai import AI


class Battleship:
    def __init__(self, seed=None):
        self.rng = random.Random(seed)
        self.player = Board()
        self.enemy = Board()
        self.ai = AI(Board.SIZE, rng=self.rng)
        self._setup()

    def _setup(self):
        self.player.place_fleet_randomly(self.rng)
        self.enemy.place_fleet_randomly(self.rng)

    def show(self):
        left = self.player.render(reveal=True)
        right = self.enemy.render(reveal=False)
        print(f"\n{'Your fleet':<17}   Enemy waters")
        for a, b in zip(left, right):
            print(f"{a:<17}   {b}")
        print("Enemy ships afloat:", len(self.enemy.ships_afloat()),
              "| Your ships afloat:", len(self.player.ships_afloat()))
        print("Enter row,col (e.g. 2,3) or q to quit.")

    @staticmethod
    def shot_message(shooter, pos, result, ship):
        """The single feedback line for one real shot."""
        where = format_coord(pos)
        if result == SUNK:
            return f"{shooter} fired at {where}: HIT - sunk the {ship.name}!"
        return f"{shooter} fired at {where}: " + ("HIT!" if result == HIT else "MISS.")

    def take_shot(self, shooter, target, pos):
        """Fire one real shot and report it exactly once. Returns (result, ship)."""
        result, ship = target.fire(pos)
        print(self.shot_message(shooter, pos, result, ship))
        return result, ship

    def read_player_target(self):
        """Prompt until a valid new target is entered. Returns a tuple, or None to quit."""
        while True:
            raw = input("> ").strip().lower()
            if raw in ("q", "quit"):
                return None
            try:
                pos = parse_coord(raw)
            except ValueError:
                print("Use row,col (e.g. 2,3).")
                continue
            if not Board.in_bounds(pos):
                print(f"Outside board. Rows and columns go from 1 to {Board.SIZE}.")
                continue
            if pos in self.enemy.shots:
                print("Already fired there. Pick another cell.")
                continue
            return pos

    def run(self):
        print("Battleship")
        while True:
            self.show()
            pos = self.read_player_target()
            if pos is None:
                print("Bye.")
                return
            self.take_shot("You", self.enemy, pos)
            if self.enemy.all_sunk():
                print("You sank the whole enemy fleet. You win!")
                return

            # Candidate selection inside the AI prints nothing; only the real shot is reported.
            ai_pos = self.ai.choose()
            if ai_pos is None:
                print("The AI has no cells left to fire at.")
                return
            result, ship = self.take_shot("AI", self.player, ai_pos)
            self.ai.record(ai_pos, result, ship)
            if self.player.all_sunk():
                print("The AI sank your whole fleet. You lose.")
                return
