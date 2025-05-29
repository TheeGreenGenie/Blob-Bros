#Level Loader
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
    
    def draw_with_layers(self):
        # If we have an arcade tilemap, use its draw method
        if hasattr(self, 'arcade_tilemap') and self.arcade_tilemap:
            self.arcade_tilemap.draw()
        else:
            # Fall back to our standard drawing
            self.draw()

    def get_sprite_at_position(self, x, y, layer_name="Terrain"):
        if hasattr(self, 'arcade_tilemap') and self.arcade_tilemap:
            if layer_name in self.arcade_tilemap.sprite_lists:
                sprite_list = self.arcade_tilemap.sprite_lists[layer_name]
                # Check for collision at point
                sprites = arcade.get_sprites_at_point((x, y), sprite_list)
                return sprites[0] if sprites else None
        return None

    def get_tile_properties(self, x, y):
        sprite = self.get_sprite_at_position(
            x * self.tile_size + self.tile_size // 2,
            y * self.tile_size + self.tile_size // 2
        )
        if sprite and hasattr(sprite, 'properties'):
            return sprite.properties
        return {}

    def spawn_enemies(self, enemy_manager):
        from enemies.goomba import create_goomba
        
        for spawn_data in self.enemy_spawns:
            x = spawn_data['x']
            y = spawn_data['y']
            enemy_type = spawn_data.get('type', 'goomba')
            variant = spawn_data.get('variant', 'normal')
            
            # Create the appropriate enemy type
            if enemy_type == 'goomba':
                enemy = create_goomba(x, y, variant)
                enemy_manager.enemy_list.append(enemy)
                enemy_manager.total_enemies += 1
            # Add more enemy types as needed
            
    def spawn_coins(self, coin_manager):
        if hasattr(self, 'arcade_tilemap') and self.arcade_tilemap:
            if "Collectibles" in self.arcade_tilemap.sprite_lists:
                # Remove the arcade sprites and replace with our Coin objects
                collectibles = self.arcade_tilemap.sprite_lists["Collectibles"]
                for sprite in collectibles:
                    if hasattr(sprite, 'properties') and sprite.properties.get('type') == 'coin':
                        # Determine coin type from properties or default
                        coin_type = sprite.properties.get('coin_type', 'normal')
                        coin_manager.add_coin(sprite.center_x, sprite.center_y, coin_type)
                
                # Clear the arcade sprite list since we're using our own coins
                collectibles.clear()

    def process_interactive_blocks(self):
        if hasattr(self, 'arcade_tilemap') and self.arcade_tilemap:
            for layer_name, sprite_list in self.arcade_tilemap.sprite_lists.items():
                for sprite in sprite_list:
                    if hasattr(sprite, 'properties'):
                        # Check if it's a question block
                        if sprite.properties.get('type') == 'question_block':
                            # Add our custom collision handling
                            sprite.contents = sprite.properties.get('contents', 'coin')
                            sprite.activated = False
                        
                        # Check if it's a brick block
                        elif sprite.properties.get('type') == 'brick':
                            sprite.breakable = sprite.properties.get('breakable', True)

    def create_sprites(self):
        if hasattr(self, 'arcade_tilemap') and self.arcade_tilemap:
            print("Skipping sprite creation - using TMX sprite data")
            return

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
    def draw(self):
        if hasattr(self, 'arcade_tilemap') and self.arcade_tilemap:
            # Use arcade's optimized drawing
            self.arcade_tilemap.draw()
        else:
            # Use original drawing method
            self.background_list.draw()
            self.wall_list.draw()
            self.interactive_list.draw()

    

class TileMapLoader:
    
    @staticmethod
    def load_from_json(filename):
        try:
            with open(filename, 'r') as f:
                data = json.load(f)

            width = data.get('width', 50)
            height = data.get('height', 20)
            tile_size = data.get('tile_size', settings.TILE_SIZE)

            tilemap = TileMap(width, height, tile_size)
            tilemap.name = data.get('name', os.path.basename(filename))

            tile_data = data.get('tiles', [])
            for y in range(height):
                for x in range(width):
                    if y < len(tile_data) and x < len(tile_data[y]):
                        tilemap.set_tile(x, y, tile_data[y][x])

            if 'player_spawn' in data:
                spawn = data['player_spawn']
                tilemap.player_spawn = (spawn['x'], spawn['y'])

            if 'enemy_spawns' in data:
                tilemap.enemy_spawns = [(spawn['x'], spawn['y']) for spawn in data['enemy_spawns']]

            tilemap.create_sprites()
            return tilemap

        except Exception as e:
            print(f"Error loading tilemap from {filename}: {e}")
            return None
        
    @staticmethod
    def load_from_tiled_tmx(filename):
        try:
            # Use arcade's built-in TMX loader
            # scaling factor for the tiles
            scaling = settings.TILE_SCALING
            
            # Load the tile map using arcade
            arcade_tilemap = arcade.load_tilemap(
                filename, 
                scaling=scaling,
                use_spatial_hash=True  # Optimize collision detection
            )
            
            # Get map dimensions from the arcade tilemap
            # Note: arcade_tilemap.width/height are in pixels, we need tile count
            map_width_pixels = arcade_tilemap.map_size.width
            map_height_pixels = arcade_tilemap.map_size.height
            tile_width = arcade_tilemap.tile_size.width * scaling
            tile_height = arcade_tilemap.tile_size.height * scaling
            
            # Calculate grid dimensions
            width = int(map_width_pixels / tile_width)
            height = int(map_height_pixels / tile_height)
            
            # Create our TileMap object
            tilemap = TileMap(width, height, int(tile_width))
            tilemap.name = os.path.basename(filename).replace('.tmx', '')
            
            # Clear default sprite lists
            tilemap.wall_list.clear()
            tilemap.background_list.clear()
            tilemap.interactive_list.clear()
            
            # Process sprite lists from arcade's tilemap
            # Arcade creates sprite lists based on layer names
            for layer_name, sprite_list in arcade_tilemap.sprite_lists.items():
                if layer_name.lower() == "terrain":
                    # Add all terrain sprites to wall list
                    for sprite in sprite_list:
                        tilemap.wall_list.append(sprite)
                        
                elif layer_name.lower() == "collectibles":
                    # Process collectibles - they go to interactive list
                    for sprite in sprite_list:
                        # Check if it's a coin based on properties or texture
                        if hasattr(sprite, 'properties'):
                            if sprite.properties.get('type') == 'coin' or sprite.properties.get('collectible'):
                                tilemap.interactive_list.append(sprite)
                                
                elif layer_name.lower() == "background":
                    # Add background decorations
                    for sprite in sprite_list:
                        tilemap.background_list.append(sprite)
            
            # Process object layers for spawn points and special objects
            if hasattr(arcade_tilemap, 'object_lists'):
                for object_layer in arcade_tilemap.object_lists:
                    for tmx_object in object_layer:
                        # Get object position
                        obj_x = tmx_object.location.x * scaling
                        obj_y = tmx_object.location.y * scaling
                        
                        # Handle different object types
                        if tmx_object.name == "player_spawn":
                            tilemap.player_spawn = (obj_x, obj_y)
                            
                        elif "spawn" in tmx_object.name and tmx_object.properties.get('spawn_type') == 'enemy':
                            # Create enemy spawn data
                            enemy_spawn = {
                                'x': obj_x,
                                'y': obj_y,
                                'type': tmx_object.properties.get('enemy_type', 'goomba'),
                                'variant': tmx_object.properties.get('variant', 'normal')
                            }
                            tilemap.enemy_spawns.append(enemy_spawn)
                            
                        elif tmx_object.name == "level_end":
                            tilemap.level_end = (obj_x, obj_y)
                            # Store next level info if available
                            if 'next_level' in tmx_object.properties:
                                tilemap.next_level = tmx_object.properties['next_level']
            
            # Process map properties
            if hasattr(arcade_tilemap, 'properties') and arcade_tilemap.properties:
                # Background color
                if 'background_color' in arcade_tilemap.properties:
                    hex_color = arcade_tilemap.properties['background_color'].lstrip('#')
                    tilemap.background_color = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
                
                # Music track
                if 'music' in arcade_tilemap.properties:
                    tilemap.background_music = arcade_tilemap.properties['music']
                
                # Time limit
                if 'time_limit' in arcade_tilemap.properties:
                    tilemap.time_limit = int(arcade_tilemap.properties['time_limit'])
            
            # Store the arcade tilemap reference for additional features
            tilemap.arcade_tilemap = arcade_tilemap
            
            print(f"Successfully loaded TMX level: {tilemap.name}")
            print(f"Map size: {width}x{height} tiles")
            print(f"Found {len(tilemap.wall_list)} wall sprites")
            print(f"Found {len(tilemap.interactive_list)} interactive sprites")
            print(f"Found {len(tilemap.enemy_spawns)} enemy spawns")
            
            return tilemap
            
        except Exception as e:
            print(f"Error loading TMX file {filename}: {e}")
            import traceback
        
    @staticmethod
    def create_test_level():
        #level to text functionality
        tilemap = TileMap(50, 20)
        tilemap.name = "Test Level"

        for x in range(50):
            tilemap.set_tile(x, 0, TileType.GROUND)
            tilemap.set_tile(x, 1, TileType.GROUND)

        platform_data = [
            (10, 15, 5),
            (20, 25, 8),
            (30, 35, 6),
            (40, 45, 10)
        ]

        for start_x, end_x, y in platform_data:
            for x in range(start_x, end_x):
                tilemap.set_tile(x, y, TileType.GROUND)

        tilemap.set_tile(12, 6, TileType.QUESTION_BLOCK)
        tilemap.set_tile(22, 9, TileType.QUESTION_BLOCK)
        tilemap.set_tile(32, 7, TileType.BRICK)
        tilemap.set_tile(33, 7, TileType.BRICK)
        tilemap.set_tile(34, 7, TileType.BRICK)

        coin_positions = [(15, 10), (25, 12), (35, 8), (5, 5)]
        for x, y in coin_positions:
            tilemap.set_tile(x, y, TileType.COIN)

        tilemap.player_spawn = tilemap.grid_to_pixel(3, 3)

        enemy_positions = [(18, 6), (28, 9), (38, 7)]
        for x, y in enemy_positions:
            tilemap.set_tile(x, y, TileType.ENEMY_SPAWN)
            tilemap.enemy_spawns.append(tilemap.grid_to_pixel(x, y))

        tilemap.set_tile(48, 5, TileType.LEVEL_END)
        tilemap.level_end = tilemap.grid_to_pixel(48, 5)

        tilemap.create_sprites()
        return tilemap
    
def save_tilemap_to_json(tilemap, filename):
    data = {
        'name': tilemap.name,
        'width': tilemap.width,
        'height': tilemap.height,
        'tile_size': tilemap.tile_size,
        'tiles': tilemap.tiles,
        'player_spawn': {
            'x': tilemap.player_spawn[0],
            'y': tilemap.player_spawn[1]
        },
        'enemy_spawns': [
            {'x': x, 'y': y} for x, y in tilemap.enemy_spawns
        ]
    }

    if tilemap.level_end:
        data['level_end'] = {
            'x': tilemap.level_end[0],
            'y': tilemap.level_end[1]
        }

    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Tilemap saved to {filename}")
    except Exception as e:
        print(f"Error saving tilemap to {filename}: {e}")

def load_level(filename):
    if not os.path.exists(filename):
        print(f"Level file not found: {filename}")
        return TileMapLoader.create_test_level()
    
    ext = os.path.splitext(filename)[1].lower()

    if ext == 'json':
        return TileMapLoader.load_from_json(filename)
    elif ext == '.tmx':
        print(f"For TMX files, use arcade.load_tilemap() in your game code")
        return TileMapLoader.create_test_level()
    else:
        print(f"Unsupported file format: {ext}")
        return TileMapLoader.create_test_level()
    
def create_simple_level():
    return TileMapLoader.create_test_level()