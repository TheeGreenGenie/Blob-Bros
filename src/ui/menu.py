#Menu classes (pages)
import arcade
import math
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

