#Settings and Constants
# ALL config values for the mario platform game

SCREEN_WIDTH = 1024
SCRREEN_HEIGHT = 768
SCREEN_TITLE = "Mario-Style Platformer"
FPS = 60

GRAVITY = 0.8
PLAYER_JUMP_SPEED = -16
PLAYER_MOVEMENT_SPEED = 5
TERMINAL_VELOCITY = 20

TILE_SIZE = 32
TILE_SCALING = 1.0

PLAYER_START_X = 100
PLAYER_START_Y = 200
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

ASSETS_PATH = "Mario_Case (Not Started)\MarioGame\assets"
SPRITES_PATH = f"{ASSETS_PATH}/sprites"
SOUNDS_PATH = f"{ASSETS_PATH}/sounds"
LEVELS_PATH = "Mario_Case (Not Started)\MarioGame\levels"

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