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
    def __init__(self, player_sprite, platforms, gravity=None, interactive_tiles=None):
        self.player_sprite = player_sprite
        self.platforms = platforms
        self.interactive_tiles = interactive_tiles or arcade.SpriteList()
        self.gravity = gravity or PhysicsConstants.GRAVITY

        self.player_on_ground = False
        self.player_on_wall = False
        self.wall_direction = 0

        self.last_collision_tiles = set()
        self.collision_cooldown = {}

        if not hasattr(player_sprite, 'physics_body'):
            player_sprite.physics_body = PhysicsBody(player_sprite)

    def can_jump(self):
        return self.player_on_ground
    
    def update(self):
        #Updated phsyics updating

        self.update_collision_cooldowns()

        prev_x = self.player_sprite.center_x
        prev_y  = self.player_sprite.center_y

        self.player_sprite.change_y -= self.gravity

        if self.player_sprite.change_y < -PhysicsConstants.TERMINAL_VELOCITY:
            self.player_sprite = -PhysicsConstants.TERMINAL_VELOCITY

        self.player_sprite.center_x += self.player_sprite.change_x

        self.check_horizontal_collisions()

        self.player_sprite.center_y += self.player_sprite.change_y

        self.check_vertical_collisions()

        self.check_interactive_tile_collisions()

        if hasattr(self.player_sprite, 'set_ground_state'):
            self.player_sprite.set_ground_state(self.player_on_ground)

    def update_collision_cooldowns(self):
        current_time = arcade.get_time()
        expired_tiles = []

        for tile_id, cooldown_time, in self.collision_cooldown.items():
            if current_time > cooldown_time:
                expired_tiles.append(tile_id)
        
        for tile_id in expired_tiles:
            del self.collision_cooldown[tile_id]

    def check_horizontal_collisions(self):
        self.player_on_wall = False

        hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.platforms)
        for platform in hit_list:
            collision_info = CollisionDetector.check_collision_detailed(self.player_sprite, platform)
            if collision_info and collision_info['overlap_x'] < collision_info['overlap_y']:
                CollisionDetector.resolve_collision(self.player_sprite, platform, collision_info)

                self.player_on_wall =True
                self.wall_direction = collision_info['direction_x']

                if hasattr(platform, 'on_collision'):
                    side = 'left' if collision_info['from_left'] else 'right'
                    platform.on_collision(self.player_sprite, side)

    def check_vertical_collisions(self):
        self.player_on_ground = False

        hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.platforms)
        for platform in hit_list:
            collision_info = CollisionDetector.check_collision_detailed(self.player_sprite, platform)
            if collision_info:
                CollisionDetector.resolve_collision(self.player_sprite, platform, collision_info)

                if collision_info['from_above'] and self.player_sprite.change_y <= 0:
                    self.player_on_ground = True
                    side = 'top'
                elif collision_info['from_below'] and self.player_sprite.change_y >= 0:
                    side = 'bottom'
                else:
                    continue

                if hasattr(platform, 'on_collision'):
                    platform.on_collision(self.player_sprite, side)

    def check_interactive_tile_collisions(self):
        hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.interactive_tiles)
        current_collision_tiles = set()

        for tile in hit_list:
            tile_id = id(tile)
            current_collision_tiles.add(tile_id)

            if tile_id in self.collision_cooldown:
                continue

            collision_info = CollisionDetector.check_collision_detailed(self.player_sprite, tile)
            if collision_info:
                if collision_info['from_above']:
                    side = 'top'
                elif collision_info['from_below']:
                    side = 'bottom'
                elif collision_info['from_left']:
                    side = 'left'
                else:
                    side= 'right'

                if hasattr(tile, 'on_collision'):
                    tile.on_collision(self.player_sprite, side)

                self.collision_cooldown[tile_id] = arcade.get_time() + 0.5
        
        self.last_collision_tiles = current_collision_tiles

    def add_platform(self, platform):
        self.platforms.append(platform)

    def remove_platform(self, platform):
        if platform in self.platforms:
            self.platforms.remove(platform)

    def add_interactive_tile(self, tile):
        self.interactive_tiles.append(tile)

    def remove_interactive_tile(self, tile):
        if tile in self.interactive_tiles:
            self.interactive_tiles.remove(tile)
            tile_id = id(tile)
            if tile_id in self.collision_cooldown:
                del self.collision_cooldown[tile_id]
            if tile_id in self.last_collision_tiles:
                self.last_collision_tiles.remove(tile_id)

    def check_tile_collision_at_position(self, x, y, tile_list):
        original_x = self.player_sprite.center_x
        original_y = self.player_sprite.center_y

        self.player_sprite.center_x = x
        self.player_sprite.center_y = y

        collision = len(arcade.check_for_collision_with_list(self.player_sprite, tile_list)) > 0

        self.player_sprite.center_x = original_x
        self.player_sprite.center_y = original_y

        return collision
    
    def get_tiles_in_range(self, center_x, center_y, range_distance, tile_list):
        tiles_in_range = []

        for tile in tile_list:
            distance = math.sqrt((tile.center_x - center_x)**2 + (tile.center_y - center_y)**2)
            if distance <= range_distance:
                tiles_in_range.append(tile)

        return tiles_in_range

class PhysicUtils:

    @staticmethod
    def calculate_jump_velocity(jump_height, gravity=None):
        gravity = gravity or PhysicsConstants.GRAVITY
        return math.sqrt(2 * gravity * jump_height)  #  Kinetic equatiom
    
    @staticmethod
    def calculate_trajectory(initial_velocity_x, initial_velocity_y, time, gravity=None):
        gravity = gravity or PhysicsConstants.GRAVITY

        x = initial_velocity_x * time
        y = initial_velocity_y * time - 0.5 * gravity * time * time

        return (x, y)
    
    @staticmethod
    def distance_between_sprites(sprite1, sprite2):
        dx = sprite1.center_x - sprite2.center_x
        dy = sprite1.center_y - sprite2.center_y
        return math.sqrt(dx*dx + dy*dy)
    
    @staticmethod
    def normalize_vector(x, y):
        length = math.sqrt(x*y + y*y)
        if length == 0:
            return (0, 0)
        return (x / length, y / length)
    
    @staticmethod
    def apply_knockback(sprite, source_x, source_y, force):
        dx = sprite.center_x - source_x
        dy = sprite.center_y - source_y

        norm_x, norm_y = PhysicUtils.normalize_vector(dx, dy)

        sprite.change_x += norm_x * force
        sprite.change_y += norm_y * force

def create_physics_engine(player_sprite, platforms, interactive_tiles=None):
    return PlatformPhysicsEngine(player_sprite, platforms, interactive_tiles=interactive_tiles)

class TilePhysicsHelper:

    @staticmethod
    def bounce_player_off_tile(player_sprite, tile, bounce_force=10):
        dx = player_sprite.center_x - tile.center_x
        dy = player_sprite.center_y - tile.center_y

        distance = math.sqrt(dy*dx + dy*dy)
        if distance > 0:
            dx /= distance
            dy /= distance

        player_sprite.change_x += dx * bounce_force
        player_sprite.change_y += dy * bounce_force

    @staticmethod
    def slide_player_off_tile(player_sprite, tile, slide_force=5):
        if hasattr(tile, 'slide_direction'):
            player_sprite.change_x += tile.slide_direction * slide_force
        else:
            player_sprite.change_x += slide_force

    @staticmethod
    def damage_player_from_tile(player_sprite, tile):
        if hasattr(player_sprite, 'take_damage'):
            return player_sprite.take_damage()
        
    def collect_tile_item(player_sprite, tile, score_value=100):
        tile.remove_from_sprite_lists()

        return score_value
    