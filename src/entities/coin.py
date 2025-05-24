import arcade
import math
import time
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import settings

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

    def add_coin(self, x, y, coin_type='normal', value=None):
        coin = Coin(coin_type, value)
        coin.setup_position(x, y)
        self.coin_list.append(coin)
        self.total_coins += 1
        self.total_value += coin.value

        return coin
    
    def update(self, delta_time, player_sprite=None):
        self.coin_list.update(delta_time)

        if player_sprite and self.magnetic_collection:
            for coin in self.coin_list:
                if not coin.is_collected:
                    distance = math.sqrt(
                        (player_sprite.center_x - coin.center_x)**2 +
                        (player_sprite.center_y - coin.center_y)**2
                    )

                    if distance <= self.auto_collect_distance:
                        value = coin.collect(player_sprite)
                        if value > 0:
                            self.collected_coins += 1
                            return coin.get_collection_info()
                    
                    elif coin.check_magnetic_attraction(player_sprite):
                        coin.apply_magnetic_force(player_sprite, delta_time)

        return None
    
    def check_player_collection(self, player_sprite):
        collections = []
        hit_list = arcade.check_for_collision_with_list(player_sprite, self.coin_list)

        for coin in hit_list:
            if not coin.is_collected:
                value = coin.collect(player_sprite)
                if value > 0:
                    self.collected_coins += 1
                    collections.append(coin.get_collection_info())

        return collections
    
    def get_stats(self):
        return {
            'total_coins': self.total_coins,
            'collected_coins': self.collected_coins,
            'remaining_coins': self.total_coins - self.collected_coins,
            'total_value': self.total_value,
            'collection_percentage': (self.collected_coins / max(1, self.total_coins)) * 100
        }
    
    def reset(self):
        self.coin_list.clear()
        self.total_coins = 0
        self.collected_coins = 0
        self.total_value = 0

    def draw(self):
        self.coin_list.draw()

def create_coin_line(start_x, start_y, end_x, end_y, spacing=64, coin_type='normal'):
    coins = []

    dx = end_x - start_x
    dy = end_y - start_y
    distance = math.sqrt(dx*dx + dy*dy)

    if distance == 0:
        return coins
    
    num_coins = int(distance / spacing) + 1

    for i in range(num_coins):
        progress = i / max(1, num_coins -1)
        x = start_x + dx * progress
        y = start_y + dy * progress

        coin = Coin(coin_type)
        coin.setup_position(x, y)
        coins.append(coin)

    return coins

def create_coin_circle(center_x, center_y, radius, num_coins=8, coin_type='normal'):
    coins = []

    for i in range(num_coins):
        angle = (i / num_coins) * 2 * math.pi
        x = center_x + math.cos(angle) * radius
        y = center_y + math.sin(angle) * radius

        coin = Coin(coin_type)
        coin.setup_position(x, y)
        coins.append(coin)

    return coins