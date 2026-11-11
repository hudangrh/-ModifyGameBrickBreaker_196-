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

#GLOW AND TEKS
def draw_glow(surface, color, position, radius):
    glow = pygame.Surface(
        (radius * 4, radius * 4),
        pygame.SRCALPHA
    )
    for i in range(4, 0, -1):
        alpha = 15 + (5 - i) * 15
        pygame.draw.circle(
            glow,
            (*color, alpha),
            (radius * 2, radius * 2),
            radius * i // 2
        )
    surface.blit(
        glow,
        (
            int(position[0] - radius * 2),
            int(position[1] - radius * 2)
        )
    )

def draw_text(text, font_object, color, x, y, center=True):
    image = font_object.render(text, True, color)
    rect = image.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    screen.blit(image, rect)

#PARTICLES
particles = []

class Particle:
    def __init__(self, x, y, color):
        self.x = float(x)
        self.y = float(y)
        self.vx = random.uniform(-4, 4)
        self.vy = random.uniform(-4, 4)
        self.size = random.randint(2, 5)
        self.life = random.randint(20, 40)
        self.color = color

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        self.size *= 0.96

    def draw(self):
        if self.life > 0:
            pygame.draw.circle(
                screen,
                self.color,
                (int(self.x), int(self.y)),
                max(1, int(self.size))
            )

def create_explosion(x, y, color, amount=18):
    for _ in range(amount):
        particles.append(
            Particle(x, y, color)
        )

#SOUND EFFECTS
thunder_sound = None
last_thunder_sound = 0

def create_thunder_sound():
    global thunder_sound
    try:
        mixer_info = pygame.mixer.get_init()
        if mixer_info is None:
            return
        sample_rate, audio_format, channels = mixer_info
        if audio_format != -16:
            return
        samples = array.array("h")
        duration = 1.1
        total_samples = int(sample_rate * duration)
        low_noise = 0.0
        for i in range(total_samples):
            t = i / sample_rate
            low_noise += random.uniform(-1, 1) * 0.045
            low_noise *= 0.97
            envelope = math.exp(-t * 2.8)
            crack = (
                random.uniform(-1, 1)
                * math.exp(-t * 35)
                * 0.65
            )
            value = (low_noise * 0.8 + crack) * envelope
            sample = max(
                -32767,
                min(32767, int(value * 32767))
            )
            for _ in range(channels):
                samples.append(sample)
        thunder_sound = pygame.mixer.Sound(
            buffer=samples.tobytes()
        )
        thunder_sound.set_volume(0.5)

    except (pygame.error, OSError, ValueError):
        thunder_sound = None

#LIGHTNING EFFECT
thunder_effects = []
shockwaves = []

flash_until = 0
flash_color = CYAN

class ThunderBolt:
    def __init__(self, start, end):
        self.life = random.randint(9, 15)
        self.max_life = self.life

        self.color = random.choice([
            CYAN, WHITE, BLUE, PURPLE
        ])

        x1, y1 = start
        x2, y2 = end

        self.points = []
        segments = 12

        for i in range(segments + 1):
            progress = i / segments
            x = x1 + (x2 - x1) * progress
            y = y1 + (y2 - y1) * progress
            if i not in (0, segments):
                x += random.randint(-28, 28)
            self.points.append((int(x), int(y)))

        self.branches = []
        for _ in range(3):
            index = random.randint(2, segments - 2)

            bx, by = self.points[index]

            self.branches.append([
                (bx, by),
                (
                    bx + random.randint(-35, 35),
                    by + random.randint(10, 35)
                ),
                (
                    bx + random.randint(-55, 55),
                    by + random.randint(35, 65)
                )
            ])
    def update(self):
        self.life -= 1
    def draw(self):
        if self.life <= 0:
            return
        brightness = self.life / self.max_life
        color = tuple(
            int(c * brightness)
            for c in self.color
        )
        pygame.draw.lines(
            screen, (30, 70, 180),
            False, self.points, 9
        )
        pygame.draw.lines(
            screen, color,
            False, self.points, 4
        )
        pygame.draw.lines(
            screen, WHITE,
            False, self.points, 1
        )
        for branch in self.branches:
            pygame.draw.lines(
                screen, color,
                False, branch, 2
            )

class Shockwave:
    def __init__(self, x, y, color=CYAN):
        self.x = int(x)
        self.y = int(y)
        self.radius = 5
        self.life = 22
        self.color = color
    def update(self):
        self.radius += 5
        self.life -= 1
    def draw(self):
        if self.life <= 0:
            return
        color = tuple(
            int(c * self.life / 22)
            for c in self.color
        )
        pygame.draw.circle(
            screen,
            color,
            (self.x, self.y),
            self.radius,
            3
        )

def trigger_thunder(x, y, strong=False):
    global flash_until, flash_color
    global last_thunder_sound

    x = int(x)
    y = int(y)

    count = 3 if strong else 1
    for _ in range(count):
        start_x = x + random.randint(-100, 100)

        thunder_effects.append(
            ThunderBolt(
                (
                    start_x,
                    max(55, y - random.randint(100, 190))
                ),
                (
                    x + random.randint(-15, 15),
                    y
                )
            )
        )

    shockwaves.append(
        Shockwave(
            x, y,
            ORANGE if strong else CYAN
        )
    )
    flash_until = pygame.time.get_ticks() + (
        110 if strong else 55
    )
    flash_color = PURPLE if strong else CYAN
    current_time = pygame.time.get_ticks()
    if (
        thunder_sound is not None
        and current_time - last_thunder_sound > 250
    ):
        thunder_sound.play()
        last_thunder_sound = current_time

def draw_thunderstorm(now):
    for bolt in thunder_effects[:]:
        bolt.update()
        bolt.draw()
        if bolt.life <= 0:
            thunder_effects.remove(bolt)
    for wave in shockwaves[:]:
        wave.update()
        wave.draw()
        if wave.life <= 0:
            shockwaves.remove(wave)
    if now < flash_until:
        flash_surface = pygame.Surface(
            (WIDTH, HEIGHT),
            pygame.SRCALPHA
        )
        flash_surface.fill((*flash_color, 35))
        screen.blit(flash_surface, (0, 0))

