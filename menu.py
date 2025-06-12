#!/usr/bin/env python3
"""
Game menu for Vibe Tetris.
"""
import pygame
import random
import sys
from constants import (
    QUIT, KEYDOWN, K_UP, K_DOWN, K_RETURN, K_SPACE,
    SCREEN_WIDTH, SCREEN_HEIGHT, GRID_SIZE, GRID_HEIGHT,
    BLACK, WHITE, YELLOW, GRAY,
    CYAN, BLUE, ORANGE, YELLOW, GREEN, PURPLE, RED, TETROMINOS
)


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

    def handle_events(self, events=None):
        """Handle menu input"""
        # If no events are provided, get them (for backward compatibility)
        if events is None:
            events = pygame.event.get()

        for event in events:
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
