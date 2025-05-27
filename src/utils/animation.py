#Animations
import arcade
import time
from typing import Dict, List, Optional, Tuple, Any, Callable
from enum import Enum
from pathlib import Path
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import settings

class AnimationState(Enum):

    IDLE = 'idle'
    WALKING = 'walking'
    RUNNING = 'running'
    JUMPING = 'jumping'
    FALLING = 'falling'
    CROUCHING = 'crouching'
    DYING = 'dying'
    TRANSFORMING = 'transforming'

    PATROL = 'patrol'
    ALERT = 'alert'
    ATTACKING = 'attacking'
    STUNNED = 'stunned'
    DEAD = 'dead'

    SPINNING = 'spinning'
    COLLECTED = 'collected'

    QUESTION_IDLE = 'question_idle'
    QUESTION_HIT = 'question_hit'
    QUESTION_EMPTY = 'question_empty'
    BLOCK_BREAK = 'block_break'

class AnimationPlayback(Enum):

    LOOP = 'loop'
    ONCE = 'once'
    PING_PONG = 'ping_pong'
    HOLD_LAST = 'hold_last'

class Animation:

    def __init__(self, name: str, frames: List[arcade.Texture], frame_duration: float = 0.1, playback_mode: AnimationPlayback = AnimationPlayback.LOOP):
        self.name = name
        self.frames = frames
        self.frame_duration = frame_duration
        self.playback_mode = playback_mode

        self.current_frame = 0
        self.frame_time = 0.0
        self.is_playing = True
        self.is_finished = False
        self.ping_pong_forward = True

        self.frame_events: Dict[int, List[Callable]] = {}
        self.on_complete_callbacks: List[Callable] = []

    