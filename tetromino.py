#!/usr/bin/env python3
"""
Tetromino class for Vibe Tetris.
"""
import random
import pygame
from constants import (
    TETROMINOS, GRID_WIDTH, GRID_HEIGHT, GRID_SIZE,
    GAME_AREA_START_X, GAME_AREA_START_Y
)


class PieceRandomizer:
    """
    Implements a bag-based randomizer for Tetromino pieces.
    Each piece appears once before any piece appears again,
    with occasional random repeats for variety.
    """

    def __init__(self, repeat_chance=0.1):
        """
        Initialize the randomizer with all available pieces.

        Args:
            repeat_chance: Probability (0-1) of allowing a repeated piece
        """
        self.all_pieces = list(TETROMINOS.keys())
        self.bag = list(self.all_pieces)  # Start with a full bag
        self.last_piece = None
        self.repeat_chance = repeat_chance
        random.shuffle(self.bag)  # Randomize initial bag

    def next_piece(self):
        """Get the next random piece using the bag system."""
        # Special case: if we're allowed a repeat and random chance hits
        if (self.last_piece is not None and
                random.random() < self.repeat_chance):
            return self.last_piece

        # If the bag is empty, refill it with all pieces except last chosen
        if not self.bag:
            self.bag = [p for p in self.all_pieces if p != self.last_piece]
            random.shuffle(self.bag)

        # Get a piece from the bag
        piece = self.bag.pop()
        self.last_piece = piece
        return piece


class Tetromino:
    """Class representing a tetromino (falling piece)"""

    def __init__(self, name=None, randomizer=None):
        if name is None:
            if randomizer:
                name = randomizer.next_piece()
            else:
                name = random.choice(list(TETROMINOS.keys()))
        self.name = name
        self.shape = TETROMINOS[name]['shape']
        self.color = TETROMINOS[name]['color']
        self.rotation = 0
        # Start position (center top of the grid)
        self.x = GRID_WIDTH // 2 - 1
        self.y = 0

    def rotate(self, board):
        """Rotate the tetromino clockwise with wall kicks"""
        old_rotation = self.rotation
        old_x, old_y = self.x, self.y

        # Perform rotation
        self.rotation = (self.rotation + 1) % 4

        # Wall kick data - a series of offsets to try for each rotation
        # (dx, dy) pairs to try in order
        wall_kick_offsets = [
            (0, 0),   # Try the normal rotation first
            (1, 0),   # Try shifting right
            (-1, 0),  # Try shifting left
            (0, -1),  # Try shifting up
            (1, -1),  # Try up-right
            (-1, -1),  # Try up-left
            (0, 2),   # Try shifting down 2 (for I piece)
        ]

        # Special case for I piece which needs different wall kicks
        if self.name == 'I':
            # Add more complex offset patterns specific to I piece
            wall_kick_offsets.extend([
                (2, 0),  # Try shifting right 2
                (-2, 0),  # Try shifting left 2
            ])

        # Try each offset until we find a valid position
        for dx, dy in wall_kick_offsets:
            self.x += dx
            self.y += dy

            if self.is_valid_position(board):
                return True  # Successfully rotated with this offset

            # Reset position to try next offset
            self.x, self.y = old_x, old_y

        # If no valid position was found, revert rotation
        self.rotation = old_rotation
        return False

    def get_rotated_shape(self):
        """Get the shape with the current rotation applied"""
        if self.rotation == 0:
            return self.shape
        elif self.rotation == 1:
            return [(-y, x) for x, y in self.shape]
        elif self.rotation == 2:
            return [(-x, -y) for x, y in self.shape]
        elif self.rotation == 3:
            return [(y, -x) for x, y in self.shape]

    def move(self, dx, dy, board):
        """Try to move the tetromino by dx, dy"""
        old_x, old_y = self.x, self.y
        self.x += dx
        self.y += dy

        # Check if move is valid
        if not self.is_valid_position(board):
            self.x, self.y = old_x, old_y
            return False
        return True

    def is_valid_position(self, board):
        """Check if the current position is valid"""
        for x, y in self.get_rotated_shape():
            board_x = self.x + x
            board_y = self.y + y

            # Out of bounds check
            if (board_x < 0 or board_x >= GRID_WIDTH or
                    board_y < 0 or board_y >= GRID_HEIGHT):
                return False

            # Collision check
            if board_y >= 0 and board[board_y][board_x] is not None:
                return False

        return True

    def get_ghost_position(self, board):
        """Get the position of the ghost piece (where the piece would land)"""
        ghost_x, ghost_y = self.x, self.y

        # Move the ghost piece down until it hits something
        while True:
            ghost_y += 1
            # Check if the ghost piece would be in a valid position
            for x, y in self.get_rotated_shape():
                board_x = ghost_x + x
                board_y = ghost_y + y

                # If out of bounds or collision, return the previous position
                if (board_y >= GRID_HEIGHT or
                    (board_y >= 0 and board_x >= 0 and board_x < GRID_WIDTH and
                     board[board_y][board_x] is not None)):
                    return ghost_x, ghost_y - 1

        return ghost_x, ghost_y

    def draw(self, surface):
        """Draw the tetromino on the surface"""
        for x, y in self.get_rotated_shape():
            # Main block color
            pygame.draw.rect(
                surface,
                self.color,
                (
                    GAME_AREA_START_X + (self.x + x) * GRID_SIZE,
                    GAME_AREA_START_Y + (self.y + y) * GRID_SIZE,
                    GRID_SIZE - 1,
                    GRID_SIZE - 1
                )
            )

            # Highlight (top and left edges)
            highlight_color = tuple(min(c + 70, 255) for c in self.color[:3])
            pygame.draw.line(
                surface,
                highlight_color,
                (GAME_AREA_START_X + (self.x + x) * GRID_SIZE,
                 GAME_AREA_START_Y + (self.y + y) * GRID_SIZE),
                (GAME_AREA_START_X + (self.x + x) * GRID_SIZE,
                 GAME_AREA_START_Y + (self.y + y) * GRID_SIZE + GRID_SIZE - 2),
                2
            )
            pygame.draw.line(
                surface,
                highlight_color,
                (GAME_AREA_START_X + (self.x + x) * GRID_SIZE,
                 GAME_AREA_START_Y + (self.y + y) * GRID_SIZE),
                (GAME_AREA_START_X + (self.x + x) * GRID_SIZE + GRID_SIZE -
                 2, GAME_AREA_START_Y + (self.y + y) * GRID_SIZE),
                2
            )

            # Shadow (bottom and right edges)
            shadow_color = tuple(max(c - 70, 0) for c in self.color[:3])
            pygame.draw.line(
                surface,
                shadow_color,
                (GAME_AREA_START_X + (self.x + x) * GRID_SIZE + GRID_SIZE -
                 2, GAME_AREA_START_Y + (self.y + y) * GRID_SIZE),
                (GAME_AREA_START_X + (self.x + x) * GRID_SIZE + GRID_SIZE - 2,
                 GAME_AREA_START_Y + (self.y + y) * GRID_SIZE + GRID_SIZE - 2),
                2
            )
            pygame.draw.line(
                surface,
                shadow_color,
                (GAME_AREA_START_X + (self.x + x) * GRID_SIZE,
                 GAME_AREA_START_Y + (self.y + y) * GRID_SIZE + GRID_SIZE - 2),
                (GAME_AREA_START_X + (self.x + x) * GRID_SIZE + GRID_SIZE - 2,
                 GAME_AREA_START_Y + (self.y + y) * GRID_SIZE + GRID_SIZE - 2),
                2
            )

    def draw_ghost(self, surface, board):
        """Draw the ghost of the tetromino (showing where it will land)"""
        ghost_x, ghost_y = self.get_ghost_position(board)

        for x, y in self.get_rotated_shape():
            ghost_color = (*[c // 3 for c in self.color[:3]], 128)

            # Semi-transparent fill
            pygame.draw.rect(
                surface,
                ghost_color,
                (
                    GAME_AREA_START_X + (ghost_x + x) * GRID_SIZE,
                    GAME_AREA_START_Y + (ghost_y + y) * GRID_SIZE,
                    GRID_SIZE - 1,
                    GRID_SIZE - 1
                ),
                0  # Filled
            )

            # Add subtle 3D effect with lighter border
            border_color = (*[min(c + 40, 255) for c in ghost_color[:3]], 160)
            pygame.draw.rect(
                surface,
                border_color,
                (
                    GAME_AREA_START_X + (ghost_x + x) * GRID_SIZE,
                    GAME_AREA_START_Y + (ghost_y + y) * GRID_SIZE,
                    GRID_SIZE - 1,
                    GRID_SIZE - 1
                ),
                1  # Only draw the outline
            )
