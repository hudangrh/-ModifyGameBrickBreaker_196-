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

class Paddle:
    def __init__(self):
        self.normal_width = 120
        self.width = self.normal_width

        self.height = 15
        self.x = WIDTH // 2 - self.width // 2
        self.y = HEIGHT - 65

        self.speed = 9

        self.big_timer = 0
        self.laser_timer = 0
        self.magnet_timer = 0

        self.laser_cooldown = 0

        self.rect = pygame.Rect(
            self.x, self.y,
            self.width, self.height
        )

    def update(self, direction, now):
        if self.big_timer and now >= self.big_timer:
            self.big_timer = 0
            self.width = self.normal_width

        if self.laser_timer and now >= self.laser_timer:
            self.laser_timer = 0

        if self.magnet_timer and now >= self.magnet_timer:
            self.magnet_timer = 0

        self.x += direction * self.speed

        self.x = max(
            0,
            min(WIDTH - self.width, self.x)
        )

        self.rect.update(
            int(self.x),
            self.y,
            self.width,
            self.height
        )

    def activate_big(self, now):
        self.width = 200
        self.big_timer = now + 10000

        self.x = max(
            0,
            min(WIDTH - self.width, self.x)
        )

    def activate_laser(self, now):
        self.laser_timer = now + 10000

    def activate_magnet(self, now):
        self.magnet_timer = now + 10000

    def has_magnet(self, now):
        return now < self.magnet_timer

    def has_laser(self, now):
        return now < self.laser_timer

    def draw(self, now):
        pulse = math.sin(now * 0.005)

        color = (
            0,
            int(180 + 75 * pulse),
            255
        )

        if self.has_laser(now):
            color = RED

        if self.has_magnet(now):
            color = PINK

        draw_glow(
            screen, color,
            self.rect.center, 35
        )

        pygame.draw.rect(
            screen,
            color,
            self.rect,
            border_radius=10
        )

        pygame.draw.rect(
            screen,
            WHITE,
            self.rect,
            2,
            border_radius=10
        )


# ==================================================
# BALL
# ==================================================

class Ball:
    def __init__(self, x=None, y=None, dx=None, dy=None):
        self.radius = 9
        self.speed = 6

        self.x = float(x if x is not None else WIDTH // 2)
        self.y = float(y if y is not None else HEIGHT - 100)

        self.dx = dx if dx is not None else random.choice([-0.5, 0.5])
        self.dy = dy if dy is not None else -1

        self.fire_timer = 0
        self.lightning_timer = 0

        self.attached = False
        self.trail = []

        self.rect = pygame.Rect(0, 0, 0, 0)
        self.update_rect()

    def update_rect(self):
        self.rect = pygame.Rect(
            int(self.x - self.radius),
            int(self.y - self.radius),
            self.radius * 2,
            self.radius * 2
        )

    def activate_fire(self, now):
        self.fire_timer = now + 8000

    def activate_lightning(self, now):
        self.lightning_timer = now + 10000

    def is_fire(self, now):
        return now < self.fire_timer

    def is_lightning(self, now):
        return now < self.lightning_timer

    def launch(self):
        if self.attached:
            self.attached = False
            self.dx = random.choice([-0.5, 0.5])
            self.dy = -1

    def update(self, now, paddle, slow_active):
        if self.attached:
            self.x = paddle.rect.centerx
            self.y = paddle.y - self.radius - 1
            self.update_rect()
            return False

        self.trail.append((self.x, self.y))

        if len(self.trail) > 12:
            self.trail.pop(0)

        length = math.sqrt(
            self.dx ** 2 + self.dy ** 2
        )

        speed = self.speed

        if slow_active:
            speed *= 0.55

        if length > 0:
            self.x += self.dx / length * speed
            self.y += self.dy / length * speed

        if self.x <= self.radius:
            self.x = self.radius
            self.dx = abs(self.dx)

        if self.x >= WIDTH - self.radius:
            self.x = WIDTH - self.radius
            self.dx = -abs(self.dx)

        if self.y <= 55 + self.radius:
            self.y = 55 + self.radius
            self.dy = abs(self.dy)

        self.update_rect()

        return self.y - self.radius > HEIGHT

    def bounce(self):
        self.dy = -abs(self.dy)

    def draw(self, now):
        fire = self.is_fire(now)
        lightning = self.is_lightning(now)

        if fire:
            color = ORANGE
        elif lightning:
            color = CYAN
        else:
            color = BLUE

        for i, pos in enumerate(self.trail):
            radius = max(
                1,
                int(self.radius * (i + 1) / len(self.trail))
            )

            trail_color = (
                (255, 100, 10)
                if fire else
                (20, 140, 255)
                if lightning else
                (15, 90, 190)
            )

            pygame.draw.circle(
                screen,
                trail_color,
                (int(pos[0]), int(pos[1])),
                radius
            )

        draw_glow(
            screen, color,
            (self.x, self.y), 24
        )

        if fire:
            for _ in range(2):
                px = self.x + random.randint(-5, 5)
                py = self.y + random.randint(-5, 5)

                pygame.draw.circle(
                    screen,
                    random.choice([RED, ORANGE, YELLOW]),
                    (int(px), int(py)),
                    random.randint(2, 5)
                )

        if lightning:
            for i in range(4):
                angle = now * 0.012 + i * math.pi / 2

                x1 = self.x + math.cos(angle) * 10
                y1 = self.y + math.sin(angle) * 10

                x2 = self.x + math.cos(angle + 0.5) * 25
                y2 = self.y + math.sin(angle + 0.5) * 25

                pygame.draw.lines(
                    screen,
                    CYAN,
                    False,
                    [
                        (int(x1), int(y1)),
                        (int(x2), int(y2))
                    ],
                    2
                )

        pygame.draw.circle(
            screen,
            WHITE,
            (int(self.x), int(self.y)),
            self.radius
        )


# ==================================================
# BLOCK
# ==================================================

class Block:
    def __init__(self, x, y, width, height, color):
        self.rect = pygame.Rect(
            x, y, width, height
        )

        self.color = color
        self.health = 2 if color == WHITE else 1

    def hit(self, fire):
        if fire:
            self.health = 0
        else:
            self.health -= 1

    def draw(self, now):
        if self.health <= 0:
            return

        pulse = math.sin(
            now * 0.004 + self.rect.x * 0.02
        )

        brightness = 0.8 + pulse * 0.15

        color = tuple(
            min(255, int(c * brightness))
            for c in self.color
        )

        draw_glow(
            screen, color,
            self.rect.center, 14
        )

        pygame.draw.rect(
            screen,
            color,
            self.rect,
            border_radius=5
        )

        pygame.draw.rect(
            screen,
            WHITE,
            self.rect,
            1,
            border_radius=5
        )

        if self.health > 1:
            draw_text(
                "2", small_font, WHITE,
                self.rect.centerx,
                self.rect.centery
            )


# ==================================================
# BOSS
# ==================================================

class Boss:
    def __init__(self):
        self.width = 190
        self.height = 45

        self.x = WIDTH // 2 - self.width // 2
        self.y = 75

        self.dx = 3

        self.max_hp = 30
        self.hp = self.max_hp

        self.rect = pygame.Rect(
            self.x, self.y,
            self.width, self.height
        )

    def update(self):
        self.x += self.dx

        if self.x <= 10:
            self.x = 10
            self.dx = abs(self.dx)

        if self.x + self.width >= WIDTH - 10:
            self.x = WIDTH - 10 - self.width
            self.dx = -abs(self.dx)

        self.rect.x = int(self.x)

    def hit(self, fire, lightning):
        damage = 1

        if fire:
            damage += 2

        if lightning:
            damage += 1

        self.hp = max(0, self.hp - damage)

    def draw(self, now):
        pulse = math.sin(now * 0.008)

        color = (
            255,
            int(40 + 30 * pulse),
            120
        )

        draw_glow(
            screen, color,
            self.rect.center, 55
        )

        pygame.draw.rect(
            screen,
            (80, 15, 65),
            self.rect,
            border_radius=12
        )

        pygame.draw.rect(
            screen,
            color,
            self.rect,
            3,
            border_radius=12
        )

        draw_text(
            "BOSS",
            font,
            WHITE,
            self.rect.centerx,
            self.rect.centery
        )

        bar_width = 300
        bar_x = (WIDTH - bar_width) // 2

        pygame.draw.rect(
            screen,
            (50, 20, 35),
            (bar_x, 28, bar_width, 13),
            border_radius=6
        )

        current_width = int(
            bar_width * self.hp / self.max_hp
        )

        if current_width > 0:
            pygame.draw.rect(
                screen,
                RED,
                (bar_x, 28, current_width, 13),
                border_radius=6
            )

        draw_text(
            f"BOSS HP: {self.hp}/{self.max_hp}",
            small_font,
            WHITE,
            WIDTH // 2,
            13
        )


# ==================================================
# POWER-UP
# ==================================================

class PowerUp:
    def __init__(self, x, y, kind):
        self.x = float(x)
        self.y = float(y)

        self.kind = kind
        self.speed = 3
        self.radius = 14

        self.rect = pygame.Rect(
            int(x - self.radius),
            int(y - self.radius),
            self.radius * 2,
            self.radius * 2
        )

    def update(self):
        self.y += self.speed

        self.rect.center = (
            int(self.x),
            int(self.y)
        )

    def draw(self, now):
        color = POWER_COLORS[self.kind]

        pulse = math.sin(now * 0.01)
        radius = int(self.radius + pulse * 2)

        draw_glow(
            screen, color,
            (self.x, self.y), 24
        )

        pygame.draw.circle(
            screen,
            color,
            (int(self.x), int(self.y)),
            radius
        )

        pygame.draw.circle(
            screen,
            WHITE,
            (int(self.x), int(self.y)),
            radius,
            2
        )

        draw_text(
            POWER_LABELS[self.kind],
            small_font,
            WHITE,
            int(self.x),
            int(self.y)
        )


# ==================================================
# LASER
# ==================================================

lasers = []


class Laser:
    def __init__(self, x, y):
        self.rect = pygame.Rect(
            int(x - 3),
            int(y - 15),
            6,
            18
        )

        self.speed = 10

    def update(self):
        self.rect.y -= self.speed

    def draw(self):
        draw_glow(
            screen,
            RED,
            self.rect.center,
            12
        )

        pygame.draw.rect(
            screen,
            RED,
            self.rect,
            border_radius=3
        )


# ==================================================
# CREATE LEVEL
# ==================================================

def create_blocks(level):
    blocks = []

    colors = [
        CYAN, PURPLE, PINK, GREEN, YELLOW
    ]

    block_width = 65
    block_height = 23
    gap = 10

    columns = 9

    rows = min(3 + level // 2, 7)

    total_width = (
        columns * block_width +
        (columns - 1) * gap
    )

    start_x = (WIDTH - total_width) // 2

    for row in range(rows):
        for col in range(columns):
            x = start_x + col * (block_width + gap)
            y = 120 + row * (block_height + gap)

            blocks.append(
                Block(
                    x, y,
                    block_width,
                    block_height,
                    random.choice(colors)
                )
            )

    return blocks


# ==================================================
# BALL AND PADDLE COLLISION
# ==================================================

def handle_ball_paddle(ball, paddle, now):
    if ball.attached:
        return

    if (
        ball.rect.colliderect(paddle.rect)
        and ball.dy > 0
    ):
        ball.y = paddle.y - ball.radius
        ball.update_rect()

        if paddle.has_magnet(now):
            ball.attached = True
            ball.x = paddle.rect.centerx
            ball.y = paddle.y - ball.radius - 1
            ball.update_rect()
            return

        offset = (
            ball.x - paddle.rect.centerx
        ) / (paddle.width / 2)

        ball.dx = max(-0.9, min(0.9, offset))

        if abs(ball.dx) < 0.12:
            ball.dx = random.choice([-0.15, 0.15])

        ball.dy = -abs(ball.dy)


# ==================================================
# LIGHTNING CHAIN ATTACK
# ==================================================

def lightning_chain(x, y, blocks):
    nearby = []

    for block in blocks:
        distance = math.hypot(
            block.rect.centerx - x,
            block.rect.centery - y
        )

        if distance < 115:
            nearby.append(block)

    nearby.sort(
        key=lambda b: math.hypot(
            b.rect.centerx - x,
            b.rect.centery - y
        )
    )

    destroyed = []

    for block in nearby[:3]:
        block.health = 0

        destroyed.append(block)

        create_explosion(
            block.rect.centerx,
            block.rect.centery,
            CYAN,
            10
        )

        trigger_thunder(
            block.rect.centerx,
            block.rect.centery
        )

    return destroyed


# ==================================================
# HUD
# ==================================================

def draw_hud(score, lives, level, balls, paddle, now,
             slow_timer, shield_timer):

    pygame.draw.rect(
        screen,
        (12, 18, 40),
        (0, 0, WIDTH, 55)
    )

    pygame.draw.line(
        screen,
        CYAN,
        (0, 55),
        (WIDTH, 55),
        2
    )

    draw_text(
        f"SCORE: {score}",
        font, CYAN, 90, 27
    )

    draw_text(
        f"LIVES: {lives}",
        font, PINK, WIDTH // 2 - 100, 27
    )

    draw_text(
        f"LEVEL: {level}",
        font, GREEN, WIDTH - 95, 27
    )

    active = []

    for ball in balls:
        if ball.is_fire(now):
            active.append("FIRE")

        if ball.is_lightning(now):
            active.append("LIGHTNING")

    if paddle.big_timer > now:
        active.append("BIG PADDLE")

    if paddle.laser_timer > now:
        active.append("LASER")

    if paddle.magnet_timer > now:
        active.append("MAGNET")

    if slow_timer > now:
        active.append("SLOW MOTION")

    if shield_timer > now:
        active.append("SHIELD")

    active = list(dict.fromkeys(active))

    if active:
        draw_text(
            "ACTIVE: " + " | ".join(active),
            small_font,
            WHITE,
            WIDTH // 2,
            78
        )


# ==================================================
# OVERLAY
# ==================================================

def draw_overlay(title, subtitle, alpha=175):
    overlay = pygame.Surface(
        (WIDTH, HEIGHT),
        pygame.SRCALPHA
    )

    overlay.fill((0, 0, 0, alpha))
    screen.blit(overlay, (0, 0))

    draw_text(
        title,
        big_font,
        CYAN,
        WIDTH // 2,
        HEIGHT // 2 - 35
    )

    draw_text(
        subtitle,
        font,
        WHITE,
        WIDTH // 2,
        HEIGHT // 2 + 30
    )


# ==================================================
# MAIN GAME
# ==================================================

def main():
    global particles
    global thunder_effects, shockwaves
    global lasers

    create_thunder_sound()

    state = MENU

    score = 0
    lives = 3
    level = 1

    paddle = Paddle()
    balls = [Ball()]

    blocks = create_blocks(level)
    boss = None

    powerups = []

    slow_timer = 0
    shield_timer = 0

    transition_start = 0
    transition_duration = 1400

    pause_started = 0

    running = True

    def reset_game():
        nonlocal score, lives, level
        nonlocal paddle, balls, blocks, boss
        nonlocal powerups, slow_timer, shield_timer

        score = 0
        lives = 3
        level = 1

        paddle = Paddle()
        balls = [Ball()]

        blocks = create_blocks(level)

        boss = None
        powerups = []

        slow_timer = 0
        shield_timer = 0

        particles.clear()
        thunder_effects.clear()
        shockwaves.clear()
        lasers.clear()

    def start_level():
        nonlocal blocks, boss, powerups

        blocks = create_blocks(level)
        powerups = []

        if level % 5 == 0:
            boss = Boss()
        else:
            boss = None

    def next_level(now):
        nonlocal level, state, transition_start
        nonlocal balls, slow_timer, shield_timer

        level += 1

        for ball in balls:
            ball.speed += 0.4

        balls = [Ball()]

        slow_timer = 0
        shield_timer = 0

        transition_start = now
        state = TRANSITION

    def resume_game(now):
        nonlocal state, pause_started
        nonlocal slow_timer, shield_timer

        paused_duration = now - pause_started

        if slow_timer > 0:
            slow_timer += paused_duration

        if shield_timer > 0:
            shield_timer += paused_duration

        for ball in balls:
            if ball.fire_timer > 0:
                ball.fire_timer += paused_duration

            if ball.lightning_timer > 0:
                ball.lightning_timer += paused_duration

        for timer_name in ("big_timer", "laser_timer", "magnet_timer"):
            timer_value = getattr(paddle, timer_name)

            if timer_value > 0:
                setattr(
                    paddle,
                    timer_name,
                    timer_value + paused_duration
                )

        state = PLAYING

    def apply_powerup(kind, now):
        nonlocal balls, slow_timer, shield_timer

        if kind == "fire":
            for ball in balls:
                ball.activate_fire(now)

        elif kind == "big":
            paddle.activate_big(now)

        elif kind == "lightning":
            for ball in balls:
                ball.activate_lightning(now)

        elif kind == "multi":
            new_balls = []

            for ball in balls:
                if ball.attached:
                    continue

                for direction in (-0.65, 0.65):
                    new_ball = Ball(
                        ball.x,
                        ball.y,
                        ball.dx + direction,
                        ball.dy
                    )

                    new_ball.speed = ball.speed
                    new_ball.fire_timer = ball.fire_timer
                    new_ball.lightning_timer = ball.lightning_timer

                    new_balls.append(new_ball)

            balls.extend(new_balls)

            # Limit the total number of balls
            balls = balls[:9]

        elif kind == "shield":
            shield_timer = now + 15000

        elif kind == "laser":
            paddle.activate_laser(now)

        elif kind == "slow":
            slow_timer = now + 10000

        elif kind == "magnet":
            paddle.activate_magnet(now)

        trigger_thunder(
            paddle.rect.centerx,
            paddle.y,
            strong=True
        )

        create_explosion(
            paddle.rect.centerx,
            paddle.y,
            POWER_COLORS[kind],
            25
        )

    while running:
        clock.tick(FPS)

        now = pygame.time.get_ticks()

        # ======================================
        # EVENTS
        # ======================================

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    if state == PAUSED:
                        resume_game(now)

                    elif state == PLAYING:
                        state = PAUSED
                        pause_started = now

                    elif state == MENU:
                        running = False

                if event.key == pygame.K_p:
                    if state == PLAYING:
                        state = PAUSED
                        pause_started = now

                    elif state == PAUSED:
                        resume_game(now)

                if event.key == pygame.K_SPACE:

                    if state in (MENU, GAME_OVER, VICTORY):
                        reset_game()
                        state = PLAYING

                    elif state == TRANSITION:
                        start_level()
                        state = PLAYING

                    elif state == PLAYING:
                        for ball in balls:
                            ball.launch()

        if not running:
            break

        # ======================================
        # GAME UPDATE
        # ======================================

        if state == PLAYING:

            keys = pygame.key.get_pressed()

            direction = (
                int(keys[pygame.K_RIGHT]) -
                int(keys[pygame.K_LEFT])
            )

            paddle.update(direction, now)

            slow_active = now < slow_timer

            # BALL UPDATE
            lost_balls = []

            for ball in balls:
                if ball.update(now, paddle, slow_active):
                    lost_balls.append(ball)

            # Shield protects the bottom of the arena
            if now < shield_timer:
                for ball in lost_balls:
                    ball.y = HEIGHT - 35
                    ball.dy = -abs(ball.dy)
                    ball.update_rect()

                lost_balls.clear()

            for ball in lost_balls:
                if ball in balls:
                    balls.remove(ball)

            # Lose a life only when all balls are gone
            if not balls:
                lives -= 1

                if lives <= 0:
                    state = GAME_OVER
                else:
                    balls = [Ball()]

            # PADDLE COLLISION
            for ball in balls:
                handle_ball_paddle(
                    ball,
                    paddle,
                    now
                )

            # LASER FIRING
            if paddle.has_laser(now):

                if now >= paddle.laser_cooldown:
                    lasers.append(
                        Laser(
                            paddle.rect.centerx - 25,
                            paddle.y
                        )
                    )

                    lasers.append(
                        Laser(
                            paddle.rect.centerx + 25,
                            paddle.y
                        )
                    )

                    paddle.laser_cooldown = now + 400

            # LASER UPDATE AND COLLISION
            for laser in lasers[:]:
                laser.update()

                if laser.rect.bottom < 55:
                    lasers.remove(laser)
                    continue

                hit_something = False

                for block in blocks[:]:
                    if laser.rect.colliderect(block.rect):
                        block.health = 0

                        blocks.remove(block)
                        score += 10

                        create_explosion(
                            block.rect.centerx,
                            block.rect.centery,
                            RED
                        )

                        trigger_thunder(
                            block.rect.centerx,
                            block.rect.centery
                        )

                        hit_something = True
                        break

                if (
                    not hit_something
                    and boss is not None
                    and laser.rect.colliderect(boss.rect)
                ):
                    boss.hp = max(0, boss.hp - 1)
                    hit_something = True

                if hit_something and laser in lasers:
                    lasers.remove(laser)

            # BLOCK COLLISION
            for ball in balls:

                for block in blocks[:]:

                    if ball.rect.colliderect(block.rect):

                        fire = ball.is_fire(now)
                        lightning = ball.is_lightning(now)

                        block.hit(fire)

                        if not fire:
                            ball.bounce()

                        if block.health <= 0:

                            if block in blocks:
                                blocks.remove(block)

                            score += 10

                            create_explosion(
                                block.rect.centerx,
                                block.rect.centery,
                                block.color
                            )

                            trigger_thunder(
                                block.rect.centerx,
                                block.rect.centery,
                                strong=fire or lightning
                            )

                            if lightning:
                                chained = lightning_chain(
                                    block.rect.centerx,
                                    block.rect.centery,
                                    blocks
                                )

                                for chained_block in chained:
                                    if chained_block in blocks:
                                        blocks.remove(chained_block)
                                        score += 10

                            # Random power-up drop
                            if random.random() < 0.22:

                                kind = random.choice(
                                    list(POWER_NAMES.keys())
                                )

                                powerups.append(
                                    PowerUp(
                                        block.rect.centerx,
                                        block.rect.centery,
                                        kind
                                    )
                                )

                        break

            # BOSS UPDATE
            if boss is not None:

                boss.update()

                for ball in balls:

                    if ball.rect.colliderect(boss.rect):

                        fire = ball.is_fire(now)
                        lightning = ball.is_lightning(now)

                        boss.hit(fire, lightning)

                        trigger_thunder(
                            boss.rect.centerx,
                            boss.rect.centery,
                            strong=True
                        )

                        create_explosion(
                            ball.x,
                            boss.rect.bottom,
                            ORANGE if fire else PURPLE,
                            15
                        )

                        # Push ball below boss
                        ball.y = boss.rect.bottom + ball.radius
                        ball.dy = abs(ball.dy)
                        ball.update_rect()

                        if boss.hp <= 0:
                            create_explosion(
                                boss.rect.centerx,
                                boss.rect.centery,
                                PINK,
                                70
                            )

                            trigger_thunder(
                                boss.rect.centerx,
                                boss.rect.centery,
                                strong=True
                            )

                            score += 200
                            boss = None
                            break

            # POWER-UP UPDATE
            for powerup in powerups[:]:

                powerup.update()

                if powerup.rect.colliderect(paddle.rect):

                    apply_powerup(
                        powerup.kind,
                        now
                    )

                    powerups.remove(powerup)

                elif powerup.y > HEIGHT:
                    powerups.remove(powerup)

            # PARTICLES
            for particle in particles[:]:

                particle.update()

                if particle.life <= 0:
                    particles.remove(particle)

            # LEVEL COMPLETE
            if not blocks and boss is None:
                next_level(now)

        # ======================================
        # TRANSITION
        # ======================================

        elif state == TRANSITION:

            elapsed = now - transition_start

            if elapsed >= transition_duration:
                start_level()
                state = PLAYING

        # ======================================
        # DRAW BACKGROUND
        # ======================================

        draw_background()

        # ======================================
        # DRAW GAME
        # ======================================

        if state in (PLAYING, PAUSED, TRANSITION):

            for block in blocks:
                block.draw(now)

            if boss is not None:
                boss.draw(now)

            for powerup in powerups:
                powerup.draw(now)

            for laser in lasers:
                laser.draw()

            for particle in particles:
                particle.draw()

            for ball in balls:
                ball.draw(now)

            paddle.draw(now)

            # SHIELD VISUAL
            if now < shield_timer:
                pygame.draw.line(
                    screen,
                    GREEN,
                    (30, HEIGHT - 25),
                    (WIDTH - 30, HEIGHT - 25),
                    5
                )

                draw_glow(
                    screen,
                    GREEN,
                    (WIDTH // 2, HEIGHT - 25),
                    30
                )

            draw_hud(
                score,
                lives,
                level,
                balls,
                paddle,
                now,
                slow_timer,
                shield_timer
            )

        # ======================================
        # MENU
        # ======================================

        if state == MENU:

            draw_overlay(
                "NEON BREAKER",
                "PRESS SPACE TO START | ESC TO QUIT"
            )

            draw_text(
                "P = PAUSE",
                small_font,
                CYAN,
                WIDTH // 2,
                HEIGHT // 2 + 85
            )

        # ======================================
        # PAUSE
        # ======================================

        elif state == PAUSED:

            draw_overlay(
                "PAUSED",
                "PRESS P OR ESC TO RESUME"
            )

            draw_text(
                "YOUR GAME IS PAUSED",
                small_font,
                CYAN,
                WIDTH // 2,
                HEIGHT // 2 + 80
            )

        # ======================================
        # TRANSITION
        # ======================================

        elif state == TRANSITION:

            elapsed = now - transition_start

            progress = min(
                1,
                elapsed / transition_duration
            )

            alpha = int(
                220 * abs(2 * progress - 1)
            )

            draw_overlay(
                f"LEVEL {level}",
                "GET READY FOR THE NEXT CHALLENGE!",
                alpha
            )

        # ======================================
        # GAME OVER
        # ======================================

        elif state == GAME_OVER:

            draw_overlay(
                "GAME OVER",
                f"FINAL SCORE: {score} | PRESS SPACE TO RESTART"
            )

        # ======================================
        # VICTORY
        # ======================================

        elif state == VICTORY:

            draw_overlay(
                "VICTORY!",
                f"FINAL SCORE: {score} | PRESS SPACE TO PLAY AGAIN"
            )

        # ======================================
        # THUNDER EFFECTS
        # ======================================

        if state in (PLAYING, PAUSED, TRANSITION):
            draw_thunderstorm(now)

        pygame.display.flip()

    pygame.quit()


# ==================================================
# RUN GAME
# ==================================================

if __name__ == "__main__":
    main()
