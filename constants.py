#!/usr/bin/env python3
"""
Constants and configurations for the Vibe Tetris game.
"""
import pygame
import os

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
SCREEN_WIDTH = 1000  # 800 * 1.25 = 1000
SCREEN_HEIGHT = 750  # 600 * 1.25 = 750
GRID_SIZE = 37       # 30 * 1.25 ≈ 37
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

# Sound file paths
SOUND_DIR = "sounds"
MUSIC_FILE = "tetris_theme.mp3"
MOVE_SOUND = "move.wav"
ROTATE_SOUND = "rotate.wav"
DROP_SOUND = "drop.wav"
CLEAR_SOUND = "clear.wav"
GAME_OVER_SOUND = "game_over.wav"
LEVEL_UP_SOUND = "level_up.wav"

# Scoring system
LINE_SCORES = {1: 100, 2: 300, 3: 500, 4: 800}
