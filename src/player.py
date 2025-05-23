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

    def setup(self, start_x, start_y):
        #set player at starting pos
        self.center_x = start_x
        self.center_y = start_y
        self.change_x = 0
        self.change_y = 0

    def update(self):
        #Update state animations & timers
        self.update_timers()
        self.was_on_ground = self.is_on_ground

        if self.is_on_ground and not self.is_moving:
            self.change_x *= self.friction

        if not self.is_on_ground:
            self.change_x *= self.air_resistance

        if self.change_x > 0:
            self.facing_direction = 1
        elif self.change_x < 0:
            self.facing_direction = -1

        self.update_animation_state()

        if self.invulnerable:
            self.invulnerable_timer -= 1/60  #Assuming 60 fps, change this with fps
            if self.invulnerable_timer <= 0:
                self.invulnerable = False

    def update_timers(self):
        #jump buffer & coyote time timers
        if self.jump_buffer_timer > 0:
            self.jump_buffer_timer -= 1/60  #Assuming 60 fps

        if self.was_on_ground and not self.is_on_ground:
            self.coyote_timer = settings.COYOTE_TIME
        elif self.is_on_ground:
            self.coyote_timer = 0
        elif self.coyote_timer > 0:
            self.coyote_timer -= 1/60

    def update_animation_state(self):
        #Finds right animation
        if not self.is_on_ground:
            if self.change_y > 0:
                self.current_animation = 'jumping'
            else:
                self.current_animation = 'falling'
        elif abs(self.change_x) > 0.5:
            self.current_animation = 'running'
        else:
            self.current_animation = 'idle'