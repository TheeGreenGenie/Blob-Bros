#Player module, handles sprites, movements, physics, & abilities

import arcade
import settings

class Player(arcade.Sprite):

    def __init__(self):
        super().__init__()

        self.texture = arcade.Texture.create_filled(
            "player",
            (settings.PLAYER_SIZE, settings.PLAYER_SIZE),
            settings.RED
        )

        self.facing_direction = 1  # -1 for left 
        self.is_on_ground = False
        self.is_moving = False

        self.speed = settings.PLAYER_MOVEMENT_SPEED
        self.jump_speed = settings.PLAYER_JUMP_SPEED

        self.jump_buffer_timer = 0
        self.coyote_timer = 0
        self.was_on_ground = False

        self.power_level = 0  # 0=small, 1=big, 2=fire
        self.invulnerable = False
        self.invulnerable_timer = 0

        self.animation_timer = 0
        self.current_animation = "idle"

        self.friction = settings.FRICTION
        self.air_resistance = settings.AIR_RESISTANCE

    def setup(self, start_x, start_y)