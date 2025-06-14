#!/usr/bin/env python3
"""
Vibe Tetris - A Tetris clone written in Python using Pygame
Main entry point for the game
"""
import pygame
import sys
import time
from game import TetrisGame
from menu import GameMenu
from ai_player import TetrisAI
from battle import BattleGame
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, K_r, K_RETURN, K_SPACE, QUIT, KEYDOWN, WHITE
)


def main():
    """Main function"""
    # Initialize pygame
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption('Vibe Tetris')

    # Create menu and game
    menu = GameMenu(screen)
    game = TetrisGame(sounds_enabled=menu.sounds_enabled)

    # Main loop state
    game_started = False
    demo_mode = False
    battle_mode = False
    ai_player = None
    ai_move_delay = 0.2  # Time between AI moves in seconds
    last_ai_move_time = 0
    clock = pygame.time.Clock()
    battle_game = None

    # Main game loop
    while True:
        if not game_started:
            # Menu mode
            events = pygame.event.get()
            action = menu.handle_events(events)

            if action == "start":
                game_started = True
                demo_mode = False
                battle_mode = False
                # Create a fresh game with current sound setting
                game = TetrisGame(sounds_enabled=menu.sounds_enabled)
            elif action == "battle":
                game_started = True
                demo_mode = False
                battle_mode = True
                # Battle mode will create its own larger screen
                battle_game = BattleGame(
                    screen, sounds_enabled=menu.sounds_enabled, difficulty=menu.battle_difficulty)
            elif action == "demo":
                game_started = True
                demo_mode = True
                battle_mode = False
                # Create a fresh game with current sound setting
                game = TetrisGame(sounds_enabled=menu.sounds_enabled)
                # Initialize AI player
                ai_player = TetrisAI(game)
                last_ai_move_time = time.time()
            elif action == "controls":
                menu.showing_controls = True
            elif action == "quit":
                pygame.quit()
                sys.exit()

            menu.update()
            menu.draw()
        else:
            # Game mode - handle different modes
            if battle_mode:
                # Battle mode uses its own event handling
                result = battle_game.handle_events()
                if result == "exit_to_menu":
                    game_started = False
                    battle_mode = False
                    # Restore original screen size when returning to menu
                    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
                    # Recreate menu with updated screen
                    menu = GameMenu(screen)

                # Update and draw battle game
                battle_game.update()
                battle_game.draw()
            else:
                # Regular game or demo mode
                events = pygame.event.get()  # Get events once

                # Process events for specific main loop actions
                for event in events:
                    if event.type == QUIT:
                        pygame.quit()
                        sys.exit()

                    if game.game_over:
                        if event.type == KEYDOWN:
                            if event.key == K_r:
                                # Restart game
                                game = TetrisGame(
                                    sounds_enabled=menu.sounds_enabled)
                                if demo_mode:
                                    ai_player = TetrisAI(game)
                            elif event.key == K_SPACE or event.key == K_RETURN:
                                # Return to menu
                                game_started = False
                                demo_mode = False
                        continue

                    # In demo mode only, allow ENTER to return to menu
                    if demo_mode and event.type == KEYDOWN:
                        if event.key == K_RETURN:
                            # Return to menu from demo mode only
                            game_started = False
                            demo_mode = False

                if demo_mode and not game.paused and not game.game_over and not game.pause_menu_active:
                    # AI plays the game
                    current_time = time.time()
                    if current_time - last_ai_move_time >= ai_move_delay:
                        ai_player.execute_move()
                        last_ai_move_time = current_time
                else:
                    # Human plays the game
                    result = game.handle_events(events)
                    if result == "exit_to_menu":
                        game_started = False
                        demo_mode = False

                game.update()
                game.draw()

            # Show return to menu option on game over (only for normal and demo mode)
            if not battle_mode and game.game_over:
                menu_text = game.font.render(
                    "Press ENTER to return to menu", True, WHITE)
                menu_rect = menu_text.get_rect(
                    center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 70))
                game.screen.blit(menu_text, menu_rect)
                pygame.display.flip()

            # In demo mode, show that this is AI playing
            if demo_mode and not game.game_over:
                demo_text = game.font.render(
                    "AI DEMO MODE - Press ENTER to exit", True, WHITE)
                demo_rect = demo_text.get_rect(
                    center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
                game.screen.blit(demo_text, demo_rect)
                # Only flip the display if not already done by the game
                if game.paused and not game.pause_menu_active:
                    pygame.display.flip()

        # Cap frame rate
        clock.tick(60)


if __name__ == "__main__":
    main()
