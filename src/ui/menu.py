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
        self.disbaled_color = (128, 128, 128)

        self.title_size = 48
        self.item_size = 24
        self.item_spacing  = 40
        self.title_y_offset = 150

        self.animation_timer = 0
        self.pulse_amplitude = 10

        self.input_cooldown = 0
        self.input_delay = 0.15

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
        if self.input_cooldown > 0:
            return None
        
        if key == arcade.key.UP:
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

    def select_current_items(self):
        if not self.items or self.selected_index >= len(self.items):
            return None
        
        item = self.items[self.selected_index]
        if item.enabled:
            return item.action
        return None
    
    def draw(self):
        arcade.draw_rect_filled(
            self.screen_width // 2, self.screen_height // 2,
            self.screen_width, self.screen_height,
            self.background_color
        )

        title_y = self.screen_height - self.title_y_offset
        arcade.draw_text(
            self.title,
            self.screen_width // 2, title_y,
            self.title_color, self.title_size,
            anchor_x='center', anchor_y='center'
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
                color = self.disbaled_color
                offset = 0
            elif item.selected:
                pulse = math.sin(self.animation_timer * 5) * self.pulse_amplitude
                color = self.selected_color
                offset = pulse
            else:
                color = self.item_color

        arcade.draw_text(
            item.text,
            self.screen_width // 2 + offset, y_position,
            color, self.item_size,
            anchor_x='center', anchor_y='center'
        )

        if item.selected:
            arcade.draw_text(
                "►",
                self.screen_width // 2 - 150 + offset, y_position,
                self.selected_color, self.item_size,
                anchor_x='center', anchor_y='center'
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

    def generate_background_stars(self, delta_time):
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
            arcade.draw_rect_filled(
                self.screen_width // 2, y + 2,
                self.screen_width, 4,
                color
            )

        for star in self.star_positions:
            arcade.draw_circle_filled(star[0], star[1], star[2], settings.WHITE)

        shadow_offset = 3
        arcade.draw_text(
            self.title,
            self.screen_width // 2 + shadow_offset,
            self.screen_height - self.title_y_offset - shadow_offset,
            (50, 50, 50), self.title_size,
            anchor_x='center', anchor_y='center'
        )

        arcade.draw_text(
            self.title,
            self.screen_width // 2, self.screen_height - self.title_y_offset,
            self.title_color, self.title_size,
            anchor_x='center', anchor_y='center'
        )

        self.draw_items()

        arcade.draw_text(
            "Use ↑↓ to navigate, ENTER to select",
            self.screen_width // 2, 50,
            settings.WHITE, 16,
            anchor_x='center', anchor_y='center'
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
        arcade.draw_rect_filled(
            self.screen_width // 2, self.screen_height // 2,
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
            arcade.draw_text(
                stat,
                self.screen_width // 2, stats_y - (i * 30),
                settings.WHITE, 18,
                anchor_x='center', anchor_y='center'
            )

