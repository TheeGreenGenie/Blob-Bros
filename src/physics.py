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

class 