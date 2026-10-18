"""
GameEngine: owns the board, turn state, round-end logic and the scoreboard.

You (the player) always play X and click to move. The computer always
plays O and moves automatically right after you, using a simple
random-move AI (see game/ai.py).

Controls:
    Click  - place X in an empty cell
    R      - restart the current round (scoreboard kept)
    M      - reset the whole match (scoreboard cleared)
    1      - X starts the next round
    2      - O (computer) starts the next round
"""

import pygame

from game.rules import check_winner, is_board_full
from game.renderer import board_pos_to_cell
from game.ai import choose_move

HUMAN_SYMBOL = 'X'
COMPUTER_SYMBOL = 'O'


class GameEngine:
    def __init__(self):
        # Task 2: scoreboard lives outside the per-round state
        self.scores = {'X': 0, 'O': 0, 'Draw': 0}
        # Task 4: who starts each round (takes effect on the next round)
        self.starting_player = 'X'
        self.new_round()

    # ---------- round / match control ----------

    def new_round(self):
        """Clear the board only. Scoreboard and starting choice are kept."""
        self.board = [[None] * 3 for _ in range(3)]
        self.current_player = self.starting_player
        self.round_over = False
        self.winner = None   # 'X', 'O', or None (draw, only valid when round_over)
        # If O was chosen to start, the computer makes the first move
        self._maybe_take_computer_turn()

    def reset_match(self):
        """Clear the board AND the scoreboard."""
        self.scores = {'X': 0, 'O': 0, 'Draw': 0}
        self.new_round()

    # ---------- input ----------

    def handle_click(self, pos):
        # Task 1 fix (problem 3): no moves once the round has ended
        if self.round_over:
            return
        if self.current_player != HUMAN_SYMBOL:
            return
        cell = board_pos_to_cell(pos)
        if cell is None:
            return
        row, col = cell
        # Task 3 fix: reject clicks on occupied cells - board and turn unchanged
        if self.board[row][col] is not None:
            return
        self._place(row, col)
        self._maybe_take_computer_turn()

    def handle_keydown(self, key):
        if key == pygame.K_r:
            self.new_round()
        elif key == pygame.K_m:
            self.reset_match()
        elif key == pygame.K_1:
            self.starting_player = 'X'
        elif key == pygame.K_2:
            self.starting_player = 'O'

    # ---------- turn logic ----------

    def _place(self, row, col):
        self.board[row][col] = self.current_player
        self.check_round_end()
        if not self.round_over:
            self.current_player = 'O' if self.current_player == 'X' else 'X'

    def _maybe_take_computer_turn(self):
        if self.round_over or self.current_player != COMPUTER_SYMBOL:
            return
        move = choose_move(self.board)
        if move is None:
            return
        row, col = move
        self._place(row, col)

    def check_round_end(self):
        # Task 1 fix (problem 2): look for a winner BEFORE checking for a full board
        winner = check_winner(self.board)
        if winner:
            self.round_over = True
            self.winner = winner
            self.scores[winner] += 1
        elif is_board_full(self.board):
            self.round_over = True
            self.winner = None
            self.scores['Draw'] += 1

    # ---------- drawing ----------

    def draw(self, surface, font):
        from game import renderer
        renderer.draw_board(surface, self.board)

        if self.round_over:
            turn_label = "Round over"
        elif self.current_player == HUMAN_SYMBOL:
            turn_label = "Your turn (X)"
        else:
            turn_label = "Computer's turn (O)"
        renderer.draw_text(surface, font, turn_label, (10, 8))

        s = self.scores
        renderer.draw_text(surface, font, f"X: {s['X']}   O: {s['O']}   Draws: {s['Draw']}", (10, 38))
        renderer.draw_text(surface, font, f"Next round starts: {self.starting_player} (1=X, 2=O)", (10, 68),
                           color=renderer.COLOR_HINT)

        if self.round_over:
            text = f"{self.winner} wins!" if self.winner else "Draw!"
            renderer.draw_banner(surface, font, text)
        renderer.draw_hint(surface, font, "R: new round   M: reset match")
