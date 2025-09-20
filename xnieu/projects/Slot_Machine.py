import pygame
import random
import sys

WIDTH, HEIGHT = 600, 600
FPS = 60
EMOJI_SIZE = 150
BOUNCE_HEIGHT = 80
BOUNCE_COUNT = 3
BOUNCE_SPEED = 15
STAGGER_DELAY = 5
BG_COLOR = (10, 10, 60)
PATTERN_COLOR = (20, 20, 80)
TEXT_COLOR = (255, 255, 255)
ROLL_EMOJIS = ["🍒","💎","💲","🍀","🍉","⭐","💰","7️⃣","💵","🪙","🍐"]

JACKPOT = ["7️⃣", "7️⃣", "7️⃣"]
MONEYBAGS = ["💰", "💰", "💰"]

pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bouncy Slot Machine")
clock = pygame.time.Clock()

font = pygame.font.SysFont("Segoe UI Emoji", EMOJI_SIZE, bold=True)
small_font = pygame.font.SysFont("Arial", 18)
button_font = pygame.font.SysFont("Arial", 36, bold=True)

try:
    roll_sound = pygame.mixer.Sound("roll.wav")
except:
    roll_sound = None

try:
    bg_music = pygame.mixer.Sound("slotsbg.wav")
    bg_channel = bg_music.play(-1)
    bg_channel.set_volume(0.25)
except:
    bg_channel = None

bg_muted = False

num_reels = 3
emojis = [random.choice(ROLL_EMOJIS) for _ in range(num_reels)]
targets = emojis.copy()
bounce_offsets = [0 for _ in range(num_reels)]
bounce_directions = [1 for _ in range(num_reels)]
bouncing = False
bounces_done = [0 for _ in range(num_reels)]
stagger_counters = [i*STAGGER_DELAY for i in range(num_reels)]
roll_counter = 0
winning_type = None

confetti_particles = []

pattern_offset_x = 0
pattern_offset_y = 0
pattern_speed = 0.5
pattern_spacing = 40

button_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT - 110, 200, 70)

class Confetti:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-2,2)
        self.vy = random.uniform(-5,-1)
        self.size = random.randint(4,8)
        self.color = [random.randint(200,255), random.randint(200,255), random.randint(0,255)]
        self.life = 60
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.2
        self.life -= 1
    def draw(self, surf):
        pygame.draw.rect(surf, self.color, (self.x,self.y,self.size,self.size))

def draw_text():
    lines = [
        "press x to close",
        "press m to mute",
        "press r/enter/space to roll"
    ]
    for i, line in enumerate(lines):
        surf = small_font.render(line, True, TEXT_COLOR)
        screen.blit(surf, (10, 10 + i*20))
    counter_surf = small_font.render(f"rolls: {roll_counter}", True, TEXT_COLOR)
    screen.blit(counter_surf, (WIDTH - counter_surf.get_width() - 10, 10))

def pick_emojis():
    rnd = random.random()
    if rnd < 0.005:
        return JACKPOT.copy()
    elif rnd < 0.015:
        return MONEYBAGS.copy()
    else:
        return [random.choice(ROLL_EMOJIS) for _ in range(num_reels)]

def start_bounce():
    global bouncing, targets, bounces_done, stagger_counters, roll_counter, winning_type
    bouncing = True
    targets[:] = pick_emojis()
    for i in range(num_reels):
        bounces_done[i] = 0
        stagger_counters[i] = i * STAGGER_DELAY
    winning_type = None
    if roll_sound:
        roll_sound.play()
    roll_counter += 1

def update_bounce():
    global bouncing, emojis, winning_type, confetti_particles
    all_done = True
    for i in range(num_reels):
        if stagger_counters[i] > 0:
            stagger_counters[i] -= 1
            all_done = False
            continue
        if bounces_done[i] < BOUNCE_COUNT:
            bounce_offsets[i] += BOUNCE_SPEED * bounce_directions[i]
            if bounce_offsets[i] > BOUNCE_HEIGHT:
                bounce_offsets[i] = BOUNCE_HEIGHT
                bounce_directions[i] *= -1
                emojis[i] = random.choice(ROLL_EMOJIS)
            elif bounce_offsets[i] < 0:
                bounce_offsets[i] = 0
                bounce_directions[i] *= -1
                bounces_done[i] += 1
                emojis[i] = random.choice(ROLL_EMOJIS)
            all_done = False
    if all_done and not winning_type:
        if emojis == JACKPOT:
            winning_type = "jackpot"
            for i in range(50):
                x = (i%3 + 1)*(WIDTH//4)
                confetti_particles.append(Confetti(x, HEIGHT//2))
        elif emojis == MONEYBAGS:
            winning_type = "moneybags"
            for i in range(30):
                x = (i%3 + 1)*(WIDTH//4)
                confetti_particles.append(Confetti(x, HEIGHT//2))
        elif len(set(emojis))==1:
            winning_type = "normal"

def draw_emojis():
    spacing = WIDTH // (num_reels + 1)
    for i in range(num_reels):
        x = (i+1) * spacing
        y = HEIGHT//2 - bounce_offsets[i]//2
        if winning_type == "normal" and len(set(emojis))==1:
            glow_alpha = random.randint(50,120)
            glow_surf = pygame.Surface((EMOJI_SIZE+20, EMOJI_SIZE+20), pygame.SRCALPHA)
            pygame.draw.ellipse(glow_surf, (50,50,255, glow_alpha), glow_surf.get_rect())
            screen.blit(glow_surf, glow_surf.get_rect(center=(x,y)))
        elif winning_type == "moneybags" and emojis==MONEYBAGS:
            glow_alpha = random.randint(150,200)
            glow_surf = pygame.Surface((EMOJI_SIZE+40, EMOJI_SIZE+40), pygame.SRCALPHA)
            pygame.draw.ellipse(glow_surf, (255,255,0, glow_alpha), glow_surf.get_rect())
            screen.blit(glow_surf, glow_surf.get_rect(center=(x,y)))
        elif winning_type == "jackpot" and emojis==JACKPOT:
            glow_alpha = random.randint(200,255)
            glow_surf = pygame.Surface((EMOJI_SIZE+60, EMOJI_SIZE+60), pygame.SRCALPHA)
            pygame.draw.ellipse(glow_surf, (255,255,0, glow_alpha), glow_surf.get_rect())
            screen.blit(glow_surf, glow_surf.get_rect(center=(x,y)))

        emoji_surf = font.render(emojis[i], True, (255,255,255))
        rect = emoji_surf.get_rect(center=(x, y))
        screen.blit(emoji_surf, rect)

def draw_button():
    pygame.draw.rect(screen, (30,30,80), button_rect, border_radius=15)
    surf = button_font.render("roll", True, (255,255,255))
    rect = surf.get_rect(center=button_rect.center)
    screen.blit(surf, rect)

def draw_pattern():
    global pattern_offset_x, pattern_offset_y
    for i in range(0, WIDTH, pattern_spacing):
        pygame.draw.line(screen, PATTERN_COLOR,
                         ((i + pattern_offset_x) % WIDTH, 0),
                         ((i + pattern_offset_x) % WIDTH, HEIGHT), 1)
    for j in range(0, HEIGHT, pattern_spacing):
        pygame.draw.line(screen, PATTERN_COLOR,
                         (0, (j + pattern_offset_y) % HEIGHT),
                         (WIDTH, (j + pattern_offset_y) % HEIGHT), 1)
    pattern_offset_x += pattern_speed
    pattern_offset_y += pattern_speed/2

running = True
while running:
    screen.fill(BG_COLOR)
    draw_pattern()
    draw_text()
    draw_emojis()
    draw_button()

    for conf in confetti_particles[:]:
        conf.update()
        conf.draw(screen)
        if conf.life <= 0:
            confetti_particles.remove(conf)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_x:
                running = False
            elif event.key == pygame.K_m:
                bg_muted = not bg_muted
                if bg_channel:
                    bg_channel.set_volume(0 if bg_muted else 0.25)
            elif event.key in [pygame.K_r, pygame.K_RETURN, pygame.K_SPACE]:
                start_bounce()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if button_rect.collidepoint(event.pos):
                start_bounce()

    if bouncing:
        update_bounce()

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
