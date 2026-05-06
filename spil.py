# Sonic-stil platformspil med 3 baner, svampe, spoegelser og bosskamp
#
# Bane 1: Skoven        - kun svampe
# Bane 2: Spoegelses-grotten - spoegelser + nogle svampe
# Bane 3: Skildpadde-bossen  - bosskamp uden scrolling
#
# Kontroller:
#   I menuen:               L = LET, S = SVAER
#   Mens man spiller:       Venstre/Hoejre piletast = gaa
#                           Op-pil eller mellemrum  = hop
#                           Hop oven paa monstre for at slaa dem ihjel
#   Naar spillet er slut:   MELLEMRUM = spil igen, M = tilbage til menu

import pgzrun
import pygame
import math
from pygame import Rect

# ============================================================
# Konstanter
# ============================================================
WIDTH = 800
HEIGHT = 600
TITLE = "Sonic-demo"

JORD_Y = 560
TYNGDEKRAFT = 0.6
SPRING_KRAFT = -13
LOEBE_FART = 4
MAX_FALD_FART = 16
USAARLIG_FRAMES = 60       # ca. 1 sekund efter at vaere blevet ramt
RESPAWN_FRAMES = 300       # 5 sekunder ved 60 fps
SQUASH_FRAMES = 30         # halvt sekund flad svamp/fadende spoegelse
STOMP_BOUNCE = 0.7         # bounce-styrke efter stomp
BOSS_INVULN_FRAMES = 60    # boss er kortvarigt usaarlig efter et hit
BANE_SKIFT_FRAMES = 120    # 2 sek "Bane fuldfoert!"-besked
PIXEL_SIZE = 4             # C64-pixelering

START_X = 50
START_Y = 470

# ============================================================
# Spil-tilstand (aendrer sig mens man spiller)
# ============================================================
spil_tilstand = "menu"     # "menu", "spiller", "bane_skift", "tabt", "vandt_alt"
svaerhed = "let"
bane_nr = 1
bane_skift_timer = 0

spiller = Rect(START_X, START_Y, 40, 50)
spiller_vy = 0
paa_jorden = False
spiller_facing = 1
liv = 3
usaarlig_timer = 0
camera_x = 0

# Banens elementer (fyldes naar man starter en bane)
jord_stykker = []
flydende_platforme = []
alle_platforme = []
skyer = []
svampe = []
spoegelser = []
boss = None
maal_x = None
world_width = 800
bane_navn = ""

# Sprites bygges paa foerste frame
sprite_sonic_hoejre = None
sprite_sonic_venstre = None
sprite_svampe = {}
sprite_svampe_flat = {}
sprite_spoegelse = None
sprite_boss = None

# ============================================================
# Sprite-tegning
# ============================================================
def lav_sonic(vendt_til_hoejre):
    surf = pygame.Surface((40, 50), pygame.SRCALPHA)
    spike = (20, 50, 160)
    if vendt_til_hoejre:
        pygame.draw.polygon(surf, spike, [(8, 12), (0, 18), (10, 22)])
        pygame.draw.polygon(surf, spike, [(6, 22), (0, 28), (10, 32)])
    else:
        pygame.draw.polygon(surf, spike, [(32, 12), (40, 18), (30, 22)])
        pygame.draw.polygon(surf, spike, [(34, 22), (40, 28), (30, 32)])
    pygame.draw.circle(surf, (40, 90, 220), (20, 22), 16)
    if vendt_til_hoejre:
        pygame.draw.circle(surf, (255, 210, 170), (28, 26), 7)
        eye_x, pupil_x = 26, 28
    else:
        pygame.draw.circle(surf, (255, 210, 170), (12, 26), 7)
        eye_x, pupil_x = 14, 12
    pygame.draw.ellipse(surf, (255, 255, 255), Rect(eye_x - 4, 14, 10, 12))
    pygame.draw.circle(surf, (0, 110, 0), (pupil_x, 22), 3)
    pygame.draw.ellipse(surf, (220, 30, 30), Rect(6,  40, 13, 9))
    pygame.draw.ellipse(surf, (220, 30, 30), Rect(21, 40, 13, 9))
    pygame.draw.line(surf, (255, 255, 255), (6,  44), (19, 44), 2)
    pygame.draw.line(surf, (255, 255, 255), (21, 44), (34, 44), 2)
    return surf


def lav_svamp_sprite(hat_farve, prik_farve):
    surf = pygame.Surface((40, 35), pygame.SRCALPHA)
    pygame.draw.rect(surf, (245, 230, 200), Rect(13, 18, 14, 17))
    pygame.draw.rect(surf, (200, 180, 140), Rect(13, 18, 14, 2))
    pygame.draw.ellipse(surf, hat_farve, Rect(2, 2, 36, 22))
    pygame.draw.circle(surf, prik_farve, (12, 10), 3)
    pygame.draw.circle(surf, prik_farve, (22, 8),  4)
    pygame.draw.circle(surf, prik_farve, (30, 12), 3)
    pygame.draw.circle(surf, (0, 0, 0), (17, 26), 2)
    pygame.draw.circle(surf, (0, 0, 0), (23, 26), 2)
    return surf


def lav_svamp_flat_sprite(hat_farve, prik_farve):
    """Den flade version af en svamp - den der vises lige efter et stomp."""
    surf = pygame.Surface((40, 8), pygame.SRCALPHA)
    pygame.draw.ellipse(surf, hat_farve, Rect(0, 0, 40, 8))
    pygame.draw.circle(surf, prik_farve, (12, 3), 2)
    pygame.draw.circle(surf, prik_farve, (22, 2), 3)
    pygame.draw.circle(surf, prik_farve, (30, 4), 2)
    # X-oejne (slaaet ihjel)
    pygame.draw.line(surf, (0, 0, 0), (17, 4), (20, 7), 1)
    pygame.draw.line(surf, (0, 0, 0), (20, 4), (17, 7), 1)
    return surf


def lav_spoegelse_sprite():
    surf = pygame.Surface((40, 40), pygame.SRCALPHA)
    krop = (245, 245, 250)
    pygame.draw.ellipse(surf, krop, Rect(2, 0, 36, 28))
    pygame.draw.rect(surf, krop, Rect(2, 12, 36, 22))
    # Boelget bund
    pygame.draw.polygon(surf, krop,
                        [(2, 34), (8, 30), (14, 36), (20, 30),
                         (26, 36), (32, 30), (38, 34), (38, 40), (2, 40)])
    # Hvide oejne med bla pupil
    pygame.draw.circle(surf, (255, 255, 255), (14, 17), 5)
    pygame.draw.circle(surf, (255, 255, 255), (26, 17), 5)
    pygame.draw.circle(surf, (40, 40, 220), (15, 18), 2)
    pygame.draw.circle(surf, (40, 40, 220), (27, 18), 2)
    return surf


def lav_boss_sprite():
    surf = pygame.Surface((100, 80), pygame.SRCALPHA)
    # Krop (gul mave)
    pygame.draw.ellipse(surf, (255, 220, 100), Rect(15, 35, 70, 40))
    # Skal (groen)
    pygame.draw.ellipse(surf, (50, 140, 50), Rect(15, 5, 70, 50))
    # Skal-pigge (hvide)
    for px in [30, 50, 70]:
        pygame.draw.polygon(surf, (255, 255, 255),
                            [(px - 6, 18), (px, 5), (px + 6, 18)])
    # Hoved
    pygame.draw.circle(surf, (255, 220, 100), (32, 32), 15)
    # Horn
    pygame.draw.polygon(surf, (200, 80, 80), [(20, 20), (24, 12), (27, 24)])
    pygame.draw.polygon(surf, (200, 80, 80), [(38, 20), (42, 12), (44, 24)])
    # Onde roede oejne
    pygame.draw.circle(surf, (255, 255, 255), (28, 30), 4)
    pygame.draw.circle(surf, (255, 255, 255), (38, 30), 4)
    pygame.draw.circle(surf, (220, 0, 0), (28, 30), 2)
    pygame.draw.circle(surf, (220, 0, 0), (38, 30), 2)
    # Tand
    pygame.draw.polygon(surf, (255, 255, 255), [(28, 40), (32, 46), (36, 40)])
    return surf


def byg_sprites():
    global sprite_sonic_hoejre, sprite_sonic_venstre
    global sprite_svampe, sprite_svampe_flat, sprite_spoegelse, sprite_boss

    sprite_sonic_hoejre  = lav_sonic(True)
    sprite_sonic_venstre = lav_sonic(False)

    farver = {
        "roed":  ((220, 30, 30),  (255, 255, 255)),
        "lilla": ((140, 50, 180), (255, 240, 100)),
        "brun":  ((140, 90, 50),  (240, 220, 180)),
    }
    for navn, (hat, prik) in farver.items():
        sprite_svampe[navn] = lav_svamp_sprite(hat, prik)
        sprite_svampe_flat[navn] = lav_svamp_flat_sprite(hat, prik)

    sprite_spoegelse = lav_spoegelse_sprite()
    sprite_boss = lav_boss_sprite()

# ============================================================
# Bane-data og monster-konstruktoerer
# ============================================================
def lav_svamp(x_start, farve, vx, min_x, max_x):
    return {
        "rect":          Rect(x_start, JORD_Y - 35, 40, 35),
        "start_x":       x_start,
        "vx":            vx,
        "vx_init":       vx,
        "min_x":         min_x,
        "max_x":         max_x,
        "farve":         farve,
        "levende":       True,
        "respawn_timer": 0,
        "squash_timer":  0,
    }


def lav_spoegelse(x, y, vx, min_x, max_x, bob_speed=0.04):
    return {
        "rect":          Rect(x, y, 40, 40),
        "start_x":       x,
        "start_y":       y,
        "vx":            vx,
        "vx_init":       vx,
        "min_x":         min_x,
        "max_x":         max_x,
        "bob_phase":     0.0,
        "bob_speed":     bob_speed,
        "levende":       True,
        "respawn_timer": 0,
        "squash_timer":  0,
    }


def lav_boss(svaerhed_):
    hp = 3 if svaerhed_ == "let" else 5
    fart = 1.5 if svaerhed_ == "let" else 2.5
    return {
        "rect":         Rect(WIDTH // 2 - 50, JORD_Y - 80, 100, 80),
        "vx":           fart,
        "min_x":        50,
        "max_x":        WIDTH - 50,
        "hp":           hp,
        "max_hp":       hp,
        "invuln_timer": 0,
    }


def standardskyer(width):
    return [
        {"x": 100,        "y": 80,  "r": 40},
        {"x": width // 5, "y": 130, "r": 50},
        {"x": 2 * width // 5, "y": 60,  "r": 30},
        {"x": width // 2,  "y": 110, "r": 45},
        {"x": 3 * width // 5, "y": 70,  "r": 55},
        {"x": 4 * width // 5, "y": 140, "r": 35},
        {"x": width - 200, "y": 90,  "r": 50},
    ]


def lav_bane_1(svaerhed_):
    if svaerhed_ == "let":
        svampe_ = [
            lav_svamp(250,  "roed",  0.8, 200, 600),
            lav_svamp(1050, "lilla", 1.2, 900, 1450),
            lav_svamp(1800, "brun",  1.0, 1700, 2000),
        ]
    else:
        svampe_ = [
            lav_svamp(250,  "roed",  2.0, 200, 600),
            lav_svamp(500,  "brun",  1.8, 400, 680),
            lav_svamp(1000, "lilla", 2.5, 880, 1200),
            lav_svamp(1300, "roed",  2.2, 1180, 1490),
            lav_svamp(1750, "lilla", 2.5, 1700, 1900),
            lav_svamp(1950, "brun",  2.2, 1850, 2080),
            lav_svamp(2200, "roed",  2.0, 2100, 2300),
        ]
    return {
        "navn":              "BANE 1: SKOVEN",
        "world_width":       2400,
        "jord_stykker": [
            Rect(0,    JORD_Y, 700, 40),
            Rect(850,  JORD_Y, 650, 40),
            Rect(1640, JORD_Y, 760, 40),
        ],
        "flydende_platforme": [
            Rect(180,  460, 140, 20),
            Rect(360,  360, 140, 20),
            Rect(560,  470, 130, 20),
            Rect(940,  390, 160, 20),
            Rect(1200, 460, 140, 20),
            Rect(1700, 380, 200, 20),
            Rect(2050, 460, 140, 20),
        ],
        "skyer":      standardskyer(2400),
        "svampe":     svampe_,
        "spoegelser": [],
        "boss":       None,
        "maal_x":     2350,
    }


def lav_bane_2(svaerhed_):
    if svaerhed_ == "let":
        spoegelser_ = [
            lav_spoegelse(400,  350, 1.5, 350,  700),
            lav_spoegelse(1100, 280, 1.8, 1000, 1400),
            lav_spoegelse(1800, 320, 1.5, 1700, 2050),
        ]
        svampe_ = [
            lav_svamp(900, "lilla", 1.2, 850, 1050),
        ]
    else:
        spoegelser_ = [
            lav_spoegelse(300,  350, 2.5, 250,  600),
            lav_spoegelse(700,  250, 3.0, 600,  900,  0.06),
            lav_spoegelse(1100, 320, 2.5, 1000, 1400),
            lav_spoegelse(1500, 200, 2.8, 1400, 1750),
            lav_spoegelse(1900, 350, 2.5, 1750, 2100),
            lav_spoegelse(2200, 250, 2.8, 2050, 2350, 0.05),
        ]
        svampe_ = [
            lav_svamp(800,  "lilla", 2.0, 750,  1000),
            lav_svamp(1700, "roed",  2.2, 1650, 1900),
        ]
    return {
        "navn":              "BANE 2: SPOEGELSES-GROTTEN",
        "world_width":       2400,
        "jord_stykker": [
            Rect(0, JORD_Y, 2400, 40),
        ],
        "flydende_platforme": [
            Rect(180,  470, 110, 20),
            Rect(380,  390, 110, 20),
            Rect(580,  470, 110, 20),
            Rect(780,  390, 110, 20),
            Rect(980,  470, 110, 20),
            Rect(1180, 390, 110, 20),
            Rect(1380, 470, 110, 20),
            Rect(1580, 390, 110, 20),
            Rect(1780, 470, 110, 20),
            Rect(1980, 390, 110, 20),
            Rect(2180, 470, 110, 20),
        ],
        "skyer":      standardskyer(2400),
        "svampe":     svampe_,
        "spoegelser": spoegelser_,
        "boss":       None,
        "maal_x":     2350,
    }


def lav_bane_3(svaerhed_):
    return {
        "navn":              "BANE 3: SKILDPADDE-BOSSEN",
        "world_width":       WIDTH,
        "jord_stykker":      [Rect(0, JORD_Y, WIDTH, 40)],
        "flydende_platforme": [
            Rect(120, 420, 100, 20),
            Rect(580, 420, 100, 20),
        ],
        "skyer": [
            {"x": 150, "y": 80,  "r": 35},
            {"x": 400, "y": 60,  "r": 45},
            {"x": 650, "y": 100, "r": 40},
        ],
        "svampe":     [],
        "spoegelser": [],
        "boss":       lav_boss(svaerhed_),
        "maal_x":     None,
    }


def lav_bane(nr, svaerhed_):
    if nr == 1: return lav_bane_1(svaerhed_)
    if nr == 2: return lav_bane_2(svaerhed_)
    return lav_bane_3(svaerhed_)


def set_bane(bane):
    global jord_stykker, flydende_platforme, alle_platforme
    global skyer, svampe, spoegelser, boss, maal_x, world_width, bane_navn
    jord_stykker       = bane["jord_stykker"]
    flydende_platforme = bane["flydende_platforme"]
    alle_platforme     = jord_stykker + flydende_platforme
    skyer              = bane["skyer"]
    svampe             = bane["svampe"]
    spoegelser         = bane["spoegelser"]
    boss               = bane["boss"]
    maal_x             = bane["maal_x"]
    world_width        = bane["world_width"]
    bane_navn          = bane["navn"]

# ============================================================
# Spil-funktioner
# ============================================================
def nulstil_spiller():
    global spiller_vy, paa_jorden, spiller_facing, usaarlig_timer, camera_x
    spiller.x = START_X
    spiller.y = START_Y
    spiller_vy = 0
    paa_jorden = False
    spiller_facing = 1
    usaarlig_timer = 0
    camera_x = 0


def start_spil(valgt_svaerhed):
    """Starter et helt nyt spil paa bane 1."""
    global svaerhed, bane_nr, spil_tilstand, liv
    svaerhed = valgt_svaerhed
    bane_nr = 1
    set_bane(lav_bane(1, valgt_svaerhed))
    nulstil_spiller()
    liv = 3
    spil_tilstand = "spiller"


def start_naeste_bane():
    """Gaar fra bane 1->2 eller 2->3. Bevarer liv og svaerhed."""
    global bane_nr, spil_tilstand
    bane_nr += 1
    if bane_nr > 3:
        spil_tilstand = "vandt_alt"
        sounds.vinder.play()
        return
    set_bane(lav_bane(bane_nr, svaerhed))
    nulstil_spiller()
    spil_tilstand = "spiller"


def respawn_spiller():
    global spiller_vy, paa_jorden, usaarlig_timer
    spiller.x = START_X
    spiller.y = START_Y
    spiller_vy = 0
    paa_jorden = False
    usaarlig_timer = USAARLIG_FRAMES


def mist_liv():
    global liv, spil_tilstand
    sounds.auch.play()
    liv = liv - 1
    if liv <= 0:
        spil_tilstand = "tabt"
        sounds.gameover.play()
    else:
        respawn_spiller()


def update():
    global spil_tilstand
    global spiller_vy, paa_jorden, spiller_facing
    global usaarlig_timer, camera_x, bane_skift_timer

    # --- Menu ---
    if spil_tilstand == "menu":
        if keyboard.l:
            start_spil("let")
        elif keyboard.s:
            start_spil("svaer")
        return

    # --- Slut-skaerm (tabt eller vandt_alt) ---
    if spil_tilstand in ("tabt", "vandt_alt"):
        if keyboard.space:
            start_spil(svaerhed)
        elif keyboard.m:
            spil_tilstand = "menu"
        return

    # --- Bane-skift overgang ---
    if spil_tilstand == "bane_skift":
        bane_skift_timer = bane_skift_timer - 1
        if bane_skift_timer <= 0:
            start_naeste_bane()
        return

    # --- Spiller (spil_tilstand == "spiller") ---

    # 1. Input
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
    if spiller.right > world_width:
        spiller.right = world_width

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

    if spiller.top > HEIGHT:
        mist_liv()
        return

    # 5a. Flyt svampe (med squash + respawn)
    for s in svampe:
        if s["squash_timer"] > 0:
            s["squash_timer"] -= 1
            if s["squash_timer"] == 0:
                s["respawn_timer"] = RESPAWN_FRAMES
            continue
        if not s["levende"]:
            s["respawn_timer"] -= 1
            if s["respawn_timer"] <= 0:
                s["levende"] = True
                s["rect"].x = s["start_x"]
                s["vx"] = s["vx_init"]
            continue
        s["rect"].x = s["rect"].x + s["vx"]
        if s["rect"].left < s["min_x"]:
            s["rect"].left = s["min_x"]
            s["vx"] = -s["vx"]
        if s["rect"].right > s["max_x"]:
            s["rect"].right = s["max_x"]
            s["vx"] = -s["vx"]

    # 5b. Flyt spoegelser (vandret + bobbing op-ned)
    for g in spoegelser:
        if g["squash_timer"] > 0:
            g["squash_timer"] -= 1
            if g["squash_timer"] == 0:
                g["respawn_timer"] = RESPAWN_FRAMES
            continue
        if not g["levende"]:
            g["respawn_timer"] -= 1
            if g["respawn_timer"] <= 0:
                g["levende"] = True
                g["rect"].x = g["start_x"]
                g["rect"].y = g["start_y"]
                g["vx"] = g["vx_init"]
            continue
        g["bob_phase"] = g["bob_phase"] + g["bob_speed"]
        bob = int(math.sin(g["bob_phase"]) * 25)
        g["rect"].y = g["start_y"] + bob
        g["rect"].x = g["rect"].x + g["vx"]
        if g["rect"].left < g["min_x"]:
            g["rect"].left = g["min_x"]
            g["vx"] = -g["vx"]
        if g["rect"].right > g["max_x"]:
            g["rect"].right = g["max_x"]
            g["vx"] = -g["vx"]

    # 5c. Flyt boss
    if boss is not None:
        if boss["invuln_timer"] > 0:
            boss["invuln_timer"] -= 1
        if boss["hp"] > 0:
            boss["rect"].x = boss["rect"].x + boss["vx"]
            if boss["rect"].left < boss["min_x"]:
                boss["rect"].left = boss["min_x"]
                boss["vx"] = -boss["vx"]
            if boss["rect"].right > boss["max_x"]:
                boss["rect"].right = boss["max_x"]
                boss["vx"] = -boss["vx"]

    # 6. Tjek monster-kollisioner
    if usaarlig_timer > 0:
        usaarlig_timer -= 1

    forrige_bund = spiller.bottom - int(spiller_vy)

    # Svampe
    for s in svampe:
        if not s["levende"] or s["squash_timer"] > 0:
            continue
        if not spiller.colliderect(s["rect"]):
            continue
        er_stomp = spiller_vy > 0 and forrige_bund <= s["rect"].top + 4
        if er_stomp:
            s["levende"] = False
            s["squash_timer"] = SQUASH_FRAMES
            spiller_vy = SPRING_KRAFT * STOMP_BOUNCE
            sounds.hop.play()
            break
        elif usaarlig_timer == 0:
            mist_liv()
            return

    # Spoegelser
    for g in spoegelser:
        if not g["levende"] or g["squash_timer"] > 0:
            continue
        if not spiller.colliderect(g["rect"]):
            continue
        er_stomp = spiller_vy > 0 and forrige_bund <= g["rect"].top + 6
        if er_stomp:
            g["levende"] = False
            g["squash_timer"] = SQUASH_FRAMES
            spiller_vy = SPRING_KRAFT * STOMP_BOUNCE
            sounds.hop.play()
            break
        elif usaarlig_timer == 0:
            mist_liv()
            return

    # Boss
    if boss is not None and boss["hp"] > 0 and spiller.colliderect(boss["rect"]):
        er_stomp = spiller_vy > 0 and forrige_bund <= boss["rect"].top + 8
        if er_stomp:
            spiller_vy = SPRING_KRAFT * STOMP_BOUNCE
            if boss["invuln_timer"] == 0:
                boss["hp"] -= 1
                boss["invuln_timer"] = BOSS_INVULN_FRAMES
                sounds.hop.play()
                if boss["hp"] <= 0:
                    spil_tilstand = "vandt_alt"
                    sounds.vinder.play()
                    return
        elif usaarlig_timer == 0:
            mist_liv()
            return

    # 7. Tjek maal (kun for baner med maal_x)
    if maal_x is not None and spiller.x >= maal_x:
        if bane_nr < 3:
            spil_tilstand = "bane_skift"
            bane_skift_timer = BANE_SKIFT_FRAMES
        else:
            spil_tilstand = "vandt_alt"
            sounds.vinder.play()

    # 8. Kameraet foelger spilleren (hvis verden er bredere end skaermen)
    if world_width > WIDTH:
        nyt_kamera = spiller.centerx - WIDTH // 3
        if nyt_kamera < 0:
            nyt_kamera = 0
        if nyt_kamera > world_width - WIDTH:
            nyt_kamera = world_width - WIDTH
        camera_x = nyt_kamera
    else:
        camera_x = 0


def pixelater():
    """Skalerer skaermen ned med PIXEL_SIZE og op igen for C64-pixelering."""
    lille_w = WIDTH // PIXEL_SIZE
    lille_h = HEIGHT // PIXEL_SIZE
    lille = pygame.transform.scale(screen.surface, (lille_w, lille_h))
    pygame.transform.scale(lille, (WIDTH, HEIGHT), screen.surface)


def tegn_skyer_paa_menu():
    menu_skyer = [(120, 90, 30), (320, 140, 40), (560, 70, 25),
                  (660, 180, 35), (200, 220, 28)]
    for sx, sy, r in menu_skyer:
        screen.draw.filled_circle((sx, sy), r, "white")
        screen.draw.filled_circle((sx + int(r * 0.7), sy + int(r * 0.2)), int(r * 0.8), "white")
        screen.draw.filled_circle((sx - int(r * 0.7), sy + int(r * 0.2)), int(r * 0.7), "white")


def tegn_menu():
    screen.fill((110, 180, 240))
    tegn_skyer_paa_menu()

    big_sonic = pygame.transform.scale(sprite_sonic_hoejre, (110, 140))
    screen.blit(big_sonic, (90, 360))
    big_svamp = pygame.transform.scale(sprite_svampe["roed"], (75, 70))
    screen.blit(big_svamp, (245, 425))
    big_ghost = pygame.transform.scale(sprite_spoegelse, (75, 75))
    screen.blit(big_ghost, (370, 420))
    big_boss = pygame.transform.scale(sprite_boss, (130, 100))
    screen.blit(big_boss, (530, 395))

    screen.draw.text("SONIC DEMO",
                     center=(WIDTH // 2, 70), fontsize=80, color="white")
    screen.draw.text("3 baner. Hop paa monstre. Slaa bossen.",
                     center=(WIDTH // 2, 130), fontsize=28, color="white")
    screen.draw.text("Vaelg svaerhedsgrad",
                     center=(WIDTH // 2, 200), fontsize=36, color="white")
    screen.draw.text("Tryk  L  -  LET",
                     center=(WIDTH // 2, 260), fontsize=50, color=(120, 230, 120))
    screen.draw.text("Tryk  S  -  SVAER",
                     center=(WIDTH // 2, 320), fontsize=50, color=(255, 180, 80))


def tegn_verden():
    """Tegner alt der hoerer til selve banen - bruges naar man spiller, ved bane-skift og slut-skaerm."""
    screen.fill((110, 180, 240))

    # Skyer (parallax)
    for sky in skyer:
        sx = int(sky["x"] - camera_x * 0.3)
        sy = sky["y"]
        if sx < -150 or sx > WIDTH + 150:
            continue
        r = sky["r"]
        screen.draw.filled_circle((sx, sy), r, "white")
        screen.draw.filled_circle((sx + int(r * 0.7), sy + int(r * 0.2)), int(r * 0.8), "white")
        screen.draw.filled_circle((sx - int(r * 0.7), sy + int(r * 0.2)), int(r * 0.7), "white")

    # Jord-stykker
    graes     = (60, 180, 70)
    graes_top = (35, 130, 45)
    jord_brun = (130, 90, 50)

    for p in jord_stykker:
        x = p.x - camera_x
        if x + p.width < 0 or x > WIDTH:
            continue
        screen.draw.filled_rect(Rect(x, p.y + 8, p.width, p.height - 8), jord_brun)
        screen.draw.filled_rect(Rect(x, p.y, p.width, 8), graes)
        screen.draw.filled_rect(Rect(x, p.y, p.width, 3), graes_top)

    # Flydende platforme
    for p in flydende_platforme:
        x = p.x - camera_x
        if x + p.width < 0 or x > WIDTH:
            continue
        screen.draw.filled_rect(Rect(x, p.y, p.width, p.height), graes)
        screen.draw.filled_rect(Rect(x, p.y, p.width, 3), graes_top)

    # Maal-flag
    if maal_x is not None:
        mx = maal_x - camera_x
        if -50 < mx < WIDTH:
            screen.draw.filled_rect(Rect(mx, JORD_Y - 80, 4, 80), (140, 100, 60))
            screen.draw.filled_rect(Rect(mx + 4, JORD_Y - 80, 26, 18), "yellow")

    # Svampe (med squash-animation)
    for s in svampe:
        sx = s["rect"].x - camera_x
        if sx < -100 or sx > WIDTH + 100:
            continue
        if s["squash_timer"] > 0:
            screen.blit(sprite_svampe_flat[s["farve"]], (sx, JORD_Y - 8))
        elif s["levende"]:
            screen.blit(sprite_svampe[s["farve"]], (sx, s["rect"].y))

    # Spoegelser (fader ved squash)
    for g in spoegelser:
        sx = g["rect"].x - camera_x
        if sx < -100 or sx > WIDTH + 100:
            continue
        if g["squash_timer"] > 0:
            if (g["squash_timer"] // 4) % 2 == 0:
                screen.blit(sprite_spoegelse, (sx, g["rect"].y))
        elif g["levende"]:
            screen.blit(sprite_spoegelse, (sx, g["rect"].y))

    # Boss
    if boss is not None and boss["hp"] > 0:
        bx = boss["rect"].x - camera_x
        if boss["invuln_timer"] == 0 or (boss["invuln_timer"] // 5) % 2 == 0:
            screen.blit(sprite_boss, (bx, boss["rect"].y))

    # Spilleren - blink hvis usaarlig
    blink = (usaarlig_timer // 5) % 2 == 0
    if usaarlig_timer == 0 or blink:
        if spiller_facing == 1:
            sprite = sprite_sonic_hoejre
        else:
            sprite = sprite_sonic_venstre
        screen.blit(sprite, (spiller.x - camera_x, spiller.y))

    # HUD
    screen.draw.text("Liv: " + str(liv), topleft=(10, 10), fontsize=30, color="white")
    if svaerhed == "let":
        sv_tekst = "Svaerhed: LET"
    else:
        sv_tekst = "Svaerhed: SVAER"
    screen.draw.text(sv_tekst, topleft=(10, 42), fontsize=22, color="white")
    screen.draw.text(bane_navn, topleft=(10, 67), fontsize=22, color="white")

    # Boss HP-bar
    if boss is not None and boss["hp"] > 0:
        bar_x = WIDTH // 2 - 120
        bar_y = 24
        bar_w = 240
        bar_h = 20
        screen.draw.filled_rect(Rect(bar_x, bar_y, bar_w, bar_h), (50, 50, 50))
        fill_w = int(bar_w * (boss["hp"] / boss["max_hp"]))
        screen.draw.filled_rect(Rect(bar_x, bar_y, fill_w, bar_h), (220, 50, 50))
        screen.draw.text("BOSS",
                         center=(WIDTH // 2, bar_y + bar_h // 2),
                         fontsize=22, color="white")


def draw():
    if sprite_sonic_hoejre is None:
        byg_sprites()

    if spil_tilstand == "menu":
        tegn_menu()
        pixelater()
        return

    tegn_verden()

    if spil_tilstand == "bane_skift":
        screen.draw.text("BANE FULDFOERT!",
                         center=(WIDTH // 2, HEIGHT // 2 - 30),
                         fontsize=70, color="yellow")
        if bane_nr < 3:
            screen.draw.text("Bane " + str(bane_nr + 1) + " starter...",
                             center=(WIDTH // 2, HEIGHT // 2 + 30),
                             fontsize=36, color="white")
    elif spil_tilstand == "tabt":
        screen.draw.text("GAME OVER",
                         center=(WIDTH // 2, HEIGHT // 2 - 30),
                         fontsize=80, color="white")
        screen.draw.text("Tryk MELLEMRUM for at proeve igen",
                         center=(WIDTH // 2, HEIGHT // 2 + 30),
                         fontsize=28, color="white")
        screen.draw.text("Tryk M for menu",
                         center=(WIDTH // 2, HEIGHT // 2 + 70),
                         fontsize=24, color="white")
    elif spil_tilstand == "vandt_alt":
        screen.draw.text("DU HAR VUNDET!",
                         center=(WIDTH // 2, HEIGHT // 2 - 70),
                         fontsize=80, color="yellow")
        screen.draw.text("Du besejrede skildpadden!",
                         center=(WIDTH // 2, HEIGHT // 2 - 10),
                         fontsize=36, color="white")
        screen.draw.text("Tryk MELLEMRUM for at spille igen",
                         center=(WIDTH // 2, HEIGHT // 2 + 50),
                         fontsize=28, color="white")
        screen.draw.text("Tryk M for menu",
                         center=(WIDTH // 2, HEIGHT // 2 + 90),
                         fontsize=24, color="white")

    pixelater()


pgzrun.go()
