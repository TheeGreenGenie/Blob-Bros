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

    def _update_collection_animation(self, delta_time):
        self.collection_timer += delta_time

        progress = self.collection_timer / self.collection_duration

        if progress >= 1.0:
            self.remove_from_sprite_lists()
        else:
            scale_factor = 1.0 + progress * 0.5  # 50% larger
            self.scale = scale_factor

            if not hasattr(self, '_collection_start_y'):
                self._collection_start_y = self.center_y
            self.center_y = self._collection_start_y + progress * 20

    def _update_sparkles(self, delta_time):
        self.sparkle_timer += delta_time

        if self.sparkle_timer > 1.0:
            self.sparkle_timer = 0

    def collect(self, collector_sprite=None):
        if self.is_collected:
            return 0
        
        self.is_collected = True
        self.collection_timer = 0

        if collector_sprite:
            self._start_magnetic_collection(collector_sprite)

        return self.value
    
    def _start_magnetic_collection(self, target_sprite):
        dx = target_sprite.center_x - self.center_x
        dy = target_sprite.center_y - self.center_y
        distance = math.sqrt(dx*dx + dy*dy)

        if distance > 0:
            self.change_x = (dx / distance) * self.magnetic_speed
            self.change_y = (dy / distance) * self.magnetic_speed

    def check_magnetic_attraction(self, target_sprite):
        if self.is_collected:
            return False
        
        distance = math.sqrt(
            (target_sprite.center_x - self.center_x)**2 +
            (target_sprite.center_y - self.center_y)**2
        )

        return distance <= self.magnetic_range
    
    def apply_magnetic_force(self, target_sprite, delta_time):
        if self.is_collected:
            return
        
        dx = target_sprite.center_x - self.center_x
        dy = target_sprite.center_y - self.center_y
        distance = math.sqrt(dx*dx + dy*dy)

        if distance > 0  and distance <= self.magnetic_range:
            force_strength = (self.magnetic_range - distance) / self.magnetic_range
            force_strength = force_strength * self.magnetic_speed

            self.center_x += (dx / distance) * force_strength * delta_time
            self.center_y += (dy / distance) * force_strength * delta_time

    def get_collection_info(self):
        return {
            'type': 'coin',
            'coin_type': self.coin_type,
            'value': self.value,
            'sound': self.collection_sound,
            'effect': 'sparkle'
        }

class CoinManager:

    def __init__(self):
        self.coin_list = arcade.SpriteList(use_spatial_hash=True)
        self.total_coins = 0
        self.collected_coins = 0
        self.total_value = 0

        self.magnetic_collection = True
        self.auto_collect_distance = 30

    