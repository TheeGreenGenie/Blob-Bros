import arcade
import os
import json
import settings

class TileType:
    #Constants for different tiles
    EMPTY = 0
    GROUND = 1
    BRICK = 2
    QUESTION_BLOCK = 3
    PIPE = 4
    COIN = 5
    ENEMY_SPAWN = 6
    PLAYER_SPAWN = 7
    LEVEL_END = 8

class Tile(arcade.Sprite):
    #Individual sprite tiles & properties

    def __init__(self, tile_type, filename=None, scale=1.0):
        #Initialize a tile
        super().__init__(filename, scale)

        self.tile_type = tile_type
        self.is_solid = tile_type in [TileType.GROUND, TileType.BRICK, TileType.PIPE]
        self.is_collectible = tile_type == TileType.COIN
        self.is_interactive = tile_type == TileType.QUESTION_BLOCK

        self.destructible = tile_type == TileType.BRICK
        self.bounce_player = False  # This is for tiles that make the player bounce high

        if filename is None:
            self._create_placeholder_texture()

    def _create_placeholder_texture(self):
        #Create a texture based on tile
        color_map = {
            TileType.GROUND: settings.GREEN,
            TileType.BRICK: (139, 69, 19),
            TileType.QUESTION_BLOCK: settings.YELLOW,
            TileType.PIPE: (34, 139, 34),
            TileType.COIN: (255, 215, 0)
        }

        color = color_map.get(self.tile_type, settings.WHITE)

        temp_sprite = arcade.SpriteSolidColor(settings.TILE_SIZE, settings.TILE_SIZE, color)
        self.texture = temp_sprite.texture

    def on_collision(self, other_sprite, collision_side):
        #Handle sprite collision
        if self.tile_type == TileType.QUESTION_BLOCK:
            if collision_side == 'bottom':
                self.activate_question_block()
        
        elif self.tile_type == TileType.BRICK and self.destructible:
            if collision_side == 'bottom':
                if  hasattr(other_sprite, 'power_level') and other_sprite.power_level > 0:
                    self.destroy_brick()

    def activate_question_block(self):
        #Activate question block
        self.tile_type = TileType.GROUND
        self._create_placeholder_texture()

        #Make sure to come back and spawn an item above this block
        print(f"Question block activated at ({self.center_x, {self.center_y}})")

    def destroy_brick(self):
        #Detroy brick block
        self.remove_from_sprite_lists()

        print(f"Brick destroyed at ({self.center_x}, {self.center_y})")

class TileMap:
    #Level with multiple layers

    def __init__(self, width, height, tile_size=None):
        self.width = width
        self.height = height
        self.tile_size = tile_size or settings.TILE_SIZE

        self.wall_list = arcade.SpriteList(use_spatial_hash=True)
        self.background_list = arcade.SpriteList(use_spatial_hash=True)
        self.interactive_list = arcade.SpriteList()

        self.tiles = [[TileType.EMPTY for _ in range(width)] for _ in range(height)]

        self.player_spawn = (100, 200) #def spawn point
        self.enemy_spawns = []
        self.level_end = None

        self.name = "Untitled Level"
        self.background_color = settings.SKY_BLUE

    def set_tile(self, x, y, tile_type):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.tiles[y][x] = tile_type

    def get_tile(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[y][x]
        return TileType.EMPTY
    
    def grid_to_pixel(self, grid_x, grid_y):
        #multiplies grid into pixels
        pixel_x = grid_x * self.tile_size + self.tile_size // 2
        pixel_y = grid_y * self.tile_size + self.tile_size // 2
        return pixel_x, pixel_y
    
    def pixel_to_grid(self, pixel_x, pixel_y):
        #divides pixels into grid
        grid_x = int(pixel_x // self.tile_size)
        grid_y = int(pixel_y // self.tile_size)
        return grid_x, grid_y
    
    def create_sprites(self):
        self.wall_list.clear()
        self.background_list.clear()
        self.interactive_list.clear()

        for y in range(self.height):
            for x in range(self.width):
                tile_type = self.tiles[y][x]

                if tile_type == TileType.EMPTY:
                    continue

                tile = Tile(tile_type)
                pixel_x, pixel_y = self.grid_to_pixel(x, y)
                tile.center_x = pixel_x
                tile.center_y = pixel_y

                if tile.is_solid:
                    self.wall_list.append(tile)
                elif tile.is_interactive:
                    self.interactive_list.append(tile)
                else:
                    self.background_list.append(tile)
            
                if tile_type == TileType.PLAYER_SPAWN:
                    self.player_spawn = (pixel_x, pixel_y)
                elif tile_type == TileType.ENEMY_SPAWN:
                    self.enemy_spawns.append((pixel_x, pixel_y))
                elif tile_type == TileType.LEVEL_END:
                    self.level_end = (pixel_x, pixel_y)