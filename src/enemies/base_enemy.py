#Basic Enemy class
import arcade
import math
import random
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import settings

class EnemyState:
    IDLE ='idle'
    WALKING = 'walking'
    CHASING ='chasing'
    STUNNED = 'stunned'
    DYING = 'dying'
    DEAD = 'dead'

class BaseEnemy(arcade.Sprite):

    def __init__(self, enemy_type='generic', scale=1.0):
        super().__init__(scale=scale)

        self.enemy_type = enemy_type
        self.enemy_id = id(self)

        self.state = EnemyState.WALKING
        self.previous_state = EnemyState.IDLE
        self.state_timer = 0

        self.speed = settings.ENEMY_SPEED
        self.direction = random.choice([-1, 1])  # - left + right
        self.max_speed = self.speed * 2
        self.acceleration = 0.2

        self.on_ground = False
        self.can_jump = False
        self.jump_strength = -12
        self.affected_by_gravity = True

        self.vision_range = 150
        self.attack_range = 32
        self.patrol_distance = 128
        self.patrol_start_x = 0
        self.player_last_seen = None
        self.chase_timeout = 3.0

        self.bounces_off_walls = True
        self.bounces_off_edges = True
        self.can_fall_off_platforms = False

        self.health = 1
        self.max_health = 1
        self.damage_to_player = 1
        self.can_be_stomped = True
        self.stomp_kills = True
        self.invulnerable = False
        self.invulnerable_timer = 0

        self.animation_timer = 0
        self.walk_animation_speed = 0.2
        self.current_animation = 'walk'

        self.score_value = 200
        self.death_timer = 0
        self.death_duration = 0.5

        self.can_interact_with_blocks = False
        self.can_activate_switches = False
        self.pushes_other_enemeies = True

        self._create_enemy_texture()