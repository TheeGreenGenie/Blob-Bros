#Classic goomba character class
import arcade
import math
import random
from base_enemy import BaseEnemy, EnemyState
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import settings

class Goomba(BaseEnemy):

    def __init__(self, scale=1.0, variant='normal'):
        super().__init__("goomba", scale)

        self.variant = variant

        self._setup_variant_properties()

        self.walk_animation_frames = 2
        self.squish_duration = 0.3  # how long until squished goomba dissapears
        self.squished = False

        self.movement_pattern = 'walk'
        self.charge_distance = 0
        self.charge_speed_multiplier = 2.0

        self.can_change_direction_randomly = False
        self.direction_change_chance = 0.02
        
        self._create_goomba_texture()

    def _setup_variant_properties(self):
        if self.variant == 'normal':
            self.speed = settings.ENEMY_SPEED
            self.health = 1
            self.score_value = 100
            self.vision_range = 100

        elif self.variant == 'fast':
            self.speed = settings.ENEMY_SPEED * 1.5
            self.health = 1
            self.score_value = 200
            self.vision_range = 120
            self.can_change_direction_randomly = True

        elif self.variant == 'large':
            self.speed = settings.ENEMY_SPEED * 1.2
            self.health = 2  #  number of stomps to kill
            self.score_value = 300
            self.vision_range = 150
            self.scale = 1.3

        elif self.variant == 'elite':
            self.speed = settings.ENEMY_SPEED * 1.2
            self.health = 1
            self.score_value = 500
            self.vision_range = 200
            self.can_change_direction_randomly = True
            self.movement_pattern = 'charge'

        self.max_health = self.health

    def _create_goomba_texture(self):
        variant_colors  = {  #         Brown, saddle brown, dark brown, & indigo
            'normal': (139, 69, 19),
            'fast': (160, 82, 45),
            'large': (101, 67, 33),
            'elite': (75, 0, 130)
        }

        color = variant_colors.get(self.variant, variant_colors['normal'])

        size = 28 if self.variant != 'large' else 36

        temp_sprite = arcade.SpriteSolidColor(size, size, color)
        self.texture = temp_sprite.texture

    def update(self, delta_time=1/60):
        #call parent update function first
        super().update(delta_time)

        if self.state == EnemyState.WALKING:
            self._update_goomba_walking(delta_time)
        elif self.state == EnemyState.CHASING and self.movement_pattern == 'charge':
            self._update_charging(delta_time)

        if self.squished:
            self._update_squished(delta_time)

    def _update_goomba_walking(self, delta_time):
        if self.can_change_direction_randomly:
            if random.random() < self.direction_change_chance:
                self.direction *= -1

        self.change_x = self.direction * self.speed

    def _update_charging(self, delta_time):
        if self.player_last_seen:
            target_x, target_y = self.player_last_seen

            if abs(self.center_x - target_x) > 10:
                charge_speed = self.speed * self.charge_speed_multiplier

                if self.center_x < target_x:
                    self.direction = 1
                    self.change_x = charge_speed
                else:
                    self.direction = -1
                    self.change_x = -charge_speed
            else:
                self.set_state(EnemyState.WALKING)

    def _update_squished(self, delta_time):
        self.change_x = 0

        if self.state_timer > self.squish_duration:
            self.squished = False
            if self.health > 0:
                self.set_state(EnemyState.WALKING)

    def take_damage(self, damage=1, damage_type='normal'):
        if self.squished or self.state in [EnemyState.DYING, EnemyState.DEAD]:
            return False
        
        if damage_type == 'stomp':
            if self.variant == 'large' and self.health > 1:
                self.health -= 1
                self.squished = True
                self.set_state(EnemyState.STUNNED)
                self.scale = 1.0
                self._create_goomba_texture()
                return False
            
            else:
                self.health = 0
                self.die()
                return True
            
    def die(self):
        self.squished = True
        self.set_state(EnemyState.DYING)

        self.scale = (self.scale, 0.3)

        self.change_x = 0
        self.change_y = 0

    def handle_wall_collisions(self, wall_side):
        if wall_side in ['left', 'right'] and not self.squished:
            self.direction *= -1
            self.change_x = self.direction * self.speed

    def detect_player(self, player_sprite):
        if not player_sprite or self.squished:
            return False
        
        detected = super().detect_player(player_sprite)

        if self.variant == 'elite' and detected:
            if self.state == EnemyState.WALKING:
                self.set_state(EnemyState.CHASING)

        return detected
    
    def interact_with_player(self, player_sprite, collision_side):
        if self.squished or self.state in [EnemyState.DYING, EnemyState.DEAD]:
            return None
        
        if collision_side == 'top':
            died = self.take_damage(1, 'stomp')

            bounce_height = 8
            if self.variant == 'large':
                bounce_height = 12
            elif self.variant == 'elite':
                bounce_height = 15

            return {
                'type': 'stomp',
                'enemy_type': 'goomba',
                'variant': self.variant,
                'enemy_died': died,
                'score': self.score_value if died else self.score_value // 2,
                'bounce_player': True,
                'bounce_height': bounce_height,
                'sound': 'enemy_stomp'
            }
        
        else:
            return {
                'type': 'damage',
                'enemy_type': 'goomba',
                'dmage_to_player': self.damage_to_player,
                'enemy_died': False,
                'knockback': True,
                'sound': 'player_hurt'
            }
        
    def get_special_abilities(self):
        abilities = []

        if self.variant == 'fast':
            abilities.append('increased_speed')
            abilities.append('random_direction_changes')
        elif self.variant == 'large':
            abilities.append('two_hit_kill')
            abilities.append('size_reduction')
        elif self.variant == 'elite':
            abilities.append('charging_attack')
            abilities.append('enhanced_vision')
            abilities.append('random_direction_changes')

        return abilities
    
    def get_debug_info(self):
        base_info =  super().get_debug_info()
        goomba_info = {
            'wariant': self.variant,
            'squished': self.squished,
            'movement_pattern': self.movement_pattern,
            'abilities': self.get_special_abilities()
        }

        return {**base_info, **goomba_info}
    
class GoombaSpawner:

    @staticmethod
    def spawn_normal_goomba(x, y):
        return Goomba(variant='normal').setup_position(x, y)
    
    @staticmethod
    def spawn_fast_goomba(x, y):
        return Goomba(variant='fast').setup_position(x, y)
    
    @staticmethod
    def spawn_large_goomba(x, y):
        return Goomba(variant='large').setup_position(x, y)

    @staticmethod
    def spawn_elite_goomba(x, y):
        return Goomba(variant='elite').setup_position(x, y)
    
    @staticmethod
    def spawn_goomba_group(positions, variant_weights=None):
        if variant_weights is None:
            variant_weights = {
                'normal': 0.6,
                'fast': 0.2,
                'large': 0.15,
                'elite': 0.05
            }
        
        goombas = []
        variants = list(variant_weights.keys())
        weights = list(variant_weights.values())

        for x, y in positions:
            variant = random.choices(variants, weights=weights)[0]
            goomba = Goomba(variant=variant)
            goomba.setup_position(x, y)
            goombas.append(goomba)

        return goombas
    
    @staticmethod
    def create_goomba_formation(center_x, center_y, formation='line'):
        goombas = []

        if formation == 'line':
            positions = [
                (center_x - 64, center_y),
                (center_x, center_y),
                (center_x + 64, center_y)
            ]
            for i, (x,y) in enumerate(positions):
                variant = 'normal' if i != 1 else 'fast'  # Middle one is fast
                goomba = Goomba(variant=variant)
                goomba.setup_position(x, y)
                goombas.append(goomba)

        elif formation == 'triangle':
            positions = [
                (center_x, center_y + 32),
                (center_x - 48, center_y),
                (center_x + 48, center_y)
            ]
            variants = ['elite', 'normal', 'normal']
            for (x, y), variant in zip(positions, variants):
                goomba = Goomba(variant=variant)
                goomba.setup_position(x, y)
                goombas.append(goomba)

        elif formation == 'square':
            positions - [
                (center_x - 32, center_y + 32),
                (center_x + 32, center_y + 32),
                (center_x - 32, center_y - 32),
                (center_x + 32, center_y - 32)
            ]
            variants = ['normal', 'fast', 'normal', 'large']
            for (x, y), variant in zip(positions, variants):
                goomba = Goomba(variant=variant)
                goomba.setup_position(x, y)
                goombas.append(goomba)

        return goombas
    
def create_goomba(x, y, variant='normal'):
    goomba = Goomba(variant=variant)
    goomba.setup_position(x, y)
    return goomba

def create_goomba_patrol(start_x, start_y, end_x, num_goombas=3, variants=None):
    if variants is None:
        variants = ['normal'] * num_goombas

    goombas = []
    spacing = (end_x - start_x) / max(1, num_goombas - 1)

    for i in range(num_goombas):
        x = start_x + (i * spacing)
        variant = variants[i % len(variants)]
        goomba = create_goomba(x, start_y, variant)
        goombas.append(goomba)

    return goombas

