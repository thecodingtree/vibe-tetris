#!/usr/bin/env python3
"""
Helper functions for custom drawing in Tetris.
This file provides utilities to extend the drawing capabilities of the tetris game.
"""

import pygame
from constants import (
    GRID_SIZE, GAME_AREA_WIDTH, GAME_AREA_HEIGHT,
    WHITE, BLACK
)


def draw_game_at_position(game, surface, pos_x, pos_y):
    """Draw a game at a specific position on the surface
    
    Args:
        game: The TetrisGame instance to draw
        surface: The surface to draw on
        pos_x: X position to draw the game area
        pos_y: Y position to draw the game area
    """
    # Draw game area border
    pygame.draw.rect(
        surface,
        WHITE,
        (
            pos_x - 2,
            pos_y - 2,
            GAME_AREA_WIDTH + 4,
            GAME_AREA_HEIGHT + 4
        ),
        2
    )

    # Draw the grid cells
    for y in range(len(game.board)):
        for x in range(len(game.board[y])):
            color = game.board[y][x] or BLACK

            # Main block color
            pygame.draw.rect(
                surface,
                color,
                (
                    pos_x + x * GRID_SIZE,
                    pos_y + y * GRID_SIZE,
                    GRID_SIZE - 1,
                    GRID_SIZE - 1
                )
            )

            # Only add 3D effects to colored blocks (not BLACK)
            if color != BLACK:
                # Highlight (top and left edges)
                highlight_color = tuple(min(c + 70, 255) for c in color[:3])
                pygame.draw.line(
                    surface,
                    highlight_color,
                    (pos_x + x * GRID_SIZE, pos_y + y * GRID_SIZE),
                    (pos_x + x * GRID_SIZE, pos_y + y * GRID_SIZE + GRID_SIZE - 2),
                    2
                )
                pygame.draw.line(
                    surface,
                    highlight_color,
                    (pos_x + x * GRID_SIZE, pos_y + y * GRID_SIZE),
                    (pos_x + x * GRID_SIZE + GRID_SIZE - 2, pos_y + y * GRID_SIZE),
                    2
                )

                # Shadow (bottom and right edges)
                shadow_color = tuple(max(c - 70, 0) for c in color[:3])
                pygame.draw.line(
                    surface,
                    shadow_color,
                    (pos_x + x * GRID_SIZE + GRID_SIZE - 2, pos_y + y * GRID_SIZE),
                    (pos_x + x * GRID_SIZE + GRID_SIZE - 2,
                     pos_y + y * GRID_SIZE + GRID_SIZE - 2),
                    2
                )
                pygame.draw.line(
                    surface,
                    shadow_color,
                    (pos_x + x * GRID_SIZE, pos_y + y * GRID_SIZE + GRID_SIZE - 2),
                    (pos_x + x * GRID_SIZE + GRID_SIZE - 2,
                     pos_y + y * GRID_SIZE + GRID_SIZE - 2),
                    2
                )

    # Draw the ghost piece
    if not game.game_over and not game.paused:
        game.current_piece.draw_ghost(surface, game.board, pos_x, pos_y)

    # Draw the current piece
    if not game.game_over:
        game.current_piece.draw(surface, pos_x, pos_y)
        
    # Draw the sidebar
    draw_sidebar(game, surface, pos_x + GAME_AREA_WIDTH + 20, pos_y)
    
def draw_sidebar(game, surface, x, y):
    """Draw the game's sidebar at the specified position
    
    Args:
        game: The TetrisGame instance 
        surface: The surface to draw on
        x: X position for the sidebar
        y: Y position for the sidebar (typically same as game area)
    """
    # Draw held piece box
    held_piece_text = game.font.render("Hold:", True, WHITE)
    surface.blit(held_piece_text, (x, y - 160))
    
    # Draw held piece preview box
    pygame.draw.rect(
        surface,
        WHITE,
        (
            x,
            y - 120,
            120,
            120
        ),
        1
    )
    
    # Draw the held piece in the preview box if there is one
    if game.held_piece:
        draw_centered_piece(
            game.held_piece, 
            surface, 
            x + 60,  # Center of box 
            y - 60   # Center of box
        )
    
    # Draw next piece box
    next_piece_text = game.font.render("Next:", True, WHITE)
    surface.blit(next_piece_text, (x, y))
    
    # Draw next piece preview box
    pygame.draw.rect(
        surface,
        WHITE,
        (
            x,
            y + 40,
            120,
            120
        ),
        1
    )
    
    # Draw the next piece in the preview box
    draw_centered_piece(
        game.next_piece, 
        surface, 
        x + 60,  # Center of box
        y + 100  # Center of box
    )
    
    # Draw score
    score_text = game.font.render(f"Score: {game.score}", True, WHITE)
    surface.blit(score_text, (x, y + 180))
    
    # Draw level
    level_text = game.font.render(f"Level: {game.level}", True, WHITE)
    surface.blit(level_text, (x, y + 220))
    
    # Draw lines cleared
    lines_text = game.font.render(f"Lines: {game.lines_cleared}", True, WHITE)
    surface.blit(lines_text, (x, y + 260))
    
def draw_centered_piece(piece, surface, center_x, center_y):
    """Draw a tetromino piece centered at the given position
    
    Args:
        piece: The Tetromino instance to draw
        surface: The surface to draw on
        center_x: X position for the center of the piece
        center_y: Y position for the center of the piece
    """
    if piece is None:
        return
    
    # Calculate bounds of the piece to center it
    min_x = min(x for x, y in piece.shape)
    max_x = max(x for x, y in piece.shape)
    min_y = min(y for x, y in piece.shape)
    max_y = max(y for x, y in piece.shape)
    width = max_x - min_x + 1
    height = max_y - min_y + 1
    
    # Adjust starting position to center the piece
    piece_x = center_x - ((width * GRID_SIZE) // 2)
    piece_y = center_y - ((height * GRID_SIZE) // 2)
    
    for x, y in piece.shape:
        # Adjusted coordinates
        adj_x = piece_x + (x - min_x) * GRID_SIZE
        adj_y = piece_y + (y - min_y) * GRID_SIZE
        
        # Main block color
        pygame.draw.rect(
            surface,
            piece.color,
            (
                adj_x,
                adj_y,
                GRID_SIZE - 1,
                GRID_SIZE - 1
            )
        )
        
        # Highlight (top and left edges)
        highlight_color = tuple(min(c + 70, 255) for c in piece.color[:3])
        pygame.draw.line(
            surface,
            highlight_color,
            (adj_x, adj_y),
            (adj_x, adj_y + GRID_SIZE - 2),
            2
        )
        pygame.draw.line(
            surface,
            highlight_color,
            (adj_x, adj_y),
            (adj_x + GRID_SIZE - 2, adj_y),
            2
        )
        
        # Shadow (bottom and right edges)
        shadow_color = tuple(max(c - 70, 0) for c in piece.color[:3])
        pygame.draw.line(
            surface,
            shadow_color,
            (adj_x + GRID_SIZE - 2, adj_y),
            (adj_x + GRID_SIZE - 2, adj_y + GRID_SIZE - 2),
            2
        )
        pygame.draw.line(
            surface,
            shadow_color,
            (adj_x, adj_y + GRID_SIZE - 2),
            (adj_x + GRID_SIZE - 2, adj_y + GRID_SIZE - 2),
            2
        )
