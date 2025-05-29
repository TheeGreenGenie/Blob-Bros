#Main game class
import sys
import os
import arcade
import settings
from user import Player, PlayerInputHandler
from physics import PlatformPhysicsEngine
from entities.coin import CoinManager
from enemies.enemy_base import EnemyManager, EnemyState
from enemies.goomba import Goomba, create_goomba
from ui.hud import HUD
from ui.menu import MenuManager
from utils.asset_loader import AssetLoader, get_asset_loader, load_game_assets
from utils.sound_manager import SoundManager, get_sound_manager, initialize_sound_manager
from utils.animation import AnimationManager, get_animation_manager, initialize_animation_manager, setup_player_animations, setup_enemy_animations
from tilemap import load_level

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
        self.enemy_manager  = None
        self.coin_manager = None

        self.hud_manager = None
        self.menu_manager = None

        self.asset_loader = None
        self.sound_manager = None
        self.animation_manager = None
        self.assets_loaded = False
        self.loading_error = None

        self.level_start_time = 0
        self.level_time = 0

        self.player_sprite = None
        self.player_input = None

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
        print("Starting game setup...")

        success = self._initialize_asset_system()
        if not success:
            print(f"Asset loading issues: {self.loading_error}")
            print("Continuing with available assets")
        
        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList(use_spatial_hash=True)
        self.coin_manager = CoinManager()
        self.enemy_manager = EnemyManager()

        self.camera = arcade.camera.Camera2D()
        self.gui_camera = arcade.camera.Camera2D()

        self.player_sprite = Player()
        self.player_sprite.setup(settings.PLAYER_START_X, settings.PLAYER_START_Y)
        self.player_list.append(self.player_sprite)

        if self.animation_manager:
            try:
                self.player_animation_controller = setup_player_animations(
                    self.player_sprite, self.animation_manager
                )
                print("Player animations set up successfully")
            except Exception as e:
                print(f"Animation setup failed: {e}")
                self.player_animation_controller = None
        else:
            print("No animation manager available")
            self.player_animation_controller = None

        self.player_input = PlayerInputHandler(self.player_sprite)

        try:
            self.load_level_from_file('')
        except:
            self.create_test_level()

        self.physics_engine = PlatformPhysicsEngine(
            self.player_sprite,
            self.wall_list,
            gravity=settings.GRAVITY,
            interactive_tiles=self.coin_manager.coin_list
        )

        self.hud_manager = HUD(settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
        self.menu_manager = MenuManager(settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
        self.menu_manager.show_menu('main', push_current=False)

        self.current_state = settings.GAME_STATES['MENU']
        self.level_start_time = 0
        self.level_time = 0

        if self.sound_manager:
            self.sound_manager.play_music('menu')

        print('Game setup complete!')
    
    def _initialize_asset_system(self):
        try:
            print("Loading game assets...")
            self.asset_loader = get_asset_loader()
            self.assets_loaded = self.asset_loader.load_all_assets()

            if not self.assets_loaded:
                self.loading_error = "Asset loading failed"
                return False
            
            print("Initializing sound system...")
            self.sound_manager = initialize_sound_manager(self.asset_loader)

            if self.sound_manager and self.asset_loader:
                success = self.sound_manager.set_asset_loader(self.asset_loader)
                if success:
                    print('Sound manager properly connected to asset loader')
                else:
                    print('Failed to connect sound manager to asset loader')

            print("Initializing animation system...")
            self.animation_manager = initialize_animation_manager(self.asset_loader)

            if not self.asset_loader.validate_critical_assets():
                self.loading_error = "Critical assets missing"
                return False
            
            print("All asset sysems intialized successfully!")
            return True
        
        except Exception as e:
            self.loading_error = f"Asset system intializtion failed: {e}"
            print(self.loading_error)
            return False

    def load_level_from_file(self, level_filename):
        level_path = os.path.join("levels", level_filename)
        self.current_level = load_level(level_path)
        
        if self.current_level:
            # Clear existing sprites
            self.wall_list.clear()
            self.coin_manager.reset()
            self.enemy_manager.reset()
            
            # Get the wall list from the tilemap
            self.wall_list = self.current_level.wall_list
            
            # Spawn enemies from the level data
            self.current_level.spawn_enemies(self.enemy_manager)
            
            # Spawn coins from the level data
            self.current_level.spawn_coins(self.coin_manager)
            
            # Set player starting position
            if self.current_level.player_spawn:
                self.player_sprite.center_x = self.current_level.player_spawn[0]
                self.player_sprite.center_y = self.current_level.player_spawn[1]
            
            # Set level properties
            if hasattr(self.current_level, 'background_color'):
                arcade.set_background_color(self.current_level.background_color)
            
            if hasattr(self.current_level, 'background_music') and self.sound_manager:
                self.sound_manager.play_music(self.current_level.background_music)
            
            if hasattr(self.current_level, 'time_limit'):
                self.level_time_limit = self.current_level.time_limit
            
            # Recreate physics engine with new walls
            self.physics_engine = PlatformPhysicsEngine(
                self.player_sprite,
                self.wall_list,
                gravity=settings.GRAVITY,
                interactive_tiles=self.current_level.interactive_list
            )
            
            print(f"Level '{self.current_level.name}' loaded successfully!")
            return True
        else:
            print(f"Failed to load level: {level_filename}")
            # Fall back to test level
            self.create_test_level()
            return False

    def create_test_level(self):
        #Simple test level with platforms & coins, will be replaced

        for x in range(0, 800, settings.TILE_SIZE):  # Ground Platforms
            wall = arcade.Sprite()
            wall.center_x = x
            wall.center_y = settings.TILE_SIZE // 2

            if hasattr(self, 'asset_loader') and self.asset_loader:
                ground_texture = self.asset_loader.get_tile_texture('ground')
                if ground_texture:
                    wall.texture = ground_texture
                else:
                    wall = arcade.SpriteSolidColor(
                        settings.TILE_SIZE,
                        settings.TILE_SIZE,
                        settings.GREEN
                    )
                    wall.center_x = x
                    wall.center_y =  settings.TILE_SIZE // 2
            self.wall_list.append(wall)


        platform_data = [
            (300, 150),
            (500, 200),
            (700, 250),
        ]

        for x, y in platform_data:
            for offset in range(0, settings.TILE_SIZE * 3, settings.TILE_SIZE):
                wall = arcade.Sprite()
                wall.center_x = x + offset
                wall.center_y = y

                if hasattr(self, 'asset_loader') and self.asset_loader:
                    ground_texture = self.asset_loader.get_tile_texture('ground')
                    if ground_texture:
                        wall.texture = ground_texture

            self.wall_list.append(wall)
        
        coin_positions = [
            (200, 50, 'normal'),
            (400, 80, 'silver'),
            (600, 100, 'gold'),
            (350, 70, 'normal'),
            (500, 90, 'special')
        ]

        for x, y, coin_type in coin_positions:
            self.coin_manager.add_coin(x, y, coin_type)

        enemy_positions = [
            (250, 50, 'normal'),
            (450, 80, 'fast'), 
            (650, 80, 'large'),
            (750, 50, 'normal'),
            (550, 80, 'elite')
        ]
    
        for x, y, variant in enemy_positions:
            goomba = create_goomba(x, y, variant)
            self.enemy_manager.enemy_list.append(goomba)
            self.enemy_manager.total_enemies += 1

        for enemy in self.enemy_manager.enemy_list:
            enemy.change_y = 0

    def on_draw(self):
        #Render screen
        self.clear()

        if self.current_state == settings.GAME_STATES['MENU']:
            self.menu_manager.draw()
        elif self.current_state in [settings.GAME_STATES['PLAYING'], settings.GAME_STATES['PAUSED'], settings.GAME_STATES['GAME_OVER']]:
            self._draw_game_world()
            self.hud_manager.draw()

            if self.current_state == settings.GAME_STATES['PAUSED']:
                self.menu_manager.draw()
            elif self.current_state == settings.GAME_STATES['GAME_OVER']:
                self.menu_manager.draw()

    def _draw_game_world(self):
        self.gui_camera.use()

        if hasattr(self, 'asset_loader') and self.asset_loader:
            sky_texture = self.asset_loader.get_texture('sky')
            if sky_texture:
                arcade.draw_texture_rect(
                    sky_texture,
                    arcade.XYWH(
                        settings.SCREEN_WIDTH // 2,
                        settings.SCREEN_HEIGHT // 2,
                        settings.SCREEN_WIDTH,
                        settings.SCREEN_HEIGHT
                    )
                )

        self.camera.use()
        self.wall_list.draw()
        self.coin_manager.coin_list.draw()
        self.enemy_manager.enemy_list.draw()
        self.player_list.draw()

        self.gui_camera.use()

    def draw_ui(self):
        #Draw ui like score & lives

        arcade.draw_text(
            f"Score: {self.score}",
            10, settings.SCREEN_HEIGHT - 30,
            settings.LIVES_COLOR,
            18
        )

        arcade.draw_text(
            f"Lives: {self.lives}",
            10, settings.SCREEN_HEIGHT - 60,
            settings.LIVES_COLOR,
            18
        )

        coin_stats = self.coin_manager.get_stats()
        arcade.draw_text(
            f"Coins: {coin_stats['collected_coins']}/{coin_stats['total_coins']}",
            10, settings.SCREEN_HEIGHT - 90,
            settings.WHITE,
            18
        )

        if settings.SHOW_ENEMIES:
            enemy_stats = self.enemy_manager.get_stats()
            arcade.draw_text(
                f"Enemies: {enemy_stats['defeated_enemies']}/{enemy_stats['total_enemies']}",
                10, settings.SCREEN_HEIGHT - 120,
                settings.WHITE,
                18
            )

        if settings.SHOW_FPS:
            fps = f"FPS: {int(arcade.get_fps())}"
            arcade.draw_text(
                fps,
                settings.SCREEN_WIDTH - 100, settings.SCREEN_HEIGHT - 30,
                settings.WHITE,
                14
            )

    def draw_debug_info(self):
        debug_text = f"Player: ({int(self.player_sprite.center_x)}, {int(self.player_sprite.center_y)})"
        arcade.draw_text(
            debug_text,
            10, 50,
            settings.WHITE,
            14
        )

        if hasattr(self.physics_engine, 'player_on_ground'):
            ground_text = f"On Ground: {self.physics_engine.player_on_ground}"
            arcade.draw_text(
                ground_text,
                10, 30,
                settings.WHITE,
                14
            )

        if hasattr(self.physics_engine, 'player_on_wall'):
            wall_text = f"On Wall: {self.physics_engine.player_on_wall}"
            arcade.draw_text(
                wall_text,
                10, 10,
                settings.WHITE,
                14
            )

        if settings.SHOW_HITBOXES:
            #Would draw collision rectanges - input later
            pass

        if settings.DEBUG_MODE:
            self.enemy_manager.draw_debug()

    def on_update(self, delta_time):
        #Update logic, called once per frame
        if self.current_state == settings.GAME_STATES['MENU']:
            self.menu_manager.update(delta_time)
        elif self.current_state == settings.GAME_STATES['PLAYING']:
            self._update_gameplay(delta_time)
        elif self.current_state == settings.GAME_STATES['PAUSED']:
            self.menu_manager.update(delta_time)
        elif self.current_state == settings.GAME_STATES['GAME_OVER']:
            self.menu_manager.update(delta_time)

    def _update_gameplay(self, delta_time):
        self.frame_count += 1
        self.level_time += delta_time

        if self.player_input:
            self.player_input.update()
        else:
            print("Warning: player_input is None")
            return  # Exit early w/o essential components

        self.player_input.update()
        for enemy in self.enemy_manager.enemy_list:
            if enemy.state != 'dead':
                old_x = enemy.center_x
                enemy.center_x += enemy.change_x

                wall_hits = arcade.check_for_collision_with_list(enemy, self.wall_list)
                for wall in wall_hits:
                    enemy.center_x = old_x
                    enemy.handle_wall_collision('left' if enemy.change_x > 0  else 'right')
                    break

                if enemy.affected_by_gravity:
                    enemy.change_y -= settings.GRAVITY

                    if enemy.change_y < -settings.TERMINAL_VELOCITY:
                        enemy.change_y = -settings.TERMINAL_VELOCITY

                    enemy.center_y += enemy.change_y

                    ground_hits = arcade.check_for_collision_with_list(enemy, self.wall_list)
                    enemy.on_ground = False
                    for wall in ground_hits:
                        if enemy.change_y < 0 and enemy.bottom <= wall.top + 5:
                            enemy.bottom = wall.top
                            enemy.change_y = 0
                            enemy.on_ground = True
                            break

        self.enemy_manager.update(delta_time, self.player_sprite)
        self.physics_engine.update()
        self.player_sprite.set_ground_state(self.physics_engine.can_jump())
        self.player_list.update()
        if self.animation_manager:
            self.animation_manager.update_all(delta_time)

        collection_info = self.coin_manager.update(delta_time, self.player_sprite)
        if collection_info:
            self.score += collection_info['value']
            print(f"Collected {collection_info['coin_type']} coin! +{collection_info['value']} points. Score: {self.score}")

        self.check_coin_collections()
        self.check_enemy_interactions()
        self.update_camera()
        self.check_game_state()

        hud_data = {
            'score': self.score,
            'lives': self.lives,
            'level_time': self.level_time,
            'level_name': '1-1',
            'coins_collected': self.coin_manager.collected_coins,
            'total_coins': self.coin_manager.total_coins,
            'enemies_defeated': self.enemy_manager.defeated_enemies,
            'total_enemies': self.enemy_manager.total_enemies
        }
        self.hud_manager.update(delta_time, hud_data)


    def check_coin_collections(self):
        collections = self.coin_manager.check_player_collection(self.player_sprite)
        for collection_info in collections:
            self.score += collection_info['value']
            print(f"Collected {collection_info['coin_type']} coin! +{collection_info['value']} points. Score: {self.score}")

            self.sound_manager.play_sound('coin')

    def check_enemy_interactions(self):
        interactions = self.enemy_manager.check_player_interactions(self.player_sprite, self.physics_engine)

        for interaction in interactions:
            if interaction['type'] == 'stomp':
                self.score += interaction['score']
                print(f"Stomped {interaction['enemy_type']} {interaction['variant']} +{interaction['score']} points. Score: {self.score}")

                if interaction['bounce_player']:
                    bounce_height = interaction.get('bounce_height', 8)
                    self.player_sprite.change_y = bounce_height

                self.sound_manager.play_sound('stomp')

            elif interaction['type'] == 'damage':
                if not settings.INVINCIBLE_MODE:
                    print(f"Player should take damage from {interaction['enemy_type']}")
                    damage = interaction['damage_to_player']

                    if hasattr(self.player_sprite, 'take_damage'):
                        player_died = self.player_sprite.take_damage() if hasattr(self.player_sprite, 'take_damage') else False
                    else:
                        self.lives -= 1
                        player_died = self.lives <= 0


                    if player_died:
                        self.player_die()
                    else:
                        print(f"Player hurt by {interaction['enemy_type']}")

                        if interaction.get('knockback'):
                            self.player_sprite.change_x = 3 if self.player_sprite.change_x >= 0 else -3

                    self.sound_manager.play_sound('death')

    def update_camera(self):
        #update camera to follow player
        target_x = self.player_sprite.center_x - 400
        target_y = self.player_sprite.center_y - 300
        
        # Don't scroll past the left edge
        if target_x < 0:
            target_x = 0
            
        # Don't scroll below ground level
        if target_y < 0:
            target_y = 0
        
        # Get current camera position
        current_x, current_y = self.camera.position
        
        # Smoothly interpolate toward target position
        # The closer to 1.0, the faster the camera follows
        follow_speed = 0.1  # Adjust this for different feel (0.05 = slow, 0.2 = fast)
        
        new_x = current_x + (target_x - current_x) * follow_speed
        new_y = current_y + (target_y - current_y) * follow_speed
        
        # Set the new camera position
        self.camera.position = (new_x, new_y)

    
    def check_game_state(self):
        #Checks for level or game over

        if self.player_sprite.center_y < -100:
            self.player_die()

        if self.player_sprite.center_x > settings.LEVEL_END_X:
            self.level_complete = True
            #Maybe add something here after completion? - come back later

    def player_die(self):
        self.lives -= 1

        if self.lives <= 0:
            self.current_state = settings.GAME_STATES["GAME_OVER"]
            self.menu_manager.set_game_over_stats(
                self.score, '1-1',
                self.coin_manager.collected_coins,
                self.enemy_manager.defeated_enemies
            )
            self.menu_manager.show_menu('game_over', push_current=False)
            print("Game Over!")
        else:
            self.respawn_player()

    def respawn_player(self):
        #Respawn at starting position
        self.player_sprite.center_x = settings.PLAYER_START_X
        self.player_sprite.center_y = settings.PLAYER_START_Y
        self.player_sprite.change_x = 0
        self.player_sprite.change_y = 0

    def on_key_press(self, key, modifiers):

        #Handles key presses
        if self.current_state == settings.GAME_STATES['MENU']:
            action = self.menu_manager.handle_input(key)
            self._handle_menu_action(action)
        elif self.current_state == settings.GAME_STATES['PLAYING']:
            self.player_input.on_key_press(key, modifiers)

            if key == arcade.key.F1:
                self.show_debug = not self.show_debug
            elif key == arcade.key.P or key == arcade.key.ESCAPE:
                self.current_state = settings.GAME_STATES['PAUSED']
                self.menu_manager.show_menu('pause', push_current=False)
        elif self.current_state == settings.GAME_STATES['PAUSED']:
            action = self.menu_manager.handle_input(key)
            self._handle_menu_action(action)
        elif self.current_state == settings.GAME_STATES['GAME_OVER']:
            action = self.menu_manager.handle_input(key)
            self._handle_menu_action(action)

    def _handle_menu_action(self, action):
        if action == 'start_game':
            self._start_new_game()
            self.sound_manager.play_sound('menu_select')
        elif action == 'settings':  # Add this
            self.menu_manager.show_menu('settings')
            self.sound_manager.play_sound('menu_select')
        elif action == 'high_scores':  # Add this
            self._show_high_scores()
            self.sound_manager.play_sound('menu_select')
        elif action == 'credits':  # Add this
            self._show_credits()
            self.sound_manager.play_sound('menu_select')
        elif action == 'resume':
            self.current_state = settings.GAME_STATES['PLAYING']
            self.sound_manager.resume_music()
        elif action == 'restart_level':
            self._restart_game()
            self.sound_manager.play_sound('menu_select')
        elif action == 'play_again':
            self._start_new_game()
            self.sound_manager.play_sound('menu_select')
        elif action == 'restart':
            self._restart_game()
            self.sound_manager.play_sound('menu_select')
        elif action == 'main_menu':
            self.current_state = settings.GAME_STATES["MENU"]
            self.menu_manager.show_menu('main', push_current=False)
            self.sound_manager.play_sound('menu_select')
        elif action == 'quit':
            self.close()
            

    def _show_high_scores(self):
        print("High scores feature not yer implemented")

    def _show_credits(self):
        print("Credits not implemented yet")

    def _start_new_game(self):
        self.score = 0
        self.lives = settings.PLAYER_LIVES
        self.level_time = 0
        self.level_start_time = 0

        self.respawn_player()
        self.coin_manager.reset()
        self.enemy_manager.reset()

        self.create_test_level()

        self.physics_engine = PlatformPhysicsEngine(
            self.player_sprite,
            self.wall_list,
            gravity=settings.GRAVITY,
            interactive_tiles=self.coin_manager.coin_list
        )

        self.current_state = settings.GAME_STATES['PLAYING']
        self.sound_manager.play_music('overworld')

    def _restart_game(self):
        self.level_time = 0
        self.respawn_player()
        self.current_state = settings.GAME_STATES['PLAYING']

    def on_key_release(self, key, modifiers):
        self.player_input.on_key_release(key, modifiers)

    def restart_game(self):
        #Restart game from beginnning

        self.score = 0
        self.lives = settings.PLAYER_LIVES
        self.level_complete = False
        self.current_state = settings.GAME_STATES["PLAYING"]

        self.respawn_player()

        self.coin_list = arcade.SpriteList(use_spatial_hash=True)
        self.create_test_level()

def main():
    #runs the game
    game = PlatformGame()
    game.setup()

    arcade.run()

if __name__ == "__main__":
    main()