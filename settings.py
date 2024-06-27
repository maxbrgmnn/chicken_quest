import pygame
import sys
from pygame.math import Vector2 as vector

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
TILE_SIZE = 64
ANIMATION_SPEED = 6

PLAYER_SPEED = 200

# gravity reset
PLAYER_GRAVITY = 50
def set_player_gravity(value):
    global PLAYER_GRAVITY
    PLAYER_GRAVITY = value

def get_player_gravity():
    return PLAYER_GRAVITY





#layers
Z_LAYERS = {
    'Behind':-1,
    'BG': 0,
    'layer1': 1,
    'layer2': 2,
    'layer3': 3


}
