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