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

class AnimationController:

    def __init__(self, sprite: arcade.Sprite):
        self.sprite = sprite
        self.animations: Dict[str, Animation] = {}
        self.current_animation_name = None
        self.current_animation = None
        self.previous_animation_name = None

        self.transition_duration = 0.0
        self.transition_time = 0.0
        self.transitioning = False

        self.state_history: List[Tuple[str, float]] = []
        self.max_history = 10

        self.mirrored = False
        self.auto_mirror = True

    def add_anmiation(self, animation: Animation):
        self.animations[animation.name] = animation

        if self.current_animation is None:
            self.set_animation(animation.name)

    def set_animation(self, animation_name: str, force_restart: bool = False) -> bool:
        if animation_name not in self.animations:
            if settings.DEBUG_MODE:
                print(f"Animation '{animation_name}' not found")
            return False
        
        if self.current_animation_name == animation_name and not force_restart:
            return True
        
        self.previous_animation_name == self.current_animation_name

        current_time = time.time()
        self.state_history.append((animation_name, current_time))
        if len(self.state_history) > self.max_history:
            self.state_history.pop(0)

        self.current_animation_name = animation_name
        self.current_animation = self.animations[animation_name]

        if force_restart or self.previous_animation_name != animation_name:
            self.current_animation.restart()

        self._update_sprite_texture()

        return True
    
    def update(self, delta_time: float):
        if not self.current_animation:
            return
        
        if self.auto_mirror and hasattr(self.sprite, 'change_x'):
            if self.sprite.change_x > 0:
                self.mirrored = False
            elif self.sprite.change_x < 0:
                self.mirrored = True

        frame_changed = self.current_animation.update(delta_time)

        if frame_changed:
            self._update_sprite_texture()

    def _update_sprite_texture(self):
        if not self.current_animation:
            return
        
        texture = self.current_animation.get_current_texture()
        if texture:
            if self.mirrored:
                texture = texture.texture.flip_horizontally()

            self.sprite.texture = texture

    def get_current_animation_name(self) -> Optional[str]:
        return self.current_animation_name
    
    def is_animation_finished(self) -> bool:
        return self.current_animation.is_finished if self.current_animation else True
    
    def pause_current_animation(self):
        if self.current_animation:
            self.current_animation.pause()

    def resume_current_animation(self):
        if self.current_animation:
            self.current_animation.resume()

    def set_mirrored(self, mirrored: bool):
        if self.mirrored != mirrored:
            self.mirrored = mirrored
            self._update_sprite_texture()

class Animationmanager:

    def __init__(self, asset_loader=None):
        self.asset_loader = asset_loader
        self.controllers = Dict[arcade.Sprite, AnimationController] = {}

        self.animation_definitions = self._create_animation_definitions()

        self.global_effects: List[Callable] = []

    