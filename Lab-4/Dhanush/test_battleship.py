"""Tests for the README's 'Required testing' list. Run: python -m unittest -v"""
import builtins
import contextlib
import io
import random
import unittest

from ai import AI
from board import Board, HIT, MISS, SUNK, parse_coord, format_coord
from game import Battleship


def fixed_game(seed=0):
    """Game with known ship positions on both boards."""
    g = Battleship(seed)
    for b in (g.player, g.enemy):
        b.fleet.clear()
        b.shots.clear()
        b.place_ship("Cruiser", {(0, 0), (0, 1), (0, 2)})
        b.place_ship("Destroyer", {(2, 2), (3, 2)})
    return g


def play(game, inputs):
    """Run the game loop with scripted input, return printed output."""
    feed = iter(inputs)
    out = io.StringIO()
    old = builtins.input
    builtins.input = lambda prompt="": next(feed)
    try:
        with contextlib.redirect_stdout(out):
            game.run()
    finally:
        builtins.input = old
    return out.getvalue()


class CoordinateTests(unittest.TestCase):
    def test_round_trip(self):
        self.assertEqual(parse_coord("2,3"), (1, 2))
        self.assertEqual(format_coord((1, 2)), "2,3")

    def test_every_ship_cell_hits_every_empty_cell_misses(self):
        g = fixed_game()
        ships = g.enemy.ships
        for r in range(Board.SIZE):
            for c in range(Board.SIZE):
                result, _ = g.enemy.fire((r, c))
                self.assertEqual(result != MISS, (r, c) in ships, (r, c))

    def test_ai_shot_uses_board_coordinates(self):
        g = fixed_game()
        g.ai.tried = {(r, c) for r in range(6) for c in range(6)} - {(0, 0)}
        pos = g.ai.choose()
        self.assertEqual(pos, (0, 0))
        self.assertEqual(g.player.fire(pos)[0], HIT)


class FleetTests(unittest.TestCase):
    def test_hit_miss_sink_and_win(self):
        g = fixed_game()
        self.assertEqual(g.enemy.fire((0, 0))[0], HIT)
        self.assertEqual(g.enemy.fire((5, 5))[0], MISS)
        self.assertEqual(g.enemy.fire((0, 1))[0], HIT)
        result, ship = g.enemy.fire((0, 2))
        self.assertEqual((result, ship.name), (SUNK, "Cruiser"))
        self.assertFalse(g.enemy.all_sunk())
        g.enemy.fire((2, 2))
        self.assertEqual(g.enemy.fire((3, 2))[0], SUNK)
        self.assertTrue(g.enemy.all_sunk())

    def test_repeated_shot_rejected(self):
        b = Board()
        b.place_ship("A", {(1, 1)})
        b.fire((1, 1))
        with self.assertRaises(ValueError):
            b.fire((1, 1))

    def test_random_fleet_is_valid(self):
        for seed in range(200):
            b = Board()
            b.place_fleet_randomly(random.Random(seed))
            self.assertEqual(len(b.fleet), 3)
            self.assertEqual(len(b.ships), sum(n for _, n in Board.FLEET))
            self.assertTrue(all(Board.in_bounds(p) for p in b.ships))

    def test_overlap_and_out_of_bounds_placement_rejected(self):
        b = Board()
        b.place_ship("A", {(0, 0)})
        with self.assertRaises(ValueError):
            b.place_ship("B", {(0, 0)})
        with self.assertRaises(ValueError):
            b.place_ship("C", {(6, 0)})


class AITests(unittest.TestCase):
    def test_never_repeats_and_handles_full_board(self):
        ai = AI(6, random.Random(1))
        seen = set()
        for _ in range(36):
            p = ai.choose()
            self.assertNotIn(p, seen)
            seen.add(p)
        self.assertIsNone(ai.choose())

    def test_targets_adjacent_cells_after_hit(self):
        ai = AI(6, random.Random(2))
        ai.tried.add((2, 2))
        ai.record((2, 2), HIT)
        for _ in range(4):
            p = ai.choose()
            self.assertEqual(abs(p[0] - 2) + abs(p[1] - 2), 1)
            ai.record(p, MISS)

    def test_corner_hit_stays_in_bounds(self):
        ai = AI(6, random.Random(3))
        ai.tried.add((0, 0))
        ai.record((0, 0), HIT)
        self.assertIn(ai.choose(), {(0, 1), (1, 0)})

    def test_ai_sinks_every_fleet_without_repeats(self):
        for seed in range(100):
            b = Board()
            b.place_fleet_randomly(random.Random(seed))
            ai = AI(6, random.Random(seed))
            while not b.all_sunk():
                p = ai.choose()
                r, s = b.fire(p)  # would raise on a repeat
                ai.record(p, r, s)


class GameLoopTests(unittest.TestCase):
    def test_invalid_inputs_and_quit(self):
        out = play(fixed_game(), ["abc", "7,1", "0,3", "1", "q"])
        self.assertIn("Use row,col", out)
        self.assertEqual(out.count("Outside board"), 2)
        self.assertIn("Bye.", out)
        self.assertNotIn("fired at", out)

    def test_repeated_shot_does_not_cost_a_turn(self):
        out = play(fixed_game(), ["1,1", "1,1", "q"])
        self.assertEqual(out.count("You fired at"), 1)
        self.assertEqual(out.count("AI fired at"), 1)
        self.assertIn("Already fired there", out)

    def test_feedback_once_per_shot_and_win(self):
        out = play(fixed_game(), ["1,1", "1,2", "1,3", "3,3", "4,3"])
        self.assertEqual(out.count("You fired at"), 5)
        self.assertEqual(out.count("AI fired at"), 4)  # game ends before AI's 5th shot
        self.assertIn("sunk the Cruiser", out)
        self.assertIn("You win!", out)


if __name__ == "__main__":
    unittest.main()
