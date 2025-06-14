#!/usr/bin/env python3
"""
AI Player for Vibe Tetris.
This module provides AI functionality to automatically play Tetris in demo mode.
The AI evaluates possible moves and selects the best one based on heuristics
like avoiding holes, minimizing height differences, and clearing lines.
"""
import random
import copy
from constants import (
    GRID_WIDTH, GRID_HEIGHT
)


class TetrisAI:
    """
    AI player for Tetris that evaluates possible moves and selects the best one.
    Can make deliberate mistakes based on a difficulty setting.
    """

    def __init__(self, game, mistake_chance=0.1):
        self.game = game
        self.next_move = None
        self.move_queue = []
        self.thinking_time = 0
        self.mistake_chance = mistake_chance  # Chance to make a sub-optimal move

    def decide_move(self):
        """
        Decide the next series of moves for the current piece.
        Returns a queue of moves to make.
        """
        if self.move_queue:
            return self.move_queue.pop(0)

        # Get current piece information
        piece = self.game.current_piece

        # Evaluate all possible positions (x position and rotation)
        best_score = float('-inf')
        best_moves = None

        # For each rotation
        for rotation in range(4):  # Try all 4 rotations
            # Create a copy for simulation
            test_piece = copy.deepcopy(piece)
            rotation_moves = []

            # Apply rotation
            for _ in range(rotation):
                if test_piece.rotate(self.game.board):
                    rotation_moves.append('rotate')
                else:
                    break

            # For each x position
            for target_x in range(-2, GRID_WIDTH):
                # Reset horizontal position for this test
                test_piece = copy.deepcopy(piece)
                for _ in range(rotation):
                    test_piece.rotate(self.game.board)

                # Calculate moves to reach target_x
                x_moves = []
                while test_piece.x < target_x:
                    if test_piece.move(1, 0, self.game.board):
                        x_moves.append('right')
                    else:
                        break

                while test_piece.x > target_x:
                    if test_piece.move(-1, 0, self.game.board):
                        x_moves.append('left')
                    else:
                        break

                # If we couldn't reach the target position, skip
                if test_piece.x != target_x:
                    continue

                # Simulate dropping
                test_board = copy.deepcopy(self.game.board)
                while test_piece.move(0, 1, test_board):
                    pass

                # Lock the piece in our test board
                for x, y in test_piece.get_rotated_shape():
                    board_x = test_piece.x + x
                    board_y = test_piece.y + y

                    if 0 <= board_y < GRID_HEIGHT and 0 <= board_x < GRID_WIDTH:
                        test_board[board_y][board_x] = test_piece.color

                # Evaluate position
                score = self._evaluate_position(test_board)

                if score > best_score:
                    best_score = score
                    # Full sequence: rotations, movements, then hard drop
                    best_moves = rotation_moves + x_moves + ['drop']

        # If we found a good move, queue it up
        if best_moves:
            # Introduce a chance of making a mistake based on difficulty setting
            if random.random() < self.mistake_chance:
                # Make a mistake by using a random move or a suboptimal move
                mistake_options = ['left', 'right', 'rotate', 'drop']
                
                if random.choice([True, False]):
                    # Either choose a completely random move
                    self.move_queue = [random.choice(mistake_options)]
                else:
                    # Or choose a suboptimal move by evaluating more positions and taking a worse one
                    # For example, here we're just rotating the piece randomly
                    self.move_queue = ['rotate'] + best_moves[1:] if len(best_moves) > 1 else ['drop']
            else:
                # No mistake, use the best move
                self.move_queue = best_moves
                
            return self.move_queue.pop(0)
        else:
            # Fallback - just drop
            return 'drop'

    def _evaluate_position(self, board):
        """
        Evaluate a board position based on several heuristics.
        Returns a score - higher is better.
        """
        score = 0

        # 1. Count holes (empty cells with filled cells above them)
        holes = self._count_holes(board)
        score -= holes * 8  # Heavily penalize holes

        # 2. Height of each column
        heights = [self._get_column_height(board, x)
                   for x in range(GRID_WIDTH)]
        max_height = max(heights) if heights else 0

        # Penalize high stacks
        score -= max_height * 2

        # 3. Complete lines
        complete_lines = self._count_complete_lines(board)
        score += complete_lines * 20  # Reward complete lines

        # 4. Bumpiness (difference between adjacent columns)
        bumpiness = sum(abs(heights[i] - heights[i+1])
                        for i in range(len(heights)-1))
        score -= bumpiness * 2  # Penalize unevenness

        # 5. Well depth (encourages wells for I-pieces)
        wells = self._detect_wells(heights)
        score += wells * 3

        # 6. Landing height (prefer low placing of pieces)
        score -= max_height * 1.5

        return score

    def _count_holes(self, board):
        """Count empty cells with filled cells above them."""
        holes = 0
        for x in range(GRID_WIDTH):
            block_found = False
            for y in range(GRID_HEIGHT):
                if board[y][x] is not None:
                    block_found = True
                elif block_found:
                    holes += 1
        return holes

    def _get_column_height(self, board, x):
        """Get the height of a specific column."""
        for y in range(GRID_HEIGHT):
            if board[y][x] is not None:
                return GRID_HEIGHT - y
        return 0

    def _count_complete_lines(self, board):
        """Count complete lines in the board."""
        return sum(1 for y in range(GRID_HEIGHT) if all(board[y][x] is not None for x in range(GRID_WIDTH)))

    def _detect_wells(self, heights):
        """Detect and score wells (good for I-pieces)."""
        wells = 0
        # Check internal wells
        for i in range(1, len(heights) - 1):
            if heights[i] + 3 < heights[i-1] and heights[i] + 3 < heights[i+1]:
                wells += 1
        # Check edge wells
        if len(heights) > 0 and heights[0] + 3 < heights[1]:
            wells += 1
        if len(heights) > 1 and heights[-1] + 3 < heights[-2]:
            wells += 1
        return wells

    def execute_move(self):
        """
        Execute the next move from the AI's decision.
        Returns the move that was executed.
        """
        move = self.decide_move()

        if move == 'left':
            self.game.current_piece.move(-1, 0, self.game.board)
        elif move == 'right':
            self.game.current_piece.move(1, 0, self.game.board)
        elif move == 'rotate':
            self.game.current_piece.rotate(self.game.board)
        elif move == 'drop':
            self.game.hard_drop()

        return move
