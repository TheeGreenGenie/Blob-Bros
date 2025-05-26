#Main game class
import sys
import os
import arcade
import settings
from user import Player, PlayerInputHandler
from physics import PlatformPhysicsEngine
from entities.coin import CoinManager

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

from enemies.enemy_base import EnemyManager, EnemyState
from enemies.goomba import Goomba, create_goomba

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

        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList(use_spatial_hash=True)
        self.coin_manager = CoinManager()
        self.enemy_manager = EnemyManager()

        self.camera = arcade.camera.Camera2D()
        self.gui_camera = arcade.camera.Camera2D()

        self.player_sprite = Player()
        self.player_sprite.setup(settings.PLAYER_START_X, settings.PLAYER_START_Y)
        self.player_list.append(self.player_sprite)

        self.player_input = PlayerInputHandler(self.player_sprite)

        self.create_test_level()

        self.physics_engine = PlatformPhysicsEngine(
            self.player_sprite,
            self.wall_list,
            gravity=settings.GRAVITY,
            interactive_tiles=self.coin_manager.coin_list
        )


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

        self.camera.use()

        self.wall_list.draw()

        for coin in self.coin_manager.coin_list:
            if hasattr(coin, 'coin_color'):
                arcade.draw_circle_filled(
                    coin.center_x, coin.center_y,
                    settings.COIN_SIZE // 2,
                    coin.coin_color
                )

        for enemy in self.enemy_manager.enemy_list:
            if hasattr(enemy, 'goomba_color') and hasattr(enemy, 'goomba_size'):
                arcade.draw_circle_filled(
                    enemy.center_x, enemy.center_y,
                    enemy.goomba_size // 2,
                    enemy.goomba_color
                )

        self.player_list.draw()

        self.gui_camera.use()

        self.draw_ui()

        if self.show_debug:
            self.draw_debug_info()

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
        if self.current_state != settings.GAME_STATES["PLAYING"]:
            return
        
        self.frame_count += 1

        self.player_input.update()
        self.physics_engine.update()
        self.player_sprite.set_ground_state(self.physics_engine.can_jump())

        self.player_list.update()

        collection_info = self.coin_manager.update(delta_time, self.player_sprite)
        if collection_info:
            self.score += collection_info['value']
            print(f"Collected {collection_info['coin_type']} coin! +{collection_info['value']} points. Score: {self.score}")

        self.enemy_manager.update(delta_time, self.player_sprite)

        for enemy in self.enemy_manager.enemy_list:
            if enemy.state != EnemyState.DEAD:
                old_x = enemy.center_x
                enemy.center_x += enemy.change_x

                wall_hits = arcade.check_for_collision_with_list(enemy, self.wall_list)
                for wall in wall_hits:
                    enemy.center_x = old_x
                    enemy.handle_wall_collision('left' if enemy.change_x > 0 else "right")
                    break

                if enemy.on_ground:
                    # Create a small test point below the enemy to check for edge
                    test_x = enemy.center_x + (enemy.change_x * 2)  # Look ahead
                    test_y = enemy.center_y - 50  # Look down
                    
                    # If no ground ahead, turn around
                    ground_ahead = False
                    for wall in self.wall_list:
                        if (wall.left <= test_x <= wall.right and 
                            wall.bottom <= test_y <= wall.top):
                            ground_ahead = True
                            break
                    
                    if not ground_ahead:
                        enemy.handle_edge_detection(True)
                
                if enemy.affected_by_gravity:
                    # Apply gravity
                    enemy.change_y -= settings.GRAVITY
                    
                    # Terminal velocity
                    if enemy.change_y < -settings.TERMINAL_VELOCITY:
                        enemy.change_y = -settings.TERMINAL_VELOCITY
                    
                    # Update vertical position
                    enemy.center_y += enemy.change_y
                    
                    # Check collision with ground
                    ground_hits = arcade.check_for_collision_with_list(enemy, self.wall_list)
                    enemy.on_ground = False
                    for wall in ground_hits:
                        if enemy.change_y < 0 and enemy.bottom <= wall.top + 5:
                            enemy.bottom = wall.top
                            enemy.change_y = 0
                            enemy.on_ground = True
                            break

        # THEN update enemy manager (handles AI and behavior)
        self.enemy_manager.update(delta_time, self.player_sprite)
        self.check_coin_collections()
        self.check_enemy_interactions()

        self.update_camera()

        self.check_game_state()

    def check_coin_collections(self):
        collections = self.coin_manager.check_player_collection(self.player_sprite)
        for collection_info in collections:
            self.score += collection_info['value']
            print(f"Collected {collection_info['coin_type']} coin! +{collection_info['value']} points. Score: {self.score}")

            #Play sound when we load it
            # self.sound_manage.play_sound("collection_info['sound']")

    def check_enemy_interactions(self):
        interactions = self.enemy_manager.check_player_interactions(self.player_sprite, self.physics_engine)

        for interaction in interactions:
            print(f"Enemy Interaction: {interaction}") #Debug
            if interaction['type'] == 'stomp':
                self.score += interaction['score']
                print(f"Stomped {interaction['enemy_type']} {interaction['variant']} +{interaction['score']} points. Score: {self.score}")

                if interaction['bounce_player']:
                    bounce_height = interaction.get('bounce_height', 8)
                    self.player_sprite.change_y = bounce_height

                # Play sound effect when we add sounds
                # self.sound_manager.play_sound(interaction['sound'])

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

                    # Play sound effect when we add sounds
                    # self.sound_manager.play_sound(interaction['sound'])

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
        #Calls player class for movement and universal controls f1 & p
        self.player_input.on_key_press(key, modifiers)
        #toggle debug mode
        if key == arcade.key.F1:
            self.show_debug = not self.show_debug

        elif key == arcade.key.P:
            if self.current_state == settings.GAME_STATES["PLAYING"]:
                self.current_state = settings.GAME_STATES["PAUSED"]
            elif self.current_state == settings.GAME_STATES["PAUSED"]:
                self.current_state = settings.GAME_STATES["PLAYING"]

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