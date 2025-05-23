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


