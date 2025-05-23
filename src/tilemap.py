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
        