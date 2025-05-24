import arcade
import math
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

    