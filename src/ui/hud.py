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

    