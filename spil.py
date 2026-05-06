# Sonic-stil platformspil - demo med 1 stor bane
#
# Kontroller:
#   Venstre/Hoejre piletast - gaa
#   Op-pil eller mellemrum  - hop
#   Mellemrum               - start forfra naar spillet er slut
#
# Filer:
#   sounds/hop.wav   - lyd ved spring
#   sounds/auch.wav  - lyd naar man bliver ramt

import pgzrun
import pygame
from pygame import Rect

# ============================================================
# Konstanter
# ============================================================
WIDTH = 800
HEIGHT = 600
TITLE = "Sonic-demo"

WORLD_WIDTH = 2400        # Banen er bredere end skaermen - kameraet scroller
JORD_Y = 560

TYNGDEKRAFT = 0.6
SPRING_KRAFT = -13
LOEBE_FART = 4
MAX_FALD_FART = 16
USAARLIG_FRAMES = 60      # ca. 1 sekund efter at vaere blevet ramt

START_X = 50
START_Y = 470

# ============================================================
# Banen: jord-stykker (med pits imellem) + flydende platforme
# ============================================================
jord_stykker = [
    Rect(0,    JORD_Y, 700,                40),
    Rect(850,  JORD_Y, 650,                40),
    Rect(1640, JORD_Y, WORLD_WIDTH - 1640, 40),
]

flydende_platforme = [
    Rect(180,  460, 140, 20),
    Rect(360,  360, 140, 20),
    Rect(560,  470, 130, 20),
    Rect(940,  390, 160, 20),
    Rect(1200, 460, 140, 20),
    Rect(1700, 380, 200, 20),
    Rect(2050, 460, 140, 20),
]

alle_platforme = jord_stykker + flydende_platforme
maal = Rect(2350, JORD_Y - 60, 30, 60)

# ============================================================
# Skyer (parallax baggrund)
# ============================================================
skyer = [
    {"x": 100,  "y": 80,  "r": 40},
    {"x": 350,  "y": 130, "r": 50},
    {"x": 600,  "y": 60,  "r": 30},
    {"x": 900,  "y": 110, "r": 45},
    {"x": 1200, "y": 70,  "r": 55},
    {"x": 1500, "y": 140, "r": 35},
    {"x": 1800, "y": 90,  "r": 50},
    {"x": 2100, "y": 60,  "r": 40},
]

# ============================================================
# Svampe - flere typer med forskellig farve og fart
# ============================================================
def lav_svamp(x_start, farve, vx, min_x, max_x):
    return {
        "rect":     Rect(x_start, JORD_Y - 35, 40, 35),
        "start_x":  x_start,
        "vx":       vx,
        "vx_init":  vx,
        "min_x":    min_x,
        "max_x":    max_x,
        "farve":    farve,
    }

svampe = [
    lav_svamp(250,  "roed",   1,   200, 600),
    lav_svamp(1050, "lilla",  2,   900, 1450),
    lav_svamp(1800, "brun",   1.5, 1700, 2000),
]

# ============================================================
# Spil-tilstand (aendrer sig mens man spiller)
# ============================================================
spiller = Rect(START_X, START_Y, 40, 50)
spiller_vy = 0
paa_jorden = False
spiller_facing = 1        # 1 = kigger mod hoejre, -1 = mod venstre
liv = 3
usaarlig_timer = 0
spil_slut = False
vandt = False
camera_x = 0

# Sprites bygges paa foerste frame (efter pgzero har startet pygame)
sprite_sonic_hoejre = None
sprite_sonic_venstre = None
sprite_svampe = {}

# ============================================================
# Sprite-tegning (koerer kun en gang, ved opstart)
# ============================================================
def lav_sonic(vendt_til_hoejre):
    surf = pygame.Surface((40, 50), pygame.SRCALPHA)

    spike = (20, 50, 160)
    if vendt_til_hoejre:
        # spikes peger bagud (til venstre)
        pygame.draw.polygon(surf, spike, [(8, 12), (0, 18), (10, 22)])
        pygame.draw.polygon(surf, spike, [(6, 22), (0, 28), (10, 32)])
    else:
        pygame.draw.polygon(surf, spike, [(32, 12), (40, 18), (30, 22)])
        pygame.draw.polygon(surf, spike, [(34, 22), (40, 28), (30, 32)])

    # Krop - blaa cirkel
    pygame.draw.circle(surf, (40, 90, 220), (20, 22), 16)

    # Ansigt - lys hudfarve
    if vendt_til_hoejre:
        pygame.draw.circle(surf, (255, 210, 170), (28, 26), 7)
        eye_x, pupil_x = 26, 28
    else:
        pygame.draw.circle(surf, (255, 210, 170), (12, 26), 7)
        eye_x, pupil_x = 14, 12

    # Stort hvidt oeje med groen pupil
    pygame.draw.ellipse(surf, (255, 255, 255), Rect(eye_x - 4, 14, 10, 12))
    pygame.draw.circle(surf, (0, 110, 0), (pupil_x, 22), 3)

    # Roede sko nederst
    pygame.draw.ellipse(surf, (220, 30, 30), Rect(6,  40, 13, 9))
    pygame.draw.ellipse(surf, (220, 30, 30), Rect(21, 40, 13, 9))
    pygame.draw.line(surf, (255, 255, 255), (6, 44),  (19, 44), 2)
    pygame.draw.line(surf, (255, 255, 255), (21, 44), (34, 44), 2)

    return surf


def lav_svamp_sprite(hat_farve, prik_farve):
    surf = pygame.Surface((40, 35), pygame.SRCALPHA)

    # Stilk - cremehvid
    pygame.draw.rect(surf, (245, 230, 200), Rect(13, 18, 14, 17))
    pygame.draw.rect(surf, (200, 180, 140), Rect(13, 18, 14, 2))

    # Hat - farvet ellipse
    pygame.draw.ellipse(surf, hat_farve, Rect(2, 2, 36, 22))

    # Prikker paa hatten
    pygame.draw.circle(surf, prik_farve, (12, 10), 3)
    pygame.draw.circle(surf, prik_farve, (22, 8),  4)
    pygame.draw.circle(surf, prik_farve, (30, 12), 3)

    # Smaa oejne under hatten
    pygame.draw.circle(surf, (0, 0, 0), (17, 26), 2)
    pygame.draw.circle(surf, (0, 0, 0), (23, 26), 2)

    return surf


def byg_sprites():
    global sprite_sonic_hoejre, sprite_sonic_venstre, sprite_svampe
    sprite_sonic_hoejre  = lav_sonic(True)
    sprite_sonic_venstre = lav_sonic(False)
    sprite_svampe = {
        "roed":  lav_svamp_sprite((220, 30, 30),  (255, 255, 255)),
        "lilla": lav_svamp_sprite((140, 50, 180), (255, 240, 100)),
        "brun":  lav_svamp_sprite((140, 90, 50),  (240, 220, 180)),
    }

# ============================================================
# Spil-funktioner
# ============================================================
def nulstil_spil():
    global spiller_vy, paa_jorden, spiller_facing, liv, usaarlig_timer
    global spil_slut, vandt, camera_x
    spiller.x = START_X
    spiller.y = START_Y
    spiller_vy = 0
    paa_jorden = False
    spiller_facing = 1
    liv = 3
    usaarlig_timer = 0
    spil_slut = False
    vandt = False
    camera_x = 0
    for s in svampe:
        s["rect"].x = s["start_x"]
        s["vx"] = s["vx_init"]


def respawn_spiller():
    global spiller_vy, paa_jorden, usaarlig_timer
    spiller.x = START_X
    spiller.y = START_Y
    spiller_vy = 0
    paa_jorden = False
    usaarlig_timer = USAARLIG_FRAMES


def mist_liv():
    global liv, spil_slut
    sounds.auch.play()
    liv = liv - 1
    if liv <= 0:
        spil_slut = True
    else:
        respawn_spiller()


def update():
    global spiller_vy, paa_jorden, spiller_facing
    global usaarlig_timer, spil_slut, vandt, camera_x

    if spil_slut:
        if keyboard.space:
            nulstil_spil()
        return

    # 1. Laes input
    vx = 0
    if keyboard.left:
        vx = -LOEBE_FART
        spiller_facing = -1
    if keyboard.right:
        vx = LOEBE_FART
        spiller_facing = 1

    if (keyboard.up or keyboard.space) and paa_jorden:
        spiller_vy = SPRING_KRAFT
        paa_jorden = False
        sounds.hop.play()

    # 2. Tyngdekraft
    spiller_vy = spiller_vy + TYNGDEKRAFT
    if spiller_vy > MAX_FALD_FART:
        spiller_vy = MAX_FALD_FART

    # 3. Vandret bevaegelse + kollision
    spiller.x = spiller.x + vx
    for p in alle_platforme:
        if spiller.colliderect(p):
            if vx > 0:
                spiller.right = p.left
            elif vx < 0:
                spiller.left = p.right
    if spiller.left < 0:
        spiller.left = 0
    if spiller.right > WORLD_WIDTH:
        spiller.right = WORLD_WIDTH

    # 4. Lodret bevaegelse + kollision
    spiller.y = spiller.y + spiller_vy
    paa_jorden = False
    for p in alle_platforme:
        if spiller.colliderect(p):
            if spiller_vy > 0:
                spiller.bottom = p.top
                spiller_vy = 0
                paa_jorden = True
            elif spiller_vy < 0:
                spiller.top = p.bottom
                spiller_vy = 0

    # Faldt ned i en pit?
    if spiller.top > HEIGHT:
        mist_liv()
        return

    # 5. Flyt svampene
    for s in svampe:
        s["rect"].x = s["rect"].x + s["vx"]
        if s["rect"].left < s["min_x"]:
            s["rect"].left = s["min_x"]
            s["vx"] = -s["vx"]
        if s["rect"].right > s["max_x"]:
            s["rect"].right = s["max_x"]
            s["vx"] = -s["vx"]

    # 6. Tjek svamp-kollision
    if usaarlig_timer > 0:
        usaarlig_timer = usaarlig_timer - 1
    else:
        for s in svampe:
            if spiller.colliderect(s["rect"]):
                mist_liv()
                return

    # 7. Tjek maal
    if spiller.colliderect(maal):
        vandt = True
        spil_slut = True

    # 8. Kameraet foelger spilleren (med graenser)
    nyt_kamera = spiller.centerx - WIDTH // 3
    if nyt_kamera < 0:
        nyt_kamera = 0
    if nyt_kamera > WORLD_WIDTH - WIDTH:
        nyt_kamera = WORLD_WIDTH - WIDTH
    camera_x = nyt_kamera


def draw():
    if sprite_sonic_hoejre is None:
        byg_sprites()

    # Baggrund - himmelblaa
    screen.fill((110, 180, 240))

    # Skyer (parallax - bevaeger sig langsommere end verden)
    for sky in skyer:
        sx = int(sky["x"] - camera_x * 0.3)
        sy = sky["y"]
        if sx < -150 or sx > WIDTH + 150:
            continue
        r = sky["r"]
        screen.draw.filled_circle((sx, sy), r, "white")
        screen.draw.filled_circle((sx + int(r * 0.7), sy + int(r * 0.2)), int(r * 0.8), "white")
        screen.draw.filled_circle((sx - int(r * 0.7), sy + int(r * 0.2)), int(r * 0.7), "white")

    # Jord-stykker - groen graes paa toppen, brun jord nedenunder
    graes        = (60, 180, 70)
    graes_top    = (35, 130, 45)
    jord_brun    = (130, 90, 50)

    for p in jord_stykker:
        x = p.x - camera_x
        if x + p.width < 0 or x > WIDTH:
            continue
        screen.draw.filled_rect(Rect(x, p.y + 8, p.width, p.height - 8), jord_brun)
        screen.draw.filled_rect(Rect(x, p.y,     p.width, 8),            graes)
        screen.draw.filled_rect(Rect(x, p.y,     p.width, 3),            graes_top)

    # Flydende platforme - ren groen
    for p in flydende_platforme:
        x = p.x - camera_x
        if x + p.width < 0 or x > WIDTH:
            continue
        screen.draw.filled_rect(Rect(x, p.y, p.width, p.height), graes)
        screen.draw.filled_rect(Rect(x, p.y, p.width, 3),        graes_top)

    # Maal-flag
    mx = maal.x - camera_x
    if -50 < mx < WIDTH:
        screen.draw.filled_rect(Rect(mx, maal.y - 20, 4, maal.height + 20), (140, 100, 60))
        screen.draw.filled_rect(Rect(mx + 4, maal.y - 20, 26, 18), "yellow")

    # Svampe
    for s in svampe:
        sx = s["rect"].x - camera_x
        if -100 < sx < WIDTH + 100:
            screen.blit(sprite_svampe[s["farve"]], (sx, s["rect"].y))

    # Spilleren - blink hvert 5. frame mens man er usaarlig
    blink = (usaarlig_timer // 5) % 2 == 0
    if usaarlig_timer == 0 or blink:
        if spiller_facing == 1:
            sprite = sprite_sonic_hoejre
        else:
            sprite = sprite_sonic_venstre
        screen.blit(sprite, (spiller.x - camera_x, spiller.y))

    # HUD
    screen.draw.text("Liv: " + str(liv), topleft=(10, 10), fontsize=30, color="white")

    # Slut-skaerm
    if spil_slut:
        if vandt:
            besked = "DU VANDT!"
        else:
            besked = "GAME OVER"
        screen.draw.text(besked,
                         center=(WIDTH // 2, HEIGHT // 2 - 30),
                         fontsize=80, color="white")
        screen.draw.text("Tryk MELLEMRUM for at spille igen",
                         center=(WIDTH // 2, HEIGHT // 2 + 40),
                         fontsize=30, color="white")


pgzrun.go()
