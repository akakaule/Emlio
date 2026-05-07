#!pgzero
# Sonic-stil platformspil med 3 baner, monstre, boss, moenter og fireballs
#
# Bane 1: Skoven        - kun svampe
# Bane 2: Spoegelses-grotten - spoegelser + nogle svampe
# Bane 3: Skildpadde-bossen  - bosskamp; bossen kaster ildkugler
#
# Moent-system:
#   - Saml moenter rundt om paa banerne
#   - 1 moent per monster du draeber
#   - Boss giver 10 moenter
#   - For hver 5 moenter faar du 1 ekstra liv (vist som hjerter)
#
# Kontroller:
#   I menuen:               L = LET, S = SVAER
#   Mens man spiller:       Venstre/Hoejre piletast = gaa
#                           Op-pil eller mellemrum  = hop
#                           Hop oven paa monstre for at slaa dem ihjel
#   Naar spillet er slut:   MELLEMRUM = spil igen, M = tilbage til menu

import pgzero.runner as pgzrun
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
USAARLIG_FRAMES = 60
RESPAWN_FRAMES = 300
SQUASH_FRAMES = 30
STOMP_BOUNCE = 0.7
BOSS_INVULN_FRAMES = 60
BANE_SKIFT_FRAMES = 120
PIXEL_SIZE = 4

MOENTER_PER_LIV = 5            # for hver 5 moenter faar man et ekstra liv
BOSS_BONUS_MOENTER = 10        # bossen giver saa mange moenter naar man besejrer ham

FIREBALL_FART = 5.0
FIREBALL_INTERVAL_LET = 110    # frames mellem fireballs paa LET
FIREBALL_INTERVAL_SVAER = 65   # frames mellem fireballs paa SVAER
FIREBALL_STR = 16              # stoerrelse paa fireball-kollisionsboks

# Spillerens egne fireballs (TAB-knappen)
SPILLER_FB_FART = 9.0
SPILLER_FB_STR  = 14

START_X = 50
START_Y = 470

# ============================================================
# Spil-tilstand (aendrer sig mens man spiller)
# ============================================================
spil_tilstand = "menu"
svaerhed = "let"
bane_nr = 1
bane_skift_timer = 0

spiller = Rect(START_X, START_Y, 40, 50)
spiller_vy = 0
paa_jorden = False
spiller_facing = 1
liv = 3
moenter = 0
usaarlig_timer = 0
camera_x = 0
udoedelig = False              # snydekode: TAB-toggle med L-knappen
spiller_fireballs = []         # liste af {rect, vx} fra spillerens egne skud

jord_stykker = []
flydende_platforme = []
alle_platforme = []
skyer = []
svampe = []
spoegelser = []
moenter_liste = []
boss = None
maal_x = None
world_width = 800
bane_navn = ""

sprite_sonic_hoejre = None
sprite_sonic_venstre = None
sprite_svampe = {}
sprite_svampe_flat = {}
sprite_spoegelse = None
sprite_boss = None
sprite_moent = None
sprite_hjerte = None

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
    surf = pygame.Surface((40, 8), pygame.SRCALPHA)
    pygame.draw.ellipse(surf, hat_farve, Rect(0, 0, 40, 8))
    pygame.draw.circle(surf, prik_farve, (12, 3), 2)
    pygame.draw.circle(surf, prik_farve, (22, 2), 3)
    pygame.draw.circle(surf, prik_farve, (30, 4), 2)
    pygame.draw.line(surf, (0, 0, 0), (17, 4), (20, 7), 1)
    pygame.draw.line(surf, (0, 0, 0), (20, 4), (17, 7), 1)
    return surf


def lav_spoegelse_sprite():
    surf = pygame.Surface((40, 40), pygame.SRCALPHA)
    krop = (245, 245, 250)
    pygame.draw.ellipse(surf, krop, Rect(2, 0, 36, 28))
    pygame.draw.rect(surf, krop, Rect(2, 12, 36, 22))
    pygame.draw.polygon(surf, krop,
                        [(2, 34), (8, 30), (14, 36), (20, 30),
                         (26, 36), (32, 30), (38, 34), (38, 40), (2, 40)])
    pygame.draw.circle(surf, (255, 255, 255), (14, 17), 5)
    pygame.draw.circle(surf, (255, 255, 255), (26, 17), 5)
    pygame.draw.circle(surf, (40, 40, 220), (15, 18), 2)
    pygame.draw.circle(surf, (40, 40, 220), (27, 18), 2)
    return surf


def lav_boss_sprite():
    surf = pygame.Surface((100, 80), pygame.SRCALPHA)
    pygame.draw.ellipse(surf, (255, 220, 100), Rect(15, 35, 70, 40))
    pygame.draw.ellipse(surf, (50, 140, 50), Rect(15, 5, 70, 50))
    for px in [30, 50, 70]:
        pygame.draw.polygon(surf, (255, 255, 255),
                            [(px - 6, 18), (px, 5), (px + 6, 18)])
    pygame.draw.circle(surf, (255, 220, 100), (32, 32), 15)
    pygame.draw.polygon(surf, (200, 80, 80), [(20, 20), (24, 12), (27, 24)])
    pygame.draw.polygon(surf, (200, 80, 80), [(38, 20), (42, 12), (44, 24)])
    pygame.draw.circle(surf, (255, 255, 255), (28, 30), 4)
    pygame.draw.circle(surf, (255, 255, 255), (38, 30), 4)
    pygame.draw.circle(surf, (220, 0, 0), (28, 30), 2)
    pygame.draw.circle(surf, (220, 0, 0), (38, 30), 2)
    pygame.draw.polygon(surf, (255, 255, 255), [(28, 40), (32, 46), (36, 40)])
    return surf


def lav_moent_sprite():
    surf = pygame.Surface((20, 20), pygame.SRCALPHA)
    pygame.draw.circle(surf, (180, 130, 20), (10, 10), 9)
    pygame.draw.circle(surf, (255, 220, 60), (10, 10), 8)
    pygame.draw.circle(surf, (180, 130, 20), (10, 10), 5)
    pygame.draw.circle(surf, (255, 240, 130), (10, 10), 3)
    return surf


def lav_hjerte_sprite():
    surf = pygame.Surface((26, 24), pygame.SRCALPHA)
    roed       = (220, 30, 50)
    moerk_roed = (150, 15, 30)
    lys        = (255, 170, 190)
    # Moerk omrids
    pygame.draw.circle(surf, moerk_roed, (8, 8), 8)
    pygame.draw.circle(surf, moerk_roed, (18, 8), 8)
    pygame.draw.polygon(surf, moerk_roed, [(0, 9), (26, 9), (13, 23)])
    # Selve hjertet
    pygame.draw.circle(surf, roed, (8, 8), 6)
    pygame.draw.circle(surf, roed, (18, 8), 6)
    pygame.draw.polygon(surf, roed, [(2, 9), (24, 9), (13, 21)])
    # Glanslys
    pygame.draw.circle(surf, lys, (6, 6), 2)
    return surf


def byg_sprites():
    global sprite_sonic_hoejre, sprite_sonic_venstre
    global sprite_svampe, sprite_svampe_flat, sprite_spoegelse, sprite_boss
    global sprite_moent, sprite_hjerte

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
    sprite_moent = lav_moent_sprite()
    sprite_hjerte = lav_hjerte_sprite()

# ============================================================
# Bane-data og monster-konstruktoerer
# ============================================================
def lav_svamp(x_start, farve, vx, min_x, max_x, kan_hoppe=False):
    return {
        "rect":          Rect(x_start, JORD_Y - 35, 40, 35),
        "start_x":       x_start,
        "vx":            vx,
        "vx_init":       vx,
        "vy":            0.0,
        "paa_jorden":    True,
        "min_x":         min_x,
        "max_x":         max_x,
        "farve":         farve,
        "levende":       True,
        "respawn_timer": 0,
        "squash_timer":  0,
        "kan_hoppe":     kan_hoppe,
        "hop_cooldown":  0,
    }


def lav_spoegelse(x, y, vx, min_x, max_x, bob_speed=0.04, bob_amplitude=25):
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
        "bob_amplitude": bob_amplitude,
        "levende":       True,
        "respawn_timer": 0,
        "squash_timer":  0,
    }


def lav_moent(x, y):
    return {"rect": Rect(x, y, 20, 20), "samlet": False}


def lav_boss(svaerhed_):
    hp = 3 if svaerhed_ == "let" else 5
    fart = 1.5 if svaerhed_ == "let" else 2.5
    interval = FIREBALL_INTERVAL_LET if svaerhed_ == "let" else FIREBALL_INTERVAL_SVAER
    return {
        "rect":              Rect(WIDTH // 2 - 50, JORD_Y - 80, 100, 80),
        "vx":                fart,
        "min_x":             50,
        "max_x":             WIDTH - 50,
        "hp":                hp,
        "max_hp":            hp,
        "invuln_timer":      0,
        "fireballs":         [],
        "fireball_timer":    interval,
        "fireball_interval": interval,
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
    moenter_ = [
        lav_moent(220,  430),    # paa platform 1
        lav_moent(395,  330),    # paa platform 2 (hoej)
        lav_moent(605,  440),    # paa platform 3
        lav_moent(770,  460),    # i luften over pit 1
        lav_moent(990,  360),    # paa platform 4
        lav_moent(1235, 430),    # paa platform 5
        lav_moent(1565, 480),    # i luften over pit 2
        lav_moent(1750, 350),    # paa platform 6
        lav_moent(2090, 430),    # paa platform 7
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
        "moenter":    moenter_,
        "boss":       None,
        "maal_x":     2350,
    }


def lav_bane_2(svaerhed_):
    if svaerhed_ == "let":
        spoegelser_ = [
            lav_spoegelse(400,  330, 1.4, 300,  700,  0.035, bob_amplitude=170),
            lav_spoegelse(900,  300, 1.5, 800,  1150, 0.040, bob_amplitude=190),
            lav_spoegelse(1300, 340, 1.6, 1200, 1550, 0.035, bob_amplitude=160),
            lav_spoegelse(1750, 310, 1.5, 1650, 1950, 0.040, bob_amplitude=180),
            lav_spoegelse(2150, 330, 1.7, 2000, 2350, 0.035, bob_amplitude=170),
        ]
        svampe_ = [
            lav_svamp(700,  "lilla", 1.8, 600,  950,  kan_hoppe=True),
            lav_svamp(1450, "roed",  1.8, 1300, 1650, kan_hoppe=True),
        ]
    else:
        spoegelser_ = [
            lav_spoegelse(300,  320, 2.2, 200,  650,  0.040, bob_amplitude=200),
            lav_spoegelse(700,  300, 2.4, 600,  950,  0.045, bob_amplitude=210),
            lav_spoegelse(1100, 330, 2.2, 1000, 1400, 0.040, bob_amplitude=190),
            lav_spoegelse(1500, 300, 2.4, 1400, 1800, 0.045, bob_amplitude=200),
            lav_spoegelse(1900, 320, 2.2, 1750, 2150, 0.040, bob_amplitude=210),
            lav_spoegelse(2250, 300, 2.4, 2050, 2350, 0.045, bob_amplitude=200),
            lav_spoegelse(550,  310, 2.0, 400,  900,  0.035, bob_amplitude=180),
            lav_spoegelse(1700, 330, 2.0, 1500, 2000, 0.035, bob_amplitude=180),
        ]
        svampe_ = [
            lav_svamp(500,  "lilla", 2.6, 350,  750,  kan_hoppe=True),
            lav_svamp(1000, "roed",  2.8, 850,  1200, kan_hoppe=True),
            lav_svamp(1700, "lilla", 2.6, 1500, 1900, kan_hoppe=True),
            lav_svamp(2100, "brun",  2.8, 2000, 2300, kan_hoppe=True),
        ]
    moenter_ = [
        lav_moent(215,  440),
        lav_moent(405,  360),
        lav_moent(615,  440),
        lav_moent(805,  360),
        lav_moent(1015, 440),
        lav_moent(1215, 360),
        lav_moent(1415, 440),
        lav_moent(1605, 360),
        lav_moent(1815, 440),
        lav_moent(2005, 360),
        lav_moent(2205, 440),
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
        "moenter":    moenter_,
        "boss":       None,
        "maal_x":     2350,
    }


def lav_bane_3(svaerhed_):
    moenter_ = [
        lav_moent(155, 390),    # paa venstre svaevende platform
        lav_moent(615, 390),    # paa hoejre svaevende platform
        lav_moent(250, 530),    # paa jorden venstre
        lav_moent(550, 530),    # paa jorden hoejre
    ]
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
        "moenter":    moenter_,
        "boss":       lav_boss(svaerhed_),
        "maal_x":     None,
    }


def lav_bane(nr, svaerhed_):
    if nr == 1: return lav_bane_1(svaerhed_)
    if nr == 2: return lav_bane_2(svaerhed_)
    return lav_bane_3(svaerhed_)


def set_bane(bane):
    global jord_stykker, flydende_platforme, alle_platforme
    global skyer, svampe, spoegelser, moenter_liste, boss, maal_x
    global world_width, bane_navn
    jord_stykker       = bane["jord_stykker"]
    flydende_platforme = bane["flydende_platforme"]
    alle_platforme     = jord_stykker + flydende_platforme
    skyer              = bane["skyer"]
    svampe             = bane["svampe"]
    spoegelser         = bane["spoegelser"]
    moenter_liste      = bane["moenter"]
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
    """Starter et helt nyt spil paa bane 1 med fersk liv- og moent-tael."""
    global svaerhed, bane_nr, spil_tilstand, liv, moenter, udoedelig
    svaerhed = valgt_svaerhed
    bane_nr = 1
    set_bane(lav_bane(1, valgt_svaerhed))
    nulstil_spiller()
    liv = 3
    moenter = 0
    udoedelig = False
    spiller_fireballs.clear()
    spil_tilstand = "spiller"


def start_naeste_bane():
    """Bane 1->2 eller 2->3. Bevarer liv, moenter og svaerhed."""
    global bane_nr, spil_tilstand
    bane_nr += 1
    if bane_nr > 3:
        spil_tilstand = "vandt_alt"
        sounds.vinder.play()
        return
    set_bane(lav_bane(bane_nr, svaerhed))
    nulstil_spiller()
    spiller_fireballs.clear()
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
    if udoedelig:
        # Snydekode aktiv: ingen skade, men tjek om vi faldt ud af verden
        if spiller.top > HEIGHT:
            respawn_spiller()
        return
    sounds.auch.play()
    liv = liv - 1
    if liv <= 0:
        spil_tilstand = "tabt"
        sounds.gameover.play()
    else:
        respawn_spiller()


def skyd_fireball():
    """Affyrer en fireball i den retning spilleren peger."""
    if spiller_facing == 1:
        bx = spiller.right + 4
    else:
        bx = spiller.left - 4
    by = spiller.centery
    spiller_fireballs.append({
        "rect": Rect(bx - SPILLER_FB_STR // 2, by - SPILLER_FB_STR // 2,
                     SPILLER_FB_STR, SPILLER_FB_STR),
        "vx":   SPILLER_FB_FART * spiller_facing,
    })
    sounds.hop.play()


def on_key_down(key):
    """TAB = skyd, L = skift mellem doedelig/usaarlig (kun mens man spiller)."""
    global udoedelig
    if spil_tilstand != "spiller":
        return
    if key == keys.L:
        udoedelig = not udoedelig
    elif key == keys.TAB:
        skyd_fireball()


def tilfoej_moenter(antal):
    """Tilfoej moenter til toelleren. For hver MOENTER_PER_LIV faar man et liv."""
    global moenter, liv
    for _ in range(antal):
        moenter = moenter + 1
        if moenter % MOENTER_PER_LIV == 0:
            liv = liv + 1
            sounds.extra_liv.play()


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

    # --- Spiller ---

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

    # 5a. Flyt svampe (med squash + respawn + valgfri hop-AI)
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
                s["rect"].y = JORD_Y - 35
                s["vx"] = s["vx_init"]
                s["vy"] = 0.0
                s["paa_jorden"] = True
                s["hop_cooldown"] = 0
            continue

        # Vandret bevaegelse
        s["rect"].x = s["rect"].x + s["vx"]
        if s["rect"].left < s["min_x"]:
            s["rect"].left = s["min_x"]
            s["vx"] = -s["vx"]
        if s["rect"].right > s["max_x"]:
            s["rect"].right = s["max_x"]
            s["vx"] = -s["vx"]

        # Hop-AI: hop hvis spilleren staar paa en platform over svampen
        if s["kan_hoppe"]:
            if s["hop_cooldown"] > 0:
                s["hop_cooldown"] -= 1
            if s["paa_jorden"] and s["hop_cooldown"] == 0:
                dx = abs(spiller.centerx - s["rect"].centerx)
                spiller_over = s["rect"].top - spiller.bottom
                if dx < 250 and 30 < spiller_over < 240:
                    s["vy"] = -16.0
                    s["paa_jorden"] = False
                    s["hop_cooldown"] = 90

        # Tyngdekraft + lodret kollision (saa svampe lander paa platforme)
        s["vy"] = s["vy"] + TYNGDEKRAFT
        if s["vy"] > MAX_FALD_FART:
            s["vy"] = MAX_FALD_FART
        s["rect"].y = s["rect"].y + int(s["vy"])
        s["paa_jorden"] = False
        for p in alle_platforme:
            if s["rect"].colliderect(p):
                if s["vy"] > 0:
                    s["rect"].bottom = p.top
                    s["vy"] = 0
                    s["paa_jorden"] = True
                elif s["vy"] < 0:
                    s["rect"].top = p.bottom
                    s["vy"] = 0

    # 5b. Flyt spoegelser
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
        # Bevaeg lodret (bob) og vandret
        g["bob_phase"] = g["bob_phase"] + g["bob_speed"]
        bob = int(math.sin(g["bob_phase"]) * g["bob_amplitude"])
        g["rect"].y = g["start_y"] + bob
        g["rect"].x = g["rect"].x + g["vx"]

        # Kant-bouncer
        if g["rect"].left < g["min_x"]:
            g["rect"].left = g["min_x"]
            g["vx"] = -g["vx"]
        if g["rect"].right > g["max_x"]:
            g["rect"].right = g["max_x"]
            g["vx"] = -g["vx"]

        # Platform-kollision: skub spoegelset ud paa siden med mindst overlap
        # (forhindrer at det krydser en hvilken som helst forhindring)
        for p in alle_platforme:
            if not g["rect"].colliderect(p):
                continue
            ov_top    = g["rect"].bottom - p.top
            ov_bund   = p.bottom - g["rect"].top
            ov_venstre = g["rect"].right - p.left
            ov_hoejre  = p.right - g["rect"].left
            mindst = min(ov_top, ov_bund, ov_venstre, ov_hoejre)
            if mindst == ov_top:
                g["rect"].bottom = p.top
            elif mindst == ov_bund:
                g["rect"].top = p.bottom
            elif mindst == ov_venstre:
                g["rect"].right = p.left
                g["vx"] = -abs(g["vx"])
            else:
                g["rect"].left = p.right
                g["vx"] = abs(g["vx"])
            break

    # 5c. Flyt boss + spawn fireballs
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

            # Spawn fireball
            boss["fireball_timer"] -= 1
            if boss["fireball_timer"] <= 0:
                bx = boss["rect"].centerx
                by = boss["rect"].centery + 5
                if spiller.centerx > bx:
                    ball_vx = FIREBALL_FART
                else:
                    ball_vx = -FIREBALL_FART
                boss["fireballs"].append({
                    "rect": Rect(bx - FIREBALL_STR // 2, by - FIREBALL_STR // 2,
                                 FIREBALL_STR, FIREBALL_STR),
                    "vx":   ball_vx,
                })
                boss["fireball_timer"] = boss["fireball_interval"]

        # Flyt eksisterende fireballs (selv hvis bossen er doed)
        nye_fb = []
        for f in boss["fireballs"]:
            f["rect"].x = f["rect"].x + f["vx"]
            if -50 < f["rect"].x < world_width + 50:
                nye_fb.append(f)
        boss["fireballs"] = nye_fb

    # 5d. Flyt spillerens fireballs (TAB)
    nye_pfb = []
    for f in spiller_fireballs:
        f["rect"].x = f["rect"].x + f["vx"]
        if not (-50 < f["rect"].x < world_width + 50):
            continue

        truffet = False

        # Ram svampe
        for s in svampe:
            if not s["levende"] or s["squash_timer"] > 0:
                continue
            if f["rect"].colliderect(s["rect"]):
                s["levende"] = False
                s["squash_timer"] = SQUASH_FRAMES
                tilfoej_moenter(1)
                sounds.hop.play()
                truffet = True
                break

        # Ram spoegelser
        if not truffet:
            for g in spoegelser:
                if not g["levende"] or g["squash_timer"] > 0:
                    continue
                if f["rect"].colliderect(g["rect"]):
                    g["levende"] = False
                    g["squash_timer"] = SQUASH_FRAMES
                    tilfoej_moenter(1)
                    sounds.hop.play()
                    truffet = True
                    break

        # Ram bossen
        if not truffet and boss is not None and boss["hp"] > 0:
            if f["rect"].colliderect(boss["rect"]):
                if boss["invuln_timer"] == 0:
                    boss["hp"] -= 1
                    boss["invuln_timer"] = BOSS_INVULN_FRAMES
                    sounds.hop.play()
                    if boss["hp"] <= 0:
                        tilfoej_moenter(BOSS_BONUS_MOENTER)
                        spil_tilstand = "vandt_alt"
                        sounds.vinder.play()
                truffet = True

        if not truffet:
            nye_pfb.append(f)
    spiller_fireballs[:] = nye_pfb

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
            tilfoej_moenter(1)
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
            tilfoej_moenter(1)
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
                    tilfoej_moenter(BOSS_BONUS_MOENTER)
                    spil_tilstand = "vandt_alt"
                    sounds.vinder.play()
                    return
        elif usaarlig_timer == 0:
            mist_liv()
            return

    # Boss-fireballs
    if boss is not None and usaarlig_timer == 0:
        for f in boss["fireballs"]:
            if spiller.colliderect(f["rect"]):
                mist_liv()
                return

    # 6.5 Saml moenter
    for m in moenter_liste:
        if m["samlet"]:
            continue
        if spiller.colliderect(m["rect"]):
            m["samlet"] = True
            sounds.coin.play()
            tilfoej_moenter(1)

    # 7. Tjek maal
    if maal_x is not None and spiller.x >= maal_x:
        if bane_nr < 3:
            spil_tilstand = "bane_skift"
            bane_skift_timer = BANE_SKIFT_FRAMES
        else:
            spil_tilstand = "vandt_alt"
            sounds.vinder.play()

    # 8. Kameraet foelger spilleren
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
    big_moent = pygame.transform.scale(sprite_moent, (40, 40))
    screen.blit(big_moent, (700, 425))

    screen.draw.text("SONIC DEMO",
                     center=(WIDTH // 2, 70), fontsize=80, color="white")
    screen.draw.text("3 baner. Saml moenter. Slaa bossen.",
                     center=(WIDTH // 2, 130), fontsize=28, color="white")
    screen.draw.text("Hver 5 moenter = 1 ekstra liv",
                     center=(WIDTH // 2, 165), fontsize=22, color=(255, 220, 60))
    screen.draw.text("Vaelg svaerhedsgrad",
                     center=(WIDTH // 2, 215), fontsize=36, color="white")
    screen.draw.text("Tryk  L  -  LET",
                     center=(WIDTH // 2, 270), fontsize=50, color=(120, 230, 120))
    screen.draw.text("Tryk  S  -  SVAER",
                     center=(WIDTH // 2, 325), fontsize=50, color=(255, 180, 80))


def tegn_verden():
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

    # Moenter (kun de der ikke er samlet endnu)
    for m in moenter_liste:
        if m["samlet"]:
            continue
        mx = m["rect"].x - camera_x
        if -30 < mx < WIDTH + 30:
            screen.blit(sprite_moent, (mx, m["rect"].y))

    # Svampe (med squash-animation)
    for s in svampe:
        sx = s["rect"].x - camera_x
        if sx < -100 or sx > WIDTH + 100:
            continue
        if s["squash_timer"] > 0:
            screen.blit(sprite_svampe_flat[s["farve"]], (sx, s["rect"].bottom - 8))
        elif s["levende"]:
            screen.blit(sprite_svampe[s["farve"]], (sx, s["rect"].y))

    # Spoegelser
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

    # Boss-fireballs
    if boss is not None:
        for f in boss["fireballs"]:
            fx = f["rect"].centerx - camera_x
            fy = f["rect"].centery
            if -20 < fx < WIDTH + 20:
                screen.draw.filled_circle((fx, fy), 10, (220, 50, 0))
                screen.draw.filled_circle((fx, fy), 7, (255, 140, 0))
                screen.draw.filled_circle((fx, fy), 4, (255, 230, 80))

    # Spillerens fireballs (blaa)
    for f in spiller_fireballs:
        fx = f["rect"].centerx - camera_x
        fy = f["rect"].centery
        if -20 < fx < WIDTH + 20:
            screen.draw.filled_circle((fx, fy), 9, (20,  60, 200))
            screen.draw.filled_circle((fx, fy), 6, (80, 180, 255))
            screen.draw.filled_circle((fx, fy), 3, (220, 240, 255))

    # Glorie naar man er usaarlig
    if udoedelig:
        cx = spiller.centerx - camera_x
        cy = spiller.centery
        screen.draw.circle((cx, cy), 32, (255, 230, 80))
        screen.draw.circle((cx, cy), 30, (255, 200, 30))

    # Spilleren
    blink = (usaarlig_timer // 5) % 2 == 0
    if usaarlig_timer == 0 or blink:
        if spiller_facing == 1:
            sprite = sprite_sonic_hoejre
        else:
            sprite = sprite_sonic_venstre
        screen.blit(sprite, (spiller.x - camera_x, spiller.y))



def tegn_hud():
    """Tegner HUD med skarp moderne skrift og hjerter (kaldes EFTER pixelater)."""
    # Hjerter for liv (max 10 vises)
    hjerte_w = sprite_hjerte.get_width()
    vis_liv = min(liv, 10)
    for i in range(vis_liv):
        screen.blit(sprite_hjerte, (10 + i * (hjerte_w + 4), 10))
    if liv > 10:
        screen.draw.text("x" + str(liv),
                         topleft=(10 + 10 * (hjerte_w + 4) + 4, 12),
                         fontsize=22, color="white")

    # Moenter
    screen.blit(pygame.transform.scale(sprite_moent, (22, 22)), (10, 42))
    screen.draw.text(str(moenter), topleft=(38, 44),
                     fontsize=24, color=(255, 220, 60))

    if svaerhed == "let":
        sv_tekst = "Svaerhed: LET"
    else:
        sv_tekst = "Svaerhed: SVAER"
    screen.draw.text(sv_tekst, topleft=(10, 72), fontsize=22, color="white")
    screen.draw.text(bane_navn, topleft=(10, 96), fontsize=22, color="white")

    # Tilstands-indikator (oeverst hoejre)
    if udoedelig:
        tilstand_tekst = "USAARLIG"
        tilstand_farve = (100, 255, 100)
    else:
        tilstand_tekst = "DOEDELIG"
        tilstand_farve = (255, 255, 255)
    screen.draw.text(tilstand_tekst, topright=(WIDTH - 10, 10),
                     fontsize=28, color=tilstand_farve)
    screen.draw.text("L: skift  TAB: skyd",
                     topright=(WIDTH - 10, 42),
                     fontsize=18, color=(210, 210, 210))

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
        screen.draw.text("Tryk MELLEMRUM for at starte forfra (bane 1)",
                         center=(WIDTH // 2, HEIGHT // 2 + 30),
                         fontsize=26, color="white")
        screen.draw.text("Tryk M for menu",
                         center=(WIDTH // 2, HEIGHT // 2 + 70),
                         fontsize=24, color="white")
    elif spil_tilstand == "vandt_alt":
        screen.draw.text("DU HAR VUNDET!",
                         center=(WIDTH // 2, HEIGHT // 2 - 90),
                         fontsize=80, color="yellow")
        screen.draw.text("Du besejrede skildpadden!",
                         center=(WIDTH // 2, HEIGHT // 2 - 30),
                         fontsize=36, color="white")
        screen.draw.text("Du samlede " + str(moenter) + " moenter",
                         center=(WIDTH // 2, HEIGHT // 2 + 10),
                         fontsize=28, color=(255, 220, 60))
        screen.draw.text("Tryk MELLEMRUM for at spille igen",
                         center=(WIDTH // 2, HEIGHT // 2 + 60),
                         fontsize=28, color="white")
        screen.draw.text("Tryk M for menu",
                         center=(WIDTH // 2, HEIGHT // 2 + 100),
                         fontsize=24, color="white")

    pixelater()
    tegn_hud()


pgzrun.go()
