#!/usr/bin/env python3
"""
Battle mode for Vibe Tetris.
This mode allows the player to compete against the AI.
"""
import pygame
import sys
import time
from game import TetrisGame
from ai_player import TetrisAI
from game_draw import draw_game_at_position
from constants import (
    QUIT, KEYDOWN, K_LEFT, K_RIGHT, K_DOWN, K_UP, K_SPACE, K_p, K_c, K_m, K_r, K_ESCAPE, K_RETURN,
    GRID_WIDTH, GRID_HEIGHT, GRID_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT,
    GAME_AREA_WIDTH, GAME_AREA_HEIGHT, GAME_AREA_START_X, GAME_AREA_START_Y,
    BLACK, WHITE, RED, GRAY, YELLOW, GREEN, SOUND_DIR, MUSIC_FILE
)

# Battle mode screen width needs to be wider to accommodate two game areas side by side
# with some spacing between them and the sidebar for each game
BATTLE_SCREEN_WIDTH = GAME_AREA_WIDTH * 2 + 500  # Two game areas plus sidebars plus spacing (increased for 25% larger window)

# Battle mode constants
BATTLE_TARGET_SCORE = 1000  # First to reach this score wins

# AI difficulty settings
AI_DIFFICULTY_LEVELS = {
    'easy': {
        'move_delay': 0.39,      # Slower moves (30% slower)
        'mistake_chance': 0.3,  # 30% chance to make a mistake
    },
    'medium': {
        'move_delay': 0.195,     # Medium speed (30% slower)
        'mistake_chance': 0.1,  # 10% chance to make a mistake
    },
    'hard': {
        'move_delay': 0.104,     # Fast moves (30% slower)
        'mistake_chance': 0.02, # 2% chance to make a mistake
    }
}


class BattleGame:
    """
    Battle mode game class.
    Manages two Tetris games side by side - one for player, one for AI.
    """

    def __init__(self, screen, sounds_enabled=False, difficulty='medium'):
        # Resize the screen to fit both game boards side by side
        self.screen = pygame.display.set_mode((BATTLE_SCREEN_WIDTH, SCREEN_HEIGHT))
        self.font = pygame.font.Font(None, 36)
        self.large_font = pygame.font.Font(None, 72)

        # Set AI difficulty
        self.difficulty = difficulty if difficulty in AI_DIFFICULTY_LEVELS else 'medium'
        self.ai_move_delay = AI_DIFFICULTY_LEVELS[self.difficulty]['move_delay']
        self.ai_mistake_chance = AI_DIFFICULTY_LEVELS[self.difficulty]['mistake_chance']

        # Create player and AI games
        self.player_game = TetrisGame(sounds_enabled=sounds_enabled)
        # AI game has no sounds
        self.ai_game = TetrisGame(sounds_enabled=False)
        
        # Keep a reference to the original screen for both games
        self.player_game.screen = self.screen
        self.ai_game.screen = self.screen

        # Adjust game area positions for side-by-side layout
        self._adjust_game_positions()

        # Create AI controller for the AI game with appropriate difficulty
        self.ai_player = TetrisAI(self.ai_game, mistake_chance=self.ai_mistake_chance)

        # Game state
        self.game_over = False
        self.winner = None  # 'player' or 'ai' when game ends
        self.ai_last_move_time = time.time()

        # Initialize clock
        self.clock = pygame.time.Clock()

    def _adjust_game_positions(self):
        """Adjust game positions for side-by-side layout"""
        # Calculate new positions for side-by-side games
        # We need space for both game boards and their sidebar areas
        
        # Store original position for reference
        self.original_game_area_start_x = GAME_AREA_START_X
        
        # Calculate optimal spacing
        spacing = 80  # Space between the two game areas
        sidebar_width = 200  # Width for each sidebar
        
        # Calculate the total width needed for both games with sidebars
        total_width = (GAME_AREA_WIDTH * 2) + (sidebar_width * 2) + spacing
        
        # Player game on left side, with enough space for its sidebar
        self.player_game.game_area_start_x = (BATTLE_SCREEN_WIDTH - total_width) // 2
        
        # AI game on right side, positioned after player game + sidebar + spacing
        self.ai_game.game_area_start_x = self.player_game.game_area_start_x + GAME_AREA_WIDTH + sidebar_width + spacing

    def handle_events(self):
        """Handle keyboard and window events"""
        events = pygame.event.get()
        result = None

        for event in events:
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            # Handle ESC key for pause menu
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                return "exit_to_menu"

            # Handle game over state
            if self.game_over:
                if event.type == KEYDOWN:
                    if event.key == K_r:
                        self.reset_game()
                    elif event.key == K_RETURN or event.key == K_SPACE:
                        return "exit_to_menu"
                continue

        # Only pass events to player game
        player_result = self.player_game.handle_events(events)
        if player_result == "exit_to_menu":
            return player_result

        return None

    def update(self):
        """Update game state"""
        if self.game_over:
            return

        # Update player game
        self.player_game.update()

        # Update AI game and make AI moves
        self.ai_game.update()
        current_time = time.time()
        if current_time - self.ai_last_move_time >= self.ai_move_delay:
            self.ai_player.execute_move()
            self.ai_last_move_time = current_time

        # Check for winner
        if self.player_game.score >= BATTLE_TARGET_SCORE:
            self.game_over = True
            self.winner = 'player'
        elif self.ai_game.score >= BATTLE_TARGET_SCORE:
            self.game_over = True
            self.winner = 'ai'

        # Check for game over
        if self.player_game.game_over:
            self.game_over = True
            self.winner = 'ai'
        elif self.ai_game.game_over:
            self.game_over = True
            self.winner = 'player'

    def draw(self):
        """Draw the battle screen"""
        # Fill background
        self.screen.fill(BLACK)

        # Draw player and AI games
        self._draw_player_game()
        self._draw_ai_game()

        # Draw score labels and VS
        self._draw_battle_ui()

        # Draw game over message if needed
        if self.game_over:
            self._draw_game_over()

        pygame.display.flip()

    def _draw_player_game(self):
        """Draw the player's game"""
        # Use the independent drawing function to draw the game at the specific position
        draw_game_at_position(
            self.player_game, 
            self.screen, 
            self.player_game.game_area_start_x, 
            GAME_AREA_START_Y
        )

        # Draw player label
        player_text = self.font.render("PLAYER", True, WHITE)
        player_rect = player_text.get_rect(
            center=(self.player_game.game_area_start_x + GAME_AREA_WIDTH // 2,
                    GAME_AREA_START_Y - 30)
        )
        self.screen.blit(player_text, player_rect)

        # Draw score
        score_text = self.font.render(
            f"Score: {self.player_game.score}", True, WHITE)
        score_rect = score_text.get_rect(
            center=(self.player_game.game_area_start_x + GAME_AREA_WIDTH // 2,
                    GAME_AREA_START_Y + GAME_AREA_HEIGHT + 30)
        )
        self.screen.blit(score_text, score_rect)

    def _draw_ai_game(self):
        """Draw the AI's game"""
        # Use the independent drawing function to draw the game at the specific position
        draw_game_at_position(
            self.ai_game, 
            self.screen, 
            self.ai_game.game_area_start_x, 
            GAME_AREA_START_Y
        )

        # Draw AI label
        ai_text = self.font.render("AI", True, WHITE)
        ai_rect = ai_text.get_rect(
            center=(self.ai_game.game_area_start_x + GAME_AREA_WIDTH // 2,
                    GAME_AREA_START_Y - 30)
        )
        self.screen.blit(ai_text, ai_rect)

        # Draw score
        score_text = self.font.render(
            f"Score: {self.ai_game.score}", True, WHITE)
        score_rect = score_text.get_rect(
            center=(self.ai_game.game_area_start_x + GAME_AREA_WIDTH // 2,
                    GAME_AREA_START_Y + GAME_AREA_HEIGHT + 30)
        )
        self.screen.blit(score_text, score_rect)

    def _draw_battle_ui(self):
        """Draw the battle UI elements"""
        # Draw VS in center with larger font
        vs_font = pygame.font.Font(None, 60)
        vs_text = vs_font.render("VS", True, RED)
        vs_rect = vs_text.get_rect(
            center=(BATTLE_SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(vs_text, vs_rect)

        # Draw target score
        target_text = self.font.render(
            f"First to {BATTLE_TARGET_SCORE} wins!", True, YELLOW)
        target_rect = target_text.get_rect(center=(BATTLE_SCREEN_WIDTH // 2, 30))
        self.screen.blit(target_text, target_rect)
        
        # Draw difficulty level
        difficulty_color = {
            'easy': GREEN,
            'medium': YELLOW,
            'hard': RED
        }.get(self.difficulty, WHITE)
        
        difficulty_text = self.font.render(
            f"Difficulty: {self.difficulty.upper()}", True, difficulty_color)
        difficulty_rect = difficulty_text.get_rect(center=(BATTLE_SCREEN_WIDTH // 2, 70))
        self.screen.blit(difficulty_text, difficulty_rect)

        # Draw instructions
        instr_text = self.font.render("Press ESC to quit", True, GRAY)
        instr_rect = instr_text.get_rect(
            center=(BATTLE_SCREEN_WIDTH // 2, SCREEN_HEIGHT - 20))
        self.screen.blit(instr_text, instr_rect)

    def _draw_game_over(self):
        """Draw game over screen"""
        # Create semi-transparent overlay
        overlay = pygame.Surface(
            (BATTLE_SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Black with alpha
        self.screen.blit(overlay, (0, 0))

        # Draw game over message
        if self.winner == 'player':
            result_text = "YOU WIN!"
            color = GREEN
        else:
            result_text = "AI WINS!"
            color = RED

        game_over_text = self.large_font.render("GAME OVER", True, WHITE)
        game_over_rect = game_over_text.get_rect(
            center=(BATTLE_SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(game_over_text, game_over_rect)

        result_text = self.large_font.render(result_text, True, color)
        result_rect = result_text.get_rect(
            center=(BATTLE_SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        self.screen.blit(result_text, result_rect)

        # Draw instructions
        restart_text = self.font.render(
            "Press R to restart or ENTER to exit", True, WHITE)
        restart_rect = restart_text.get_rect(
            center=(BATTLE_SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 90))
        self.screen.blit(restart_text, restart_rect)

    def reset_game(self):
        """Reset the battle game"""
        # Reset player and AI games
        self.player_game = TetrisGame(
            sounds_enabled=self.player_game.sounds_enabled)
        self.ai_game = TetrisGame(sounds_enabled=False)
        
        # Keep a reference to the screen for both games
        self.player_game.screen = self.screen
        self.ai_game.screen = self.screen

        # Adjust positions
        self._adjust_game_positions()

        # Reset AI with the same difficulty setting
        self.ai_player = TetrisAI(self.ai_game, mistake_chance=self.ai_mistake_chance)

        # Reset game state
        self.game_over = False
        self.winner = None
        self.ai_last_move_time = time.time()

    def run(self):
        """Main game loop for battle mode"""
        while True:
            if self.handle_events() == "exit_to_menu":
                return

            self.update()
            self.draw()
            self.clock.tick(60)  # 60 FPS
