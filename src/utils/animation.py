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

    def update(self, delta_time: float) -> bool:
        if not self.is_playing or self.is_finished or not self.frames:
            return False
        
        self.frame_time += delta_time
        frame_changed = False

        if self.frame_time >= self.frame_duration:
            frame_changed = True
            self.frame_time = 0.0

            if self.current_frame in self.frame_events:
                for callback in self.frame_events[self.current_frame]:
                    try:
                        callback()
                    except Exception as e:
                        print(f"Animation frame event error: {e}")

            self._advance_frame()

        return frame_changed
    
    def _advance_frame(self):
        if self.playback_mode == AnimationPlayback.LOOP:
            self.current_frame = (self.current_frame + 1) % len(self.frames)

        elif self.playback_mode == AnimationPlayback.ONCE:
            if self.current_frame < len(self.frames) - 1:
                self.current_frame += 1
            else:
                self.is_finished = True
                self._trigger_completion()

        elif self.playback_mode == AnimationPlayback.PING_PONG:
            if self.ping_pong_forward:
                self.current_frame += 1
                if self.current_frame >= len(self.frames) -1:
                    self.ping_pong_forward = False

            else:
                self.current_frame -= 1
                if self.current_frame <= 0:
                    self.ping_pong_forward = True

        elif self.playback_mode == AnimationPlayback.HOLD_LAST:
            if self.current_frame < len(self.frames) - 1:
                self.current_frame += 1
            else:
                self.is_finished = True
                self._trigger_completion()

    def _trigger_completion(self):
        for callback in self.on_complete_callbacks:
            try:
                callback()
            except Exception as e:
                print(f"Animation completion callback error: {e}")

    def get_current_texture(self) -> Optional[arcade.Texture]:
        if not self.frames or self.current_frame >= len(self.frames):
            return None
        return self.frames[self.current_frame]
    
    def restart(self):
        self.current_frame = 0
        self.frame_time = 0.0
        self.is_finished = False
        self.ping_pong_forward = True
        self.is_playing = True

    def pause(self):
        self.is_playing = False

    def resume(self):
        self.is_playing = True

    def set_frame(self, frame_index: int):
        if 0 <= frame_index < len(self.frames):
            self.current_frame = frame_index
            self.frame_time = 0.0

    def add_frame_event(self, frame_index: int, callback: Callable):
        if frame_index not in self.frame_events:
            self.frame_events[frame_index] = []
        self.frame_events[frame_index].append(callback)

    def add_completion_callback(self, callback: Callable):
        self.on_complete_callbacks.append(callback)

