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

#BACKGROUND
stars = []
for _ in range(110):
    stars.append([
        random.randint(0, WIDTH),
        random.randint(0, HEIGHT),
        random.uniform(0.3, 1.5),
        random.randint(1, 2)
    ])

def draw_background():
    screen.fill(BLACK)
    for star in stars:
        star[1] += star[2]
        if star[1] > HEIGHT:
            star[1] = 0
            star[0] = random.randint(0, WIDTH)
        brightness = random.randint(80, 180)
        pygame.draw.circle(
            screen,
            (brightness // 3, brightness // 2, brightness),
            (int(star[0]), int(star[1])),
            star[3]
        )
    for x in range(0, WIDTH, 50):
        pygame.draw.line(
            screen, (14, 19, 38),
            (x, 55), (x, HEIGHT), 1
        )
    for y in range(55, HEIGHT, 50):
        pygame.draw.line(
            screen, (14, 19, 38),
            (0, y), (WIDTH, y), 1
        )

