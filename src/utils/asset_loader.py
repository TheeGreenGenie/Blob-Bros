import arcade
from typing import Dict, List, Optional, Tuple, Any
from PIL import Image
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import sys
import io
import time
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import settings

class AssetLoader:

    def __init__(self):
        self.base_path = Path(__file__).parent.parent.parent
        self.assets_path = self.base_path / 'assets'

        self.textures: Dict[str, arcade.Texture] = {}
        self.sounds: Dict[str, arcade.Sound] = {}
        self.sprite_sheets: Dict[str, List[arcade.Texture]] = {}
        self.tile_textures: Dict[str, arcade.Texture] = {}

        self.paths = {
            'sprites': self.assets_path / 'sprites',
            'sounds': self.assets_path / 'sounds',
            'music': self.assets_path / 'music',
            'tiles': self.assets_path / 'tiles',
            'backgrounds': self.assets_path / 'backgrounds',
            'ui': self.assets_path / 'ui'
        }

        self._create_asset_directories()

        self.loaded = False
        self.loading_errors: List[str] = []

    def _create_asset_directories(self):
        for path in self.paths.values():
            path.mkdir(parents=True, exist_ok=True)

    def load_all_assets(self) -> bool:
        print("Loading game assets...")

        try:
            print("Loading player assets...")
            self._load_player_assets()
            print("Creating player animations...")
            self._create_player_animations()
            print("Loading enemy assets...")
            self._load_enemy_assets()
            print("Loading tile assets...")
            self._load_tile_assets()
            print("Loading UI assets...")
            self._load_ui_assets()
            print("Loading sound assets...")
            self._load_sound_assets()
            print("Loading background assets...")
            self._load_background_assets()

            self.loaded = True
            print(f"Successfully loaded {len(self.textures)} textures and {len(self.sounds)} sounds")

            if self.loading_errors:
                print(f"Warning: {len(self.loading_errors)} assets failed to load:")
                for error in self.loading_errors:
                    print(f" - {error}")

            return True
        
        except Exception as e:
            print(f"Failed to load assets: {e}")
            self.loading_errors.append(str(e))
            return False
        
    def _load_player_assets(self):
        player_path = self.paths['sprites'] / 'player'

        player_assets = {
            'player_idle': 'mario_idle.png',
            'player_walk_1': 'mario_walk1.png',
            'player_walk_2': 'mario_walk2.png',
            'player_jump': 'mario_jump.png',
            'player_crouch': 'mario_crouch.png',
            'player_small': 'mario_idle.png',
            'player_big': 'mario_idle.png',
            'player_fire': 'mario_fire.png'
        }

        for name, filename in player_assets.items():
            texture = self._load_texture_with_fallback(
                player_path / filename,
                name,
                size=(48, 48),
                color=(255, 0, 0)
            )
            self.textures[name] = texture

    def _create_player_animations(self):
        walk_frames = [
            self.textures.get('player_walk_1', self.textures['player_idle']),
            self.textures.get('player_walk_2', self.textures['player_idle'])
        ]
        self.sprite_sheets['player_walk'] = walk_frames

        self.sprite_sheets['player_run'] = walk_frames

    def _load_enemy_assets(self):
        enemy_path = self.paths['sprites'] / 'enemies'

        goomba_assets = {
            'goomba_normal': ('goomba.png', (139, 69, 19)),
            'goomba_fast': ('goomba_fast.png', (255, 100, 100)),
            'goomba_large': ('goomba_large.png', (150, 75, 0)),
            'goomba_elite': ('goomba_elite.png', (100, 0, 100)),
            'goomba_dead': ('goomba_squished.png', (100, 100, 100))
        }

        for name, (filename, fallback_color) in goomba_assets.items():
            size = (36, 36) if 'large' not in name else (48, 48)
            texture = self._load_texture_with_fallback(
                enemy_path / filename,
                name,
                size=size,
                color=fallback_color
            )
            self.textures[name] = texture

        koopa_assets = {
            'koopa_grey': ('koopa_grey.png', (0, 255, 0)),
            'koopa_red': ('koopa_red.png', (255, 0, 0)),
            'koopa_shell': ('koopa_shell.png', (0, 100, 0))
        }

        for name, (filename, fallback_color) in koopa_assets.items():
            texture = self._load_texture_with_fallback(
                enemy_path / filename,
                name,
                size=(24, 32),
                color=fallback_color
            )
            self.textures[name] = texture

    def _load_tile_assets(self):
        tiles_path = self.paths['tiles']

        tile_assets = {
            'ground': ('ground.png', settings.GREEN),
            'brick': ('brick.png', (165, 42, 42)),
            'question_block': ('questions.png', (255, 215, 0)),
            'question_block_empty': ('question_empty.png', (139, 69, 19)),
            'pipe_top': ('pipe_top.png', (0, 128, 0)),
            'pipe_body': ('pipe_body.png', (0, 100, 0)),
            'castle': ('castle.png', (128, 128, 128)),
            'flag_pole': ('flag_pole.png', (255, 255, 255)),
            'flag': ('flag.png', (255, 0, 0))
        }

        for name, (filename, fallback_color) in tile_assets.items():
            texture = self._load_texture_with_fallback(
                tiles_path / filename,
                name,
                size=(settings.TILE_SIZE, settings.TILE_SIZE),
                color=fallback_color
            )
            self.tile_textures[name] = texture

    def _load_ui_assets(self):
        ui_path = self.paths['ui']

        ui_assets = {
            'coin_normal': ('coin.png', (255, 255, 0)),
            'coin_silver': ('coin_silver.png', (192, 192, 192)),
            'coin_gold': ('coin_gold.png', (255, 215, 0)),
            'coin_special': ('coin_special.png', (255, 215, 0)),
            'life_icon': ('life.png', settings.LIVES_COLOR),
            'score_popup': ('score_popup.png', settings.SCORE_COLOR),
            'button_start': ('button_start.png', (100, 200, 100)),
            'button_quit': ('button_quit.png', (200, 200, 100))
        }

        for name, (filename, fallback_color) in ui_assets.items():
            size = (16, 16) if 'coin' in name else (32, 32)
            texture = self._load_texture_with_fallback(
                ui_path / filename,
                name,
                size=size,
                color=fallback_color
            )
            self.textures[name] = texture

    def _load_background_assets(self):
        bg_path = self.paths['backgrounds']

        bg_assets = {
            'sky': ('sky.png', settings.SKY_BLUE),
            'clouds': ('clouds.png', settings.WHITE),
            'hills': ('hills.png', (100, 150, 100)),
            'mushroom': ('mushroom.png', (64, 64, 64))
        }

        for name, (filename, fallback_color) in bg_assets.items():
            texture = self._load_texture_with_fallback(
                bg_path / filename,
                name,
                size=(settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT),
                color=fallback_color
            )
            self.textures[name] = texture

    def _load_sound_assets(self):
        if not settings.ENABLE_SOUND:
            print("Sound disabled, skipping audio assets")
            return
        
        sound_path = self.paths['sounds']
        music_path = self.paths['music']

        sound_effects = [
            'jump.ogg', 'coin.ogg', 'powerup.ogg', 'stomp.ogg',
            'death.ogg', 'level_complete.ogg', 'pause.ogg',
            'menu_select.ogg', 'menu_move.ogg'
        ]

        for sound_file in sound_effects:
            sound_name = sound_file.replace('.ogg', '')
            try:
                if (sound_path / sound_file).exists():
                    self.sounds[sound_name] = arcade.load_sound(sound_path / sound_file)
                else:
                    self.sounds[sound_name] = None
                    self.loading_errors.append(f"Sound not found: {sound_file}")
            except Exception as e:
                self.loading_errors.append(f"Failed to load sound {sound_file}: {e}")
                self.sounds[sound_name] = None

        music_files = [
            'overworld.ogg', 'underground.ogg', 'castle.ogg',
            'game_over.ogg', 'victory.ogg'
        ]

        for music_file in music_files:
            music_name = music_file.replace('.ogg', '')
            try:
                if (music_path / music_file).exists():
                    self.sounds[f"music_{music_name}"] = arcade.load_sound(music_path / music_file)
                else:
                    self.sounds[f"music_{music_name}"] = None
                    self.loading_errors.append(f"Music not found: {music_file}")
            except Exception as e:
                self.loading_errors.append(f"Failed to load music {music_file}: {e}")
                self.sounds[f"music_{music_name}"] = None

    def _load_texture_with_fallback(self, filepath: Path, name: str, size: Tuple[int, int], color: Tuple[int, int, int]) -> arcade.Texture:
        try:
            #DEBUGGING
            print(f"Attempting to load: {filepath}")
            print(f"File exists: {filepath.exists()}")

            if filepath.exists():
                #DEBUGGING
                print(f"Loading real asset: {filepath}")
                original_texture = arcade.load_texture(str(filepath))
                #DEBUGGING
                print(f"Successfully loaded {filepath}, size: {original_texture.width}x{original_texture.height}")

                if (original_texture.width, original_texture.height) != size:
                    if settings.DEBUG_MODE:
                        print(f"Resizing {filepath.name}: {original_texture.width}x{original_texture.height} -> {size[0]}x{size[1]}")

                    resized_texture = self._resize_texture(original_texture, size, name)
                    return resized_texture
                else:
                    return original_texture
            else:
                #DEBUGGING
                print(f"File not found, creating placeholder: {filepath}")
                return self._create_colored_texture(name, size, color)
        except Exception as e:
            #DEBUGGING
            print(f"Error loading {filepath}: {e}")
            self.loading_errors.append(f'Failed to load {filepath}: {e}')
            return self._create_colored_texture(name, size, color)
        
    def _resize_texture(self, original_texture: arcade.Texture, target_size: Tuple[int, int], name: str) -> arcade.Texture:
        try:
            pil_image = original_texture.image

            #Resize with LANCZOS if downsizing, with BICUPIC if largening
            if target_size[0] < pil_image.width or target_size[1] < pil_image.height:
                resample_method = Image.Resampling.LANCZOS
            else:
                resample_method = Image.Resampling.BICUBIC

            resized_image = pil_image.resize(target_size, resample_method)

            resized_texture = arcade.Texture(resized_image)
            return resized_texture

        except Exception as e:
            print(f"Failed to resize texture {name}: {e}")
            #falls back to og texture
            return original_texture

    def _create_colored_texture(self, name: str, size: Tuple[int, int], color: Tuple[int, int, int]) -> arcade.Texture:
        try:
            image = Image.new('RGBA', size, color + (255,))

            texture = arcade.Texture(image)
            return texture

        except Exception as e:
            print(f"Failed to create colored texture {name}: {e}")
            return arcade.Texture.create_empty(name, size)

    def get_enemy_texture(self, enemy_type: str, variant: str = 'normal') -> Optional[arcade.Texture]:
        if enemy_type == 'goomba':
            return self.get_goomba_texture(variant)
        elif enemy_type == 'koopa':
            texture_name = f"koopa_{variant}"
            return self.textures.get(texture_name)
        else:
            return self.textures.get(f"{enemy_type}_{variant}")

    def get_coin_texture(self, coin_type: str) -> Optional[arcade.Texture]:
        texture_name = f"coin_{coin_type}"
        return self.textures.get(texture_name)
    
    def get_coin_color(self, coin_type: str) -> Tuple[int, int, int]:
        coin_colors = {
            'normal': (255, 255, 0),
            'silver': (192, 192, 192),
            'gold': (255, 215, 0),
            'special': (255, 0, 255)
        }
        return coin_colors.get(coin_type, (255, 255, 0))   # default color yellow

    def get_goomba_texture(self, variant: str) -> Optional[arcade.Texture]:
        texture_name = f"goomba_{variant}"
        return self.textures.get(texture_name)
    
    def get_goomba_color(self, variant: str) -> Tuple[int, int, int]:
        goomba_colors = {
            'normal': (139, 69, 19),
            'fast': (255, 100, 100),
            'large': (150, 75, 0),
            'elite': (100, 0, 100),
            'dead': (100, 100, 100)
        }
        return goomba_colors.get(variant, (139, 69, 19))
    
    def get_goomba_size(self, variant: str) -> Tuple[int, int]:
        goomba_sizes = {
            'normal': (24, 24),
            'fast': (24, 24),
            'large': (32, 32),
            'elite': (24, 24),
            'dead': (24, 12)
        }
        return goomba_sizes.get(variant, (24, 24))

    def get_texture(self, name: str) -> Optional[arcade.Texture]:
        return self.textures.get(name)
    
    def get_tile_texture(self, name: str) -> Optional[arcade.Texture]:
        return self.tile_textures.get(name)
    
    def get_sound(self, name: str) -> Optional[arcade.Sound]:
        return self.sounds.get(name)
    
    def get_animation(self, name: str) -> List[arcade.Texture]:
        return self.sprite_sheets.get(name, [])
    
    def play_sound(self, name: str, volume: float = 1.0) -> bool:
        if not settings.ENABLE_SOUND:
            return False
        
        sound = self.sounds.get(name)
        if sound:
            try:
                arcade.play_sound(sound, volume)
                return True
            except Exception as e:
                print(f"Failed to play sound {name}: {e}")
            return False
        return False
        
    def get_asset_info(self) -> Dict[str, Any]:
        return {
            'textures_loaded': len(self.textures),
            'tile_textures_loaded': len(self.tile_textures),
            'sounds_loaded': len(self.sounds),
            'animations_loaded': len(self.sprite_sheets),
            'loading_errors': len(self.loading_errors),
            'fully_loaded': self.loaded
        }
    
    def reload_assets(self) -> bool:
        print("Reloading assets...")

        self.textures.clear()
        self.sounds.clear()
        self.sprite_sheets.clear()
        self.tile_textures.clear()
        self.loading_errors.clear()
        self.loaded = False

        return self.load_all_assets()
    
    def validate_critical_assets(self):
        critical_assets = {
            'player_idle', 'goomba_normal', 'coin_normal'
        }
        critical_tile_assets = {'ground'}

        missing = []
        for asset in critical_assets:
            if asset not in self.textures:
                missing.append(asset)

        for asset in critical_tile_assets:
            if asset not in self.tile_textures:
                missing.append(asset)

        if missing:
            print(f"WARNING: Missing critical assets: {missing}")
            return False
        return True
    
_asset_loader = None

def get_asset_loader() -> AssetLoader:
    global _asset_loader
    if _asset_loader is None:
        _asset_loader = AssetLoader()
    return _asset_loader

def load_game_assets() -> bool:
    loader = get_asset_loader()
    return loader.load_all_assets()

def get_texture(name: str) -> Optional[arcade.Texture]:
    return get_asset_loader().get_texture(name)

def get_tile_texture(name: str) -> Optional[arcade.Texture]:
    return get_asset_loader().get_tile_texture(name)

def get_sound(name: str) -> Optional[arcade.Sound]:
    return get_asset_loader().get_sound(name)

def play_sound(name: str, volume: float = 1.0) -> bool:
    return get_asset_loader().play_sound(name, volume)

def get_animation(name: str) -> List[arcade.Texture]:
    return get_asset_loader().get_animation(name)

def get_coin_texture(coin_type: str) -> Optional[arcade.Texture]:
    return get_asset_loader().get_coin_texture(coin_type)

def get_coin_color(coin_type: str) -> Tuple[int, int, int]:
    return get_asset_loader().get_coin_color(coin_type)

def get_goomba_texture(variant: str) -> Optional[arcade.Texture]:
    return get_asset_loader().get_goomba_texture(variant)

def get_goomba_color(variant: str) -> Tuple[int, int, int]:
    return get_asset_loader().get_goomba_color(variant)

def get_goomba_size(variant: str) -> Tuple[int, int]:
    return get_asset_loader().get_goomba_size(variant)

def get_enemy_texture(enemy_type: str, variant: str = 'normal') -> Optional[arcade.Texture]:
    return get_asset_loader().get_enemy_texture(enemy_type, variant)

def validate_assets() -> bool:
    return get_asset_loader().validate_critical_assets()