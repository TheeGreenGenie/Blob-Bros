#Main game class

import arcade
from . import settings

class PlatformGame(arcade.Window):
    #Main game class managing window, game loop, & game state

    def __init__(self):
        #initialize game window
        super().__init__(
            settings.SCREEN_WIDTH,
            settings.SCREEN_HEIGHT,
            settings.SCREEN_TITLE
        )

        arcade.set_background_color(settings.SKY_BLUE)

        self.current_state = settings.GAME_STATES["PLAYING"]

        self.player_list = None
        self.wall_list = None
        self.coin_list = None
        self.enemy_list  = None

        self.player_sprite = None

        self.physics_engine = None # For Collisions & Movement

        #Camera for scrolling
        self.camera = None
        self.gui_camera = None

        self.score = 0
        self.lives = settings.PLAYER_LIVES
        self.level_complete = False

        self.frame_count = 0

        self.show_debug = settings.DEBUG_MODE

    def setup(self):
        #Setup game and initialize starting vars, called after creating window

        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList(use_spatial_hash=True)
        self.coin_list = arcade.SpriteList(use_spatial_hash=True)
        self.enemy_list = arcade.SpriteList()

        self.camera = arcade.Camera(settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
        self.gui_camera = arcade.Camera(settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)

        self.player_sprite = arcade.SpriteSolidColor(
            settings.PLAYER_SIZE,
            settings.PLAYER_SIZE,
            settings.RED
        )
        self.player_sprite.center_x = settings.PLAYER_START_X
        self.player_sprite.center_y = settings.PLAYER_START_Y
        self.player_list.append(self.player_sprite)

        self.create_test_level()

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite,
            self.wall_list,
            gravity_constant=settings.GRAVITY
        )

        print("Game setup complete!")

    def create_test_level(self):
        #Simple test level with platforms & coins, will be replaced

        for x in range(0, 800, settings.TILE_SIZE):  # Ground Platforms
            wall = arcade.SpriteSolidColor(
                settings.TILE_SIZE,
                settings.TILE_SIZE,
                settings.GREEN
            )
            wall.center_x = x
            wall.center_y = settings.TILE_SIZE // 2
            self.wall_list.append(wall)

        platform_data = [
            (300, 150),
            (500, 200),
            (700, 250),
        ]

        for x, y in platform_data:
            for offset in range(0, settings.TILE_SIZE * 3, settings.TILE_SIZE):
                wall = arcade.SpriteSolidColor(
                    settings.TILE_SIZE,
                    settings.TILE_SIZE,
                    settings.GREEN
                )
        
        coin_positions = [
            (200, 100),
            (400, 250),
            (600, 300),
            (350, 250),
        ]

        for x, y in coin_positions:
            coin = arcade.SpriteSolidColor(
                settings.COIN_SIZE,
                settings.COIN_SIZE,
                settings.YELLOW
            )
            coin.center_x = x
            coin.center_y = y
            self.coin_list.append(coin)