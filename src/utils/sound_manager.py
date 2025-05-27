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