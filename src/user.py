#Player module, handles sprites, movements, physics, & abilities

import arcade
import settings

class Player(arcade.Sprite):

    def __init__(self):
        super().__init__()

        image = arcade.make_circle_texture(settings.PLAYER_SIZE, settings.RED)
        self.texture = image

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

    def update(self, delta_time=1/60):
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

    def move_left(self):
        self.change_x = -self.speed
        self.is_moving =True

    def move_right(self):
        self.change_x = self.speed
        self.is_moving = True

    def stop_moving(self):
        self.is_moving = False

    def jump(self):
        self.jump_buffer_timer = settings.JUMP_BUFFER_TIME
        return self.try_jump()
    
    def try_jump(self):
        #determines whether a jump is possible
        can_jump = (self.is_on_ground or self.coyote_timer > 0) and self.jump_buffer_timer > 0

        if can_jump:
            self.change_y = self.jump_speed
            self.jump_buffer_timer = 0
            self.coyote_timer = 0
            return True
        
        return False
    
    def set_ground_state(self, on_ground):
        self.is_on_ground = on_ground

    def take_damage(self):
        if self.invulnerable:
            return False
        
        if self.power_level > 0:
            self.power_level -= 1
            self.make_invulnerable(2.0)
            return False
        else:
            return True
        
    def make_invulnerable(self, duration):
        self.invulnerable = True
        self.invulnerable_timer = duration

    def power_up(self, power_type=1):
        if self.power_level < power_type:
            self.power_level = power_type
            #Change sprite texture based on power level - come back to this
    
    def reset_to_checkpoint(self, x, y):
        self.center_x = x
        self.center_y = y
        self.change_x = 0
        self.change_y = 0
        self.is_on_ground = False
        self.invulnerable = False
        self.invulnerable_timer = 0

    def get_debug_info(self):
        return {
            'position': (int(self.center_x), int(self.center_y)),
            'velocity': (round(self.change_x), round(self.change_y)),
            'on_ground': self.is_on_ground,
            'facing': 'right' if self.facing_direction > 0 else 'left',
            'animation': self.current_animation,
            'power_level': self.power_level,
            'invulnerable': self.invulnerable
        }

    def draw_debug(self, camera_x=0, camera_y=0):
        if settings.SHOW_HITBOXES:
            arcade.draw_rect_outline(
                self.center_x - camera_x,
                self.center_y - camera_y,
                self.width,
                self.height,
                settings.YELLOW,
                2 
            )

        if settings.DEBUG_MODE:
            indicator_x = self.center_x + (self.facing_direction * 20) - camera_x
            indicator_y = self.center_y + 20 - camera_y
            arcade.draw_circle_filled(indicator_x, indicator_y, 3, settings.GREEN)

class PlayerInputHandler:
    
    def __init__(self, theplayer):
        self.player = theplayer
        self.keys_pressed = set()

    def on_key_press(self, key, modifiers):
        self.keys_pressed.add(key)

        if key == arcade.key.SPACE:
            self.player.jump()

        elif key == arcade.key.LEFT:
            self.player.move_left()
        elif key == arcade.key.RIGHT:
            self.player.move_right()

    def on_key_release(self, key, modifiers):
        if key in self.keys_pressed:
            self.keys_pressed.remove(key)
        
        if key in (arcade.key.LEFT, arcade.key.RIGHT):
            if arcade.key.LEFT not in self.keys_pressed and arcade.key.RIGHT not in self.keys_pressed:
                self.player.stop_moving()

    def update(self):

        if arcade.key.LEFT in self.keys_pressed and arcade.key.RIGHT not in self.keys_pressed:
            self.player.move_left()
        elif arcade.key.LEFT not in self.keys_pressed and arcade.key.RIGHT in self.keys_pressed:
            self.player.move_right()
        elif arcade.key.LEFT not in self.keys_pressed and arcade.key.RIGHT not in self.keys_pressed:
            self.player.stop_moving()

        if self.player.jump_buffer_timer > 0:
            self.player.try_jump()
