#Main entry point for game
#Run python main.py to start game

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.game import PlatformGame
    import arcade
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Make sure you have installed the required dependencies")
    print("pip install arcade")
    sys
    
def main():
    #Creates and runs game
    try:
        print("Starting Blob Platformer...")
        game = PlatformGame()
        game.setup()
        print("Game initialized successfully. Press ESC to quit.")
        arcade.run()
    except Exception as e:
        print(f"Error running the game: {e}")
        print("Check that all game files are in the correct locations.")
        sys.exit(1)

if __name__ == "__main__":
    main()