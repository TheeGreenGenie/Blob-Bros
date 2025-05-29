#Sound manager
import arcade
import time
from typing import Dict, Optional, List, Tuple
from pathlib import Path
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import settings

class SoundManager:
    
    def __init__(self):
        self.master_volume = settings.MASTER_VOLUME
        self.sfx_volume = settings.SFX_VOLUME
        self.music_volume = settings.MUSIC_VOLUME
        self.sound_enabled = settings.ENABLE_SOUND

        self.current_music = None
        self.paused_music_name = None
        self.current_music_name = None
        self.music_player = None
        self.music_loop = False

        self.active_sounds: Dict[str, List] = {}
        self.sound_cooldowns: Dict[str, float] = {}
        self.last_played: Dict[str, float] = {}

        self.asset_loader = None
        
        self.sound_configs = {
            #Player
            'jump': {'cooldown': 0.1, 'priority': 'high'},
            'land': {'cooldown': 0.2, 'priority': 'medium'},
            'run': {'cooldown': 0.3, 'priority': 'low'},
            'death': {'cooldown': 1.0, 'priority': 'critical'},

            #Collection
            'coin': {'cooldown': 0.05, 'priority': 'high'},
            'powerup': {'cooldown': 0.5, 'priority': 'high'},
            'life': {'cooldown': 1.0, 'priority': 'critical'},

            #Enemy
            'stomp': {'cooldown': 0.1, 'priority': 'high'},
            'enemy_death': {'cooldown': 0.2, 'priority': 'medium'},
            'enemy_hit': {'cooldown': 0.1, 'priority': 'medium'},

            #Levels
            'level_complete': {'cooldown': 2.0, 'priority': 'critical'},
            'level_start': {'cooldown': 2.0, 'priority': 'high'},
            'checkpoint': {'cooldown': 1.0, 'priority': 'high'},

            #UI
            'menu_select': {'cooldown': 0.2, 'priority': 'medium'},
            'menu_move': {'cooldown': 0.1, 'priority': 'low'},
            'pause': {'cooldown': 0.3, 'priority': 'medium'},
            'unpause': {'cooldown': 0.3, 'priority': 'medium'},

            #SpecEfx
            'explosion': {'cooldown': 0.5, 'priority': 'high'},
            'warp': {'cooldown': 1.0, 'priority': 'high'},
        }

        self.music_tracks = {
            'overworld': {'loop': True},
            'underground': {'loop': True},
            'castle': {'loop': True},
            'underwater': {'loop': True},
            'boss': {'loop': True},
            'victory': {'loop': False},
            'game_over': {'loop': False},
            'menu': {'loop': True},
        }

        print("SoundManager initialized")

    def set_asset_loader(self, asset_loader):
        if asset_loader is None:
            print('Error: asset_loader is None')
            return False

        self.asset_loader = asset_loader
        print("SoundManager connected to AssetLoader")
        return True

    def play_sound(self, sound_name: str, volume_override: Optional[float] = None, force_play: bool = False) -> bool:
        if not self.sound_enabled or not self.asset_loader:
            print(f"Warning: Unconfigured sound: {sound_name}")
            return False
        
        current_time = time.time()

        if not force_play and sound_name in self.last_played:
            cooldown = self.sound_configs.get(sound_name, {}).get('cooldown', 0.1)
            if (current_time - self.last_played.get(sound_name, 0)) < cooldown:
                return False
            
        sound = self.asset_loader.get_sound(sound_name)
        if not sound:
            if settings.DEBUG_MODE:
                print(f"Sound not found: {sound_name}")
            return False
        
        final_volume = volume_override if volume_override is not None else 1.0
        final_volume *= self.sfx_volume * self.master_volume
        final_volume = max(0.0, min(1.0, final_volume))
        

        try:
            arcade.play_sound(sound, volume=final_volume)
            self.last_played[sound_name] = current_time

            if sound_name not in self.active_sounds:
                self.active_sounds[sound_name] = []
            self.active_sounds[sound_name].append(current_time)

            if settings.DEBUG_MODE:
                print(f"Played sound: {sound_name} at volume {final_volume:.2f}")

            return True
        except Exception as e:
            print(f"Error playing sound {sound_name}: {e}")
            return False
        
    def play_music(self, music_name: str, volume_override: Optional[float] = None) -> bool:
        if not self.sound_enabled or not self.asset_loader:
            return False
        
        self.stop_music()

        music_key = f"music_{music_name}"
        music = self.asset_loader.get_sound(music_key)
        if not music:
            if settings.DEBUG_MODE:
                print(f"Music not found: {music_name}")
            return False
        
        track_info = self.music_tracks.get(music_name, {})
        should_loop = track_info.get('loop', True)

        target_volume = volume_override if volume_override is not None else 1.0
        target_volume *= self.music_volume * self.master_volume
        target_volume = max(0.0, min(1.0, target_volume))

        try:
            if should_loop:
                self.music_player = arcade.play_sound(music, volume=target_volume, looping=True)
            else:
                self.music_player = arcade.play_sound(music, volume=target_volume)

            self.current_music = music
            self.current_music_name = music_name
            self.music_loop = should_loop

            print(f"Started playing music: {music_name}")
            return True
        
        except Exception as e:
            print(f"Error playing music {music_name}: {e}")
            return False
        
    def stop_music(self):
        if not self.current_music:
            return

        try:
            if self.music_player:
                self.music_player.delete()
            self.current_music = None
            self.current_music_name = None
            self.music_player = None
            self.music_loop = False
            print("music stopped")
        except Exception as e:
            print(f"Error stopping music: {e}")

    def pause_music(self):
        if self.music_player and self.current_music_name:
            self.paused_music_name = self.current_music_name
            self.stop_music()
            print(f"music paused: {self.current_music_name}")

    def resume_music(self):
        if hasattr(self, 'paused_music_name') and self.paused_music_name:
            self.play_music(self.paused_music_name)
            self.current_music_name = self.paused_music_name
            print(f"Music resumed: {self.current_music_name}")
        elif self.current_music_name:
            self.play_music(self.current_music_name)
            print(f"Starting: {self.current_music_name}")

    def set_master_volume(self, volume: float):
        self.master_volume = max(0.0, min(1.0, volume))
        print(f"Master volume set to {self.master_volume:.2f}")

    def set_sfx_volume(self, volume: float):
        self.sfx_volume = max(0.0, min(1.0, volume))
        print(f"SFX volume set to {self.sfx_volume:.2f}")

    def set_music_volume(self, volume: float):
        self.music_volume = max(0.0, min(1.0, volume))
        print(f"Music volume set to {self.music_volume:.2f}")

    def toggle_sound(self) -> bool:
        self.sound_enabled = not self.sound_enabled
        if not self.sound_enabled:
            self.stop_music()
        print(f"Sound {'enabled' if self.sound_enabled else 'disabled'}")
        return self.sound_enabled
    
    def cleanup_old_sounds(self):
        current_time = time.time()
        cleanup_threshold = 5.0

        for sound_name in list(self.active_sounds.keys()):
            self.active_sounds[sound_name] = [
                timestamp for timestamp in self.active_sounds[sound_name]
                if current_time - timestamp < cleanup_threshold
            ]

            if not self.active_sounds[sound_name]:
                del self.active_sounds[sound_name]

    def get_sound_info(self) -> Dict:
        return {
            'sound_enabled': self.sound_enabled,
            'current_music': self.current_music_name,
            'music_looping': self.music_loop,
            'active_sounds': len(self.active_sounds),
        }
    
    def update(self, delta_time: float):
        if hasattr(self, '_last_cleanup'):
            if time.time() - self._last_cleanup > 1.0:
                self.cleanup_old_sounds()
                self._last_cleanup = time.time()
        else:
            self._last_cleanup = time.time()

    def preload_level_sounds(self, level_type: str):
        level_sound_sets = {
            'overworld': ['jump', 'coin', 'stomp', 'powerup'],
            'underground': ['jump', 'coin', 'stomp', 'echo_jump'],
            'castle': ['jump', 'coin', 'stomp', 'enemy_hit', 'explosion'],
            'water': ['swim', 'bubble', 'coin',  'enemy_hit']
        }

        sounds_to_preload = level_sound_sets.get(level_type, [])
        print(f"Preloading sounds for {level_type}: {sounds_to_preload}")

    def play_level_music(self, level_type: str):
        music_mapping = {
            'overworld': 'overworld',
            'underground': 'underground',
            'castle': 'castle',
            'water': 'underwater',
            'boss': 'boss'
        }

        music_name = music_mapping.get(level_type, 'overworld')
        self.play_music(music_name)

_sound_manager = None

def get_sound_manager() -> SoundManager:
    global _sound_manager
    if _sound_manager is None:
        _sound_manager = SoundManager()
    return _sound_manager

def play_sound(sound_name: str, volume: Optional[float] = None, force: bool = False) -> bool:
    return get_sound_manager().play_sound(sound_name, volume, force)

def play_music(music_name: str) -> bool:
    return get_sound_manager().play_music(music_name)

def stop_music():
    get_sound_manager().stop_music()

def toggle_sound() -> bool:
    return get_sound_manager().toggle_sound()

def initialize_sound_manager(asset_loader):
    sound_manager = get_sound_manager()
    success = sound_manager.set_asset_loader(asset_loader)
    if success:
        print("Sound manager successfully connected to asset loader")
    else:
        print("Failed to connect sound manager to asset loader")

    return sound_manager