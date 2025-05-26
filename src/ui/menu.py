#Menu classes (pages)
import arcade
import math
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import settings

class MenuItem:
    
    def __init__(self, text, action=None, enabled=True, submenu=None):
        self.text = text
        self.action = action
        self.enabled = enabled
        self.submenu = submenu

        self.selected = False
        self.hover_time = 0
        self.flash_timer = 0

