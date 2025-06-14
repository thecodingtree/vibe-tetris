# Vibe Tetris

A classic Tetris clone built in Python using Pygame.

## Description

Vibe Tetris is a modern implementation of the classic Tetris game. It features all the standard Tetris gameplay elements:

- Seven different tetromino shapes
- Increasing difficulty levels
- Score tracking
- Preview of next piece
- Clean, vibrant graphics
- Ghost piece preview (showing where the piece will land)
- Hold piece functionality
- Line clearing animations
- Sound effects and background music
- Game menu with customizable options
- AI demo mode where the computer plays automatically
- Battle mode where you compete against the AI (first to 200 points wins)

## Controls

- **Left/Right Arrow Keys**: Move the tetromino horizontally
- **Up Arrow Key**: Rotate the tetromino clockwise
- **Down Arrow Key**: Soft drop (accelerate downward movement)
- **Spacebar**: Hard drop (instantly drop the tetromino)
- **C Key**: Hold the current piece
- **M Key**: Toggle music on/off
- **ESC Key**: Open the pause menu (with Continue/Exit options)
- **P Key**: Pause/Resume the game
- **R Key**: Restart the game (when game over)
- **Enter Key**: Select menu options (in main menu, pause menu, and game over screen)

## Installation

1. Ensure you have Python 3.6+ installed
2. Clone this repository:
   ```
   git clone https://github.com/yourusername/vibe-tetris.git
   cd vibe-tetris
   ```
3. (Optional) Set up a virtual environment:

   ```bash
   # Create a virtual environment
   python -m venv venv

   # Activate the virtual environment
   # On macOS/Linux:
   source venv/bin/activate
   # On Windows:
   venv\Scripts\activate
   ```

4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Running the Game

```bash
# Run the game using the main entry point
python main.py
```

## Game Rules

- Tetrominoes fall from the top of the play field
- You can move and rotate them to fit them together
- When a horizontal line is completely filled, it disappears and you score points
- The game ends when the tetrominoes stack up to the top of the play field
- As you clear more lines, the game speed increases
- Use the hold feature (C key) to save a piece for later use

## Scoring System

- 1 line cleared: 100 × level
- 2 lines cleared: 300 × level
- 3 lines cleared: 500 × level
- 4 lines cleared: 800 × level

## Features

- Game menu with options
- Sound toggle in menu (off by default)
- Ghost piece showing where the tetromino will land
- Hold piece functionality to save pieces for strategic use
- Advanced wall kick system for better rotation handling
- Line clearing animations
- Sound effects and music (when enabled)
- AI Demo mode that showcases automated gameplay
- Battle mode where you compete against the AI (first to 200 points wins)
- AI demo mode where you can watch the computer play

## License

[MIT License](LICENSE)

---

Enjoy the game! Pull requests and suggestions for improvement are welcome.
