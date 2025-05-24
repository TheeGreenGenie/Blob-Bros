#Settings and Constants
# ALL config values for the mario platform game

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
SCREEN_TITLE = "Mario-Style Platformer"
FPS = 60

GRAVITY = 0.8
PLAYER_JUMP_SPEED = 16
PLAYER_MOVEMENT_SPEED = 5
TERMINAL_VELOCITY = 20

TILE_SIZE = 32
TILE_SCALING = 1.0

PLAYER_START_X = 100
PLAYER_START_Y = 300
PLAYER_LIVES = 3
PLAYER_SIZE = 32

ENEMY_SPEED = 1
ENEMY_BOUNCE_BACK = True

COIN_VALUE = 100
COIN_SIZE = 24

CAMERA_SPEED = 5
LEVEL_END_X = 3000

JUMP_KEY = "SPACE"
LEFT_KEY = "LEFT"
RIGHT_KEY = "RIGHT"
PAUSE_KEY = "P"

ASSETS_PATH = "..\MarioGame\assets"
SPRITES_PATH = f"{ASSETS_PATH}/sprites"
SOUNDS_PATH = f"{ASSETS_PATH}/sounds"
LEVELS_PATH = "..\MarioGame\levels"

PLAYER_SPRITES = {
    'small': f"{SPRITES_PATH}/player/mario_small.png",
    'big': f"{SPRITES_PATH}/player/mario_big.png",
    'fire': f"{SPRITES_PATH}/player/mario_fire.png"
}

ENEMY_SPRITES = {
    'goomba': f"{SPRITES_PATH}/enemies/goomba.png",
    'koopa': f"{SPRITES_PATH}/enemies/koopa.png"
}

ITEM_SPRITES = {
    'coin': f"{SPRITES_PATH}/items/coin.png",
    'mushroom': f"{SPRITES_PATH}/items/mushroom.png",
    'fire_flower': f"{SPRITES_PATH}/items/fire_flower.png"
}

BLOCK_SPRITES = {
    'ground': f"{SPRITES_PATH}/blocks/ground.png",
    'brick': f"{SPRITES_PATH}/blocks/brick.png",
    'question': f"{SPRITES_PATH}/blocks/question.png",
    'pipe': f"{SPRITES_PATH}/blocks/pipe.png"
}

SOUND_FILES = {
    'jump': f"{SOUNDS_PATH}/sfx/jump.wav",
    'coin': f"{SOUNDS_PATH}/sfx/coin.wav",
    'powerup': f"{SOUNDS_PATH}/sfx/powerup.wav",
    'enemy_stomp': f"{SOUNDS_PATH}/sfx/enemy_stomp.wav",
    'game_over': f"{SOUNDS_PATH}/sfx/game_over.wav",
    'level_complete': f"{SOUNDS_PATH}/sfx/level_complete.wav"
}

MUSIC_FILES = {
    'overworld': f"{SOUNDS_PATH}/music/overworld.ogg",
    'underground': f"{SOUNDS_PATH}/music/underground.ogg"
}

SKY_BLUE = (135, 206, 235)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

SCORE_COLOR = WHITE
LIVES_COLOR = RED
TIMER_COLOR = YELLOW

DEBUG_MODE = True
SHOW_HITBOXES = False
SHOW_FPS = True
INVINCIBLE_MODE = False #For testing

DEFAULT_LEVEL_WIDTH = 100
DEFAULT_LEVEL_HEIGHT = 20
GROUND_HEIGHT = 3

ANIMATION_SPEED = 0.1
COIN_SPIN_SPEED = 0.15
ENEMY_WALK_SPEED = 0.2

SCORE_COIN = 100
SCORE_ENEMY_STOMP = 200
SCORE_LEVEL_COMPLETE = 1000
EXTRA_LIFE_SCORE = 10000

FRICTION = 0.8
AIR_RESISTANCE = 0.95
JUMP_BUFFER_TIME = 0.1
COYOTE_TIME = 0.1  #Seconds player can jump after leaving platform

GAME_STATES = {
    "MENU": 'menu',
    "PLAYING": 'playing',
    "PAUSED": 'paused',
    "GAME_OVER": 'game_over',
    "LEVEL_COMPLETE": 'level_complete'
}