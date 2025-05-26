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

    def _create_enemy_texture(self):
        colors = {
            'goomba': (139, 69, 19),
            'koopa': (34, 139, 34),
            'generic': (255, 0, 0),
            'flying': (128, 0, 128),
            'boss': (255, 165, 0)
        }

        color = colors.get(self.enemy_type, colors['generic'])

        size = 32
        temp_sprite = arcade.SpriteSolidColor(size, size, color)
        self.texture = temp_sprite.texture

    def setup_position(self, x, y):
        self.center_x = x
        self.center_y = y
        self.patrol_start_x = x

        self.set_state(EnemyState.WALKING)

        self.change_x = self.direction * self.speed

    def update(self, delta_time=1/60):
        self.state_timer += delta_time
        self.animation_timer += delta_time

        if self.invulnerable:
            self.invulnerable_timer -= delta_time
            if self.invulnerable_timer <= 0:
                self.invulnerable = False
        
        if self.state == EnemyState.WALKING:
            self._update_walking(delta_time)
        elif self.state == EnemyState.CHASING:
            self._update_charging(delta_time)
        elif self.state == EnemyState.STUNNED:
            self._update_stunned(delta_time)
        elif self.state == EnemyState.DYING:
            self._update_dying(delta_time)
        elif self.state == EnemyState.DEAD:
            return 

        self._update_animations(delta_time)

    def _update_walking(self, delta_time):
        self.change_x = self.direction * self.speed

        distance_from_start = abs(self.center_x - self.patrol_start_x)
        if distance_from_start > self.patrol_distance:
            self.direction *= -1

    def _update_stunned(self, delta_time):
        self.change_x = 0

        if self.state_timer > 1.0:
            self.set_state(EnemyState.WALKING)

    def _update_chsaing(self, delta_time):
        if self.player_last_seen:
            target_x, target_y = self.player_last_seen

            if abs(self.center_x - target_x) > 10:
                if self.center_x < target_x:
                    self.direction = 1
                    self.change_x = self.max_speed
                else:
                    self.direction = -1
                    self.change_x = -self.max_speed
            else:
                self.set_state(EnemyState.WALKING)

        if self.state_timer > self.chase_timeout:
            self.set_state(EnemyState.WALKING)

    def _update_dying(self, delta_time):
        self.death_timer += delta_time

        if self.death_timer < self.death_duration:
            scale_factor = 1.0 - (self.death_timer / self.death_duration)
            self.scale = max(0.1, scale_factor)
        else:
            self.set_state(EnemyState.DEAD)
            self.remove_from_sprite_lists()
    
    def _update_animations(self, delta_time):
        if abs(self.change_x) > 0.1:
            self.current_animation = 'walk'
        else:
            self.current_animation = 'idle'

        #Come back and integrate the sprite sheet into this

    def set_state(self, new_state):
        if new_state != self.state:
            self.previous_state = self.state
            self.state = new_state
            self.state_timer = 0

            if new_state == EnemyState.DYING:
                self.death_timer = 0
                self.change_x = 0
                self.change_y = -5

    def handle_wall_collision(self, wall_side):
        if self.bounces_off_walls and wall_side in ['left', 'right']:
            self.direction *= -1
            self.change_x = self.direction * self.speed

    def handle_edge_detection(self, on_edge):
        if self.bounces_off_edges and on_edge and not self.can_fall_off_platforms:
            self.direction *= -1

    def detect_player(self, player_sprite):
        if not player_sprite:
            return False
        
        distance = math.sqrt(
            (player_sprite.center_x - self.center_x)**2 +
            (player_sprite.center_y - self.center_y)**2
        )

        if distance <= self.vision_range:
            self.player_last_seen = (player_sprite.center_x, player_sprite.center_y)
            return True
        
        return False
    
    def can_attack_player(self, player_sprite):
        if not player_sprite:
            return False
        
        distance = math.sqrt(
            (player_sprite.center_x - self.center_x)**2 +
            (player_sprite.center_y - self.center_y)**2
        )

        return distance <= self.attack_range
    
    def take_damage(self, damage=1, damage_type='normal'):
        if self.invulnerable or self.state in [EnemyState.DYING, EnemyState.DEAD]:
            return False
        
        if damage_type == 'stomp':
            if not self.can_be_stomped:
                return False
            if self.stomp_kills:
                self.health = 0
            else:
                self.health -= damage
                self.set_state(EnemyState.STUNNED)

        else:
            self.health -= damage

        if self.health <= 0:
            self.die()
            return True
        else:
            self.make_invulnerable(0.5)
            return False
        
    def die(self):
        self.set_state(EnemyState.DYING)

        self.change_x = 0

        #Play death sound wehn added
        #sound_manager.play_sound("enemy_death")

    def make_invulnerable(self, duration):
        self.invulnerable = True
        self.invulnerable_timer = duration

    def get_damage_to_player(self):
        return self.damage_to_player
    
    def get_score_value(self):
        return self.score_value
    
    def interact_with_player(self, player_sprite, collision_side):
        if self.state in [EnemyState.DYING, EnemyState.DEAD]:
            return None
        
        if collision_side == 'top':
            if self.can_be_stomped:
                died = self.take_damage(1, 'stomp')
                return {
                    'type': 'stomp',
                    'enemy_died': died,
                    'score': self.score_value if died else 0,
                    'bounce_player': True
                }
            
        else:
            return {
                'type': 'damage',
                'damage_to_player': self.damage_to_player,
                'enemy_died': False,
                'knockback': True
            }
        
    def get_debug_info(self):
        return {
            'type': self.enemy_type,
            'state': self.state,
            'position': (int(self.center_x), int(self.center_y)),
            'health': self.health,
            'on_ground': self.on_ground,
            'vision_range': self.vision_range
        }
    
class EnemyManager:

    def __init__(self):
        self.enemy_list = arcade.SpriteList()
        self.total_enemies = 0
        self.defeated_enemies = 0

    def add_enemy(self, enemy_class, x, y, **kwargs):
        enemy = enemy_class(**kwargs)
        enemy.setup_position(x, y)
        self.enemy_list.append(enemy)
        self.total_enemies+=1

        return enemy
    
    def update(self, delta_time, player_sprite=None):
        for enemy in self.enemy_list:
            if player_sprite and enemy.state != EnemyState.DEAD:
                if enemy.detect_player(player_sprite):
                    if enemy.state == EnemyState.WALKING:
                        enemy.set_state(EnemyState.CHASING)

            enemy.update(delta_time)

    def check_player_interactions(self, player_sprite, physics_engine=None):
        interactions = []
        hit_list = arcade.check_for_collision_with_list(player_sprite, self.enemy_list)

        for enemy in hit_list:
            if enemy.state in [EnemyState.DYING, EnemyState.DEAD]:
                continue

            player_falling = player_sprite.change_y < 0
            player_above = player_sprite.bottom > enemy.center_y

            if player_falling and player_above:
                collision_side = 'top'
            else:
                collision_side = 'side'

            interaction = enemy.interact_with_player(player_sprite, collision_side)
            if interaction:
                interactions.append(interaction)

                if interaction['enemy_died']:
                    self.defeated_enemies += 1

        return interactions
    
    def get_stats(self):
        return {
            'total_enemies': self.total_enemies,
            'defeated_enemies': self.defeated_enemies,
            'remaining_enemies': self.total_enemies - self.defeated_enemies,
            'defeat_percentage': (self.defeated_enemies / max(1, self.total_enemies)) * 100
        }
    
    def reset(self):
        self.enemy_list.clear()
        self.total_enemies = 0
        self.defeated_enemies = 0

    def draw(self):
        self.enemy_list.draw()

    def draw_debug(self):
        for enemy in self.enemy_list:
            if settings.SHOW_HITBOXES:
                arcade.draw_rect_outline(
                    enemy.center_x, enemy.center_y,
                    enemy.width, enemy.height,
                    arcade.color.RED, 2
                )

            if settings.DEBUG_MODE:
                arcade.draw_circle_outline(
                    enemy.center_x, enemy.center_y,
                    enemy.vision_range,
                    arcade.color.YELLOW, 1
                )

            