"""
=====================================================================
 IL FONDALE MISTERIOSO - Gioco sul benthos per Sharper Night 2026
 CNR - Stand del centro citta di Ancona - 25 settembre 2026
=====================================================================

Tre livelli, ognuno con un sotto-livello FACILE e uno DIFFICILE
(1 sfida ciascuno). Un solo avatar/nome e un'unica classifica finale.

LIVELLO 1 - Trova l'intruso   (1 gruppo facile + 1 gruppo difficile)
LIVELLO 2 - Trascina l'animale nel suo habitat
            (facile: aria/spiaggia - colonna d'acqua - fondale;
             difficile: interfaccia aria-acqua / acqua-fondale)
LIVELLO 3 - Quiz              (1 domanda facile + 1 difficile)

---------------------------------------------------------------------
STRUTTURA DELLE CARTELLE (tutto viene LETTO DALLE CARTELLE: aggiungere
o togliere immagini/gruppi non richiede di toccare il codice, tranne
per l'"intruso" dei gruppi del livello 1, vedi INTRUDERS piu' sotto)

placeholder/
  avatars/                 avatar_squalo, avatar_polpo, ... (png/jpg)
  background/sfondo.jpg    sfondo generico (opzionale)
  level1_trova_intruso/
      easy/       group1/ group2/ ...   (4 immagini per gruppo)
      difficult/  group1/ group2/ ...
  level2_trascinamento/
      sfondo.jpg           (aria-acqua / colonna d'acqua / fondale)
      easy/       aria_spiaggia/ colonna_acqua/ fondale/
      difficult/  aria_acqua/ acqua_fondale/
  level3_quiz/questions_level3.json

Le immagini mancanti sono sostituite da un riquadro colorato con le
iniziali, quindi il gioco parte anche con cartelle incomplete.
---------------------------------------------------------------------
"""

import pygame
import random
import time
import json
import os
import math
import re
import zlib

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
BORDER_COLOR = (232, 236, 240)
SELECTED_COLOR = (255, 215, 0)

# --- Custom events ---
ADVANCE_EVENT = pygame.USEREVENT + 1   # fine del feedback -> prossima sfida

# =====================================================================
# FONT PIU' ACCATTIVANTE (con fallback automatico al font di sistema)
# =====================================================================
# Prova, in ordine, alcuni font "amichevoli" spesso presenti sul sistema;
# se nessuno e' installato usa il font di default di pygame senza errori.
PREFERRED_FONT_NAMES = [
    "baloo2", "poppins", "quicksand", "nunito", "varelaround",
    "segoeuisemibold", "segoeui", "trebuchetms", "comicsansms",
    "dejavusans", "verdana", "arial",
]
_FONT_CACHE = {}
_font_path_cache = {"resolved": False, "path": None}


def _resolve_font_path():
    if not _font_path_cache["resolved"]:
        _font_path_cache["resolved"] = True
        for name in PREFERRED_FONT_NAMES:
            try:
                path = pygame.font.match_font(name)
            except Exception:
                path = None
            if path:
                _font_path_cache["path"] = path
                break
    return _font_path_cache["path"]


def load_font(size, bold=False):
    size = max(1, int(size))
    key = (size, bold)
    if key in _FONT_CACHE:
        return _FONT_CACHE[key]
    path = _resolve_font_path()
    try:
        f = pygame.font.Font(
            path, size) if path else pygame.font.Font(None, size)
    except Exception:
        f = pygame.font.Font(None, size)
    try:
        f.set_bold(bold)
    except Exception:
        pass
    _FONT_CACHE[key] = f
    return f

# =====================================================================
# CONFIGURAZIONE
# =====================================================================


PLACEHOLDER_DIR = "placeholder"
L1_DIR = os.path.join(PLACEHOLDER_DIR, "level1_trova_intruso")
L2_DIR = os.path.join(PLACEHOLDER_DIR, "level2_trascinamento")
L2_BACKGROUND = os.path.join(L2_DIR, "sfondo")        # .jpg/.png ok
GENERIC_BG_CANDIDATES = [os.path.join(PLACEHOLDER_DIR, "background", "sfondo"),
                         os.path.join(PLACEHOLDER_DIR, "backgrounds", "sfondo")]
QUIZ_FILE_CANDIDATES = [
    os.path.join(BASE_DIR, PLACEHOLDER_DIR, "level3_quiz",
                 "questions_level3.json"),
    os.path.join(BASE_DIR, "questions_level3.json"),
]
LEADERBOARD_FILE = os.path.join(BASE_DIR, "leaderboard.json")

SUBLEVELS = ("easy", "difficult")
SUB_LABEL = {"easy": "Facile", "difficult": "Difficile"}

# Numero massimo di caratteri per il nome del giocatore
MAX_NAME_LEN = 7

# Penalita' (secondi aggiunti al tempo per ogni errore)
PENALTY_L1 = 8
PENALTY_L2 = 5
PENALTY_L3 = 8

# Livello saltato: vale zero (nessun tempo). Siccome la classifica e' a tempo,
# saltare non deve convenire: ogni livello saltato fa scendere il punteggio
# di questo valore (in "secondi equivalenti"), cosi' chi salta finisce
# SOTTO chiunque abbia completato piu' livelli. Metti 0 per non penalizzare.
SKIP_RANK_PENALTY = 100000

PLAY_STATES = ("L1_PLAY", "L2_PLAY", "L3_PLAY")

# Durata del feedback dopo una risposta (ms). NON conta nel tempo di gioco.
L1_FEEDBACK_MS = 3000
L2_FEEDBACK_MS = 900
L3_FEEDBACK_MS = 1300

# Livello 2: quanti animali (al massimo) per zona in ogni sotto-livello,
# scelti a caso a ogni partita. Metti None per usarli TUTTI.
L2_MAX_PER_ZONE = {"easy": 3, "difficult": 4}

IMG_EXTS = (".jpg", ".jpeg", ".png", ".webp")

# ---------------------------------------------------------------------
# LIVELLO 1: QUAL E' L'INTRUSO DI OGNI GRUPPO?
# Chiave: (sotto-livello, nome cartella del gruppo senza spazi/underscore)
# Valore: (nome file dell'intruso SENZA estensione, spiegazione mostrata)
# !!! Le mie scelte sono DEDUZIONI dai nomi dei file: controllale e
# !!! correggile. I gruppi senza voce qui vengono saltati (con avviso).
# ---------------------------------------------------------------------
INTRUDERS = {
    ("easy", "group1"): ("orata", "L'orata è un pesce: gli altri sono invertebrati che vivono sul fondale."),
    ("easy", "group2"): ("delfino", "Il delfino è un mammifero: gli altri sono pesci."),
    ("easy", "group3"): ("occhiata", "L'occhiata è un pesce: gli altri sono invertebrati che vivono sul fondale."),
    ("easy", "group4"): ("riccio", "Il riccio di mare è un invertebrato: gli altri sono pesci."),
    ("easy", "group5"): ("tartaruga", "La tartaruga marina è un rettile e deve uscire fuori dall'acqua per respirare."),
    ("difficult", "group1"): ("granchio_blu", "Il granchio blu è una specie aliena, non nativa del Mediterraneo."),
    ("difficult", "group2"): ("posidonia", "La Posidonia è una pianta con radici e fiori: le altre sono alghe."),
    ("difficult", "group3"): ("cystoseira", "La Cystoseira è un'alga: gli altri sono animali."),
    ("difficult", "group4"): ("spugna", "La spugna non è un mollusco: gli altri tre lo sono."),
    ("difficult", "group5"): ("pesce_scorpione", "Il pesce scorpione è una specie aliena, non nativa del Mediterraneo."),
}

# ---------------------------------------------------------------------
# LIVELLO 2: dove si trova ogni zona su sfondo.jpg
# (frazioni verticali (alto, basso) dell'area dello sfondo: 0 = cima, 1 = fondo)
# Regola i valori se le fasce del tuo sfondo sono diverse.
# ---------------------------------------------------------------------
ZONE_BANDS = {
    "aria_spiaggia": (0.00, 0.34),
    "colonna_acqua": (0.34, 0.68),
    "fondale": (0.68, 1.00),
    "aria_acqua": (0.00, 0.40),
    "acqua_fondale": (0.60, 1.00),
}
ZONE_LABELS = {
    "aria_spiaggia": "Aria / spiaggia",
    "colonna_acqua": "Colonna d'acqua",
    "fondale": "Fondale",
    "aria_acqua": "Interfaccia aria-acqua",
    "acqua_fondale": "Interfaccia acqua-fondale",
}
L2_HINTS = {
    "easy": "Trascina ogni animale nella zona in cui vive!",
    "difficult": "Attenzione: alcuni animali vivono sulle 'interfacce' (aria-acqua o acqua-fondale)",
}

AVATARS = [
    {"id": "squalo_avatar", "name": "Squalo",
        "icon": "placeholder/avatars/avatar_squalo.png"},
    {"id": "polpo_avatar", "name": "Polpo",
        "icon": "placeholder/avatars/avatar_polpo.png"},
    {"id": "stella_avatar", "name": "Stella",
        "icon": "placeholder/avatars/avatar_stella.png"},
    {"id": "delfino_avatar", "name": "Delfino",
        "icon": "placeholder/avatars/avatar_delfino.png"},
    {"id": "tartaruga_avatar", "name": "Tartaruga",
        "icon": "placeholder/avatars/avatar_tartaruga.png"},
    {"id": "cavalluccio_avatar", "name": "Cavalluccio",
        "icon": "placeholder/avatars/avatar_cavalluccio.png"},
]

# =====================================================================
# UTILITA' FILE / NOMI
# =====================================================================


def _resolve(path):
    return path if os.path.isabs(path) else os.path.join(BASE_DIR, path)


def find_image_path(path):
    """Ritorna il percorso reale del file, provando altre estensioni."""
    full = _resolve(path)
    if os.path.isfile(full):
        return full
    base, _ = os.path.splitext(full)
    for e in IMG_EXTS:
        for cand in (base + e, base + e.upper()):
            if os.path.isfile(cand):
                return cand
    return None


def natural_key(s):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", s)]


def norm_key(s):
    return re.sub(r"[\s_\-]+", "", s.lower())


def list_dirs(folder):
    try:
        names = os.listdir(_resolve(folder))
    except OSError:
        return []
    names = [n for n in names if os.path.isdir(
        os.path.join(_resolve(folder), n))]
    return sorted(names, key=natural_key)


def list_images(folder):
    """Percorsi (relativi a BASE_DIR) delle immagini in una cartella."""
    try:
        names = os.listdir(_resolve(folder))
    except OSError:
        return []
    names = [n for n in names if n.lower().endswith(IMG_EXTS)]
    return [os.path.join(folder, n) for n in sorted(names, key=natural_key)]


def stem_of(path):
    return os.path.splitext(os.path.basename(path))[0]


def split_name(stem):
    """'stella_marina_Astropecten_irregularis' -> ('Stella marina', 'Astropecten irregularis')"""
    tokens = stem.split("_")
    idx = next((i for i, t in enumerate(tokens)
                if i > 0 and t[:1].isupper()), None)
    common = tokens[:idx] if idx else tokens
    sci = tokens[idx:] if idx else []
    return " ".join(common).capitalize(), " ".join(sci)


def full_name(stem):
    common, sci = split_name(stem)
    return f"{common} ({sci})" if sci else common


def zone_label(key):
    return ZONE_LABELS.get(key.lower(), key.replace("_", " ").capitalize())


# =====================================================================
# CARICAMENTO CONTENUTI DALLE CARTELLE
# =====================================================================

def discover_l1_groups(sub):
    base = os.path.join(L1_DIR, sub)
    groups = []
    for gname in list_dirs(base):
        imgs = list_images(os.path.join(base, gname))
        if len(imgs) < 2:
            continue
        info = INTRUDERS.get((sub, norm_key(gname)))
        if info is None:
            print(
                f"[AVVISO] Nessun intruso definito per {sub}/{gname}: gruppo saltato")
            continue
        stems = [stem_of(p).lower() for p in imgs]
        if info[0].lower() not in stems:
            print(
                f"[AVVISO] L'intruso '{info[0]}' non e' in {sub}/{gname}: gruppo saltato")
            continue
        groups.append({"name": gname,
                       "images": [{"path": p, "stem": stem_of(p)} for p in imgs],
                       "intruder": info[0].lower(), "reason": info[1]})
    return groups


def discover_l2_zones(sub):
    base = os.path.join(L2_DIR, sub)
    zones = []
    for zname in list_dirs(base):
        imgs = list_images(os.path.join(base, zname))
        if imgs:
            zones.append({"key": zname, "images": imgs})
    return zones


def load_quiz_questions():
    for path in QUIZ_FILE_CANDIDATES:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    return data
            except Exception as e:
                print(f"Errore caricamento quiz JSON: {e}")
    return {
        "easy": [{"q": "Lo squalo balena è uno squalo o una balena?", "options": ["Squalo", "Balena"], "correct": 0}],
        "difficult": [{"q": "Che cos'è l'ecosistema?", "options": ["L'acqua", "Il sistema ecologico", "L'insieme di organismi viventi e non viventi che interagiscono tra loro e con l'ambiente"], "correct": 2}],
    }


def collect_particle_icons():
    icons = []
    for sub in SUBLEVELS:
        for z in discover_l2_zones(sub):
            for p in z["images"]:
                icons.append((p, split_name(stem_of(p))[0]))
    return icons or [("__none__", "Benthos")]


# =====================================================================
# IMMAGINI CON FALLBACK
# =====================================================================

ORIGINAL_IMAGES = {}
SCALED_CACHE = {}


def load_original(path):
    if path in ORIGINAL_IMAGES:
        return ORIGINAL_IMAGES[path]
    img = None
    real = find_image_path(path)
    if real:
        try:
            img = pygame.image.load(real).convert_alpha()
        except Exception:
            img = None
    ORIGINAL_IMAGES[path] = img
    return img


def _fallback_color(label):
    import colorsys
    h = (zlib.crc32(label.encode("utf-8")) % 360) / 360.0
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
    f = load_font(max(10, int(min(w, h) * 0.32)), bold=True)
    words = [wd for wd in label.split() if wd]
    letters = "".join(wd[0] for wd in words[:2]).upper() if words else "?"
    txt = f.render(letters, True, WHITE)
    surf.blit(txt, txt.get_rect(center=(w // 2, h // 2)))
    return surf


def get_scaled(path, size, label="", mode="stretch", radius=0):
    """mode: 'stretch' (riempie), 'fit' (mantiene proporzioni, contenuta),
    'cover' (mantiene proporzioni, riempie e ritaglia - ideale per foto)."""
    size = (max(2, int(size[0])), max(2, int(size[1])))
    key = (path, size, mode, radius)
    if key in SCALED_CACHE:
        return SCALED_CACHE[key]
    original = load_original(path)
    scaled = None
    if original is not None:
        try:
            w, h = size
            ow, oh = original.get_size()
            if mode == "cover":
                k = max(w / ow, h / oh)
                nw, nh = max(1, round(ow * k)), max(1, round(oh * k))
                tmp = pygame.transform.smoothscale(original, (nw, nh))
                scaled = pygame.Surface((w, h), pygame.SRCALPHA)
                scaled.blit(tmp, ((w - nw) // 2, (h - nh) // 2))
                if radius > 0:
                    mask = pygame.Surface((w, h), pygame.SRCALPHA)
                    pygame.draw.rect(mask, (255, 255, 255, 255),
                                     (0, 0, w, h), border_radius=radius)
                    scaled.blit(mask, (0, 0),
                                special_flags=pygame.BLEND_RGBA_MIN)
            elif mode == "fit":
                k = min(w / ow, h / oh)
                scaled = pygame.transform.smoothscale(
                    original, (max(1, round(ow * k)), max(1, round(oh * k))))
            else:
                scaled = pygame.transform.smoothscale(original, size)
        except Exception:
            scaled = None
    if scaled is None:
        scaled = make_fallback_surface(size, label)
    SCALED_CACHE[key] = scaled
    return scaled


# =====================================================================
# FONT E DISEGNO DI BASE
# =====================================================================

scale_ratio = 1.0
title_font = subtitle_font = status_font = label_font = None
leaderboard_font = message_font = button_font = quiz_font = option_font = None
small_font = tiny_font = None


def initialize_fonts():
    global scale_ratio, title_font, subtitle_font, status_font
    global label_font, leaderboard_font, message_font, button_font
    global quiz_font, option_font, small_font, tiny_font

    scale_ratio = min(SCREEN_WIDTH / INITIAL_SCREEN_WIDTH,
                      SCREEN_HEIGHT / INITIAL_SCREEN_HEIGHT)
    scale_ratio = max(scale_ratio, 0.3)

    title_font = load_font(int(100 * scale_ratio), bold=True)
    subtitle_font = load_font(int(70 * scale_ratio))
    status_font = load_font(int(70 * scale_ratio))
    label_font = load_font(int(50 * scale_ratio))
    leaderboard_font = load_font(int(46 * scale_ratio))
    message_font = load_font(int(56 * scale_ratio), bold=True)
    button_font = load_font(int(60 * scale_ratio), bold=True)
    quiz_font = load_font(int(70 * scale_ratio), bold=True)
    option_font = load_font(int(54 * scale_ratio))
    small_font = load_font(int(38 * scale_ratio))
    tiny_font = load_font(int(28 * scale_ratio))


def draw_text(text, font, color, x, y, align="center"):
    surf = font.render(text, True, color)
    r = surf.get_rect()
    if align == "center":
        r.center = (x, y)
    elif align == "left":
        r.left = x
        r.centery = y
    elif align == "right":
        r.right = x
        r.centery = y
    screen.blit(surf, r)
    return r


def draw_text_fit(text, font, color, cx, cy, max_w):
    surf = font.render(text, True, color)
    if surf.get_width() > max_w > 4:
        h = max(1, int(surf.get_height() * max_w / surf.get_width()))
        surf = pygame.transform.smoothscale(surf, (int(max_w), h))
    screen.blit(surf, surf.get_rect(center=(cx, cy)))


def draw_wrapped_text(text, font, color, rect, top_offset=0, vcenter=False, max_width_ratio=0.92):
    max_width = rect.width * max_width_ratio
    lines, current = [], ""
    for w in text.split(" "):
        trial = (current + " " + w).strip()
        if font.size(trial)[0] <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = w
    if current:
        lines.append(current)
    lh = font.get_height() + int(4 * scale_ratio)
    if vcenter:
        start_y = rect.centery - lh * len(lines) / 2 + lh / 2
    else:
        start_y = rect.top + top_offset + lh / 2
    for i, line in enumerate(lines):
        draw_text(line, font, color, rect.centerx, start_y + i * lh)


def draw_panel(rect, alpha=140):
    s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    s.fill((0, 0, 0, alpha))
    screen.blit(s, (rect.x, rect.y))
    pygame.draw.rect(screen, BORDER_COLOR, rect, 2, border_radius=20)


def draw_overlay(rect, color, alpha):
    s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    s.fill((*color, alpha))
    screen.blit(s, rect.topleft)


def draw_button(rect, text, font=None, enabled=True, base_color=None):
    font = font or button_font
    color = base_color or (BUTTON_COLOR if enabled else BUTTON_COLOR_DISABLED)
    pygame.draw.rect(screen, color, rect, border_radius=14)
    pygame.draw.rect(screen, BORDER_COLOR, rect, 2, border_radius=14)
    draw_text(text, font, BLACK, rect.centerx, rect.centery)
    return rect


_generic_bg = {"searched": False, "path": None}


def draw_background():
    if not _generic_bg["searched"]:
        _generic_bg["searched"] = True
        for c in GENERIC_BG_CANDIDATES:
            p = find_image_path(c)
            if p:
                _generic_bg["path"] = p
                break
    if _generic_bg["path"]:
        screen.blit(get_scaled(_generic_bg["path"],
                    (SCREEN_WIDTH, SCREEN_HEIGHT), "Sfondo"), (0, 0))
        return
    for y in range(0, SCREEN_HEIGHT, 4):
        t = y / max(1, SCREEN_HEIGHT)
        col = tuple(int(SEA_BLUE_DARK[i] + (SEA_BLUE_LIGHT[i] - SEA_BLUE_DARK[i]) * t)
                    for i in range(3))
        pygame.draw.rect(screen, col, (0, y, SCREEN_WIDTH, 4))


def draw_header(level_label=""):
    draw_text("Il Fondale Misterioso", title_font, WHITE,
              SCREEN_WIDTH / 2, SCREEN_HEIGHT * 0.07)
    draw_text("Sharper Night 2026 - CNR", subtitle_font,
              SUBTITLE_COLOR, SCREEN_WIDTH / 2, SCREEN_HEIGHT * 0.13)
    if player_name:
        draw_text(player_name, small_font, WHITE,
                  SCREEN_WIDTH * 0.03, SCREEN_HEIGHT * 0.04, align="left")
    if level_label:
        draw_text(level_label, label_font, WHITE,
                  SCREEN_WIDTH * 0.97, SCREEN_HEIGHT * 0.07, align="right")


# =====================================================================
# CLASSIFICA
# =====================================================================

leaderboard = []


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


def get_player_rank(username, score):
    sorted_lb = sorted(leaderboard, key=lambda x: x.get(
        "final_score", 0), reverse=True)
    for i, entry in enumerate(sorted_lb):
        if entry["username"] == username and entry["final_score"] == score:
            return i + 1
    return None


def resolve_avatar_icon(entry):
    """Ritorna (percorso_icona, etichetta) per una voce di classifica.
    Gestisce anche le voci salvate da versioni precedenti del gioco, che
    non avevano 'avatar_icon': in quel caso cerca l'avatar per id/nome."""
    label = entry.get("avatar", "")
    path = entry.get("avatar_icon")
    if not path:
        match = None
        aid = entry.get("avatar_id")
        if aid:
            match = next((a for a in AVATARS if a["id"] == aid), None)
        if not match and label:
            match = next(
                (a for a in AVATARS if a["name"].lower() == label.lower()), None)
        if match:
            path = match["icon"]
    return path or "__avatar_sconosciuto__", (label or "?")


def draw_leaderboard_box(rect):
    draw_panel(rect)
    draw_text("Classifica:", status_font, WHITE,
              rect.centerx, rect.top + 35 * scale_ratio)
    sorted_lb = sorted(leaderboard, key=lambda x: x.get(
        "final_score", 0), reverse=True)
    icon_size = int(leaderboard_font.get_height() * 0.9)
    row_h = icon_size + int(10 * scale_ratio)
    text_x = rect.left + 25 * scale_ratio + icon_size + int(12 * scale_ratio)
    y = rect.top + 90 * scale_ratio
    any_skipped = False
    for i, entry in enumerate(sorted_lb[:5]):
        sk = entry.get("skipped", 0)
        suffix = f" (salt. {sk})" if sk else ""
        any_skipped = any_skipped or bool(sk)
        icon_path, icon_label = resolve_avatar_icon(entry)
        icon = get_scaled(icon_path, (icon_size, icon_size), icon_label,
                          mode="cover", radius=max(4, int(icon_size * 0.22)))
        screen.blit(icon, (rect.left + 25 * scale_ratio, y - icon_size / 2))
        draw_text(f"{i + 1}. {entry['username']} - {entry.get('time', 'N/A')}s{suffix}",
                  leaderboard_font, WHITE, text_x, y, align="left")
        y += row_h
    if any_skipped:
        draw_text("salt. = livelli saltati", tiny_font, SUBTITLE_COLOR,
                  rect.left + 25 * scale_ratio, rect.bottom - 22 * scale_ratio, align="left")


# =====================================================================
# EFFETTO PARTICELLE FINALE
# =====================================================================

PARTICLES = []
PARTICLE_ICONS = []


class BenthosParticle:
    def __init__(self, x, y, size):
        path, label = random.choice(PARTICLE_ICONS)
        self.image = get_scaled(path, (size, size), label,
                                mode="cover", radius=size // 4)
        self.rect = self.image.get_rect(center=(x, y))
        self.x, self.y = float(x), float(y)
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
            angle = math.degrees(math.atan2(self.vy, self.vx))
            rot = pygame.transform.rotate(self.image, -angle)
            surface.blit(rot, rot.get_rect(center=self.rect.center))


def launch_win_effect(cx, cy, count=250):
    PARTICLES.clear()
    size = int(80 * scale_ratio)
    for _ in range(count):
        PARTICLES.append(BenthosParticle(
            cx + random.uniform(-20, 20), cy + random.uniform(-20, 20), size))


# =====================================================================
# STATO GLOBALE
# =====================================================================

STATE = "AVATAR"  # AVATAR -> L1_INTRO -> L1_PLAY -> L2_INTRO -> L2_PLAY
#                 -> L3_INTRO -> L3_PLAY -> RESULTS

selected_avatar_idx = None
player_name = ""
name_active = True

level1_time = level2_time = level3_time = 0.0
level1_wrong = level2_wrong = level3_wrong = 0
level_start_time = 0.0

# Livello 1
l1_queue = []        # [(sub, group)]
l1_pos = 0
l1_group = None      # gruppo corrente (immagini mescolate)
l1_sub = "easy"
l1_answered = False
l1_selected = None

# Livello 2
l2_queue = []        # [(sub, zones_data)]
l2_pos = 0
l2_zones = []
l2_items = []
l2_matched = 0
l2_locked = False
dragging_item = None
drag_offset = (0, 0)
flash_zone = None    # (zone, color, until_time)

# Livello 3
quiz_set = []
quiz_index = 0
quiz_answered = False
quiz_selected = None

skipped_levels = set()    # numeri dei livelli saltati (1, 2, 3)
skip_confirm = False      # finestra "vuoi saltare?" aperta
skip_confirm_start = 0.0

LAYOUT = {}


def current_sub():
    try:
        if STATE == "L1_PLAY":
            return l1_sub
        if STATE == "L2_PLAY":
            return l2_queue[l2_pos][0]
        if STATE == "L3_PLAY":
            return quiz_set[quiz_index]["_sub"]
    except IndexError:
        pass
    return "easy"


# =====================================================================
# LAYOUT
# =====================================================================

def update_layout():
    """Ricalcola tutti i rettangoli della schermata corrente."""
    global LAYOUT
    LAYOUT = {}
    W, H = SCREEN_WIDTH, SCREEN_HEIGHT

    if STATE == "AVATAR":
        card_size = int(260 * scale_ratio)
        margin = int(40 * scale_ratio)
        cols, rows = 3, 2
        grid_w = cols * card_size + (cols - 1) * margin
        grid_h = rows * card_size + (rows - 1) * margin
        grid_x = (W - grid_w) / 2
        grid_y = H * 0.28
        LAYOUT["avatar_rects"] = [
            pygame.Rect(grid_x + (i % cols) * (card_size + margin),
                        grid_y + (i // cols) * (card_size + margin), card_size, card_size)
            for i in range(len(AVATARS))]
        LAYOUT["avatar_size"] = card_size
        box_w, box_h = int(W * 0.16), int(70 * scale_ratio)
        LAYOUT["name_box"] = pygame.Rect(
            W / 2 - box_w / 2, grid_y + grid_h + int(60 * scale_ratio), box_w, box_h)
        btn_w, btn_h = int(280 * scale_ratio), int(80 * scale_ratio)
        LAYOUT["start_btn"] = pygame.Rect(
            W / 2 - btn_w / 2, LAYOUT["name_box"].bottom + int(70 * scale_ratio), btn_w, btn_h)

    elif STATE in ("L1_INTRO", "L2_INTRO", "L3_INTRO"):
        btn_w, btn_h = int(320 * scale_ratio), int(90 * scale_ratio)
        LAYOUT["continue_btn"] = pygame.Rect(
            W / 2 - btn_w / 2, H * 0.78, btn_w, btn_h)

    elif STATE == "L1_PLAY":
        n = len(l1_group["images"]) if l1_group else 4
        margin = int(W * 0.02)
        card = int(min((W * 0.92 - (n - 1) * margin) / n, H * 0.40))
        x0 = (W - (n * card + (n - 1) * margin)) / 2
        LAYOUT["l1_rects"] = [pygame.Rect(x0 + i * (card + margin), H * 0.34, card, card)
                              for i in range(n)]
        LAYOUT["l1_feedback"] = pygame.Rect(
            W * 0.1, H * 0.83, W * 0.8, H * 0.15)

    elif STATE == "L2_PLAY":
        scene = pygame.Rect(int(W * 0.03), int(H * 0.235),
                            int(W * 0.66), int(H * 0.73))
        LAYOUT["scene"] = scene
        n = max(1, len(l2_zones))
        for i, z in enumerate(l2_zones):
            y0, y1 = ZONE_BANDS.get(z["key"].lower(), (i / n, (i + 1) / n))
            z["rect"] = pygame.Rect(scene.x, scene.y + int(scene.h * y0),
                                    scene.w, int(scene.h * (y1 - y0)))
        # vassoio degli animali (a destra)
        tray = pygame.Rect(int(W * 0.72), scene.y, int(W * 0.25), scene.h)
        LAYOUT["tray"] = tray
        gap = max(4, int(16 * scale_ratio))
        cnt = max(1, len(l2_items))
        best, best_cols = 0, 1
        for cols in range(1, cnt + 1):
            rows = math.ceil(cnt / cols)
            s = min((tray.w - (cols + 1) * gap) / cols,
                    (tray.h - (rows + 1) * gap) / rows)
            if s > best:
                best, best_cols = s, cols
        size = int(min(best, 200 * scale_ratio))
        grid_w = best_cols * size + (best_cols - 1) * gap
        gx = tray.x + (tray.w - grid_w) / 2
        for i, it in enumerate(l2_items):
            r, c = divmod(i, best_cols)
            it["home_rect"] = pygame.Rect(
                gx + c * (size + gap), tray.y + gap + r * (size + gap), size, size)
            if not it["placed"] and not it["dragging"]:
                it["rect"] = it["home_rect"].copy()
        # animali gia' piazzati: disposti dentro la loro zona
        ps = int(110 * scale_ratio)
        label_h = small_font.get_height() + int(24 * scale_ratio)
        for z in l2_zones:
            x = z["rect"].x + gap
            y = z["rect"].y + label_h + gap
            for it in z["placed"]:
                if x + ps > z["rect"].right - gap:
                    x = z["rect"].x + gap
                    y += ps + gap
                it["rect"] = pygame.Rect(x, y, ps, ps)
                x += ps + gap

    elif STATE == "L3_PLAY":
        box_w = W * 0.7
        LAYOUT["question_rect"] = pygame.Rect(
            W / 2 - box_w / 2, H * 0.27, box_w, int(140 * scale_ratio))
        opt_h, opt_gap = int(100 * scale_ratio), int(24 * scale_ratio)
        top = LAYOUT["question_rect"].bottom + int(50 * scale_ratio)
        LAYOUT["option_rects"] = [
            pygame.Rect(W / 2 - box_w / 2, top + i *
                        (opt_h + opt_gap), box_w, opt_h)
            for i in range(4)]

    elif STATE == "RESULTS":
        pad = int(20 * scale_ratio)
        lb_w, lb_h = W * 0.32, H * 0.36
        LAYOUT["leaderboard_rect"] = pygame.Rect(
            pad, H - lb_h - pad, lb_w, lb_h)
        msg_h = H * 0.12
        LAYOUT["message_rect"] = pygame.Rect(
            pad, LAYOUT["leaderboard_rect"].top - msg_h - int(10 * scale_ratio), lb_w, msg_h)
        btn_w, btn_h = int(320 * scale_ratio), int(90 * scale_ratio)
        LAYOUT["play_again_btn"] = pygame.Rect(
            W / 2 - btn_w / 2, H - btn_h - int(40 * scale_ratio), btn_w, btn_h)

    if STATE in PLAY_STATES:
        # pulsante "Salta livello" (in alto a sinistra, sotto il nome)
        LAYOUT["skip_btn"] = pygame.Rect(int(W * 0.03), int(H * 0.085),
                                         int(270 * scale_ratio), int(64 * scale_ratio))
        # finestra di conferma
        mw, mh = int(W * 0.5), int(H * 0.32)
        modal = pygame.Rect(int(W / 2 - mw / 2), int(H / 2 - mh / 2), mw, mh)
        LAYOUT["skip_modal"] = modal
        bw = int(min(400 * scale_ratio, mw * 0.44))
        bh = int(80 * scale_ratio)
        gap = int(30 * scale_ratio)
        by = modal.bottom - bh - int(30 * scale_ratio)
        LAYOUT["skip_yes"] = pygame.Rect(
            modal.centerx - bw - gap // 2, by, bw, bh)
        LAYOUT["skip_no"] = pygame.Rect(modal.centerx + gap // 2, by, bw, bh)


def change_state(new_state):
    global STATE
    STATE = new_state
    update_layout()


def skip_feedback_time(ms):
    """Il tempo del feedback (risposta mostrata) non conta nel cronometro."""
    global level_start_time
    level_start_time += ms / 1000.0


# =====================================================================
# LIVELLO 1 - TROVA L'INTRUSO
# =====================================================================

def prepare_level1():
    global l1_queue
    l1_queue = []
    for sub in SUBLEVELS:
        groups = discover_l1_groups(sub)
        if groups:
            l1_queue.append((sub, random.choice(groups)))
    if l1_queue:
        change_state("L1_INTRO")
    else:
        print("[AVVISO] Nessun gruppo valido per il livello 1: livello saltato")
        prepare_level2()


def load_l1_group():
    global l1_group, l1_sub, l1_answered, l1_selected
    l1_sub, g = l1_queue[l1_pos]
    imgs = list(g["images"])
    random.shuffle(imgs)
    l1_group = {**g, "images": imgs}
    l1_answered, l1_selected = False, None


def start_level1_play():
    global l1_pos, level1_wrong, level_start_time
    l1_pos, level1_wrong = 0, 0
    load_l1_group()
    change_state("L1_PLAY")
    level_start_time = time.time()


def draw_level1():
    g = l1_group
    draw_text("Trova l'intruso!", quiz_font, WHITE,
              SCREEN_WIDTH / 2, SCREEN_HEIGHT * 0.235)
    draw_text("Quale immagine non c'entra con le altre?", label_font,
              SUBTITLE_COLOR, SCREEN_WIDTH / 2, SCREEN_HEIGHT * 0.29)
    radius = int(24 * scale_ratio)
    for i, im in enumerate(g["images"]):
        rect = LAYOUT["l1_rects"][i]
        label = full_name(im["stem"])
        screen.blit(get_scaled(im["path"], rect.size, label,
                    mode="cover", radius=radius), rect.topleft)
        color, width = BORDER_COLOR, max(2, int(3 * scale_ratio))
        if l1_answered:
            if im["stem"].lower() == g["intruder"]:
                color, width = MATCHED_COLOR, max(6, int(12 * scale_ratio))
            elif i == l1_selected:
                color, width = WRONG_COLOR, max(6, int(12 * scale_ratio))
        pygame.draw.rect(screen, color, rect, width, border_radius=radius)
        draw_wrapped_text(label, label_font, WHITE,
                          pygame.Rect(rect.x, rect.bottom + int(10 * scale_ratio),
                                      rect.w, int(90 * scale_ratio)), top_offset=0)
    if l1_answered:
        fb = LAYOUT["l1_feedback"]
        chosen = g["images"][l1_selected]["stem"].lower() == g["intruder"]
        draw_panel(fb, alpha=170)
        draw_text("Esatto!" if chosen else "Non proprio!", message_font,
                  MATCHED_COLOR if chosen else WRONG_COLOR, fb.centerx, fb.top + int(38 * scale_ratio))
        draw_wrapped_text(g["reason"], label_font, WHITE,
                          fb, top_offset=int(70 * scale_ratio))


def handle_level1_click(pos):
    global l1_answered, l1_selected, level1_wrong
    if l1_answered:
        return
    for i, r in enumerate(LAYOUT["l1_rects"]):
        if r.collidepoint(pos):
            l1_answered, l1_selected = True, i
            if l1_group["images"][i]["stem"].lower() != l1_group["intruder"]:
                level1_wrong += 1
            pygame.time.set_timer(ADVANCE_EVENT, L1_FEEDBACK_MS, loops=1)
            return


def advance_level1():
    global l1_pos, level1_time
    skip_feedback_time(L1_FEEDBACK_MS)
    l1_pos += 1
    if l1_pos >= len(l1_queue):
        level1_time = time.time() - level_start_time
        prepare_level2()
    else:
        load_l1_group()
        update_layout()


# =====================================================================
# LIVELLO 2 - TRASCINA L'ANIMALE NELLA SUA ZONA
# =====================================================================

def prepare_level2():
    global l2_queue
    l2_queue = []
    for sub in SUBLEVELS:
        zones = discover_l2_zones(sub)
        if zones:
            l2_queue.append((sub, zones))
    if l2_queue:
        change_state("L2_INTRO")
    else:
        print("[AVVISO] Nessuna immagine per il livello 2: livello saltato")
        prepare_level3()


def load_l2_sublevel():
    global l2_zones, l2_items, l2_matched, l2_locked, dragging_item, flash_zone
    sub, zones_data = l2_queue[l2_pos]
    cap = L2_MAX_PER_ZONE.get(sub)
    l2_zones, l2_items = [], []
    for zd in zones_data:
        l2_zones.append({"key": zd["key"], "label": zone_label(zd["key"]),
                         "rect": None, "placed": []})
        chosen = zd["images"]
        if cap and len(chosen) > cap:
            chosen = random.sample(chosen, cap)
        for p in chosen:
            l2_items.append({"zone": zd["key"], "path": p,
                             "label": split_name(stem_of(p))[0],
                             "placed": False, "dragging": False,
                             "rect": None, "home_rect": None})
    random.shuffle(l2_items)
    l2_matched, l2_locked, dragging_item, flash_zone = 0, False, None, None


def start_level2_play():
    global l2_pos, level2_wrong, level_start_time
    l2_pos, level2_wrong = 0, 0
    load_l2_sublevel()
    change_state("L2_PLAY")
    level_start_time = time.time()


def _zone_fallback_color(key):
    k = key.lower()
    if k.startswith("aria"):
        return (135, 190, 225)
    if "colonna" in k:
        return (30, 100, 160)
    if "fondale" in k:
        return (190, 165, 110)
    return (60, 90, 130)


def _draw_item(item):
    rect = item["rect"]
    pad = max(3, int(6 * scale_ratio))
    pygame.draw.rect(screen, CARD_BACK_COLOR, rect, border_radius=16)
    inner = pygame.Rect(rect.x + pad, rect.y + pad,
                        rect.w - 2 * pad, rect.h - 2 * pad)
    screen.blit(get_scaled(item["path"], inner.size, item["label"], mode="cover",
                           radius=max(4, int(12 * scale_ratio))), inner.topleft)
    if rect.w >= 90 * scale_ratio:
        sh = tiny_font.get_height() + 8
        strip = pygame.Surface((inner.w, sh), pygame.SRCALPHA)
        strip.fill((0, 0, 0, 170))
        screen.blit(strip, (inner.x, inner.bottom - sh))
        draw_text_fit(item["label"], tiny_font, WHITE,
                      inner.centerx, inner.bottom - sh / 2, inner.w - 8)
    pygame.draw.rect(screen, BORDER_COLOR, rect, max(
        1, int(2 * scale_ratio)), border_radius=16)


def draw_level2():
    sub = l2_queue[l2_pos][0]
    draw_text(L2_HINTS.get(sub, ""), label_font, SUBTITLE_COLOR,
              SCREEN_WIDTH / 2, SCREEN_HEIGHT * 0.195)
    scene = LAYOUT["scene"]
    bg_path = find_image_path(L2_BACKGROUND)
    has_bg = bg_path is not None
    if has_bg:
        screen.blit(get_scaled(bg_path, scene.size, "Sfondo"), scene.topleft)
    hover_center = dragging_item["rect"].center if dragging_item else None

    for z in l2_zones:
        r = z["rect"]
        if not has_bg:
            pygame.draw.rect(screen, _zone_fallback_color(z["key"]), r)
        else:
            draw_overlay(r, (0, 0, 0), 25)
        border, bw = BORDER_COLOR, 2
        if flash_zone and flash_zone[0] is z and time.time() < flash_zone[2]:
            draw_overlay(r, flash_zone[1], 130)
        elif hover_center and r.collidepoint(hover_center):
            draw_overlay(r, SELECTED_COLOR, 70)
            border, bw = SELECTED_COLOR, 6
        pygame.draw.rect(screen, border, r, bw)
        # etichetta della zona
        txt = small_font.render(z["label"], True, WHITE)
        pill = pygame.Rect(r.x + int(12 * scale_ratio), r.y + int(10 * scale_ratio),
                           txt.get_width() + int(28 * scale_ratio), txt.get_height() + int(12 * scale_ratio))
        draw_overlay(pill, (0, 0, 0), 170)
        screen.blit(txt, txt.get_rect(center=pill.center))

    draw_panel(LAYOUT["tray"], alpha=110)
    top_item = None
    for it in l2_items:
        if it["dragging"]:
            top_item = it
        else:
            _draw_item(it)
    if top_item:
        _draw_item(top_item)


def handle_level2_mousedown(pos):
    global dragging_item, drag_offset
    if l2_locked:
        return
    for it in reversed(l2_items):
        if not it["placed"] and it["rect"].collidepoint(pos):
            dragging_item = it
            it["dragging"] = True
            drag_offset = (pos[0] - it["rect"].centerx,
                           pos[1] - it["rect"].centery)
            return


def handle_level2_mousemotion(pos):
    if dragging_item is not None:
        dragging_item["rect"].center = (pos[0] - drag_offset[0],
                                        pos[1] - drag_offset[1])


def handle_level2_mouseup(pos):
    global dragging_item, l2_matched, level2_wrong, flash_zone, l2_locked
    if dragging_item is None:
        return
    it = dragging_item
    dragging_item = None
    it["dragging"] = False
    zone = next((z for z in l2_zones
                 if z["rect"].collidepoint(it["rect"].center)), None)
    if zone is None:
        it["rect"] = it["home_rect"].copy()
        return
    if zone["key"] == it["zone"]:
        it["placed"] = True
        zone["placed"].append(it)
        l2_matched += 1
        flash_zone = (zone, MATCHED_COLOR, time.time() + 0.4)
        update_layout()
        if l2_matched == len(l2_items):
            l2_locked = True
            pygame.time.set_timer(ADVANCE_EVENT, L2_FEEDBACK_MS, loops=1)
    else:
        level2_wrong += 1
        it["rect"] = it["home_rect"].copy()
        flash_zone = (zone, WRONG_COLOR, time.time() + 0.4)


def advance_level2():
    global l2_pos, level2_time
    skip_feedback_time(L2_FEEDBACK_MS)
    l2_pos += 1
    if l2_pos >= len(l2_queue):
        level2_time = time.time() - level_start_time
        prepare_level3()
    else:
        load_l2_sublevel()
        update_layout()


# =====================================================================
# LIVELLO 3 - QUIZ
# =====================================================================

def prepare_level3():
    global quiz_set, quiz_index, quiz_answered, quiz_selected, level3_wrong
    pools = load_quiz_questions()
    quiz_set = []
    for sub in SUBLEVELS:
        pool = pools.get(sub) or []
        if pool:
            q = dict(random.choice(pool))
            q["_sub"] = sub
            order = list(range(len(q["options"])))
            random.shuffle(order)
            q["_display_options"] = [q["options"][i] for i in order]
            q["_correct_display_idx"] = order.index(q["correct"])
            quiz_set.append(q)
    quiz_index, quiz_answered, quiz_selected, level3_wrong = 0, False, None, 0
    if quiz_set:
        change_state("L3_INTRO")
    else:
        setup_results()


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
        pygame.draw.rect(screen, BORDER_COLOR, rect, max(1, int(
            2 * scale_ratio)), border_radius=14)
        draw_wrapped_text(opt_text, option_font, WHITE,
                          rect, top_offset=0, vcenter=True)


def handle_level3_click(pos):
    global quiz_answered, quiz_selected, level3_wrong
    if quiz_answered:
        return
    q = quiz_set[quiz_index]
    for i in range(len(q["_display_options"])):
        if LAYOUT["option_rects"][i].collidepoint(pos):
            quiz_answered, quiz_selected = True, i
            if i != q["_correct_display_idx"]:
                level3_wrong += 1
            pygame.time.set_timer(ADVANCE_EVENT, L3_FEEDBACK_MS, loops=1)
            return


def advance_quiz():
    global quiz_index, quiz_answered, quiz_selected, level3_time
    skip_feedback_time(L3_FEEDBACK_MS)
    quiz_index += 1
    quiz_answered, quiz_selected = False, None
    if quiz_index >= len(quiz_set):
        level3_time = time.time() - level_start_time
        setup_results()


# =====================================================================
# SALTA LIVELLO
# =====================================================================

def skip_available():
    """Il pulsante e' attivo solo quando non c'e' un feedback in corso."""
    if STATE == "L1_PLAY":
        return not l1_answered
    if STATE == "L2_PLAY":
        return not l2_locked and dragging_item is None
    if STATE == "L3_PLAY":
        return not quiz_answered
    return False


def skip_current_level():
    global level1_time, level2_time, level3_time
    global level1_wrong, level2_wrong, level3_wrong, dragging_item
    pygame.time.set_timer(ADVANCE_EVENT, 0)
    if dragging_item is not None:
        dragging_item["dragging"] = False
        dragging_item = None
    if STATE == "L1_PLAY":
        skipped_levels.add(1)
        level1_time, level1_wrong = 0.0, 0
        prepare_level2()
    elif STATE == "L2_PLAY":
        skipped_levels.add(2)
        level2_time, level2_wrong = 0.0, 0
        prepare_level3()
    elif STATE == "L3_PLAY":
        skipped_levels.add(3)
        level3_time, level3_wrong = 0.0, 0
        setup_results()


def handle_skip_click(pos):
    """Ritorna True se il click e' stato consumato dalla UI di skip."""
    global skip_confirm, skip_confirm_start, level_start_time
    if skip_confirm:
        if LAYOUT["skip_yes"].collidepoint(pos):
            skip_confirm = False
            skip_current_level()
        elif LAYOUT["skip_no"].collidepoint(pos):
            skip_confirm = False
            level_start_time += time.time() - skip_confirm_start  # pausa
        return True
    if skip_available() and LAYOUT["skip_btn"].collidepoint(pos):
        skip_confirm = True
        skip_confirm_start = time.time()
        return True
    return False


def draw_skip_ui():
    if skip_available():
        draw_button(LAYOUT["skip_btn"], "Salta livello",
                    font=small_font, base_color=(215, 215, 215))
    if skip_confirm:
        overlay = pygame.Surface(
            (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        screen.blit(overlay, (0, 0))
        modal = LAYOUT["skip_modal"]
        pygame.draw.rect(screen, (25, 45, 65), modal, border_radius=20)
        pygame.draw.rect(screen, BORDER_COLOR, modal, 2, border_radius=20)
        draw_text("Vuoi saltare questo livello?", message_font, WHITE,
                  modal.centerx, modal.top + int(50 * scale_ratio))
        draw_wrapped_text("Il livello varrà zero e in classifica scenderai sotto chi lo completa.",
                          label_font, SUBTITLE_COLOR, modal, top_offset=int(90 * scale_ratio))
        draw_button(LAYOUT["skip_yes"], "Sì, salta",
                    font=small_font, base_color=(230, 120, 120))
        draw_button(LAYOUT["skip_no"], "Continua a giocare", font=small_font)


def on_advance():
    if STATE == "L1_PLAY":
        advance_level1()
    elif STATE == "L2_PLAY":
        advance_level2()
    elif STATE == "L3_PLAY":
        advance_quiz()


# =====================================================================
# RISULTATI
# =====================================================================

final_score = 0
total_time_display = 0
player_rank = None


def setup_results():
    global leaderboard, final_score, total_time_display, player_rank
    total_time = (level1_time + level2_time + level3_time
                  + level1_wrong * PENALTY_L1 + level2_wrong * PENALTY_L2
                  + level3_wrong * PENALTY_L3)
    total_time_display = round(total_time, 1)
    n_skipped = len(skipped_levels)
    final_score = 1000000 - total_time - SKIP_RANK_PENALTY * n_skipped
    chosen_avatar = AVATARS[selected_avatar_idx]
    entry = {"username": player_name, "avatar": chosen_avatar["name"],
             "avatar_id": chosen_avatar["id"], "avatar_icon": chosen_avatar["icon"],
             "final_score": final_score, "time": total_time_display,
             "skipped": n_skipped}
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
    if skipped_levels:
        draw_text(f"Livelli saltati: {len(skipped_levels)} (valgono zero)", label_font,
                  SUBTITLE_COLOR, SCREEN_WIDTH / 2, SCREEN_HEIGHT * 0.33)
    msg_rect = LAYOUT["message_rect"]
    draw_panel(msg_rect)
    rank_text = f"Posizione in classifica: #{player_rank}" if player_rank else "Posizione in classifica: -"
    draw_text(rank_text, message_font, WHITE,
              msg_rect.centerx, msg_rect.centery)
    draw_leaderboard_box(LAYOUT["leaderboard_rect"])
    draw_button(LAYOUT["play_again_btn"], "Gioca ancora")


def reset_game():
    global selected_avatar_idx, player_name, name_active
    global level1_time, level2_time, level3_time
    global level1_wrong, level2_wrong, level3_wrong
    global skip_confirm, skip_confirm_start
    selected_avatar_idx = None
    player_name = ""
    name_active = True
    level1_time = level2_time = level3_time = 0.0
    level1_wrong = level2_wrong = level3_wrong = 0
    skipped_levels.clear()
    skip_confirm = False
    skip_confirm_start = 0.0
    PARTICLES.clear()
    change_state("AVATAR")


# =====================================================================
# AVATAR / NOME
# =====================================================================

def draw_avatar_screen():
    draw_text("Scegli il tuo avatar e scrivi il tuo nome", subtitle_font, WHITE,
              SCREEN_WIDTH / 2, SCREEN_HEIGHT * 0.2)
    for i, av in enumerate(AVATARS):
        rect = LAYOUT["avatar_rects"][i]
        selected = (i == selected_avatar_idx)
        pygame.draw.rect(screen, SELECTED_COLOR if selected else (35, 65, 95),
                         rect, border_radius=18)
        pygame.draw.rect(screen, BORDER_COLOR, rect, max(1, int(
            2 * scale_ratio)), border_radius=18)
        icon_size = LAYOUT["avatar_size"] - int(70 * scale_ratio)
        img = get_scaled(av["icon"], (icon_size, icon_size),
                         av["name"], mode="fit")
        screen.blit(img, img.get_rect(
            center=(rect.centerx, rect.centery - int(15 * scale_ratio))))
        draw_text(av["name"], small_font, BLACK if selected else WHITE,
                  rect.centerx, rect.bottom - int(24 * scale_ratio))

    box = LAYOUT["name_box"]
    pygame.draw.rect(screen, (25, 45, 65), box, border_radius=14)
    pygame.draw.rect(screen, (255, 255, 255) if name_active else (150, 160, 175),
                     box, max(1, int(2 * scale_ratio)), border_radius=14)
    display_name = player_name if player_name else "Nome"
    draw_text_fit(display_name, status_font, WHITE if player_name else (150, 170, 190),
                  box.centerx, box.centery, box.width - int(24 * scale_ratio))
    draw_text(f"max {MAX_NAME_LEN} caratteri", tiny_font, SUBTITLE_COLOR,
              box.centerx, box.bottom + int(22 * scale_ratio))
    draw_button(LAYOUT["start_btn"], "Inizia!",
                enabled=selected_avatar_idx is not None)


def handle_avatar_click(pos):
    global selected_avatar_idx, name_active
    for i, rect in enumerate(LAYOUT["avatar_rects"]):
        if rect.collidepoint(pos):
            selected_avatar_idx = i
            return
    if LAYOUT["name_box"].collidepoint(pos):
        name_active = True
        return
    name_active = False
    if LAYOUT["start_btn"].collidepoint(pos) and selected_avatar_idx is not None:
        start_adventure()


def start_adventure():
    global player_name
    if not player_name.strip():
        player_name = "Ospite"
    prepare_level1()


# =====================================================================
# SCHERMATE DI INTRODUZIONE
# =====================================================================

INTRO_TEXTS = {
    "L1_INTRO": ("Livello 1 - Trova l'intruso",
                 "In ogni gruppo un'immagine non c'entra con le altre: trovala! Prima una sfida facile, poi una difficile."),
    "L2_INTRO": ("Livello 2 - Trascina!",
                 "Trascina ogni animale nella zona in cui vive: aria, colonna d'acqua o fondale. Poi si sale di difficoltà!"),
    "L3_INTRO": ("Livello 3 - Quiz",
                 "Rispondi alle domande sul mare il più velocemente possibile!"),
}


def draw_level_intro():
    title, subtitle = INTRO_TEXTS[STATE]
    draw_text(title, title_font, WHITE, SCREEN_WIDTH / 2, SCREEN_HEIGHT * 0.4)
    draw_wrapped_text(subtitle, status_font, SUBTITLE_COLOR,
                      pygame.Rect(SCREEN_WIDTH * 0.2, SCREEN_HEIGHT * 0.48,
                                  SCREEN_WIDTH * 0.6, SCREEN_HEIGHT * 0.2))
    draw_button(LAYOUT["continue_btn"], "Vai!")


def handle_level_intro_click(pos):
    if LAYOUT["continue_btn"].collidepoint(pos):
        if STATE == "L1_INTRO":
            start_level1_play()
        elif STATE == "L2_INTRO":
            start_level2_play()
        elif STATE == "L3_INTRO":
            start_level3_play()


# =====================================================================
# MAIN LOOP
# =====================================================================

def main():
    global SCREEN_WIDTH, SCREEN_HEIGHT, screen, leaderboard, player_name, name_active
    global PARTICLE_ICONS

    leaderboard = load_leaderboard()
    PARTICLE_ICONS = collect_particle_icons()
    initialize_fonts()
    change_state("AVATAR")

    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
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
                elif event.unicode and len(player_name) < MAX_NAME_LEN and event.unicode.isprintable():
                    player_name += event.unicode

            elif event.type == ADVANCE_EVENT:
                on_advance()

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos
                if STATE == "AVATAR":
                    handle_avatar_click(pos)
                elif STATE in ("L1_INTRO", "L2_INTRO", "L3_INTRO"):
                    handle_level_intro_click(pos)
                elif STATE in PLAY_STATES and handle_skip_click(pos):
                    pass  # click consumato dal bottone/dialogo "Salta livello"
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

        # --- Drawing ---
        draw_background()

        if STATE == "AVATAR":
            draw_header()
            draw_avatar_screen()
        elif STATE in ("L1_INTRO", "L2_INTRO", "L3_INTRO"):
            draw_header()
            draw_level_intro()
        elif STATE == "L1_PLAY":
            draw_header(f"Livello 1/3 - {SUB_LABEL[current_sub()]}")
            draw_level1()
            draw_skip_ui()
        elif STATE == "L2_PLAY":
            draw_header(f"Livello 2/3 - {SUB_LABEL[current_sub()]}")
            draw_level2()
            draw_skip_ui()
        elif STATE == "L3_PLAY":
            draw_header(f"Livello 3/3 - {SUB_LABEL[current_sub()]}")
            draw_level3()
            draw_skip_ui()
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
