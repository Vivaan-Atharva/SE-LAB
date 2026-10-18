"""
GameEngine: owns the board, turn state, round-end logic and the scoreboard.

You (the player) always play X and click to move. The computer always
plays O and moves automatically right after you, using a simple
random-move AI (see game/ai.py).
"""

from game.rules import check_winner, is_board_full
from game.renderer import board_pos_to_cell
from game.ai import choose_move

HUMAN_SYMBOL = 'X'
COMPUTER_SYMBOL = 'O'


class GameEngine:
    def __init__(self):
        # Task 2: the scoreboard is created once and survives new rounds
        self.scores = {'X': 0, 'O': 0, 'Draw': 0}
        self.new_round()

    def new_round(self):
        """Clear the board only - the scoreboard is kept."""
        self.board = [[None] * 3 for _ in range(3)]
        self.current_player = 'X'
        self.round_over = False
        self.winner = None   # 'X', 'O', or None (meaning draw, only valid when round_over)

    def reset_match(self):
        """Clear the board AND the scoreboard."""
        self.scores = {'X': 0, 'O': 0, 'Draw': 0}
        self.new_round()

    def handle_click(self, pos):
        if self.round_over:
            return   # Task 1: no moves once the round has ended
        if self.current_player != HUMAN_SYMBOL:
            return   # not your turn - the computer is about to move (or already has)
        cell = board_pos_to_cell(pos)
        if cell is None:
            return
        row, col = cell
        if self.board[row][col] is not None:
            return   # Task 3: occupied cell - reject, board and turn unchanged
        self.board[row][col] = self.current_player
        self.check_round_end()
        self.current_player = 'O' if self.current_player == 'X' else 'X'
        self._maybe_take_computer_turn()

    def _maybe_take_computer_turn(self):
        if self.round_over or self.current_player != COMPUTER_SYMBOL:
            return
        move = choose_move(self.board)
        if move is None:
            return
        row, col = move
        self.board[row][col] = self.current_player
        self.check_round_end()
        self.current_player = 'O' if self.current_player == 'X' else 'X'

    def handle_keydown(self, key):
        import pygame
        if key == pygame.K_r:
            self.new_round()      # R: new round, scoreboard kept
        elif key == pygame.K_m:
            self.reset_match()    # M: reset whole match, scoreboard cleared

    def check_round_end(self):
        # Task 1: look for a winner FIRST, only then check for a draw
        winner = check_winner(self.board)
        if winner:
            self.round_over = True
            self.winner = winner
            self.scores[winner] += 1        # Task 2
        elif is_board_full(self.board):
            self.round_over = True
            self.winner = None
            self.scores['Draw'] += 1        # Task 2

    def draw(self, surface, font):
        from game import renderer
        renderer.draw_board(surface, self.board)
        turn_label = "Your turn (X)" if self.current_player == HUMAN_SYMBOL else "Computer's turn (O)"
        renderer.draw_text(surface, font, turn_label, (10, 20))
        s = self.scores   # Task 2: scoreboard always visible
        renderer.draw_text(surface, font, f"X: {s['X']}   O: {s['O']}   Draws: {s['Draw']}", (10, 55))

        if self.round_over:
            text = f"{self.winner} wins!" if self.winner else "Draw!"
            renderer.draw_banner(surface, font, f"{text} R: new round  M: reset")
