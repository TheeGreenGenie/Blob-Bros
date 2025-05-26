#Display
import arcade
import time
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import settings

class HUD:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.score = 0
        self.lives = 3
        self.level_time = 0
        self.level_time_limit = 400
        self.level_name = "1-1"

        self.coins_collected = 0
        self.total_coins = 0
        self.enemies_defeated = 0
        self.total_enemies = 0

        self.margin = 20
        self.top_margin = 30
        self.font_size_large = 24
        self.font_size_medium = 18
        self.font_size_small = 14

        self.text_color = settings.WHITE
        self.score_color = settings.SCORE_COLOR
        self.lives_color = settings.LIVES_COLOR
        self.time_color = settings.TIMER_COLOR
        self.warning_color = (255, 100, 100)

        self.score_anmiation_timer = 0
        self.score_flash = False
        self.lives_flash = False
        self.lives_flash_timer = 0
        self.time_warning = False

        self.use_fast_text = not settings.SHOW_FPS

        self.layout = {}
        self.update_layout()

    def update_layout(self):
         self.layout = {
             'score_pos': (self.margin, self.screen_height - self.top_margin),
             'lives_pos': (self.margin, self.screen_height - self.top_margin - 35),
             'time_pos': (self.screen_width - 150, self.screen_height - self.top_margin),
             'level_pos': (self.screen_width // 2, self.screen_height - self.top_margin),

             'coins_pos': (self.margin, self.screen_height - 100),
             'enemies_pos': (self.margin, self.screen_height - 130),

             'fps_pos': (self.screen_width - 100, self.screen_height - 60),
             'debug_pos': (self.margin, 80),

             'message_pos': (self.screen_width // 2, self.screen_height - 100)

         }

    def update(self, delta_time, game_data):
        if 'score' in game_data:
            old_score = self.score
            self.score = game_data['score']

            if self.score > old_score:
                self.score_anmiation_timer = 0.5
                self.score_flash = True

        if 'lives' in game_data:
            old_lives = self.lives
            self.lives = game_data['lives']

            if self.lives != old_lives:
                self.lives_flash = True
                self.lives_flash_timer = 1.0

        if 'level_time' in game_data:
            self.level_time = game_data['level_time']

        if 'level_name' in game_data:
            self.level_name = game_data['level_name']

        if 'coins_collected' in game_data:
            self.coins_collected = game_data['coins_collected']
        if 'total_coins' in game_data:
            self.total_coins = game_data['total_coins']
        if 'enemies_defeated' in game_data:
            self.enemies_defeated = game_data['enemies_defeated']
        if 'total_enemies' in game_data:
            self.total_enemies = game_data['total_enemies']

        self._update_anmiations(delta_time)

        self._check_warnings()

    def _update_anmiations(self, delta_time):
        if self.score_anmiation_timer > 0:
            self.score_anmiation_timer -= delta_time
            if self.score_anmiation_timer <= 0:
                self.score_flash = False

        if self.lives_flash_timer > 0:
            self.lives_flash_timer -= delta_time
            self.lives_flash = (self.lives_flash_timer * 5) % 1 > 0.5
            if self.lives_flash_timer <= 0:
                self.lives_flash = False

    def _check_warnings(self):
        remaining_time = self.level_time_limit - self.level_time
        self.time_warning = remaining_time <= 100 and remaining_time > 0

    def draw(self):
        self._draw_main_info()
        self._draw_progress_info()

        if settings.SHOW_FPS:
            self._draw_performance_info()
        
        if settings.DEBUG_MODE:
            self._draw_debug_info()

    def _draw_main_info(self):
        score_color = self.score_color if not self.score_flash else self.warning_color
        self._draw_text(
            f"SCORE: {self.score:06d}",
            self.layout['score_pos'][0], self.layout['score_pos'][1],
            score_color, self.font_size_large
        )

        lives_color = self.lives_color if not self.lives_flash else self.warning_color
        lives_text = f"LIVES: {self.lives}"
        if self.lives == 1:
            lives_text += " ⚠"

        self._draw_text(
            lives_text,
            self.layout['lives_pos'][0], self.layout['lives_pos'][1],
            lives_color, self.font_size_large
        )

        remaining_time = max(0, self.level_time_limit - self.level_time)
        time_color = self.time_color if not self.time_warning else self.warning_color

        self._draw_text(
            f"TIME: {remaining_time:03d}",
            self.layout['time_pos'][0], self.layout['times_pos'][1],
            time_color, self.font_size_large
        )

        self._draw_text(
            f"WORLD {self.level_name}",
            self.layout['level_pos'][0], self.layout['level_pos'][1],
            self.text_color, self.font_size_medium,
            anchor_x='center'
        )

    def _draw_progress_info(self):
        coin_percentage = (self.coins_collected / max(1, self.total_coins)) * 100
        coin_text = f"COINS: {self.coins_collected}/{self.total_coins} ({coin_percentage:.0f})"

        self._draw_text(
            coin_text,
            self.layout['coins_pos'][0], self.layout['coins_pos'][1],
            (255, 215, 0), self.font_size_medium
        )

        self._draw_progress_bar(
            self.layout['coins_pos'][0] + 200, self.layout['coins_pos'][1] - 5,
            100, 10, coin_percentage, (255, 215, 0)
        )

        enemy_percentage = (self.enemies_defeated / max(1, self.total_enemies)) * 100
        enemy_text = f"ENEMIES: {self.enemies_defeated}/{self.total_enemies} ({enemy_percentage:.0f}%)"

        self._draw_text(
            enemy_text,
            self.layout['enemies_pos'][0], self.layout['enemies_pos'][1],
            (255, 100, 100), self.font_size_medium
        )

        self._draw_progress_bar(
            self.layout['enemies_pos'][0] + 200, self.layout['enemies_pos'][1] - 5,
            100, 10, enemy_percentage, (255, 100, 100)
        )

    