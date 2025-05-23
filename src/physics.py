#Physics engine & utilities

import arcade
import math
import settings

class PhysicsConstants:
    #Centralized constants that can be tweaked

    GRAVITY = settings.GRAVITY
    TERMINAL_VELOCITY = settings.TERMINAL_VELOCITY

    PLAYER_FRICTION = settings.FRICTION
    PLAYER_AIR_RESISTANCE = settings.AIR_RESISTANCE
    PLAYER_JUMP_SPEED = settings.PLAYER_JUMP_SPEED
    PLAYER_MOVEMENT_SPEED = settings.PLAYER_MOVEMENT_SPEED

    BOUNCE_DAMPING = 0.7
    SLIDE_THRESHOLD = 0.1

    COLLISION_TOLERANCE = 0.1
    GROUND_DETECTION_OFFSET = 1

class PhysicsBody:
    #body that can be attached to sprites for advanced physics
    def __init__(self, sprite, mass=1.0, friction = 1.0, bounce =0.0):
        self.sprite = sprite
        self.mass = mass
        self.friction = friction
        self.bounce = bounce

        self.velocity_x = 0
        self.velocity_y = 0
        self.previous_x = sprite.center_x
        self.previous_y = sprite.center_y

        self.on_ground = False
        self.on_wall = False
        self.wall_direction = 0

        self.applied_forces_x = []
        self.applied_forces_y = []

    def apply_force(self, force_x, force_y):
        self.applied_forces_x.append(force_x)
        self.applied_forces_y.append(force_y)

    def apply_impulse(self, impulse_x, impulse_y):
        self.velocity_x += impulse_x / self.mass
        self.velocity_y += impulse_y / self.mass

    def update(self, delta_time):
        total_force_x = sum(self.applied_forces_x)
        total_force_y = sum(self.applied_forces_y)

        self.applied_forces_x.clear()
        self.applied_forces_y.clear()

        self.velocity_x += (total_force_x / self.mass) * delta_time
        self.velocity_y += (total_force_y / self.mass) * delta_time

        if self.on_ground:
            friction_force = self.velocity_x * self.friction * PhysicsConstants.PLAYER_FRICTION
            self.velocity_x -= friction_force * delta_time

            if abs(self.velocity_x) < PhysicsConstants.SLIDE_THRESHOLD:
                self.velocity_x = 0

        if not self.on_ground:
            self.velocity_x *= PhysicsConstants.PLAYER_AIR_RESISTANCE

        if self.velocity_y < PhysicsConstants.TERMINAL_VELOCITY:
            self.velocity_y = -PhysicsConstants.TERMINAL_VELOCITY

        self.previous_x = self.sprite.center_x
        self.previous_y = self.sprite.center_y

        self.sprite.center_x += self.velocity_x * delta_time * 60  # assuming 60 fps
        self.sprite.center_y += self.velocity_y * delta_time * 60

class CollisionDetector:

    @staticmethod
    def check_collision_detailed(sprite1, sprite2):
        if not arcade.check_for_collision(sprite1, sprite2):
            return None
        
        left1, right1 = sprite1.left, sprite1.right
        top1, bottom1 = sprite1.top, sprite1.bottom
        left2, right2, = sprite2.left, sprite2.right
        top2, bottom2 = sprite2.top, sprite2.bottom

        overlap_x = min(right1, right2) - max(left1, left2)
        overlap_y = min(top1, top2) - max(bottom1, bottom2)

        center1_x, center1_y = sprite1.center_x, sprite1.center_y
        center2_x, center2_y = sprite2.center_x, sprite2.center_y

        direction_x = 1 if center1_x > center2_x else -1
        direction_y = 1 if center1_y > center2_y else -1

        return {
            'overlap x': overlap_x,
            'overlap y': overlap_y,
            'direction_x': direction_x,
            'direction_y': direction_y,
            'from_above': center1_y > center2_y,
            'from_below': center1_y < center2_y,
            'from_left': center1_x < center2_x,
            'from_right': center1_y > center2_x
        }

    @staticmethod
    def resolve_collision(moving_sprite, static_sprite, collision_info):
        if not collision_info:
            return
        
        overlap_x = collision_info['overlap_x']
        overlap_y = collision_info['overlap_y']

        if overlap_x < overlap_y:
            if collision_info['from_left']:
                moving_sprite.right = static_sprite.left
            else:
                moving_sprite.left = static_sprite.right
            
            moving_sprite.change_x = 0

        else:
            if collision_info['from_above']:
                moving_sprite.bottom = static_sprite.top
                if moving_sprite.change_y < 0:
                    moving_sprite.change_y = 0
            else:
                moving_sprite.top = static_sprite.bottom
                if moving_sprite.change_y > 0:
                    moving_sprite.change_y = 0

class PlatformPhysicsEngine:
    def __init__(self, player_sprite, platforms, gravity=None):
        self.player_sprite = player_sprite
        self.platforms = platforms
        self.gravity = gravity or PhysicsConstants.GRAVITY

        self.player_on_ground = False
        self.player_on_wall = False
        self.wall_direction = 0

        if not hasattr(player_sprite, 'physics_body'):
            player_sprite.physics_body = PhysicsBody(player_sprite)

    def can_jump(self):
        return self.player_on_ground
    
    def update(self):
        prev_x = self.player_sprite.center_x
        prev_y = self.player_sprite.center_y

        self.player_sprite.change_y -= self.gravity

        if self.player_sprite.change_y < -PhysicsConstants.TERMINAL_VELOCITY:
            self.player_sprite.change_y = -PhysicsConstants.TERMINAL_VELOCITY

        self.player_sprite.center_x += self.player_sprite.change_x

        hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.platforms)
        for platform in hit_list:
            collision_info = CollisionDetector.check_collision_detailed(self.player_sprite, platform)
            if collision_info:
                CollisionDetector.resolve_collision(self.player_sprite, platform, collision_info)

                if collision_info['from_left'] or collision_info['from_right']:
                    self.player_on_wall = True
                    self.wall_direction = collision_info['direction_x']

        self.player_sprite.center_y += self.player_sprite.change_y

        self.player_on_ground = False
        hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.platforms)

        for platform in hit_list:
            collision_info = CollisionDetector.check_collision_detailed(self.player_sprite, platform)
            if collision_info:
                CollisionDetector.resolve_collision(self.player_sprite, platform, collision_info)

                if collision_info['from_above'] and self.player_sprite.change_y <= 0:
                    self.player_on_ground = True
        
        if not any(hit_list):
            self.player_on_wall = False
            self.wall_direction = 0

        if hasattr(self.player_sprite, 'set_ground_state'):
            self.player_sprite.set_ground_state(self.player_on_ground)

    def add_platform(self, platform):
        self.platforms.append(platform)

    def remove_platform(self, platform):
        if platform in self.platforms:
            self.platforms.remove(platform)
