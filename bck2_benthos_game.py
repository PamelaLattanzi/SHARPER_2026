"""
=====================================================================
 IL FONDALE MISTERIOSO - Gioco sul benthos per Sharper Night 2026
 CNR - Stand del centro citta di Ancona - 25 settembre 2026
=====================================================================

Tre livelli, un unico avatar/nome scelti a inizio partita, un'unica
classifica finale (come l'anno scorso, perche' "era molto accattivante").

LIVELLO 1 - Memory: abbina l'animale al suo habitat (carte coperte)
LIVELLO 2 - Trascina l'animale nel suo habitat (drag & drop)
LIVELLO 3 - Quiz a raffica su curiosita' sul benthos

---------------------------------------------------------------------
IMMAGINI DA PREPARARE (per ora il gioco funziona comunque: se un file
manca viene disegnato un riquadro colorato con le iniziali al posto
suo, quindi e' gia' giocabile/testabile cosi' com'e'. Basta aggiungere
i file con questi ESATTI nomi e percorsi quando sono pronti):

  placeholder/avatars/avatar_squalo.png
  placeholder/avatars/avatar_polpo.png
  placeholder/avatars/avatar_stella.png
  placeholder/avatars/avatar_delfino.png
  placeholder/avatars/avatar_tartaruga.png
  placeholder/avatars/avatar_cavalluccio.png

  placeholder/animals/riccio.png
  placeholder/animals/stella.png
  placeholder/animals/cavalluccio.png
  placeholder/animals/verme_tubicolo.png
  placeholder/animals/gorgonia.png
  placeholder/animals/paguro.png

  placeholder/habitats/fondale_roccioso.png
  placeholder/habitats/fondale_sabbioso.png
  placeholder/habitats/posidonia.png
  placeholder/habitats/fondale_fangoso.png
  placeholder/habitats/coralligeno.png
  placeholder/habitats/pozze_di_marea.png

  placeholder/backgrounds/sfondo.png   (sfondo generico, opzionale)

Vedi anche ASSETS_NEEDED.md nella stessa cartella.
---------------------------------------------------------------------
"""

import pygame
import random
import time
import json
import os
import math
import colorsys

# --- Pygame Initialization ---
pygame.init()

infoObject = pygame.display.Info()
SCREEN_WIDTH = infoObject.current_w
SCREEN_HEIGHT = infoObject.current_h
screen = pygame.display.set_mode(
    (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Il Fondale Misterioso - Sharper Night 2026")

INITIAL_SCREEN_WIDTH = 2400
INITIAL_SCREEN_HEIGHT = 1200

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
print(BASE_DIR)

# --- Colors ---
BLACK = (20, 20, 20)
WHITE = (255, 255, 255)
SUBTITLE_COLOR = (200, 200, 200)
SEA_BLUE_DARK = (10, 40, 70)
SEA_BLUE_LIGHT = (20, 80, 120)
CARD_BACK_COLOR = (43, 108, 176)
MATCHED_COLOR = (72, 187, 120)
WRONG_COLOR = (220, 90, 90)
BUTTON_COLOR = (255, 165, 0)
BUTTON_COLOR_DISABLED = (120, 110, 90)
BORDER_COLOR = (255, 255, 255)
LABEL_BAR_COLOR = (40, 40, 40, 220)
SELECTED_COLOR = (255, 215, 0)
PANEL_COLOR = (0, 0, 0, 120)

# --- Custom events ---
REVEAL_END_EVENT = pygame.USEREVENT + 1
FLIP_BACK_EVENT = pygame.USEREVENT + 2
QUIZ_ADVANCE_EVENT = pygame.USEREVENT + 3

# --- Leaderboard ---
LEADERBOARD_FILE = os.path.join(BASE_DIR, "leaderboard.json")
leaderboard = []

# =====================================================================
# GAME CONTENT (benthos animals, habitats, avatars, quiz questions)
# =====================================================================

AVATARS = [
    {"id": "squalo_avatar", "name": "Squalo",
        "icon": "placeholder/avatars/avatar_squalo.png"},
    {"id": "polpo_avatar", "name": "Polpo",
        "icon": "placeholder/avatars/avatar_polpo.png"},
    {"id": "stella_avatar", "name": "Stella",
        "icon": "placeholder/avatars/avatar_stella.png"},
    {"id": "delfino_avatar", "name": "Delfino",
        "icon": "placeholder/avatars/avatar_delfino.png"},
    {"id": "tartaruga_avatar", "name": "tartaruga",
        "icon": "placeholder/avatars/avatar_tartaruga.png"},
    {"id": "cavalluccio_avatar", "name": "Cavalluccio",
        "icon": "placeholder/avatars/avatar_cavalluccio.png"},
]

# Six unique animal <-> habitat pairs (used by Level 1 and Level 2)
PAIRS = [
    {"id": "riccio", "animal_name": "Riccio di mare", "animal_icon": "placeholder/animals/riccio.png",
     "habitat_name": "Fondale roccioso", "habitat_icon": "placeholder/habitats/fondale_roccioso.png"},
    {"id": "stella", "animal_name": "Stella marina", "animal_icon": "placeholder/animals/stella.png",
     "habitat_name": "Fondale sabbioso", "habitat_icon": "placeholder/habitats/fondale_sabbioso.png"},
    {"id": "cavalluccio", "animal_name": "Cavalluccio marino", "animal_icon": "placeholder/animals/cavalluccio.png",
     "habitat_name": "Prateria di Posidonia", "habitat_icon": "placeholder/habitats/posidonia.png"},
    {"id": "verme", "animal_name": "Verme tubicolo", "animal_icon": "placeholder/animals/verme_tubicolo.png",
     "habitat_name": "Fondale fangoso", "habitat_icon": "placeholder/habitats/fondale_fangoso.png"},
    {"id": "gorgonia", "animal_name": "Gorgonia", "animal_icon": "placeholder/animals/gorgonia.png",
     "habitat_name": "Fondale coralligeno", "habitat_icon": "placeholder/habitats/coralligeno.png"},
    {"id": "paguro", "animal_name": "Paguro", "animal_icon": "placeholder/animals/paguro.png",
     "habitat_name": "Pozze di marea", "habitat_icon": "placeholder/habitats/pozze_di_marea.png"},
]

'''
QUIZ_QUESTIONS = [
    {"q": "Cosa significa 'benthos'?",
     "options": ["Organismi che vivono sul o nel fondale marino",
                 "Organismi che nuotano liberamente in mare aperto",
                 "Organismi che vivono sulla superficie del mare",
                 "Organismi che vivono nelle nuvole"], "correct": 0},
    {"q": "Il riccio di mare si nutre principalmente di:",
     "options": ["Alghe", "Plastica", "Meduse", "Uccelli marini"], "correct": 0},
    {"q": "La Posidonia oceanica e':",
     "options": ["Una pianta marina che forma vere e proprie praterie",
                 "Un tipo di alga rossa", "Un pesce migratore", "Un crostaceo"], "correct": 0},
    {"q": "Il paguro protegge il suo corpo molle usando:",
     "options": ["Un guscio vuoto trovato sul fondale",
                 "Una corazza propria come il granchio", "Le pinne", "La sabbia"], "correct": 0},
    {"q": "Le gorgonie sono organismi:",
     "options": ["Coloniali, simili a piccoli coralli", "Pesci solitari",
                 "Molluschi bivalvi", "Meduse urticanti"], "correct": 0},
    {"q": "Quale di questi NON e' un animale bentonico?",
     "options": ["Tonno rosso", "Stella marina", "Riccio di mare", "Verme tubicolo"], "correct": 0},
    {"q": "Il fondale fangoso si trova tipicamente:",
     "options": ["In zone calme e profonde con poca corrente",
                 "Solo sulle spiagge", "Solo in superficie", "Solo nei fiumi"], "correct": 0},
    {"q": "Perche' le praterie di Posidonia sono importanti?",
     "options": ["Producono ossigeno e sono nursery per molte specie",
                 "Non hanno alcun ruolo ecologico", "Servono solo come decorazione",
                 "Fanno male ai pesci"], "correct": 0},
    {"q": "I nudibranchi sono:",
     "options": ["Molluschi marini senza conchiglia, spesso molto colorati",
                 "Pesci tropicali", "Piante marine", "Crostacei con chele"], "correct": 0},
    {"q": "Il CNR studia gli ambienti marini soprattutto per:",
     "options": ["Monitorare la biodiversita' e la salute degli ecosistemi",
                 "Costruire porti turistici", "Vendere pesce", "Organizzare regate"], "correct": 0},
]
'''

QUIZ_FILE = os.path.join(BASE_DIR, "questions_level3.json")


def load_quiz_questions():
    if os.path.exists(QUIZ_FILE):
        try:
            with open(QUIZ_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict) and "easy" in data and "difficult" in data:
                    return data
        except Exception as e:
            print(f"Errore caricamento quiz JSON: {e}")
    # Fallback di sicurezza
    return {
        "easy": [{"q": "Lo squalo balena è uno squalo o una balena?", "options": ["Squalo", "Balena"], "correct": 0}],
        "difficult": [{"q": "Che cos’è l’ecosistema?", "options": ["L'acqua", "Il sistema ecologico", "L'insieme di organismi viventi e non viventi che interagiscono tra di loro e con l'ambiente"], "correct": 2}]
    }

# =====================================================================
# IMAGE LOADING WITH GRACEFUL FALLBACK
# (works right now even without real images: draws a colored box with
#  initials; once real PNGs are added at the paths above, they are used
#  automatically without any code change)
# =====================================================================


ORIGINAL_IMAGES = {}
SCALED_CACHE = {}


def _resolve(path):
    return path if os.path.isabs(path) else os.path.join(BASE_DIR, path)


def load_original(path):
    if path in ORIGINAL_IMAGES:
        return ORIGINAL_IMAGES[path]
    img = None
    try:
        img = pygame.image.load(_resolve(path)).convert_alpha()
    except Exception:
        img = None
    ORIGINAL_IMAGES[path] = img
    return img


def _fallback_color(label):
    h = (abs(hash(label)) % 360) / 360.0
    r, g, b = colorsys.hsv_to_rgb(h, 0.55, 0.80)
    return int(r * 255), int(g * 255), int(b * 255)


def make_fallback_surface(size, label):
    w, h = max(2, int(size[0])), max(2, int(size[1]))
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    color = _fallback_color(label)
    radius = max(4, int(min(w, h) * 0.15))
    pygame.draw.rect(surf, color, (0, 0, w, h), border_radius=radius)
    pygame.draw.rect(surf, WHITE, (0, 0, w, h), max(
        2, int(min(w, h) * 0.02)), border_radius=radius)
    font_size = max(10, int(min(w, h) * 0.32))
    f = pygame.font.Font(None, font_size)
    words = [wd for wd in label.split() if wd]
    letters = "".join(wd[0] for wd in words[:2]).upper() if words else "?"
    txt = f.render(letters, True, WHITE)
    trect = txt.get_rect(center=(w // 2, h // 2))
    surf.blit(txt, trect)
    return surf


def get_scaled(path, size, label=""):
    size = (max(2, int(size[0])), max(2, int(size[1])))
    key = (path, size)
    if key in SCALED_CACHE:
        return SCALED_CACHE[key]
    original = load_original(path)
    scaled = None
    if original is not None:
        try:
            scaled = pygame.transform.smoothscale(original, size)
        except Exception:
            scaled = None
    if scaled is None:
        scaled = make_fallback_surface(size, label)
    SCALED_CACHE[key] = scaled
    return scaled


# =====================================================================
# FONTS
# =====================================================================

scale_ratio = 1.0
title_font = subtitle_font = status_font = card_font = label_font = None
leaderboard_font = message_font = button_font = quiz_font = option_font = small_font = None


def initialize_fonts():
    global scale_ratio, title_font, subtitle_font, status_font, card_font
    global label_font, leaderboard_font, message_font, button_font, quiz_font, option_font, small_font

    scale_ratio = min(SCREEN_WIDTH / INITIAL_SCREEN_WIDTH,
                      SCREEN_HEIGHT / INITIAL_SCREEN_HEIGHT)
    scale_ratio = max(scale_ratio, 0.3)

    title_font = pygame.font.Font(None, int(100 * scale_ratio))
    subtitle_font = pygame.font.Font(None, int(70 * scale_ratio))
    status_font = pygame.font.Font(None, int(70 * scale_ratio))
    card_font = pygame.font.Font(None, int(140 * scale_ratio))
    label_font = pygame.font.Font(None, int(50 * scale_ratio))
    leaderboard_font = pygame.font.Font(None, int(46 * scale_ratio))
    message_font = pygame.font.Font(None, int(56 * scale_ratio))
    button_font = pygame.font.Font(None, int(60 * scale_ratio))
    quiz_font = pygame.font.Font(None, int(70 * scale_ratio))
    option_font = pygame.font.Font(None, int(54 * scale_ratio))
    small_font = pygame.font.Font(None, int(38 * scale_ratio))


def draw_text(text, font, color, x, y, align="center"):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    if align == "center":
        text_rect.center = (x, y)
    elif align == "left":
        text_rect.left = x
        text_rect.centery = y
    elif align == "right":
        text_rect.right = x
        text_rect.centery = y
    screen.blit(text_surface, text_rect)
    return text_rect


def draw_panel(rect, alpha=140):
    s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    s.fill((0, 0, 0, alpha))
    screen.blit(s, (rect.x, rect.y))
    pygame.draw.rect(screen, BORDER_COLOR, rect, 2, border_radius=20)


def draw_button(rect, text, font=None, enabled=True, base_color=None):
    font = font or button_font
    color = base_color or (BUTTON_COLOR if enabled else BUTTON_COLOR_DISABLED)
    pygame.draw.rect(screen, color, rect, border_radius=14)
    pygame.draw.rect(screen, BORDER_COLOR, rect, 3, border_radius=14)
    draw_text(text, font, BLACK, rect.centerx, rect.centery)
    return rect


def draw_background():
    bg = get_scaled("placeholder/backgrounds/sfondo.png",
                    (SCREEN_WIDTH, SCREEN_HEIGHT), "Sfondo")
    # If it's a real background image it will fill nicely; if it's the
    # fallback colored box, draw a simple sea gradient instead (nicer default).
    if load_original("placeholder/backgrounds/sfondo.png") is not None:
        screen.blit(bg, (0, 0))
    else:
        for y in range(0, SCREEN_HEIGHT, 4):
            t = y / max(1, SCREEN_HEIGHT)
            r = int(SEA_BLUE_DARK[0] +
                    (SEA_BLUE_LIGHT[0] - SEA_BLUE_DARK[0]) * t)
            g = int(SEA_BLUE_DARK[1] +
                    (SEA_BLUE_LIGHT[1] - SEA_BLUE_DARK[1]) * t)
            b = int(SEA_BLUE_DARK[2] +
                    (SEA_BLUE_LIGHT[2] - SEA_BLUE_DARK[2]) * t)
            pygame.draw.rect(screen, (r, g, b), (0, y, SCREEN_WIDTH, 4))


def draw_header(level_label=""):
    draw_text("Il Fondale Misterioso", title_font, WHITE,
              SCREEN_WIDTH / 2, SCREEN_HEIGHT * 0.07)
    draw_text("Sharper Night 2026 - CNR", subtitle_font,
              SUBTITLE_COLOR, SCREEN_WIDTH / 2, SCREEN_HEIGHT * 0.13)
    if player_name:
        draw_text(f"{player_name}", small_font, WHITE,
                  SCREEN_WIDTH * 0.03, SCREEN_HEIGHT * 0.04, align="left")
    if level_label:
        draw_text(level_label, status_font, WHITE,
                  SCREEN_WIDTH * 0.92, SCREEN_HEIGHT * 0.07)


# =====================================================================
# LEADERBOARD
# =====================================================================

def load_leaderboard():
    if os.path.exists(LEADERBOARD_FILE):
        try:
            with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []


def save_leaderboard():
    try:
        leaderboard.sort(key=lambda x: x["final_score"], reverse=True)
        with open(LEADERBOARD_FILE, "w", encoding="utf-8") as f:
            json.dump(leaderboard, f, indent=4, ensure_ascii=False)
    except IOError as e:
        print(f"Errore nel salvataggio della classifica: {e}")


def get_player_rank(username, final_score):
    sorted_lb = sorted(leaderboard, key=lambda x: x.get(
        "final_score", 0), reverse=True)
    for i, entry in enumerate(sorted_lb):
        if entry["username"] == username and entry["final_score"] == final_score:
            return i + 1
    return None


def draw_leaderboard_box(rect):
    draw_panel(rect)
    draw_text("Classifica:", status_font, WHITE,
              rect.centerx, rect.top + 35 * scale_ratio)
    sorted_lb = sorted(leaderboard, key=lambda x: x.get(
        "final_score", 0), reverse=True)
    y_offset = rect.top + 90 * scale_ratio
    for i, entry in enumerate(sorted_lb[:5]):
        t = entry.get("time", "N/A")
        text = f"{i + 1}. {entry['username']} - {t}s"
        draw_text(text, leaderboard_font, WHITE, rect.left +
                  25 * scale_ratio, y_offset, align="left")
        y_offset += 46 * scale_ratio


# =====================================================================
# PARTICLE EFFECT (final win celebration - kept because it was a hit!)
# =====================================================================

PARTICLES = []
PARTICLE_ICON_PATHS = [p["animal_icon"] for p in PAIRS]


class BenthosParticle:
    def __init__(self, x, y, size):
        self.image_path = random.choice(PARTICLE_ICON_PATHS)
        label = next((p["animal_name"]
                     for p in PAIRS if p["animal_icon"] == self.image_path), "")
        self.image = get_scaled(self.image_path, (size, size), label)
        self.rect = self.image.get_rect(center=(x, y))
        self.x = float(x)
        self.y = float(y)
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(8, 18)
        self.vx = speed * math.cos(angle)
        self.vy = speed * math.sin(angle)
        self.drift_vx = random.uniform(-0.5, 0.5)
        self.drift_vy = random.uniform(-0.5, 0.5)
        self.lifetime = 110
        self.gravity = 0.4

    def update(self):
        self.vy += self.gravity
        self.vx *= 0.98
        self.vy *= 0.98
        self.x += self.vx + self.drift_vx
        self.y += self.vy + self.drift_vy
        self.rect.center = (int(self.x), int(self.y))
        self.lifetime -= 1

    def draw(self, surface):
        if self.lifetime > 0:
            if self.vx != 0 or self.vy != 0:
                angle = math.atan2(self.vy, self.vx) * (180 / math.pi)
                rotated_image = pygame.transform.rotate(self.image, -angle)
                rotated_rect = rotated_image.get_rect(center=self.rect.center)
                surface.blit(rotated_image, rotated_rect)
            else:
                surface.blit(self.image, self.rect)


def launch_win_effect(cx, cy, count=250):
    PARTICLES.clear()
    size = int(80 * scale_ratio)
    for _ in range(count):
        x0 = cx + random.uniform(-20, 20)
        y0 = cy + random.uniform(-20, 20)
        PARTICLES.append(BenthosParticle(x0, y0, size))


# =====================================================================
# GLOBAL GAME / PLAYER STATE
# =====================================================================

STATE = "AVATAR"  # AVATAR -> L1_INTRO -> L1_REVEAL -> L1_PLAY -> L2_INTRO -> L2_PLAY
#                 -> L3_INTRO -> L3_PLAY -> RESULTS

selected_avatar_idx = None
player_name = ""
name_active = True

level1_time = 0.0
level2_time = 0.0
level3_time = 0.0
level2_wrong = 0
level3_wrong = 0

level_start_time = 0.0

# --- Level 1 (memory) state ---
game_board = []
flipped_cards = []
matched_pairs_l1 = 0
can_flip_l1 = True
is_revealing_l1 = False

# --- Level 2 (drag & drop) state ---
habitat_zones = []
drag_items = []
matched_pairs_l2 = 0
dragging_item = None
drag_offset = (0, 0)
flash_zone = None  # (zone, color, until_time)

# --- Level 3 (quiz) state ---
quiz_set = []
quiz_index = 0
quiz_answered = False
quiz_selected = None
quiz_feedback_until = 0

# --- Layout rects (recomputed by update_layout per state) ---
LAYOUT = {}


# =====================================================================
# LAYOUT
# =====================================================================

def update_layout():
    """Recomputes every rect used by the current screen. Called on resize
    and whenever the state changes."""
    global LAYOUT
    LAYOUT = {}

    if STATE == "AVATAR":
        card_size = int(260 * scale_ratio)
        margin = int(40 * scale_ratio)
        cols = 3
        rows = 2
        grid_w = cols * card_size + (cols - 1) * margin
        grid_h = rows * card_size + (rows - 1) * margin
        grid_x = (SCREEN_WIDTH - grid_w) / 2
        grid_y = SCREEN_HEIGHT * 0.28
        rects = []
        for i, av in enumerate(AVATARS):
            r = i // cols
            c = i % cols
            rect = pygame.Rect(grid_x + c * (card_size + margin), grid_y + r * (card_size + margin),
                               card_size, card_size)
            rects.append(rect)
        LAYOUT["avatar_rects"] = rects
        LAYOUT["avatar_size"] = card_size

        box_w = int(SCREEN_WIDTH * 0.28)
        box_h = int(70 * scale_ratio)
        LAYOUT["name_box"] = pygame.Rect(SCREEN_WIDTH / 2 - box_w / 2, grid_y + grid_h + int(60 * scale_ratio),
                                         box_w, box_h)
        btn_w, btn_h = int(280 * scale_ratio), int(80 * scale_ratio)
        LAYOUT["start_btn"] = pygame.Rect(SCREEN_WIDTH / 2 - btn_w / 2,
                                          LAYOUT["name_box"].bottom + int(40 * scale_ratio), btn_w, btn_h)

    elif STATE in ("L1_INTRO", "L2_INTRO", "L3_INTRO"):
        btn_w, btn_h = int(320 * scale_ratio), int(90 * scale_ratio)
        LAYOUT["continue_btn"] = pygame.Rect(
            SCREEN_WIDTH / 2 - btn_w / 2, SCREEN_HEIGHT * 0.78, btn_w, btn_h)

    elif STATE in ("L1_REVEAL", "L1_PLAY"):
        card_size = int(300 * scale_ratio)
        margin = int(45 * scale_ratio)
        cols = 6
        grid_w = cols * card_size + (cols - 1) * margin
        grid_x = (SCREEN_WIDTH - grid_w) / 2
        grid_y_top = SCREEN_HEIGHT * 0.32
        grid_y_bottom = grid_y_top + card_size + margin + int(40 * scale_ratio)
        LAYOUT["card_size"] = card_size
        LAYOUT["grid_x"] = grid_x
        LAYOUT["grid_width"] = grid_w
        LAYOUT["grid_y_top"] = grid_y_top
        LAYOUT["grid_y_bottom"] = grid_y_bottom
        for i, row in enumerate(game_board):
            for j, card in enumerate(row):
                card["rect"] = pygame.Rect(grid_x + j * (card_size + margin),
                                           grid_y_top if i == 0 else grid_y_bottom,
                                           card_size, card_size)

    elif STATE == "L2_PLAY":
        zone_size = int(260 * scale_ratio)
        margin = int(35 * scale_ratio)
        n = len(habitat_zones) if habitat_zones else len(PAIRS)
        total_w = n * zone_size + (n - 1) * margin
        start_x = (SCREEN_WIDTH - total_w) / 2
        zone_y = SCREEN_HEIGHT * 0.28
        for i, zone in enumerate(habitat_zones):
            zone["rect"] = pygame.Rect(
                start_x + i * (zone_size + margin), zone_y, zone_size, zone_size)
        LAYOUT["zone_size"] = zone_size

        item_size = int(170 * scale_ratio)
        item_margin = int(30 * scale_ratio)
        total_iw = len(drag_items) * item_size + \
            (len(drag_items) - 1) * item_margin
        start_ix = (SCREEN_WIDTH - total_iw) / 2
        item_y = SCREEN_HEIGHT * 0.72
        for i, item in enumerate(drag_items):
            home = pygame.Rect(start_ix + i * (item_size +
                               item_margin), item_y, item_size, item_size)
            item["home_rect"] = home
            if not item["placed"] and not item.get("dragging"):
                item["rect"] = home.copy()
        LAYOUT["item_size"] = item_size

    elif STATE == "L3_PLAY":
        box_w = SCREEN_WIDTH * 0.7
        LAYOUT["question_rect"] = pygame.Rect(SCREEN_WIDTH / 2 - box_w / 2, SCREEN_HEIGHT * 0.27, box_w,
                                              int(140 * scale_ratio))
        opt_w = box_w
        opt_h = int(100 * scale_ratio)
        opt_gap = int(24 * scale_ratio)
        opt_rects = []
        top = LAYOUT["question_rect"].bottom + int(50 * scale_ratio)
        for i in range(4):
            r = pygame.Rect(SCREEN_WIDTH / 2 - opt_w / 2, top +
                            i * (opt_h + opt_gap), opt_w, opt_h)
            opt_rects.append(r)
        LAYOUT["option_rects"] = opt_rects

    elif STATE == "RESULTS":
        pad = int(20 * scale_ratio)
        lb_w = SCREEN_WIDTH * 0.32
        lb_h = SCREEN_HEIGHT * 0.36
        LAYOUT["leaderboard_rect"] = pygame.Rect(
            pad, SCREEN_HEIGHT - lb_h - pad, lb_w, lb_h)
        msg_h = SCREEN_HEIGHT * 0.12
        LAYOUT["message_rect"] = pygame.Rect(pad, LAYOUT["leaderboard_rect"].top - msg_h - int(10 * scale_ratio),
                                             lb_w, msg_h)
        btn_w, btn_h = int(320 * scale_ratio), int(90 * scale_ratio)
        LAYOUT["play_again_btn"] = pygame.Rect(SCREEN_WIDTH / 2 - btn_w / 2, SCREEN_HEIGHT - btn_h - int(40 * scale_ratio),
                                               btn_w, btn_h)


def change_state(new_state):
    global STATE
    STATE = new_state
    update_layout()


# =====================================================================
# LEVEL 1 - MEMORY
# =====================================================================

def setup_level1():
    global game_board, flipped_cards, matched_pairs_l1, can_flip_l1, is_revealing_l1, level_start_time
    animal_cards = [{"kind": "animal", "pair_id": i, "icon": p["animal_icon"], "label": p["animal_name"],
                     "is_flipped": False, "is_matched": False} for i, p in enumerate(PAIRS)]
    habitat_cards = [{"kind": "habitat", "pair_id": i, "icon": p["habitat_icon"], "label": p["habitat_name"],
                      "is_flipped": False, "is_matched": False} for i, p in enumerate(PAIRS)]
    random.shuffle(animal_cards)
    random.shuffle(habitat_cards)
    game_board = [animal_cards, habitat_cards]
    flipped_cards.clear()
    matched_pairs_l1 = 0
    can_flip_l1 = False
    is_revealing_l1 = True
    change_state("L1_REVEAL")
    pygame.time.set_timer(REVEAL_END_EVENT, 6000)


def draw_level1_board():
    card_size = LAYOUT["card_size"]
    for row in game_board:
        for card in row:
            rect = card["rect"]
            if is_revealing_l1 or card["is_flipped"] or card["is_matched"]:
                bg = MATCHED_COLOR if card["is_matched"] else BLACK
                pygame.draw.rect(screen, bg, rect, border_radius=20)
                pygame.draw.rect(screen, BORDER_COLOR, rect, int(
                    6 * scale_ratio), border_radius=20)
                img = get_scaled(card["icon"], (card_size - int(24 * scale_ratio), card_size - int(24 * scale_ratio)),
                                 card["label"])
                img_rect = img.get_rect(center=rect.center)
                screen.blit(img, img_rect)
            else:
                pygame.draw.rect(screen, CARD_BACK_COLOR,
                                 rect, border_radius=20)
                pygame.draw.rect(screen, BORDER_COLOR, rect, int(
                    6 * scale_ratio), border_radius=20)
                q = card_font.render("?", True, WHITE)
                qrect = q.get_rect(center=rect.center)
                screen.blit(q, qrect)

    bar_h = label_font.get_height() + int(30 * scale_ratio)
    for label, y in (("Animali:", LAYOUT["grid_y_top"]), ("Habitat:", LAYOUT["grid_y_bottom"])):
        bar_rect = pygame.Rect(
            LAYOUT["grid_x"], y - bar_h, LAYOUT["grid_width"], bar_h)
        s = pygame.Surface((bar_rect.width, bar_rect.height), pygame.SRCALPHA)
        s.fill(LABEL_BAR_COLOR)
        screen.blit(s, (bar_rect.x, bar_rect.y))
        draw_text(label, label_font, WHITE, bar_rect.centerx, bar_rect.centery)


def handle_level1_click(pos):
    global can_flip_l1, matched_pairs_l1
    if not can_flip_l1 or is_revealing_l1:
        return
    for row in game_board:
        for card in row:
            if card["rect"].collidepoint(pos) and not card["is_flipped"] and not card["is_matched"]:
                card["is_flipped"] = True
                flipped_cards.append(card)
                if len(flipped_cards) == 2:
                    can_flip_l1 = False
                    pygame.time.set_timer(FLIP_BACK_EVENT, 1100)
                return


# =====================================================================
# LEVEL 2 - DRAG & DROP
# =====================================================================

def setup_level2():
    global habitat_zones, drag_items, matched_pairs_l2, dragging_item, level2_wrong, level_start_time
    zones = [{"id": p["id"], "name": p["habitat_name"], "icon": p["habitat_icon"], "filled": False, "rect": None}
             for p in PAIRS]
    random.shuffle(zones)
    habitat_zones = zones

    items = [{"id": p["id"], "name": p["animal_name"], "icon": p["animal_icon"], "placed": False,
              "dragging": False, "rect": None, "home_rect": None} for p in PAIRS]
    random.shuffle(items)
    drag_items = items

    matched_pairs_l2 = 0
    dragging_item = None
    level2_wrong = 0
    change_state("L2_PLAY")
    level_start_time = time.time()


def draw_level2_board():
    zone_size = LAYOUT["zone_size"]
    for zone in habitat_zones:
        rect = zone["rect"]
        color = MATCHED_COLOR if zone["filled"] else (30, 60, 90)
        if flash_zone and flash_zone[0] is zone and time.time() < flash_zone[2]:
            color = flash_zone[1]
        pygame.draw.rect(screen, color, rect, border_radius=18)
        pygame.draw.rect(screen, BORDER_COLOR, rect, int(
            4 * scale_ratio), border_radius=18)
        icon_size = zone_size - int(70 * scale_ratio)
        img = get_scaled(zone["icon"], (icon_size, icon_size), zone["name"])
        img_rect = img.get_rect(
            center=(rect.centerx, rect.centery - int(15 * scale_ratio)))
        screen.blit(img, img_rect)
        draw_text(zone["name"], small_font, WHITE, rect.centerx,
                  rect.bottom - int(20 * scale_ratio))

    # draw non-dragging items first, dragging item last (always on top)
    top_item = None
    item_size = LAYOUT["item_size"]
    for item in drag_items:
        if item["placed"]:
            continue
        if item.get("dragging"):
            top_item = item
            continue
        _draw_drag_item(item, item_size)
    if top_item:
        _draw_drag_item(top_item, item_size)


def _draw_drag_item(item, item_size):
    rect = item["rect"]
    pygame.draw.rect(screen, CARD_BACK_COLOR, rect, border_radius=16)
    pygame.draw.rect(screen, BORDER_COLOR, rect, int(
        4 * scale_ratio), border_radius=16)
    img = get_scaled(item["icon"], (item_size - int(24 * scale_ratio),
                     item_size - int(24 * scale_ratio)), item["name"])
    img_rect = img.get_rect(center=rect.center)
    screen.blit(img, img_rect)


def handle_level2_mousedown(pos):
    global dragging_item, drag_offset
    for item in reversed(drag_items):
        if item["placed"]:
            continue
        if item["rect"].collidepoint(pos):
            dragging_item = item
            item["dragging"] = True
            drag_offset = (pos[0] - item["rect"].centerx,
                           pos[1] - item["rect"].centery)
            return


def handle_level2_mousemotion(pos):
    if dragging_item is not None:
        dragging_item["rect"].centerx = pos[0] - drag_offset[0]
        dragging_item["rect"].centery = pos[1] - drag_offset[1]


def handle_level2_mouseup(pos):
    global dragging_item, matched_pairs_l2, level2_wrong, level2_time, flash_zone
    if dragging_item is None:
        return
    item = dragging_item
    item["dragging"] = False
    dropped_zone = None
    for zone in habitat_zones:
        if zone["rect"].colliderect(item["rect"]) and not zone["filled"]:
            dropped_zone = zone
            break

    if dropped_zone is not None:
        if dropped_zone["id"] == item["id"]:
            dropped_zone["filled"] = True
            item["placed"] = True
            item["rect"] = dropped_zone["rect"].copy()
            matched_pairs_l2 += 1
            flash_zone = (dropped_zone, MATCHED_COLOR, time.time() + 0.4)
        else:
            level2_wrong += 1
            item["rect"] = item["home_rect"].copy()
            flash_zone = (dropped_zone, WRONG_COLOR, time.time() + 0.4)
    else:
        item["rect"] = item["home_rect"].copy()

    dragging_item = None

    if matched_pairs_l2 == len(PAIRS):
        level2_time = time.time() - level_start_time
        setup_level3()


# =====================================================================
# LEVEL 3 - QUIZ
# =====================================================================

def setup_level3():
    global quiz_set, quiz_index, quiz_answered, quiz_selected, level3_wrong, level_start_time
    pools = load_quiz_questions()

    easy_q = random.choice(pools.get("easy", [])
                           ) if pools.get("easy") else None
    diff_q = random.choice(pools.get("difficult", [])
                           ) if pools.get("difficult") else None

    selected_pair = []
    if easy_q:
        selected_pair.append(easy_q)
    if diff_q:
        selected_pair.append(diff_q)

    # Mescola l'ordine della domanda facile e difficile
    random.shuffle(selected_pair)
    quiz_set = selected_pair

    for q in quiz_set:
        order = list(range(len(q["options"])))
        random.shuffle(order)
        q["_display_options"] = [q["options"][i] for i in order]
        q["_correct_display_idx"] = order.index(q["correct"])

    quiz_index, quiz_answered, quiz_selected, level3_wrong = 0, False, None, 0
    change_state("L3_INTRO")
    level_start_time = time.time()


def start_level3_play():
    global level_start_time
    change_state("L3_PLAY")
    level_start_time = time.time()


def draw_level3():
    q = quiz_set[quiz_index]
    qrect = LAYOUT["question_rect"]
    draw_panel(qrect, alpha=160)
    draw_text(f"Domanda {quiz_index + 1}/{len(quiz_set)}", small_font, SUBTITLE_COLOR,
              qrect.centerx, qrect.top + int(24 * scale_ratio))
    draw_wrapped_text(q["q"], quiz_font, WHITE, qrect,
                      top_offset=int(50 * scale_ratio))

    for i, opt_text in enumerate(q["_display_options"]):
        rect = LAYOUT["option_rects"][i]
        color = (60, 90, 130)
        if quiz_answered:
            if i == q["_correct_display_idx"]:
                color = MATCHED_COLOR
            elif i == quiz_selected:
                color = WRONG_COLOR
        pygame.draw.rect(screen, color, rect, border_radius=14)
        pygame.draw.rect(screen, BORDER_COLOR, rect, int(
            3 * scale_ratio), border_radius=14)
        draw_wrapped_text(opt_text, option_font, WHITE,
                          rect, top_offset=0, vcenter=True)


def draw_wrapped_text(text, font, color, rect, top_offset=0, vcenter=False, max_width_ratio=0.92):
    max_width = rect.width * max_width_ratio
    words = text.split(" ")
    lines = []
    current = ""
    for w in words:
        trial = (current + " " + w).strip()
        if font.size(trial)[0] <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = w
    if current:
        lines.append(current)

    line_height = font.get_height() + int(4 * scale_ratio)
    total_h = line_height * len(lines)
    if vcenter:
        start_y = rect.centery - total_h / 2 + line_height / 2
    else:
        start_y = rect.top + top_offset + line_height / 2
    for i, line in enumerate(lines):
        draw_text(line, font, color, rect.centerx, start_y + i * line_height)


def handle_level3_click(pos):
    global quiz_answered, quiz_selected, level3_wrong
    if quiz_answered:
        return
    for i, rect in enumerate(LAYOUT["option_rects"]):
        if rect.collidepoint(pos):
            quiz_answered = True
            quiz_selected = i
            q = quiz_set[quiz_index]
            if i != q["_correct_display_idx"]:
                level3_wrong += 1
            pygame.time.set_timer(QUIZ_ADVANCE_EVENT, 1300, loops=1)
            return


def advance_quiz():
    global quiz_index, quiz_answered, quiz_selected, level3_time
    quiz_index += 1
    quiz_answered = False
    quiz_selected = None
    if quiz_index >= len(quiz_set):
        level3_time = time.time() - level_start_time
        setup_results()
    else:
        pass  # stays in L3_PLAY, update_layout not needed (static rects)

# =====================================================================
# RESULTS
# =====================================================================


final_score = 0
total_time_display = 0
player_rank = None


def setup_results():
    global leaderboard, final_score, total_time_display, player_rank
    total_time = level1_time + level2_time + \
        level3_time + level2_wrong * 5 + level3_wrong * 8
    total_time_display = round(total_time, 1)
    final_score = 1000000 - total_time
    entry = {"username": player_name, "avatar": AVATARS[selected_avatar_idx]["name"],
             "final_score": final_score, "time": total_time_display}
    leaderboard = [e for e in leaderboard if e["username"] != player_name]
    leaderboard.append(entry)
    save_leaderboard()
    player_rank = get_player_rank(player_name, final_score)
    change_state("RESULTS")
    launch_win_effect(SCREEN_WIDTH / 2, SCREEN_HEIGHT * 0.35)


def draw_results():
    draw_text("Hai completato il fondale misterioso!", message_font,
              WHITE, SCREEN_WIDTH / 2, SCREEN_HEIGHT * 0.22)
    draw_text(f"Tempo totale: {total_time_display}s", status_font,
              WHITE, SCREEN_WIDTH / 2, SCREEN_HEIGHT * 0.28)

    msg_rect = LAYOUT["message_rect"]
    draw_panel(msg_rect)
    rank_text = f"Posizione in classifica: #{player_rank}" if player_rank else "Posizione in classifica: -"
    draw_text(rank_text, message_font, WHITE,
              msg_rect.centerx, msg_rect.centery)

    draw_leaderboard_box(LAYOUT["leaderboard_rect"])
    draw_button(LAYOUT["play_again_btn"], "Gioca ancora")


def reset_game():
    global selected_avatar_idx, player_name, name_active
    global level1_time, level2_time, level3_time, level2_wrong, level3_wrong
    selected_avatar_idx = None
    player_name = ""
    name_active = True
    level1_time = level2_time = level3_time = 0.0
    level2_wrong = level3_wrong = 0
    change_state("AVATAR")


# =====================================================================
# AVATAR / NAME SCREEN
# =====================================================================

def draw_avatar_screen():
    draw_text("Scegli il tuo avatar e scrivi il tuo nome", subtitle_font, WHITE, SCREEN_WIDTH / 2,
              SCREEN_HEIGHT * 0.2)
    for i, av in enumerate(AVATARS):
        rect = LAYOUT["avatar_rects"][i]
        selected = (i == selected_avatar_idx)
        bg_color = SELECTED_COLOR if selected else (35, 65, 95)
        pygame.draw.rect(screen, bg_color, rect, border_radius=18)
        pygame.draw.rect(screen, BORDER_COLOR, rect, int(
            4 * scale_ratio), border_radius=18)
        icon_size = LAYOUT["avatar_size"] - int(70 * scale_ratio)
        img = get_scaled(av["icon"], (icon_size, icon_size), av["name"])
        img_rect = img.get_rect(
            center=(rect.centerx, rect.centery - int(15 * scale_ratio)))
        screen.blit(img, img_rect)
        text_color = BLACK if selected else WHITE
        draw_text(av["name"], small_font, text_color,
                  rect.centerx, rect.bottom - int(24 * scale_ratio))

    box = LAYOUT["name_box"]
    box_color = (255, 255, 255) if name_active else (180, 180, 180)
    pygame.draw.rect(screen, (25, 45, 65), box, border_radius=10)
    pygame.draw.rect(screen, box_color, box, 3, border_radius=10)
    display_name = player_name if player_name else "Tocca qui e scrivi il tuo nome"
    color = WHITE if player_name else (150, 170, 190)
    draw_text(display_name, status_font, color, box.centerx, box.centery)

    ready = selected_avatar_idx is not None
    draw_button(LAYOUT["start_btn"], "Inizia!", enabled=ready)


def handle_avatar_click(pos):
    global selected_avatar_idx, name_active
    for i, rect in enumerate(LAYOUT["avatar_rects"]):
        if rect.collidepoint(pos):
            selected_avatar_idx = i
            return
    if LAYOUT["name_box"].collidepoint(pos):
        name_active = True
        return
    else:
        name_active = False
    if LAYOUT["start_btn"].collidepoint(pos) and selected_avatar_idx is not None:
        start_adventure()


def start_adventure():
    global player_name
    if not player_name.strip():
        player_name = "Ospite"
    setup_level1()


# =====================================================================
# LEVEL INTRO SCREENS
# =====================================================================

INTRO_TEXTS = {
    "L1_INTRO": ("Livello 1 - Memory", "Trova le coppie: abbina ogni animale al suo habitat!"),
    "L2_INTRO": ("Livello 2 - Trascina!", "Trascina ogni animale nel riquadro del suo habitat."),
    "L3_INTRO": ("Livello 3 - Quiz", "Rispondi alle domande sul benthos il piu' velocemente possibile!"),
}


def draw_level_intro():
    title, subtitle = INTRO_TEXTS[STATE]
    draw_text(title, title_font, WHITE, SCREEN_WIDTH / 2, SCREEN_HEIGHT * 0.4)
    draw_wrapped_text(subtitle, status_font, SUBTITLE_COLOR,
                      pygame.Rect(SCREEN_WIDTH * 0.2, SCREEN_HEIGHT *
                                  0.48, SCREEN_WIDTH * 0.6, SCREEN_HEIGHT * 0.15),
                      top_offset=0)
    draw_button(LAYOUT["continue_btn"], "Vai!")


def handle_level_intro_click(pos):
    if LAYOUT["continue_btn"].collidepoint(pos):
        if STATE == "L1_INTRO":
            setup_level1()
        elif STATE == "L2_INTRO":
            setup_level2()
        elif STATE == "L3_INTRO":
            start_level3_play()


# =====================================================================
# MAIN LOOP
# =====================================================================

def main():
    global SCREEN_WIDTH, SCREEN_HEIGHT, screen, leaderboard, player_name, name_active
    global can_flip_l1, is_revealing_l1, matched_pairs_l1, level1_time, level_start_time

    leaderboard = load_leaderboard()
    initialize_fonts()
    change_state("AVATAR")

    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.VIDEORESIZE:
                SCREEN_WIDTH, SCREEN_HEIGHT = event.size
                screen = pygame.display.set_mode(
                    (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
                initialize_fonts()
                SCALED_CACHE.clear()
                update_layout()

            elif event.type == pygame.KEYDOWN and STATE == "AVATAR" and name_active:
                if event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                elif event.key == pygame.K_RETURN:
                    if selected_avatar_idx is not None:
                        start_adventure()
                elif len(player_name) < 18 and event.unicode.isprintable():
                    player_name += event.unicode

            elif event.type == REVEAL_END_EVENT:
                is_revealing_l1 = False
                can_flip_l1 = True
                level_start_time = time.time()
                pygame.time.set_timer(REVEAL_END_EVENT, 0)
                change_state("L1_PLAY")

            elif event.type == FLIP_BACK_EVENT:
                if len(flipped_cards) == 2:
                    c1, c2 = flipped_cards
                    if c1["pair_id"] == c2["pair_id"] and c1["kind"] != c2["kind"]:
                        c1["is_matched"] = True
                        c2["is_matched"] = True
                        matched_pairs_l1 += 1
                    c1["is_flipped"] = False
                    c2["is_flipped"] = False
                flipped_cards.clear()
                can_flip_l1 = True
                pygame.time.set_timer(FLIP_BACK_EVENT, 0)
                if matched_pairs_l1 == len(PAIRS):
                    level1_time = time.time() - level_start_time
                    change_state("L2_INTRO")

            elif event.type == QUIZ_ADVANCE_EVENT:
                advance_quiz()

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos
                if STATE == "AVATAR":
                    handle_avatar_click(pos)
                elif STATE in ("L1_INTRO", "L2_INTRO", "L3_INTRO"):
                    handle_level_intro_click(pos)
                elif STATE == "L1_PLAY":
                    handle_level1_click(pos)
                elif STATE == "L2_PLAY":
                    handle_level2_mousedown(pos)
                elif STATE == "L3_PLAY":
                    handle_level3_click(pos)
                elif STATE == "RESULTS":
                    if LAYOUT["play_again_btn"].collidepoint(pos):
                        reset_game()

            elif event.type == pygame.MOUSEMOTION and STATE == "L2_PLAY":
                handle_level2_mousemotion(event.pos)

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and STATE == "L2_PLAY":
                handle_level2_mouseup(event.pos)

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        # --- Drawing ---
        draw_background()

        if STATE == "AVATAR":
            draw_header()
            draw_avatar_screen()
        elif STATE in ("L1_INTRO", "L2_INTRO", "L3_INTRO"):
            draw_header()
            draw_level_intro()
        elif STATE in ("L1_REVEAL", "L1_PLAY"):
            draw_header("Livello 1/3")
            draw_level1_board()
        elif STATE == "L2_PLAY":
            draw_header("Livello 2/3")
            draw_level2_board()
        elif STATE == "L3_PLAY":
            draw_header("Livello 3/3")
            draw_level3()
        elif STATE == "RESULTS":
            draw_header()
            draw_results()
            for p in PARTICLES:
                p.update()
                p.draw(screen)
            PARTICLES[:] = [p for p in PARTICLES if p.lifetime > 0]

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
