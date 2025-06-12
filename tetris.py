#!/usr/bin/env python3
"""
Vibe Tetris - A Tetris clone written in Python using Pygame
"""
import pygame
import sys
import random
import os
import math

# Define pygame constants
QUIT = pygame.QUIT
KEYDOWN = pygame.KEYDOWN
KEYUP = pygame.KEYUP
K_LEFT = pygame.K_LEFT
K_RIGHT = pygame.K_RIGHT
K_DOWN = pygame.K_DOWN
K_UP = pygame.K_UP
K_SPACE = pygame.K_SPACE
K_p = pygame.K_p
K_r = pygame.K_r
K_c = pygame.K_c
K_m = pygame.K_m
K_RETURN = pygame.K_RETURN
K_ESCAPE = pygame.K_ESCAPE

# Game constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
SIDEBAR_WIDTH = 200
GAME_AREA_WIDTH = GRID_SIZE * GRID_WIDTH
GAME_AREA_HEIGHT = GRID_SIZE * GRID_HEIGHT
GAME_AREA_START_X = (SCREEN_WIDTH - SIDEBAR_WIDTH - GAME_AREA_WIDTH) // 2
GAME_AREA_START_Y = (SCREEN_HEIGHT - GAME_AREA_HEIGHT) // 2

# Colors (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
CYAN = (0, 255, 255)    # I piece
BLUE = (0, 0, 255)      # J piece
ORANGE = (255, 165, 0)  # L piece
YELLOW = (255, 255, 0)  # O piece
GREEN = (0, 255, 0)     # S piece
PURPLE = (128, 0, 128)  # T piece
RED = (255, 0, 0)       # Z piece

# Tetromino shapes and their colors
TETROMINOS = {
    'I': {'shape': [(0, 0), (0, 1), (0, 2), (0, 3)], 'color': CYAN},
    'J': {'shape': [(0, 0), (1, 0), (1, 1), (1, 2)], 'color': BLUE},
    'L': {'shape': [(0, 2), (1, 0), (1, 1), (1, 2)], 'color': ORANGE},
    'O': {'shape': [(0, 0), (0, 1), (1, 0), (1, 1)], 'color': YELLOW},
    'S': {'shape': [(0, 1), (0, 2), (1, 0), (1, 1)], 'color': GREEN},
    'T': {'shape': [(0, 1), (1, 0), (1, 1), (1, 2)], 'color': PURPLE},
    'Z': {'shape': [(0, 0), (0, 1), (1, 1), (1, 2)], 'color': RED}
}

# Sound file paths - these would normally be created in your project
SOUND_DIR = "sounds"
MUSIC_FILE = "tetris_theme.mp3"  # Classic tetris theme
MOVE_SOUND = "move.wav"
ROTATE_SOUND = "rotate.wav"
DROP_SOUND = "drop.wav"
CLEAR_SOUND = "clear.wav"
GAME_OVER_SOUND = "game_over.wav"
LEVEL_UP_SOUND = "level_up.wav"


class Tetromino:
    """Class representing a tetromino (falling piece)"""

    def __init__(self, name=None):
        if name is None:
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


class TetrisGame:
    """Main game class"""

    def __init__(self, sounds_enabled=False):
        pygame.init()
        pygame.mixer.init()  # Initialize the mixer for sound
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Vibe Tetris')
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)

        # Game state
        self.board = [[None for _ in range(GRID_WIDTH)]
                      for _ in range(GRID_HEIGHT)]
        self.current_piece = Tetromino()
        self.next_piece = Tetromino()
        self.held_piece = None
        self.can_hold = True
        self.game_over = False
        self.paused = False
        self.score = 0
        self.level = 1
        self.lines_cleared = 0

        # Animation state
        self.lines_to_clear = []
        self.clear_animation_start = 0
        self.clear_animation_duration = 500  # milliseconds
        self.is_animating = False

        # Game speed (milliseconds per drop)
        self.drop_speed = 500
        self.last_drop_time = 0
        self.soft_drop = False

        # Music and sounds
        self.music_playing = False
        self.sounds_enabled = sounds_enabled

        # Try to load sound effects if enabled
        if self.sounds_enabled:
            try:
                # Load sound effects
                self.move_sound = pygame.mixer.Sound(
                    os.path.join(SOUND_DIR, MOVE_SOUND))
                self.rotate_sound = pygame.mixer.Sound(
                    os.path.join(SOUND_DIR, ROTATE_SOUND))
                self.drop_sound = pygame.mixer.Sound(
                    os.path.join(SOUND_DIR, DROP_SOUND))
                self.clear_sound = pygame.mixer.Sound(
                    os.path.join(SOUND_DIR, CLEAR_SOUND))
                self.game_over_sound = pygame.mixer.Sound(
                    os.path.join(SOUND_DIR, GAME_OVER_SOUND))
                self.level_up_sound = pygame.mixer.Sound(
                    os.path.join(SOUND_DIR, LEVEL_UP_SOUND))

                # Start background music
                if os.path.exists(os.path.join(SOUND_DIR, MUSIC_FILE)):
                    pygame.mixer.music.load(
                        os.path.join(SOUND_DIR, MUSIC_FILE))
                    pygame.mixer.music.set_volume(0.5)
                    pygame.mixer.music.play(-1)  # Loop indefinitely
                    self.music_playing = True
            except:
                print("Could not load sound files. Game will continue without sound.")
                self.sounds_enabled = False

    def reset_game(self):
        """Reset the game state"""
        self.board = [[None for _ in range(GRID_WIDTH)]
                      for _ in range(GRID_HEIGHT)]
        self.current_piece = Tetromino()
        self.next_piece = Tetromino()
        self.held_piece = None
        self.can_hold = True
        self.game_over = False
        self.paused = False
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.drop_speed = 500

    def handle_events(self):
        """Handle keyboard and window events"""
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if self.game_over:
                if event.type == KEYDOWN and event.key == K_r:
                    self.reset_game()
                continue

            if event.type == KEYDOWN:
                if event.key == K_LEFT:
                    self.current_piece.move(-1, 0, self.board)
                    if self.sounds_enabled:
                        try:
                            self.move_sound.play()
                        except:
                            pass
                elif event.key == K_RIGHT:
                    self.current_piece.move(1, 0, self.board)
                    if self.sounds_enabled:
                        try:
                            self.move_sound.play()
                        except:
                            pass
                elif event.key == K_DOWN:
                    self.soft_drop = True
                elif event.key == K_UP:
                    self.current_piece.rotate(self.board)
                    if self.sounds_enabled:
                        try:
                            self.rotate_sound.play()
                        except:
                            pass
                elif event.key == K_SPACE:
                    self.hard_drop()
                elif event.key == K_p:
                    self.paused = not self.paused
                elif event.key == K_c:
                    self.hold_piece()
                elif event.key == K_m:
                    # Toggle music
                    if self.music_playing:
                        pygame.mixer.music.pause()
                        self.music_playing = False
                    else:
                        try:
                            pygame.mixer.music.unpause()
                            self.music_playing = True
                        except:
                            pass

            if event.type == KEYUP:
                if event.key == K_DOWN:
                    self.soft_drop = False

    def hold_piece(self):
        """Hold the current piece or swap with the held piece"""
        if not self.can_hold:
            return

        if self.held_piece is None:
            # Hold the current piece and get a new one from next
            self.held_piece = Tetromino(self.current_piece.name)
            self.current_piece = self.next_piece
            self.next_piece = Tetromino()
        else:
            # Swap current piece with held piece
            temp_name = self.current_piece.name
            self.current_piece = Tetromino(self.held_piece.name)
            self.held_piece = Tetromino(temp_name)

        # Reset position of current piece
        self.current_piece.x = GRID_WIDTH // 2 - 1
        self.current_piece.y = 0
        self.current_piece.rotation = 0

        # Can't hold again until piece is placed
        self.can_hold = False

    def hard_drop(self):
        """Drop the piece all the way down"""
        while self.current_piece.move(0, 1, self.board):
            pass
        self.lock_piece()

    def update(self):
        """Update game state"""
        if self.game_over or self.paused:
            return

        current_time = pygame.time.get_ticks()

        # Handle line clearing animation
        if self.is_animating:
            if current_time - self.clear_animation_start >= self.clear_animation_duration:
                self.finish_line_clearing()
            return

        # Normal game update
        drop_speed = self.drop_speed // 10 if self.soft_drop else self.drop_speed

        if current_time - self.last_drop_time >= drop_speed:
            if not self.current_piece.move(0, 1, self.board):
                self.lock_piece()
            self.last_drop_time = current_time

    def lock_piece(self):
        """Lock the current piece in place and create a new one"""
        # Add the piece to the board
        for x, y in self.current_piece.get_rotated_shape():
            board_x = self.current_piece.x + x
            board_y = self.current_piece.y + y

            if board_y < 0:
                self.game_over = True
                return

            self.board[board_y][board_x] = self.current_piece.color

        # Check for completed lines
        self.clear_lines()

        # Reset hold ability
        self.can_hold = True

        # Create a new piece
        self.current_piece = self.next_piece
        self.next_piece = Tetromino()

        # Check if the new piece can be placed
        if not self.current_piece.is_valid_position(self.board):
            self.game_over = True

    def clear_lines(self):
        """Clear completed lines and award points"""
        self.lines_to_clear = []

        for y in range(GRID_HEIGHT):
            if all(self.board[y][x] is not None for x in range(GRID_WIDTH)):
                self.lines_to_clear.append(y)

        if not self.lines_to_clear:
            return

        # Start animation
        self.is_animating = True
        self.clear_animation_start = pygame.time.get_ticks()

        # Play clear sound
        if self.sounds_enabled:
            try:
                self.clear_sound.play()
            except:
                pass

    def finish_line_clearing(self):
        """Complete the line clearing process after animation"""
        # Update score
        lines_count = len(self.lines_to_clear)
        self.lines_cleared += lines_count
        old_level = self.level
        self.level = self.lines_cleared // 10 + 1

        # Score based on number of lines cleared at once
        line_scores = {1: 100, 2: 300, 3: 500, 4: 800}
        self.score += line_scores.get(lines_count, 0) * self.level

        # Level up sound
        if self.level > old_level and self.sounds_enabled:
            try:
                self.level_up_sound.play()
            except:
                pass

        # Adjust game speed
        self.drop_speed = max(100, 500 - (self.level - 1) * 20)

        # Clear the lines
        for line in sorted(self.lines_to_clear):
            # Remove the line
            for y in range(line, 0, -1):
                self.board[y] = self.board[y-1].copy()
            # Create an empty line at the top
            self.board[0] = [None for _ in range(GRID_WIDTH)]

        # Reset animation state
        self.lines_to_clear = []
        self.is_animating = False

    def draw(self):
        """Draw the game state to the screen"""
        # Fill background
        self.screen.fill(BLACK)

        # Draw game area border
        pygame.draw.rect(
            self.screen,
            WHITE,
            (
                GAME_AREA_START_X - 2,
                GAME_AREA_START_Y - 2,
                GAME_AREA_WIDTH + 4,
                GAME_AREA_HEIGHT + 4
            ),
            2
        )

        # Draw the grid
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                color = self.board[y][x] or BLACK

                # Special animation for lines being cleared
                if self.is_animating and y in self.lines_to_clear:
                    # Calculate flash animation (alternate between white and the original color)
                    animation_progress = (pygame.time.get_ticks(
                    ) - self.clear_animation_start) / self.clear_animation_duration
                    flash_speed = 10  # Higher = faster flashing
                    flash_intensity = abs(
                        math.sin(animation_progress * flash_speed * math.pi))

                    if color != BLACK:
                        # Blend between the original color and white
                        r = int(color[0] + (255 - color[0]) * flash_intensity)
                        g = int(color[1] + (255 - color[1]) * flash_intensity)
                        b = int(color[2] + (255 - color[2]) * flash_intensity)
                        color = (r, g, b)

                # Main block color
                pygame.draw.rect(
                    self.screen,
                    color,
                    (
                        GAME_AREA_START_X + x * GRID_SIZE,
                        GAME_AREA_START_Y + y * GRID_SIZE,
                        GRID_SIZE - 1,
                        GRID_SIZE - 1
                    )
                )

                # Only add 3D effects to colored blocks (not BLACK)
                if color != BLACK:
                    # Highlight (top and left edges)
                    highlight_color = tuple(min(c + 70, 255)
                                            for c in color[:3])
                    pygame.draw.line(
                        self.screen,
                        highlight_color,
                        (GAME_AREA_START_X + x * GRID_SIZE,
                         GAME_AREA_START_Y + y * GRID_SIZE),
                        (GAME_AREA_START_X + x * GRID_SIZE,
                         GAME_AREA_START_Y + y * GRID_SIZE + GRID_SIZE - 2),
                        2
                    )
                    pygame.draw.line(
                        self.screen,
                        highlight_color,
                        (GAME_AREA_START_X + x * GRID_SIZE,
                         GAME_AREA_START_Y + y * GRID_SIZE),
                        (GAME_AREA_START_X + x * GRID_SIZE + GRID_SIZE -
                         2, GAME_AREA_START_Y + y * GRID_SIZE),
                        2
                    )

                    # Shadow (bottom and right edges)
                    shadow_color = tuple(max(c - 70, 0) for c in color[:3])
                    pygame.draw.line(
                        self.screen,
                        shadow_color,
                        (GAME_AREA_START_X + x * GRID_SIZE + GRID_SIZE -
                         2, GAME_AREA_START_Y + y * GRID_SIZE),
                        (GAME_AREA_START_X + x * GRID_SIZE + GRID_SIZE - 2,
                         GAME_AREA_START_Y + y * GRID_SIZE + GRID_SIZE - 2),
                        2
                    )
                    pygame.draw.line(
                        self.screen,
                        shadow_color,
                        (GAME_AREA_START_X + x * GRID_SIZE,
                         GAME_AREA_START_Y + y * GRID_SIZE + GRID_SIZE - 2),
                        (GAME_AREA_START_X + x * GRID_SIZE + GRID_SIZE - 2,
                         GAME_AREA_START_Y + y * GRID_SIZE + GRID_SIZE - 2),
                        2
                    )

        # Draw the ghost piece to show where the current piece will land
        if not self.game_over and not self.paused:
            self.current_piece.draw_ghost(self.screen, self.board)

        # Draw the current piece
        if not self.game_over:
            self.current_piece.draw(self.screen)

        # Draw the sidebar
        sidebar_x = GAME_AREA_START_X + GAME_AREA_WIDTH + 20

        # Draw held piece box
        held_piece_text = self.font.render("Hold:", True, WHITE)
        self.screen.blit(held_piece_text, (sidebar_x, GAME_AREA_START_Y - 160))

        # Draw held piece preview box
        pygame.draw.rect(
            self.screen,
            WHITE,
            (
                sidebar_x,
                GAME_AREA_START_Y - 120,
                120,
                120
            ),
            1
        )

        # Draw the held piece in the preview box if there is one
        if self.held_piece:
            piece_center_x = sidebar_x + 60
            piece_center_y = GAME_AREA_START_Y - 60

            for x, y in self.held_piece.shape:
                # Main block color
                pygame.draw.rect(
                    self.screen,
                    self.held_piece.color,
                    (
                        piece_center_x + x * GRID_SIZE,
                        piece_center_y + y * GRID_SIZE,
                        GRID_SIZE - 1,
                        GRID_SIZE - 1
                    )
                )

                # Highlight (top and left edges)
                highlight_color = tuple(min(c + 70, 255)
                                        for c in self.held_piece.color[:3])
                pygame.draw.line(
                    self.screen,
                    highlight_color,
                    (piece_center_x + x * GRID_SIZE,
                     piece_center_y + y * GRID_SIZE),
                    (piece_center_x + x * GRID_SIZE,
                     piece_center_y + y * GRID_SIZE + GRID_SIZE - 2),
                    2
                )
                pygame.draw.line(
                    self.screen,
                    highlight_color,
                    (piece_center_x + x * GRID_SIZE,
                     piece_center_y + y * GRID_SIZE),
                    (piece_center_x + x * GRID_SIZE + GRID_SIZE -
                     2, piece_center_y + y * GRID_SIZE),
                    2
                )

                # Shadow (bottom and right edges)
                shadow_color = tuple(max(c - 70, 0)
                                     for c in self.held_piece.color[:3])
                pygame.draw.line(
                    self.screen,
                    shadow_color,
                    (piece_center_x + x * GRID_SIZE + GRID_SIZE -
                     2, piece_center_y + y * GRID_SIZE),
                    (piece_center_x + x * GRID_SIZE + GRID_SIZE - 2,
                     piece_center_y + y * GRID_SIZE + GRID_SIZE - 2),
                    2
                )
                pygame.draw.line(
                    self.screen,
                    shadow_color,
                    (piece_center_x + x * GRID_SIZE,
                     piece_center_y + y * GRID_SIZE + GRID_SIZE - 2),
                    (piece_center_x + x * GRID_SIZE + GRID_SIZE - 2,
                     piece_center_y + y * GRID_SIZE + GRID_SIZE - 2),
                    2
                )

        # Draw next piece box
        next_piece_text = self.font.render("Next:", True, WHITE)
        self.screen.blit(next_piece_text, (sidebar_x, GAME_AREA_START_Y))

        # Draw next piece preview box
        pygame.draw.rect(
            self.screen,
            WHITE,
            (
                sidebar_x,
                GAME_AREA_START_Y + 40,
                120,
                120
            ),
            1
        )

        # Draw the next piece in the preview box
        piece_center_x = sidebar_x + 60
        piece_center_y = GAME_AREA_START_Y + 100

        for x, y in self.next_piece.shape:
            # Main block color
            pygame.draw.rect(
                self.screen,
                self.next_piece.color,
                (
                    piece_center_x + x * GRID_SIZE,
                    piece_center_y + y * GRID_SIZE,
                    GRID_SIZE - 1,
                    GRID_SIZE - 1
                )
            )

            # Highlight (top and left edges)
            highlight_color = tuple(min(c + 70, 255)
                                    for c in self.next_piece.color[:3])
            pygame.draw.line(
                self.screen,
                highlight_color,
                (piece_center_x + x * GRID_SIZE, piece_center_y + y * GRID_SIZE),
                (piece_center_x + x * GRID_SIZE,
                 piece_center_y + y * GRID_SIZE + GRID_SIZE - 2),
                2
            )
            pygame.draw.line(
                self.screen,
                highlight_color,
                (piece_center_x + x * GRID_SIZE, piece_center_y + y * GRID_SIZE),
                (piece_center_x + x * GRID_SIZE + GRID_SIZE -
                 2, piece_center_y + y * GRID_SIZE),
                2
            )

            # Shadow (bottom and right edges)
            shadow_color = tuple(max(c - 70, 0)
                                 for c in self.next_piece.color[:3])
            pygame.draw.line(
                self.screen,
                shadow_color,
                (piece_center_x + x * GRID_SIZE + GRID_SIZE -
                 2, piece_center_y + y * GRID_SIZE),
                (piece_center_x + x * GRID_SIZE + GRID_SIZE - 2,
                 piece_center_y + y * GRID_SIZE + GRID_SIZE - 2),
                2
            )
            pygame.draw.line(
                self.screen,
                shadow_color,
                (piece_center_x + x * GRID_SIZE,
                 piece_center_y + y * GRID_SIZE + GRID_SIZE - 2),
                (piece_center_x + x * GRID_SIZE + GRID_SIZE - 2,
                 piece_center_y + y * GRID_SIZE + GRID_SIZE - 2),
                2
            )

        # Draw score
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (sidebar_x, GAME_AREA_START_Y + 180))

        # Draw level
        level_text = self.font.render(f"Level: {self.level}", True, WHITE)
        self.screen.blit(level_text, (sidebar_x, GAME_AREA_START_Y + 220))

        # Draw lines cleared
        lines_text = self.font.render(
            f"Lines: {self.lines_cleared}", True, WHITE)
        self.screen.blit(lines_text, (sidebar_x, GAME_AREA_START_Y + 260))

        # Draw game over message
        if self.game_over:
            game_over_font = pygame.font.Font(None, 48)
            game_over_text = game_over_font.render("GAME OVER", True, RED)
            game_over_rect = game_over_text.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
            self.screen.blit(game_over_text, game_over_rect)

            restart_text = self.font.render("Press R to restart", True, WHITE)
            restart_rect = restart_text.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
            self.screen.blit(restart_text, restart_rect)

        # Draw pause message
        if self.paused:
            pause_font = pygame.font.Font(None, 48)
            pause_text = pause_font.render("PAUSED", True, WHITE)
            pause_rect = pause_text.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(pause_text, pause_rect)

        pygame.display.flip()

    def run(self):
        """Main game loop"""
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)  # 60 FPS


class GameMenu:
    """Main menu for the game"""

    def __init__(self, screen):
        self.screen = screen
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 36)

        # Sound state
        self.sounds_enabled = False

        # Menu options
        self.options = [
            {"text": "Start Game", "action": "start"},
            {"text": "Controls", "action": "controls"},
            {"text": f"Sounds: {'ON' if self.sounds_enabled else 'OFF'}",
                "action": "toggle_sound"},
            {"text": "Quit", "action": "quit"}
        ]
        self.selected_option = 0

        # Menu state
        self.showing_controls = False

        # Decoration for vibey effect
        self.tetrominos = []
        for _ in range(8):
            self.tetrominos.append({
                'shape': random.choice(list(TETROMINOS.values()))['shape'],
                'color': random.choice([CYAN, BLUE, ORANGE, YELLOW, GREEN, PURPLE, RED]),
                'x': random.randint(0, SCREEN_WIDTH // GRID_SIZE - 1),
                'y': random.randint(-5, GRID_HEIGHT),
                'rotation': random.randint(0, 3),
                'speed': random.uniform(0.1, 0.5)
            })

    def handle_events(self):
        """Handle menu input"""
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if self.showing_controls:
                if event.type == KEYDOWN:
                    self.showing_controls = False
                return None

            if event.type == KEYDOWN:
                if event.key == K_UP:
                    self.selected_option = (
                        self.selected_option - 1) % len(self.options)
                elif event.key == K_DOWN:
                    self.selected_option = (
                        self.selected_option + 1) % len(self.options)
                elif event.key == K_RETURN or event.key == K_SPACE:
                    action = self.options[self.selected_option]["action"]
                    if action == "toggle_sound":
                        # Toggle sound setting
                        self.sounds_enabled = not self.sounds_enabled
                        # Update the menu text
                        self.options[2]["text"] = f"Sounds: {'ON' if self.sounds_enabled else 'OFF'}"
                        return None
                    return action
        return None

    def update(self):
        """Update menu state"""
        # Update falling tetrominos
        for tetromino in self.tetrominos:
            tetromino['y'] += tetromino['speed']
            if tetromino['y'] > SCREEN_HEIGHT // GRID_SIZE:
                # Reset position when it goes off screen
                tetromino['y'] = -5
                tetromino['x'] = random.randint(
                    0, SCREEN_WIDTH // GRID_SIZE - 1)

    def draw(self):
        """Draw menu"""
        # Fill background
        self.screen.fill(BLACK)

        # Draw falling tetrominos in background
        for tetromino in self.tetrominos:
            rotation = tetromino['rotation']
            shape = tetromino['shape']

            # Get rotated coordinates
            coords = []
            for x, y in shape:
                if rotation == 0:
                    coords.append((x, y))
                elif rotation == 1:
                    coords.append((-y, x))
                elif rotation == 2:
                    coords.append((-x, -y))
                elif rotation == 3:
                    coords.append((y, -x))

            for x, y in coords:
                pygame.draw.rect(
                    self.screen,
                    tetromino['color'],
                    (
                        (tetromino['x'] + x) * GRID_SIZE,
                        (tetromino['y'] + y) * GRID_SIZE,
                        GRID_SIZE - 1,
                        GRID_SIZE - 1
                    ),
                    1  # Just outline for background effect
                )

        if self.showing_controls:
            self._draw_controls()
            return

        # Draw title
        title_text = self.font_large.render("VIBE TETRIS", True, WHITE)
        title_rect = title_text.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
        self.screen.blit(title_text, title_rect)

        # Draw menu options
        for i, option in enumerate(self.options):
            if i == self.selected_option:
                color = YELLOW  # Highlight selected option
                text = f"> {option['text']} <"
            else:
                color = WHITE
                text = option['text']

            option_text = self.font_medium.render(text, True, color)
            option_rect = option_text.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + i * 60)
            )
            self.screen.blit(option_text, option_rect)

        # Draw footer
        footer_text = self.font_small.render(
            "Use arrow keys to navigate, ENTER to select", True, GRAY)
        footer_rect = footer_text.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        self.screen.blit(footer_text, footer_rect)

        pygame.display.flip()

    def _draw_controls(self):
        """Draw the controls screen"""
        # Draw title
        title_text = self.font_medium.render("CONTROLS", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 80))
        self.screen.blit(title_text, title_rect)

        # Draw control instructions
        controls = [
            "Left/Right Arrow: Move piece",
            "Up Arrow: Rotate piece",
            "Down Arrow: Soft drop",
            "Spacebar: Hard drop",
            "C: Hold piece",
            "P: Pause game",
            "M: Toggle music",
            "R: Restart (after game over)",
            "",
            f"Sounds are currently {'ON' if self.sounds_enabled else 'OFF'}"
        ]

        for i, control in enumerate(controls):
            control_text = self.font_small.render(control, True, WHITE)
            control_rect = control_text.get_rect(
                center=(SCREEN_WIDTH // 2, 150 + i * 45)
            )
            self.screen.blit(control_text, control_rect)

        # Draw return instruction
        return_text = self.font_small.render(
            "Press any key to return to menu", True, YELLOW)
        return_rect = return_text.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80))
        self.screen.blit(return_text, return_rect)

        pygame.display.flip()


def main():
    """Main function"""
    # Initialize pygame
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Vibe Tetris')

    # Create menu and game
    menu = GameMenu(screen)
    game = TetrisGame(sounds_enabled=menu.sounds_enabled)

    # Main loop state
    game_started = False
    clock = pygame.time.Clock()

    # Main game loop
    while True:
        if not game_started:
            # Menu mode
            action = menu.handle_events()

            if action == "start":
                game_started = True
                # Create a fresh game with current sound setting
                game = TetrisGame(sounds_enabled=menu.sounds_enabled)
            elif action == "controls":
                menu.showing_controls = True
            elif action == "quit":
                pygame.quit()
                sys.exit()

            menu.update()
            menu.draw()
        else:
            # Game mode
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()

                if game.game_over:
                    if event.type == KEYDOWN:
                        if event.key == K_r:
                            # Restart game
                            game = TetrisGame()
                        elif event.key == K_SPACE or event.key == K_RETURN:
                            # Return to menu
                            game_started = False
                    continue

                if event.type == KEYDOWN:
                    if event.key == K_LEFT:
                        game.current_piece.move(-1, 0, game.board)
                        if game.sounds_enabled:
                            try:
                                game.move_sound.play()
                            except:
                                pass
                    elif event.key == K_RIGHT:
                        game.current_piece.move(1, 0, game.board)
                        if game.sounds_enabled:
                            try:
                                game.move_sound.play()
                            except:
                                pass
                    elif event.key == K_DOWN:
                        game.soft_drop = True
                    elif event.key == K_UP:
                        game.current_piece.rotate(game.board)
                        if game.sounds_enabled:
                            try:
                                game.rotate_sound.play()
                            except:
                                pass
                    elif event.key == K_SPACE:
                        game.hard_drop()
                    elif event.key == K_p:
                        game.paused = not game.paused
                    elif event.key == K_c:
                        game.hold_piece()
                    elif event.key == K_m:
                        # Toggle music
                        if game.music_playing:
                            pygame.mixer.music.pause()
                            game.music_playing = False
                        else:
                            try:
                                pygame.mixer.music.unpause()
                                game.music_playing = True
                            except:
                                pass
                    elif event.key == K_RETURN:
                        # Quick return to menu
                        game_started = False

                if event.type == KEYUP:
                    if event.key == K_DOWN:
                        game.soft_drop = False

            game.update()
            game.draw()

            # Show return to menu option on game over
            if game.game_over:
                menu_text = game.font.render(
                    "Press ENTER to return to menu", True, WHITE)
                menu_rect = menu_text.get_rect(
                    center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 70))
                game.screen.blit(menu_text, menu_rect)
                pygame.display.flip()

        # Cap frame rate
        clock.tick(60)


if __name__ == "__main__":
    main()
