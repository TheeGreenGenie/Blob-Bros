import arcade
import threading
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
        self.current_music_name = None
        self.music_player = None
        self.music_loop = False

        self.active_sounds: Dict[str, List] = {}
        self.sound_cooldowns: Dict[str, float] = {}
        self.last_played: Dict[str, float] = ()

        self.fade_thread = None
        self.fade_active = False

        self.asset_loader = None
        
        self.sound_configs = {
            #Player
            'jump': {'cooldown': 0.1, 'volume_modifier': 1.0, 'priority': 'high'},
            'land': {'cooldown': 0.2, 'volume_modifier': 0.8, 'priority': 'medium'},
            'run': {'cooldown': 0.3, 'volume_modifier': 0.6, 'priority': 'low'},
            'death': {'cooldown': 1.0, 'volume_modifier': 1.2, 'priority': 'critical'},

            #Collection
            'coin': {'cooldown': 0.05, 'volume_modifier': 0.9, 'priority': 'high'},
            'powerup': {'cooldown': 0.5, 'volume_modifier': 1.1, 'priority': 'high'},
            'life': {'cooldown': 1.0, 'volume_modifier': 1.2, 'priority': 'critical'},

            #Enemy
            'stomp': {'cooldown': 0.1, 'volume_modifier': 1.0, 'priority': 'high'},
            'enemy_death': {'cooldown': 0.2, 'volume_modifier': 0.9, 'priority': 'medium'},
            'enemy_hit': {'cooldown': 0.1, 'volume_modifier': 0.8, 'priority': 'medium'},

            #Levels
            'level_complete': {'cooldown': 2.0, 'volume_modifier': 1.3, 'priority': 'critical'},
            'level_start': {'cooldown': 2.0, 'volume_modifier': 1.1, 'priority': 'high'},
            'checkpoint': {'cooldown': 1.0, 'volume_modifier': 1.0, 'priority': 'high'},

            #UI
            'menu_select': {'cooldown': 0.2, 'volume_modifier': 0.8, 'priority': 'medium'},
            'menu_move': {'cooldown': 0.1, 'volume_modifier': 0.6, 'priority': 'low'},
            'pause': {'cooldown': 0.3, 'volume_modifier': 0.9, 'priority': 'medium'},
            'unpause': {'cooldown': 0.3, 'volume_modifier': 0.9, 'priority': 'medium'},

            #SpecEfx
            'explosion': {'cooldown': 0.5, 'volume_modifier': 1.1, 'priority': 'high'},
            'warp': {'cooldown': 1.0, 'volume_modifier': 1.0, 'priority': 'high'},
        }

        self.music_tracks = {
            'overworld': {'loop': True, 'volume_modifier': 1.0},
            'underground': {'loop': True, 'volume_modifier': 0.9},
            'castle': {'loop': True, 'volume_modifier': 1.1},
            'underwater': {'loop': True, 'volume_modifier': 0.8},
            'boss': {'loop': True, 'volume_modifier': 1.2},
            'victory': {'loop': False, 'volume_modifier': 1.3},
            'game_over': {'loop': False, 'volume_modifier': 1.1},
            'menu': {'loop': True, 'volume_modifier': 0.7},
        }

        print("SoundManager initialized")

    def set_asset_loader(self, asset_loader):
        self.asset_loader = asset_loader
        print("SoundManager connectedd to AssetLoader")

    def play_sound(self, sound_name: str, volume_override: Optional[float] = None, force_play: bool = False) -> bool:
        if not self.sound_enabled or not self.asset_loader:
            return False
        
        current_time = time.time()

        if not force_play and sound_name in self.sound_cooldowns:
            cooldown = self.sound_configs.get(sound_name, {}).get('cooldown', 0.1)
            if (current_time - self.last_played.get(sound_name, 0)) < cooldown:
                return False
            
        sound = self.asset_loader.get_sound(sound_name)
        if not sound:
            if settings.DEBUG_MODE:
                print(f"Sound not found: {sound_name}")
            return False
        
        if volume_override is not None:
            final_volume = volume_override * self.master_volume
        else:
            config = self.sound_configs.get(sound_name, {})
            volume_mod = config.get('volume_modifier', 1.0)
            final_volume = self.sfx_volume * volume_mod * self.master_volume

        final_volume = max(0.0, min(1.0, final_volume))

        try:
            arcade.play_sound(sound, volume=final_volume)
            self.last_played[sound_name] = current_time

            if sound_name not in self.active_sounds:
                self.active_sounds[sound_name] = []
            self.active_sounds[sound_name].append(current_time)

            if settings.DEBUG_MODE:
                print(f"Played sounds: {sound_name} at volume {final_volume:.2f}")

            return True
        except Exception as e:
            print(f"Error playing sound {sound_name}: {e}")
            return False
        
    def play_music(self, music_name: str, fade_in_time: float = 0.0, volume_override: Optional[float] = None) -> bool:
        if not self.sound_enabled or not self.asset_loader:
            return False
        
        self.stop_music(fade_out_time=0.5 if self.current_music else 0.0)

        music_key = f"music_{music_name}"
        music = self.asset_loader.get_sound(music_key)
        if not music:
            if settings.DEBUG_MODE:
                print(f"Music not founc: {music_name}")
            return False
        
        track_info = self.music_tracks.get(music_name, {})
        should_loop = track_info.get('loop', True)

        if volume_override is not None:
            target_volume = volume_override * self.master_volume
        else:
            volume_mod = track_info.get('volume_modifier', 1.0)
            target_volume = self.music_volume * volume_mod * self.master_volume

        target_volume = max(0.0, min(1.0, target_volume))

        try:
            if should_loop:
                self.music_player = arcade.play_sound(music, volume=target_volume, looping=True)
            else:
                self.music_player = arcade.play_sound(music, volume=target_volume)

            self.current_music = music
            self.current_music_name = music_name
            self.music_loop = should_loop

            if fade_in_time > 0.0:
                self._fade_music_in(target_volume, fade_in_time)

            print(f"Started playing music: {music_name}")
            return True
        
        except Exception as e:
            print(f"Error playing music {music_name}: {e}")
            return False
        
    def stop_music(self, fade_out_time: float = 0.0):
        if not self.current_music:
            return
        
        if fade_out_time > 0.0:
            self._fade_out_music(fade_out_time)
        else:
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
        if self.music_player:
            try:
                print("Music paused (not supported by arcade)")
                #put something in here that does this later
            except Exception as e:
                print(f"Error pausing music: {e}")

    def resume_music(self):
        if self.music_player:
            try:
                print("Music resumed: Arcade doesn't support this right now")
            except Exception as e:
                print(f"Error rsuming music: {e}")

    def set_master_volume(self, volume: float):
        self.master_volume = max(0.0, min(1.0, volume))
        print(f"Master volume set to {self.master_volume:.2f}")

    def set_sfx_volume(self, volume: float):
        self.sfx_volume = max(0.0, min(1.0, volume))
        print(f"SFX volume set to {self.sfx_volume:.2f}")

    def set_music_volume(self, volume: float):
        self.music_volume = max(0.0, min(1.0, volume))
        if self.current_music and self.music_player:
            try:
                #arcade doesn't support, would have to restart music, do later
                pass
            except Exception as e:
                print(f"Error updating music volume: {e}")
        print(f"Music volume set to {self.music_volume:.2f}")

    def toggle_sound(self) -> bool:
        self.sound_enabled = not self.sound_enabled
        if not self.sound_enabled:
            self.stop_music()
        print(f"Sound {'enabled' if self.sound_enabled else 'disabled'}")
        return self.sound_enabled
    
    def _fade_music_in(self, target_volume: float, fade_time: float):
        if self.fade_active:
            return
        
        def fade_in():
            self.fade_active = True
            steps = int(fade_time * 20)  # 20 steps per second
            volume_step = target_volume / steps
            sleep_time = fade_time / steps

            for i in range(steps):
                if not self.fade_active or not self.music_player:
                    break
                time.sleep(sleep_time)
            
            self.fade_active = True

        self.fade_thread = threading.Thread(target=fade_in)

    def _fade_music_out(self, fade_time: float):
        if self.fade_active:
            return
        
        def fade_out():
            self.fade_active = True
            steps = int(fade_time * 20)   # 20 steps per second
            sleep_time = fade_time / steps

            for i in range(steps):
                if not self.fade_active or not self.music_player:
                    break
                time.sleep(sleep_time)

            if self.current_music:
                try:
                    if self.music_player:
                        self.music_player.delete()
                    self.current_music = None
                    self.current_music_name = None
                    self.music_player = None
                    self.music_loop = False
                except Exception as e:
                    print(f"Error in fade out: {e}")

            self.fade_active = False

        self.fade_thread = threading.Thread(target=fade_out)
        self.fade_thread.start()

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
            'master_volume': self.master_volume,
            'sfx_volume': self.sfx_volume,
            'music_volume': self.music_volume,
            'current_music': self.current_music_name,
            'music_looping': self.music_loop,
            'active_sounds': len(self.active_sounds),
            'fade_active': self.fade_active
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
            'udnerground': 'underground',
            'castle': 'castle',
            'water': 'underwater',
            'boss': 'boss'
        }

        music_name = music_mapping.get(level_type, 'overworld')
        self.play_music(music_name, fade_in_time=1.0)

_sound_manager = None

def get_sound_manager() -> SoundManager:
    global _sound_manager
    if _sound_manager is None:
        _sound_manager = SoundManager()
    return _sound_manager

def play_sound(sound_name: str, volume: Optional[float] = None, force: bool = False) -> bool:
    return get_sound_manager().play_sound(sound_name, volume, force)

def play_music(music_name: str, fade_in: float = 0.0) -> bool:
    return get_sound_manager().play_music(music_name, fade_in)

def stop_music(fade_out: float = 0.0):
    get_sound_manager().stop_music(fade_out)

def set_master_volume(volume: float):
    get_sound_manager().set_master_volume(volume)

def set_sfx_volume(volume: float):
    get_sound_manager().set_sfx_volume(volume)

def set_music_volume(volume: float):
    get_sound_manager().set_music_volume(volume)

def toggle_sound() -> bool:
    return get_sound_manager().toggle_sound()

def initialize_sound_manager(asset_loader):
    sound_manager = get_sound_manager()
    sound_manager.set_asset_loader(asset_loader)
    return sound_manager