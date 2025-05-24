import arcade
import math
import time
from .. import settings

class Coin(arcade.Sprite):

    def __init__(self, coin_type='normal', value=None, scale=1.0):
        super().__init__(scale=scale)

        self.coin_type = coin_type
        self.value = value or self._get_default_value()

        self.animation_timer = 0
        self.spin_speed = settings.COIN_SPIN_SPEED
        self.bounce_height = 0
        self.bounce_speed = 2.0
        self.bounce_offset = 0

        self.is_collected = False
        self.collection_timer = 0
        self.collection_duration = 0.5

        self.floating = True
        self.magnetic_range = 50
        self.magnetic_speed = 8

        self.sparkle_timer = 0
        self.sparkle_particles = []

        self.collection_sound = 'coin'

        self._create_coin_texture()

    def _get_default_value(self):
        values = {
            'normal': settings.COIN_VALUE,
            'silver': settings.COIN_VALUE*2,
            'gold': settings.COIN_VALUE * 5,
            'special': settings.COIN_VALUE * 10
        }
        return values.get(self.coin_type, settings.COIN_VALUE)
    
    def _create_coin_texture(self):
        colors = {
            'normal': (255, 215, 0),
            'silver': (192, 192, 192),
            'gold': (255, 165, 0),
            'special': (255, 20, 147)
        }

        color = colors.get(self.coin_type, colors['normal'])

        temp_sprite = arcade.SpriteSolidColor(settings.COIN_SIZE, settings.COIN_SIZE, color)
        self.texture = temp_sprite.texture

    def setup_position(self, x, y):
        self.center_x = x
        self.center_y = y
        self.bounce_offset = time.time() * self.bounce_speed

    def update(self, delta_time=1/60):
        if self.is_collected:
            self._update_collection_animation(delta_time)
            return
        
        self.animation_timer += delta_time

        if self.floating:
            self.bounce_offset += delta_time * self.bounce_speed
            bounce_y = math.sin(self.bounce_offset) * 3  # 3 pixel bounce
            if not hasattr(self, '_original_y'):
                self._original_y = self.center_y
            self.center_y = self._original_y + bounce_y

        self._update_sparkles(delta_time)

    