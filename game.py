#!/usr/bin/env python3
"""
Main game logic for Vibe Tetris.
"""
import pygame
import sys
import os
import math
from tetromino import Tetromino, PieceRandomizer
from constants import (
    QUIT, KEYDOWN, K_LEFT, K_RIGHT, K_DOWN, K_UP, K_SPACE, K_p, K_c, K_m, K_r,
    GRID_WIDTH, GRID_HEIGHT, GRID_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT,
    GAME_AREA_WIDTH, GAME_AREA_HEIGHT, GAME_AREA_START_X, GAME_AREA_START_Y,
    BLACK, WHITE, RED, GRAY, SOUND_DIR, MUSIC_FILE, MOVE_SOUND, ROTATE_SOUND,
    DROP_SOUND, CLEAR_SOUND, GAME_OVER_SOUND, LEVEL_UP_SOUND, LINE_SCORES
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

        # Piece randomizer (ensures fair distribution of pieces)
        # Uses a "bag" system where each piece appears once before any repeats
        # with a small chance (5%) of allowing a piece to repeat for variety
        self.piece_randomizer = PieceRandomizer(repeat_chance=0.05)

        # Game state
        self.board = [[None for _ in range(GRID_WIDTH)]
                      for _ in range(GRID_HEIGHT)]
        self.current_piece = Tetromino(randomizer=self.piece_randomizer)
        self.next_piece = Tetromino(randomizer=self.piece_randomizer)
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
        # Create a fresh randomizer for new games
        self.piece_randomizer = PieceRandomizer(repeat_chance=0.05)
        self.current_piece = Tetromino(randomizer=self.piece_randomizer)
        self.next_piece = Tetromino(randomizer=self.piece_randomizer)
        self.held_piece = None
        self.can_hold = True
        self.game_over = False
        self.paused = False
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.drop_speed = 500

    def handle_events(self, events=None):
        """Handle keyboard and window events"""
        # If no events are provided, get them (for backward compatibility)
        if events is None:
            events = pygame.event.get()

        for event in events:
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

            if event.type == pygame.KEYUP:
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
            self.next_piece = Tetromino(randomizer=self.piece_randomizer)
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
        self.next_piece = Tetromino(randomizer=self.piece_randomizer)

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
        self.score += LINE_SCORES.get(lines_count, 0) * self.level

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
