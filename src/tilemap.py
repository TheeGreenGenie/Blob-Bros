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

    