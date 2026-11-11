import pygame
import random
import math
import array

pygame.init()

WIDTH, HEIGHT = 800, 600
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("NEON BREAKER - THUNDERSTORM ULTIMATE")

clock = pygame.time.Clock()

font = pygame.font.Font(None, 27)
small_font = pygame.font.Font(None, 20)
big_font = pygame.font.Font(None, 75)
#COLORS
BLACK = (7, 9, 22)
WHITE = (255, 255, 255)
CYAN = (0, 220, 255)
BLUE = (40, 100, 255)
PURPLE = (160, 70, 255)
PINK = (255, 50, 150)
RED = (255, 60, 70)
ORANGE = (255, 130, 20)
GREEN = (50, 255, 150)
YELLOW = (255, 220, 50)
#POWER-UPS
MENU = "menu"
PLAYING = "playing"
PAUSED = "paused"
TRANSITION = "transition"
GAME_OVER = "game_over"
VICTORY = "victory"

POWER_COLORS = {
    "fire": ORANGE,
    "big": CYAN,
    "lightning": BLUE,
    "multi": PURPLE,
    "shield": GREEN,
    "laser": RED,
    "slow": YELLOW,
    "magnet": PINK
}

POWER_LABELS = {
    "fire": "F",
    "big": "B",
    "lightning": "L",
    "multi": "M",
    "shield": "S",
    "laser": "R",
    "slow": "T",
    "magnet": "G"
}

POWER_NAMES = {
    "fire": "FIREBALL",
    "big": "BIG PADDLE",
    "lightning": "LIGHTNING BALL",
    "multi": "MULTI BALL",
    "shield": "SHIELD",
    "laser": "LASER PADDLE",
    "slow": "SLOW MOTION",
    "magnet": "MAGNET PADDLE"
}
