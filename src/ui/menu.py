#Menu classes (pages)
import arcade
import math
import random
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import settings

class MenuItem:
    
    def __init__(self, text, action=None, enabled=True, submenu=None):
        self.text = text
        self.action = action
        self.enabled = enabled
        self.submenu = submenu

        self.selected = False
        self.hover_time = 0
        self.flash_timer = 0

class BaseMenu:

    def __init__(self, screen_width, screen_height, title="Menu"):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.title = title

        self.items = []
        self.selected_index = 0

        self.background_color = (0, 50, 100)
        self.title_color = settings.WHITE
        self.item_color = settings.WHITE
        self.selected_color = (255, 255, 0)
        self.disabled_color = (128, 128, 128)

        self.title_size = 48
        self.item_size = 24
        self.item_spacing  = 40
        self.title_y_offset = 150

        self.animation_timer = 0
        self.pulse_amplitude = 10

        self.input_cooldown = 0
        self.input_delay = 0.05

    def add_item(self, text, action=None, enabled=True, submenu=None):
        item = MenuItem(text, action, enabled, submenu)
        self.items.append(item)
        return item
    
    def clear_items(self):
        self.items.clear()
        self.selected_index = 0

    def update(self, delta_time):
        self.animation_timer += delta_time

        if self.input_cooldown > 0:
            self.input_cooldown -= delta_time

        for i, item in enumerate(self.items):
            if i == self.selected_index:
                item.hover_time += delta_time
                item.selected = True
            else:
                item.hover_time = 0
                item.selected = False

    def handle_input(self, key):
        #DEBUG CODE
        print(f"BaseMenu handle_input called with key: {key}") 
        if self.input_cooldown > 0:
            print('Input on cooldown')
            return None
        
        if key == arcade.key.UP:
            #DEBUG CODE
            print('Up key detected')
            self.move_selection(-1)
            self.input_cooldown = self.input_delay

        elif key == arcade.key.DOWN:
            self.move_selection(1)
            self.input_cooldown = self.input_delay

        elif key == arcade.key.ENTER or key == arcade.key.SPACE:
            return self.select_current_item()
        
        return None
    
    def move_selection(self, direction):
        if not self.items:
            return
        
        start_index = self.selected_index
        while True:
            self.selected_index = (self.selected_index + direction) % len(self.items)

            if self.items[self.selected_index].enabled or self.selected_index == start_index:
                break

    def select_current_item(self):
        if not self.items or self.selected_index >= len(self.items):
            return None
        
        item = self.items[self.selected_index]
        if item.enabled:
            return item.action
        return None
    
    def draw(self):
        arcade.draw_lbwh_rectangle_filled(
            0, 0,
            self.screen_width, self.screen_height,
            self.background_color
        )

        title_y = self.screen_height - self.title_y_offset
        title_x = self.screen_width // 2 - len(self.title) * self.title_size // 4
        arcade.draw_text(
            self.title,
            title_x, title_y,
            self.title_color, self.title_size,
        )

        self.draw_items()

    def draw_items(self):
        if not self.items:
            return
        
        total_height = len(self.items) * self.item_spacing
        start_y = self.screen_height // 2 + total_height // 2

        for i, item in enumerate(self.items):
            y_position = start_y - (i *self.item_spacing)

            if not item.enabled:
                color = self.disabled_color
                offset = 0
            elif item.selected:
                pulse = math.sin(self.animation_timer * 5) * self.pulse_amplitude
                color = self.selected_color
                offset = pulse

                text_width = len(item.text) * self.item_size * 0.6
                arcade.draw_lbwh_rectangle_filled(
                    (self.screen_width // 2) - (text_width // 2) - 20,
                    y_position - 5,
                    text_width + 40,
                    self.item_size + 10,
                    (50, 50, 100, 128)
                )
            else:
                color = self.item_color
                offset = 0

            text_width = len(item.text) * self.item_size * 0.6
            text_x = (self.screen_width // 2) - (text_width // 2) + offset

            arcade.draw_text(
                item.text,
                text_x, y_position,
                color, self.item_size,
            )

            if item.selected:
                arcade.draw_text(
                    "►",
                    text_x - 50, y_position,
                    self.selected_color, self.item_size,
                )

                arcade.draw_text(
                    "◄",
                    text_x + text_width + 30, y_position,
                    self.selected_color, self.item_size
                )

class MainMenu(BaseMenu):

    def __init__(self, screen_width, screen_height):
        super().__init__(screen_width, screen_height, 'MARIO PlATFORMER')

        self.add_item("START GAME", 'start_game')
        self.add_item("SETTINGS", 'settings')
        self.add_item("HIGH SCORES", 'high_scores')
        self.add_item("CREDITS", 'credits')
        self.add_item("QUIT", 'quit')

        self.background_color = (25, 25, 112)
        self.title_color = (255, 215, 0)

        self.star_positions = []
        self.generate_background_stars()

    def generate_background_stars(self):
        for _  in range(50):
            x = random.randint(0, self.screen_width)
            y = random.randint(0, self.screen_height)
            size = random.randint(1, 3)
            speed = random.uniform(10, 30)
            self.star_positions.append([x, y, size, speed])

    def update(self, delta_time):
        super().update(delta_time)

        for star in self.star_positions:
            star[1] -= star[3] * delta_time   # Move star down
            if star[1] < 0:   # Reset if leaves screen
                star[1] = self.screen_height
                star[0] = __import__('random').randint(0, self.screen_width)

    def draw(self):
        #Gradient
        for y in range(0, self.screen_height, 4):
            intensity = y / self.screen_height
            color = (
                int(25 + intensity * 50),
                int(25 + intensity * 50),
                int(112 + intensity * 50)
            )

            arcade.draw_lbwh_rectangle_filled(
                0, y,
                self.screen_width, 4,
                color
            )

        for star in self.star_positions:
            arcade.draw_circle_filled(star[0], star[1], star[2], settings.WHITE)

        shadow_offset = 3
        
        # Calculate title positioning manually
        title_width = len(self.title) * self.title_size // 2  # Rough text width estimation
        title_x = (self.screen_width // 2) - (title_width // 2)
        title_y = self.screen_height - self.title_y_offset
        
        # Draw title shadow
        arcade.draw_text(
            self.title,
            title_x + shadow_offset,
            title_y - shadow_offset,
            (50, 50, 50), self.title_size
        )

        # Draw main title
        arcade.draw_text(
            self.title,
            title_x, title_y,
            self.title_color, self.title_size
        )

        self.draw_items()

        # Draw subtitle with manual centering
        subtitle = "Use ↑↓ to navigate, ENTER to select"
        subtitle_width = len(subtitle) * 16 // 2  # Rough text width estimation
        subtitle_x = (self.screen_width // 2) - (subtitle_width // 2)
        arcade.draw_text(
            subtitle,
            subtitle_x, 50,
            settings.WHITE, 16
        )

class PauseMenu(BaseMenu):

    def __init__(self, screen_width, screen_height):
        super().__init__(screen_width, screen_height, "PAUSED")

        self.add_item("RESUME", 'resume')
        self.add_item("RESTART LEVEL", 'restart_level')
        self.add_item("SETTINGS", 'settings')
        self.add_item("MAIN MENU", 'main_menu')

        self.background_color = (0, 0, 0, 180)
        self.title_size = 36

    def draw(self):
        arcade.draw_lbwh_rectangle_filled(
            0, 0,
            self.screen_width, self.screen_height,
            (0, 0, 0, 180)
        )

        super().draw()

class GameOverMenu(BaseMenu):

    def __init__(self, screen_width, screen_height):
        super().__init__(screen_width, screen_height, "GAME OVER")

        self.final_score  = 0
        self.level_reached = '1-1'
        self.coins_collected = 0
        self.enemies_defeated = 0

        self.add_item('PLAY AGAIN', 'play_again')
        self.add_item('MAIN MENU', 'main_menu')
        self.add_item('QUIT', 'quit')

        self.background_color = (100, 0, 0)
        self.title_color = (255, 100, 100)

    def set_game_stats(self, score, level, coins, enemies):
        self.final_score = score
        self.level_reached = level
        self.coins_collected = coins
        self.enemies_defeated = enemies

    def draw(self):
        super().draw()

        stats_y = self.screen_height // 2 - 50

        stats = [
            f"Final Score: {self.final_score:06d}",
            f"Level Reached: {self.level_reached}",
            f"Coins Collected: {self.coins_collected}",
            f"Enemies Defeated: {self.enemies_defeated}"
        ]

        for i, stat in enumerate(stats):
            stat_width = len(stat) * 18 // 2  # Rough text width
            stat_x = (self.screen_width // 2) - (stat_width // 2)
            arcade.draw_text(
                stat,
                stat_x, stats_y - (i * 30),
                settings.WHITE, 18
            )

class SettingsMenu(BaseMenu):

    def __init__(self, screen_width, screen_height):
        super().__init__(screen_width, screen_height, "SETTINGS")

        self.music_enabled = True
        self.sound_enabled = True
        self.debug_mode = settings.DEBUG_MODE
        self.show_fps = settings.SHOW_FPS

        self.rebuild_items()

    def rebuild_items(self):
        self.clear_items()

        music_text = f"Music: {'ON' if self.music_enabled else 'OFF'}"
        self.add_item(music_text, 'toggle_music')

        sound_text = f"Sound EFffects: {'ON' if self.sound_enabled else 'OFF'}"
        self.add_item(sound_text, 'toggle_sound')

        debug_text = f"Debug Mode: {'ON' if self.debug_mode else 'OFF'}"
        self.add_item(debug_text, 'toggle_debug')

        fps_text = f"Show FPS: {'ON' if self.show_fps else 'OFF'}"
        self.add_item(fps_text, 'toggle_fps')

        self.add_item("BACK", 'back')

    def handle_setting_action(self, action):
        if action == 'toggle_music':
            self.music_enabled = not self.music_enabled
        elif action == 'toggle_sound':
            self.sound_enabled = not self.sound_enabled
        elif action == 'toggle_debug':
            self.debug_mode = not self.debug_mode
            settings.DEBUG_MODE = self.debug_mode
        elif action == 'toggle_fps':
            self.show_fps = not self.show_fps
            settings.SHOW_FPS = self.show_fps
        self.rebuild_items()

class MenuManager:

    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.main_menu = MainMenu(screen_width, screen_height)
        self.pause_menu = PauseMenu(screen_width, screen_height)
        self.game_over_menu = GameOverMenu(screen_width, screen_height)
        self.settings_menu = SettingsMenu(screen_width, screen_height)

        self.menu_stack = []
        self.current_menu = self.main_menu

        self.transitioning = False
        self.transition_timer = 0
        self.transition_duration = 0.3

    def show_menu(self, menu_name, push_current=True):
        if push_current and self.current_menu:
            self.menu_stack.append(self.current_menu)

        if menu_name == 'main':
            self.current_menu = self.main_menu
        elif menu_name == 'pause':
            self.current_menu = self.pause_menu
        elif menu_name == 'game_over':
            self.current_menu = self.game_over_menu
        elif menu_name == 'settings':
            self.current_menu = self.settings_menu

    def go_back(self):
        if self.menu_stack:
            self.current_menu = self.menu_stack.pop()
            return True
        return False
    
    def update(self, delta_time):
        if self.current_menu:
            self.current_menu.update(delta_time)

    def handle_input(self, key):
        if not self.current_menu:
            return None
        
        if key == arcade.key.ESCAPE:
            if isinstance(self.current_menu, PauseMenu):
                return 'resume'
            elif self.go_back():
                return None
            else:
                return 'quit'
            
        action = self.current_menu.handle_input(key)

        if isinstance(self.current_menu, SettingsMenu) and action:
            if action == 'back':
                self.go_back()
                return None
            else:
                self.current_menu.handle_setting_action(action)
                return None
            
        return action
    
    def draw(self):
        if self.current_menu:
            self.current_menu.draw()

    def set_game_over_stats(self, score, level, coins, enemies):
        self.game_over_menu.set_game_stats(score, level, coins, enemies)

    def update_screen_size(self, width, height):
        self.screen_width = width
        self.screen_height = height

        for menu in [self.main_menu, self.pause_menu, self.game_over_menu, self.settings_menu]:
            menu.screen_width = width
            menu.screen_height = height
            if hasattr(menu, 'generate_background_stars'):
                menu.generate_background_stars()
