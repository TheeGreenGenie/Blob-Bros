# Blob-Bros
# Mario-Style Platformer Game

A classic Mario-inspired platformer game built with Python and the Arcade library. Features multiple enemy types, collectible coins, physics-based gameplay, and level completion mechanics.

## 🎮 Game Features

- **Classic Platformer Mechanics**: Run, jump, and navigate through levels
- **Multiple Enemy Types**: Face off against different Goomba variants with unique abilities
- **Collectible System**: Gather coins of different values to increase your score
- **Physics Engine**: Realistic gravity, collision detection, and movement
- **Level Progression**: Complete levels by defeating all enemies
- **Menu System**: Navigate through game states with intuitive menus
- **Sound Effects**: Immersive audio feedback for actions and events
- **Debug Mode**: Developer tools for testing and level design

## 🎯 How to Play

### Controls
- **Arrow Keys**: Move left/right
- **Spacebar**: Jump
- **P or ESC**: Pause game
- **F1**: Toggle debug mode (shows hitboxes and enemy vision ranges)

### Objective
- **Primary Goal**: Defeat all enemies in the level to advance
- **Collect Coins**: Gather different types of coins for points
  - Normal Coins: 100 points
  - Silver Coins: 200 points
  - Gold Coins: 500 points
  - Special Coins: 1000 points
- **Enemy Combat**: Jump on enemies to defeat them
- **Avoid Damage**: Don't touch enemies from the side

### Enemy Types
- **Normal Goomba**: Basic enemy that walks in straight lines
- **Fast Goomba**: Moves quickly and changes direction randomly
- **Large Goomba**: Takes two hits to defeat, becomes smaller after first hit
- **Elite Goomba**: Charges at the player when spotted

## 📥 Download & Installation

### Prerequisites
- Python 3.9 or higher
- Git (for cloning the repository)

### Step 1: Download the Repository
```bash
# Clone the repository
git clone https://github.com/TheeGreenGenie/Blob-Bros.git
cd BlobGame

# Or download as ZIP from GitHub and extract
```

### Step 2: Create Virtual Environment
```bash
# Create a new virtual environment
python -m venv game_env

# Activate the virtual environment
# On Windows:
game_env\Scripts\activate

# On macOS/Linux:
source game_env/bin/activate
```

### Step 3: Install Dependencies
```bash
# Install all required packages
pip install -r requirements.txt

# Verify installation
python -c "import arcade; print(f'Arcade {arcade.__version__} installed successfully')"
```

### Step 4: Run the Game
```bash
# Start the game
python main.py

# Alternative if main.py doesn't exist
python src/game.py
```

## 🛠️ Development Setup

### Project Structure
```
mario-platformer/
├── src/                    # Source code
│   ├── game.py            # Main game class
│   ├── settings.py        # Game configuration
│   ├── user.py            # Player character
│   ├── physics.py         # Physics engine
│   ├── entities/          # Game objects
│   │   └── coin.py        # Collectible coins
│   ├── enemies/           # Enemy classes
│   │   ├── enemy_base.py  # Base enemy functionality
│   │   └── goomba.py      # Goomba enemy variants
│   ├── ui/                # User interface
│   │   ├── hud.py         # Heads-up display
│   │   └── menu.py        # Game menus
│   └── utils/             # Utilities
│       ├── asset_loader.py # Asset management
│       ├── sound_manager.py # Audio system
│       └── animation.py    # Animation system
├── assets/                # Game assets
│   ├── sprites/           # Character and object graphics
│   ├── sounds/            # Sound effects
│   ├── music/             # Background music
│   └── tiles/             # Level building blocks
├── levels/                # Level files (TMX format)
├── requirements.txt       # Python dependencies
└── main.py               # Game entry point
```

### Dependencies
The game uses these main libraries:
- **arcade==3.2.0** - Game engine and graphics
- **pillow==11.0.0** - Image processing
- **pyglet==2.1.6** - Multimedia framework
- **pymunk==6.9.0** - Physics simulation
- **pytiled_parser==2.2.9** - TMX level file support

## 🗺️ Creating Custom Levels

### Using Tiled Map Editor

1. **Download Tiled**: Get the free Tiled map editor from [mapeditor.org](https://www.mapeditor.org/)

2. **Create a New Map**:
   - File → New → New Map
   - Orientation: Orthogonal
   - Tile size: 32x32 pixels
   - Map size: 50x20 tiles (or your preferred size)

3. **Add Tilesets**:
   - Map → New Tileset
   - Load tile images from `assets/tiles/`
   - Set tile size to 32x32

4. **Level Design Guidelines**:
   - **Ground tiles**: Use for platforms and solid surfaces
   - **Coin placement**: Spread coins throughout the level
   - **Enemy spawns**: Place in strategic locations
   - **Player spawn**: Set starting position (usually bottom-left)
   - **Level boundaries**: Ensure players can't fall infinitely

5. **Tile Types**:
   - Ground: Solid platforms
   - Brick: Destructible blocks
   - Question blocks: Interactive elements
   - Pipes: Decorative or functional elements
   - Background: Non-collidable decoration

6. **Save and Test**:
   - Save as TMX file in the `levels/` directory
   - Update game code to load your level
   - Test thoroughly for gameplay flow

### Level Design Tips
- **Start Simple**: Begin with basic platform layouts
- **Test Frequently**: Playtest your levels during development
- **Balance Difficulty**: Gradually increase challenge
- **Visual Clarity**: Make platforms and hazards clearly distinguishable
- **Player Flow**: Guide players through natural movement patterns

## 🎨 Assets and Credits

This game uses assets from the following sources:

### Graphics
- **Platformer Sprites**: [New Platformer Pack · Kenney](https://kenney.nl/assets/platformer-pack-redux)
- **Additional Tiles**: [Puzzle Pack 2 · Kenney](https://kenney.nl/assets/puzzle-pack-2)
- **Castle Graphics**: [Download castle PNG Image for Free](https://pngimg.com/image/9158)

### Audio
- **Sound Effects**: [Pixabay Sound Effects](https://pixabay.com/sound-effects/)
- **Background Music**: Various royalty-free sources

### Special Thanks
- **Kenney**: For providing high-quality, free game assets
- **Pixabay**: For royalty-free sound effects
- **Python Arcade Community**: For excellent documentation and support

### Game Settings
Edit `src/settings.py` to customize:
- Screen resolution and window title
- Player movement speed and jump height
- Enemy behavior and speeds
- Audio volume levels
- Debug display options

### Key Configuration Examples
```python
# Screen settings
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768

# Player settings
PLAYER_MOVEMENT_SPEED = 5
PLAYER_JUMP_SPEED = 16

# Audio settings
MASTER_VOLUME = 0.7
ENABLE_SOUND = True

# Debug settings
DEBUG_MODE = False
SHOW_HITBOXES = False
```

## 🐛 Troubleshooting

### Common Issues

**Game won't start:**
- Check Python version (3.9+ required)
- Verify virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

**No sound/graphics:**
- Check file paths in asset loader
- Verify assets exist in `assets/` directory
- Try disabling sound: set `ENABLE_SOUND = False` in settings

**Performance issues:**
- Lower screen resolution in settings
- Disable debug mode
- Update graphics drivers

**Import errors:**
- Activate virtual environment
- Check all dependencies are installed
- Verify Python path includes `src/` directory

### Debug Mode
Press F1 during gameplay to enable debug features:
- Red outlines around collision boxes
- Yellow circles showing enemy vision ranges
- Performance metrics and position information

## 🚀 Building Executables

To create standalone executables for distribution:

1. **Install build tools:**
   ```bash
   pip install -r requirements-build.txt
   ```

2. **Run build script:**
   ```bash
   python build_executable.py
   ```

3. **Find executables in:**
   ```
   releases/mario_platformer_[platform]/
   ```

## 📝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Code Style
- Follow PEP 8 guidelines
- Add docstrings to new functions
- Comment complex algorithms
- Test new features extensively

## 📄 License

This project is open source. Please respect the licenses of included assets:
- Kenney assets: [CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/)
- Pixabay audio: Various Creative Commons licenses
- Code: Feel free to use and modify

## 🎯 Future Features

Planned improvements:
- [ ] Multiple levels with TMX loading
- [ ] More enemy types and boss battles
- [ ] Power-ups and player abilities
- [ ] High score system
- [ ] Level editor integration
- [ ] Multiplayer support
- [ ] Achievement system

## 💬 Support

If you encounter issues or have questions:
1. Check the troubleshooting section above
2. Review the game's debug output (F1 key)
3. Ensure all dependencies are correctly installed
4. Verify asset files are in the correct directories

## 🎮 Enjoy the Game!

Thank you for playing my Mario-style platformer! We hope you enjoy both playing and potentially modifying the game. Happy gaming! 🍄