import os
import random
import time
import math
import pygame
import sys
import array

# --- CONFIGURACIÓN DE PYGAME ---
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2)
pygame.font.init()

info = pygame.display.Info()
SCREEN_WIDTH = info.current_w
SCREEN_HEIGHT = info.current_h
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Math Roulette: Cyber Elegance Pro")
clock = pygame.time.Clock()
FPS = 60
CARD_SPACING = 16
VICTORY_ROUND = 10
RESET_HOLD_SECONDS = 1.5

# --- PALETA DE COLORES CYBERPUNK PREMIUM ---
BG_DARK_MAIN = (10, 11, 18)
BG_CANVAS = (16, 20, 32)
COLOR_HEADER = (22, 27, 44)
BORDER_BLUE = (48, 63, 96)
COLOR_TEXT_MUTED = (160, 174, 192)
COLOR_GOLD = (250, 180, 25)
COLOR_CYAN = (34, 211, 238)

RARITIES = {
    "Común": {"bg": (33, 41, 54), "text": (243, 244, 246), "price": 3, "color": (156, 163, 175)},
    "Raro": {"bg": (20, 35, 75), "text": (56, 189, 248), "price": 9, "color": (14, 165, 233)},
    "Épico": {"bg": (65, 20, 85), "text": (216, 180, 254), "price": 22, "color": (168, 85, 247)},
    "Legendario": {"bg": (65, 35, 0), "text": (253, 224, 71), "price": 50, "color": (234, 179, 8)},
    "Rainbow": {"bg": (45, 5, 80), "text": (244, 63, 94), "price": 85, "color": (244, 63, 94)},
}

BAD_ITEM_STYLE = {"bg": (65, 12, 12), "text": (248, 113, 113)}

POOL_ITEMS = {
    "Común": [
        {"type": "add", "value": 1, "name": "+1 [CR]", "rarity": "Común"},
        {"type": "add", "value": 2, "name": "+2 [CR]", "rarity": "Común"},
        {"type": "add", "value": 3, "name": "+3 [CR]", "rarity": "Común"},
        {"type": "sub", "value": 1, "name": "-1 [CR]", "rarity": "Común"},
    ],
    "Raro": [
        {"type": "add", "value": 5, "name": "+5 [CR]", "rarity": "Raro"},
        {"type": "add", "value": 7, "name": "+7 [CR]", "rarity": "Raro"},
        {"type": "sub", "value": 3, "name": "-3 [CR]", "rarity": "Raro"},
        {"type": "div", "value": 1.2, "name": "/1.2 [CR]", "rarity": "Raro"},
    ],
    "Épico": [
        {"type": "add", "value": 10, "name": "+10 [CR]", "rarity": "Épico"},
        {"type": "sub", "value": 4, "name": "-4 [CR]", "rarity": "Épico"},
        {"type": "div", "value": 1.4, "name": "/1.4 [CR]", "rarity": "Épico"},
    ],
    "Legendario": [
        {"type": "mult", "value": 1.5, "name": "x1.5 [CR]", "rarity": "Legendario"},
        {"type": "mult", "value": 1.8, "name": "x1.8 [CR]", "rarity": "Legendario"},
        {"type": "div", "value": 1.5, "name": "/1.5 [CR]", "rarity": "Legendario"},
    ],
    "Rainbow": [
        {"type": "pow", "value": 2, "name": "^2 [CR]", "rarity": "Rainbow"},
        {"type": "zero", "value": 0, "name": "A 0 [CR]", "rarity": "Rainbow"},
    ],

}

BOSS_BLINDS = [
    {"id": "blind_blind", "name": "[MOD] OJO DE HALCON", "desc": "Los efectos de riesgo son invisibles en la ruleta."},
    {"id": "minus_spin", "name": "[MOD] BRAZO FUERTE", "desc": "Tienes -1 tirada maxima permitida esta ronda."},
    {"id": "inflation", "name": "[MOD] IMPUESTO", "desc": "La inflacion ataca: Todo en la tienda cuesta +30%."},
    {"id": "no_interest", "name": "[MOD] BOLSILLO ROTO", "desc": "No puedes ganar intereses de oro al acabar esta ronda."}
]

NO_BOSS = {"id": "none", "name": "[LIBRE] SIN RESTRICCIONES", "desc": "Ronda inicial de aprendizaje. Sin penalizadores."}

NEGATIVE_SCHEDULE = {
    2: {"type": "sub", "value": 1, "name": "-1 [CR]", "rarity": "Común"},
    4: {"type": "sub", "value": 3, "name": "-3 [CR]", "rarity": "Raro"},
    6: {"type": "sub", "value": 4, "name": "-4 [CR]", "rarity": "Épico"},
    8: {"type": "div", "value": 1.2, "name": "/1.2 [CR]", "rarity": "Raro"},
    10: {"type": "div", "value": 1.4, "name": "/1.4 [CR]", "rarity": "Épico"},
    12: {"type": "div", "value": 1.5, "name": "/1.5 [CR]", "rarity": "Legendario"},
}

# --- AUDIO SINTÉTICO ---
def generate_click_sound(pitch_factor=1.0, dual_mode=False):
    duration = 0.025; sample_rate = 22050
    frequency = int(480 * pitch_factor)
    num_samples = int(duration * sample_rate)
    buf = array.array('h', [0] * num_samples)
    volume = 2800 if dual_mode else 5500 
    for i in range(num_samples):
        t = i / sample_rate
        val = volume if (int(t * frequency * 2) % 2 == 0) else -volume
        buf[i] = int(val * math.pow(1.0 - (i / num_samples), 1.5))
    return pygame.mixer.Sound(buffer=buf)

def generate_win_sound():
    duration = 0.35; sample_rate = 22050
    num_samples = int(duration * sample_rate)
    buf = array.array('h', [0] * num_samples)
    for i in range(num_samples):
        t = i / sample_rate
        freq = 300 + (int(t * 12) * 65)
        val = int(10000 * math.sin(2 * math.pi * freq * t))
        buf[i] = int(val * (1.0 - (i / num_samples)))
    return pygame.mixer.Sound(buffer=buf)

def generate_fail_sound():
    duration = 0.4; sample_rate = 22050
    num_samples = int(duration * sample_rate)
    buf = array.array('h', [0] * num_samples)
    for i in range(num_samples):
        t = i / sample_rate
        freq = 180 - (i / num_samples) * 80
        val = 8000 if (int(t * freq * 2) % 2 == 0) else -8000
        buf[i] = int(val * (1.0 - (i / num_samples)))
    return pygame.mixer.Sound(buffer=buf)

SOUND_WIN = generate_win_sound()
SOUND_FAIL = generate_fail_sound()
CLICK_POOL_SINGLE = [generate_click_sound(f, False) for f in [0.9, 0.95, 1.0, 1.05, 1.1]]
CLICK_POOL_DUAL = [generate_click_sound(f, True) for f in [0.85, 0.9, 0.95, 1.0, 1.05]]

def generate_buy_sound():
    duration = 0.2; sample_rate = 22050
    num_samples = int(duration * sample_rate)
    buf = array.array('h', [0] * num_samples)
    for i in range(num_samples):
        t = i / sample_rate
        freq = 800 + (t * 2000)
        val = int(12000 * math.sin(2 * math.pi * freq * t))
        buf[i] = int(val * (1.0 - (i / num_samples)))
    return pygame.mixer.Sound(buffer=buf)

def generate_reroll_sound():
    duration = 0.15; sample_rate = 22050
    num_samples = int(duration * sample_rate)
    buf = array.array('h', [0] * num_samples)
    for i in range(num_samples):
        t = i / sample_rate
        freq = 200 + (t * 400) + int(t * 60) * 50
        val = 6000 if (int(t * freq * 2) % 2 == 0) else -6000
        buf[i] = int(val * (1.0 - (i / num_samples)))
    return pygame.mixer.Sound(buffer=buf)

def generate_next_round_sound():
    duration = 0.4; sample_rate = 22050
    num_samples = int(duration * sample_rate)
    buf = array.array('h', [0] * num_samples)
    for i in range(num_samples):
        t = i / sample_rate
        freq = 400 + (t * 600)
        val = int(10000 * (math.sin(2 * math.pi * freq * t) + 0.5 * math.sin(2 * math.pi * freq * 1.5 * t)))
        buf[i] = int(val * (1.0 - (i / num_samples)))
    return pygame.mixer.Sound(buffer=buf)

def generate_sparkle_sound():
    duration = 0.25; sample_rate = 22050
    num_samples = int(duration * sample_rate)
    buf = array.array('h', [0] * num_samples)
    for i in range(num_samples):
        t = i / sample_rate
        freq = 1200 + (t * 3000)
        val = int(8000 * math.sin(2 * math.pi * freq * t) * (0.5 + 0.5 * math.sin(2 * math.pi * 40 * t)))
        buf[i] = int(val * (1.0 - (i / num_samples)))
    return pygame.mixer.Sound(buffer=buf)

def generate_relic_sound():
    duration = 0.35; sample_rate = 22050
    num_samples = int(duration * sample_rate)
    buf = array.array('h', [0] * num_samples)
    for i in range(num_samples):
        t = i / sample_rate
        freq = 500 + (t * 1200)
        val = int(10000 * (math.sin(2 * math.pi * freq * t) + 0.3 * math.sin(2 * math.pi * freq * 2.0 * t)))
        buf[i] = int(val * (1.0 - (i / num_samples)))
    return pygame.mixer.Sound(buffer=buf)

SOUND_BUY = generate_buy_sound()
SOUND_REROLL = generate_reroll_sound()
SOUND_NEXT_ROUND = generate_next_round_sound()
SOUND_SPARKLE = generate_sparkle_sound()
SOUND_RELIC = generate_relic_sound()

MASTER_VOLUME = 1.0
SFX_VOLUME = 1.0
MUSIC_VOLUME = 1.0
MUSIC_VOLUME_CAP = 0.4

def play_sound(sound):
    sound.set_volume(MASTER_VOLUME * SFX_VOLUME)
    sound.play()

def play_dynamic_click(velocity, is_dual=False):
    factor = max(0.75, min(1.2, velocity / 40.0))
    pool = CLICK_POOL_DUAL if is_dual else CLICK_POOL_SINGLE
    sound = random.choice(pool)
    sound.set_volume(MASTER_VOLUME * SFX_VOLUME)
    sound.play()

_FONT_CACHE = {}
_FONT_NAME = "Consolas" if os.name == "nt" else "Courier New"

def get_font(size, bold=False):
    key = (size, bold)
    if key not in _FONT_CACHE:
        _FONT_CACHE[key] = pygame.font.SysFont(_FONT_NAME, size, bold)
    return _FONT_CACHE[key]

def lerp(a, b, t):
    return a + (b - a) * t

def draw_panel(surface, rect, fill, border=BORDER_BLUE, radius=10, border_w=1):
    pygame.draw.rect(surface, fill, rect, border_radius=radius)
    pygame.draw.rect(surface, border, rect, width=border_w, border_radius=radius)

def draw_progress_bar(surface, x, y, w, h, progress, fill, bg=(20, 24, 38), border=(60, 72, 95)):
    progress = max(0.0, min(1.0, progress))
    pygame.draw.rect(surface, bg, (x, y, w, h), border_radius=h // 2)
    if progress > 0:
        pygame.draw.rect(surface, fill, (x, y, int(w * progress), h), border_radius=h // 2)
    pygame.draw.rect(surface, border, (x, y, w, h), width=1, border_radius=h // 2)

def rainbow_color(t):
    r = int(127 + 127 * math.sin(t))
    g = int(127 + 127 * math.sin(t + 2.09))
    b = int(127 + 127 * math.sin(t + 4.18))
    return (r, g, b)

def scale(size):
    return max(size, int(size * SCREEN_HEIGHT / 900))

VOUCHER_DEFS = {
    "pack_up": {
        "name": "Vale: Magnate [V]", "price": 14,
        "desc": "Sobres contienen +1 opcion.",
        "primary": (234, 179, 8), "secondary": (250, 204, 21),
    },
    "shop_up": {
        "name": "Vale: Expansion [V]", "price": 18,
        "desc": "Anade +1 hueco en la tienda.",
        "primary": (59, 130, 246), "secondary": (147, 197, 253),
    },
    "dual_roulette": {
        "name": "Vale: Lazo Cuantico [V]", "price": 25,
        "desc": "Anade ruleta dual activa.",
        "primary": (168, 85, 247), "secondary": (216, 180, 254),
    },
    "extra_spin": {
        "name": "Vale: Motor Perpetuo [V]", "price": 20,
        "desc": "Aumenta +1 tus tiradas maximas.",
        "primary": (16, 185, 129), "secondary": (110, 231, 183),
    },
}

RELICS_POOL = {
    "tarjeta_clonada": {"name": "Tarjeta Clonada", "desc": "Permite saldo negativo de hasta -15 $.", "price": 12, "rarity": "Raro"},
    "mejora_progresiva": {"name": "Mejora Progresiva", "desc": "Al tocar una casilla positiva Com\u00fan o Raro, mejora permanentemente al siguiente escal\u00f3n.", "price": 28, "rarity": "\u00c9pico"},
    "duplicador_cuantico": {"name": "Duplicador Cu\u00e1ntico", "desc": "Los vales repetidos pueden aparecer en sobres. Permite acumular copias extra de vales.", "price": 40, "rarity": "Rainbow"},
    "recompensa_extra": {"name": "Recompensa Extra", "desc": "Al caer en una casilla negativa con recompensa, +2 $ extra.", "price": 4, "rarity": "Com\u00fan"},
    "racha_cortada": {"name": "Racha Cortada", "desc": "Si 2 tiradas seguidas son negativas, +2 CR.", "price": 6, "rarity": "Com\u00fan"},
    "tercera_vez": {"name": "Tercera Vez", "desc": "Si una misma casilla sale 3 veces seguidas en cualquier ruleta (<50% prob), abre un sobre gratis.", "price": 16, "rarity": "Raro"},
    "suerte_par": {"name": "Suerte Par", "desc": "Todas las casillas con recompensa de dinero dan el m\u00e1ximo de la ronda.", "price": 30, "rarity": "\u00c9pico"},
    "sobre_seguro": {"name": "Sobre Seguro", "desc": "La primera casilla de cada ronda es un sobre gratuito.", "price": 50, "rarity": "Legendario"},
}

def draw_voucher_icon(surface, voucher_id, cx, cy, size, tick=0.0):
    meta = VOUCHER_DEFS.get(voucher_id, {})
    primary = meta.get("primary", (139, 92, 246))
    secondary = meta.get("secondary", (196, 181, 253))
    s = size

    if voucher_id == "pack_up":
        for i, (ox, oy) in enumerate([(-14, -6), (0, 0), (14, 6)]):
            card = pygame.Rect(cx - s // 3 + ox, cy - s // 4 + oy, s // 2, int(s * 0.55))
            shade = tuple(max(0, c - 30 * i) for c in primary)
            pygame.draw.rect(surface, shade, card, border_radius=5)
            pygame.draw.rect(surface, secondary, card, width=2, border_radius=5)
        badge = (cx + s // 3, cy - s // 4)
        pygame.draw.circle(surface, (52, 211, 153), badge, 11)
        pygame.draw.circle(surface, (255, 255, 255), badge, 11, 1)
        draw_text(surface, "+1", get_font(scale(11), True), (15, 23, 42), badge[0], badge[1])

    elif voucher_id == "shop_up":
        base = pygame.Rect(cx - s // 2, cy - s // 5, s, int(s * 0.55))
        pygame.draw.rect(surface, primary, base, border_radius=4)
        pygame.draw.rect(surface, secondary, base, width=2, border_radius=4)
        awning_pts = [(cx - s // 2, cy - s // 5), (cx, cy - s // 2), (cx + s // 2, cy - s // 5)]
        pygame.draw.polygon(surface, secondary, awning_pts)
        pygame.draw.rect(surface, (15, 23, 42), (cx - 8, cy + 2, 16, 14), border_radius=2)
        pygame.draw.circle(surface, (52, 211, 153), (cx + s // 3, cy - s // 6), 10)
        draw_text(surface, "+", get_font(scale(14), True), (255, 255, 255), cx + s // 3, cy - s // 6)

    elif voucher_id == "dual_roulette":
        r = s // 5
        c1, c2 = (cx - s // 4, cy), (cx + s // 4, cy)
        pygame.draw.circle(surface, primary, c1, r + 2)
        pygame.draw.circle(surface, primary, c2, r + 2)
        pygame.draw.circle(surface, (15, 23, 42), c1, r)
        pygame.draw.circle(surface, (15, 23, 42), c2, r)
        pygame.draw.line(surface, secondary, c1, c2, 3)
        for i in range(6):
            ang = tick * 2 + i * math.pi / 3
            pygame.draw.line(surface, secondary, c1, (c1[0] + int(math.cos(ang) * r), c1[1] + int(math.sin(ang) * r)), 2)
            pygame.draw.line(surface, secondary, c2, (c2[0] + int(math.cos(ang + 1) * r), c2[1] + int(math.sin(ang + 1) * r)), 2)

    elif voucher_id == "extra_spin":
        gear_r = s // 3
        pulse = 1 + 0.08 * math.sin(tick * 5)
        for i in range(8):
            ang = i * math.pi / 4 + tick * 1.5
            x1 = cx + int(math.cos(ang) * gear_r * pulse)
            y1 = cy + int(math.sin(ang) * gear_r * pulse)
            x2 = cx + int(math.cos(ang) * (gear_r + 10) * pulse)
            y2 = cy + int(math.sin(ang) * (gear_r + 10) * pulse)
            pygame.draw.line(surface, primary, (x1, y1), (x2, y2), 4)
        pygame.draw.circle(surface, secondary, (cx, cy), gear_r // 2)
        pygame.draw.circle(surface, primary, (cx, cy), gear_r // 2, 2)
        arrow_ang = tick * 3
        ax = cx + int(math.cos(arrow_ang) * (gear_r + 6))
        ay = cy + int(math.sin(arrow_ang) * (gear_r + 6))
        pygame.draw.circle(surface, (52, 211, 153), (ax, ay), 5)

    else:
        pygame.draw.rect(surface, primary, (cx - s // 3, cy - s // 4, s // 1.5, s // 2), border_radius=6)
        draw_text(surface, "V", get_font(scale(16), True), secondary, cx, cy)

def draw_voucher_card(surface, rect, voucher, tick=0.0, hovered=False):
    vid = voucher["id"]
    meta = VOUCHER_DEFS.get(vid, {})
    primary = meta.get("primary", (139, 92, 246))
    bg = (28, 22, 40) if not hovered else (38, 30, 58)
    draw_panel(surface, rect, bg, primary if hovered else (139, 92, 246), 12, 3 if hovered else 2)

    draw_text(surface, voucher["name"], get_font(scale(13), True), (243, 244, 246), rect.centerx, rect.y + 16)

    icon_size = min(rect.w - 40, int(rect.h * 0.28))
    draw_voucher_icon(surface, vid, rect.centerx, rect.y + int(rect.h * 0.30), icon_size, tick)

    desc = voucher["desc"]
    if len(desc) > 34:
        desc = desc[:32] + "..."
    draw_text(surface, desc, get_font(scale(11)), COLOR_TEXT_MUTED, rect.centerx, rect.bottom - scale(66))
    draw_text(surface, f"{voucher['price']} CR", get_font(scale(15), True), COLOR_GOLD, rect.centerx, rect.bottom - scale(52))

def format_num(n):
    try:
        n = float(n)
        if n >= 1_000_000: return f"{n:.2e}"
        return f"{n:,.2f} CR"
    except (ValueError, OverflowError): return "INF"

def draw_text(surface, text, font, color, x, y, anchor="center"):
    text_surf = font.render(text, True, color)
    rect = text_surf.get_rect()
    if anchor == "center": rect.center = (x, y)
    elif anchor == "left": rect.topleft = (x, y)
    elif anchor == "right": rect.topright = (x, y)
    surface.blit(text_surf, rect)

class Button:
    def __init__(self, x, y, w, h, text, font, bg_color, hover_color, text_color, callback, condition_func=None, hotkey=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.font = font
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.callback = callback
        self.condition_func = condition_func
        self.hotkey = hotkey

    def is_enabled(self):
        return self.condition_func() if self.condition_func else True

    def draw(self, surface, mouse_pos):
        enabled = self.is_enabled()
        if not enabled:
            draw_panel(surface, self.rect, (20, 24, 35), (35, 40, 55), 8)
            draw_text(surface, self.text, self.font, (65, 75, 90), self.rect.centerx, self.rect.centery)
            return

        hovered = self.rect.collidepoint(mouse_pos)
        color = self.hover_color if hovered else self.bg_color
        draw_panel(surface, self.rect, color, BORDER_BLUE, 8)
        if hovered:
            glow = pygame.Rect(self.rect.x - 2, self.rect.y - 2, self.rect.w + 4, self.rect.h + 4)
            pygame.draw.rect(surface, (*color[:3],), glow, width=1, border_radius=10)
        label = self.text
        if self.hotkey and hovered:
            label = f"{self.text}  [{self.hotkey}]"
        draw_text(surface, label, self.font, self.text_color, self.rect.centerx, self.rect.centery)

    def handle_event(self, event, mouse_pos):
        if not self.is_enabled():
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(mouse_pos):
                self.callback()
                return True
        return False

class PygameMathRoulette:
    def __init__(self):
        self.running = True
        self.game_over = False
        self.game_won = False
        self.reset_hold_time = 0
        self.anim_tick = 0.0
        
        self.has_pack_upgrade = False
        self.has_shop_upgrade = False
        self.dual_roulette_count = 0
        self.extra_spins_per_round = 0
        
        self.is_spinning = False
        
        self.relic_slots = 3
        self._compute_layout()
        self.card_width = max(120, min(165, int(SCREEN_WIDTH * 0.095)))
        self.card_height = max(95, min(120, int(self.canvas_height * 0.52)))
        self.card_step = self.card_width + CARD_SPACING
        
        self.friction = 0.968
        self.min_velocity = 0.30
        
        self.particles = []
        self.stars = [{"x": random.randint(0, SCREEN_WIDTH), "y": random.randint(0, SCREEN_HEIGHT),
                       "spd": random.uniform(0.15, 0.6), "size": random.randint(1, 2)} for _ in range(80)]
        self.shake_intensity = 0
        self.shake_timer = 0
        self.last_winners = []
        
        self.r_hold_start = 0
        self.r_holding = False
        
        self.log_text = "Sistema inicializado. Pulsa ESPACIO o LANZAR para girar."
        self.log_color = COLOR_TEXT_MUTED
        
        self.buttons = []
        self.shop_buttons = []
        self.tooltip_queue = []
        
        self.overlay_open = False
        self.menu_open = False
        self.settings_open = False
        self.relic_selection_open = False
        self.relic_selection_options = []
        self.relic_selection_progress = 0.0
        self.selected_relic_idx = None
        self.relic_selection_clickable = []
        self.relic_selection_replace_mode = False
        self.relic_selection_replace_idx = -1
        self.booster_options = []       
        self.booster_buttons = []
        self.booster_clickable_cards = []
        self.booster_anim_progress = 0.0
        self.selected_booster_idx = None
        
        self.relics = []
        self.has_won = False
        self.upgrade_anim = None
        self.UPGRADE_MAP = {
            "+1 [CR]": {"type": "add", "value": 2, "name": "+2 [CR]", "rarity": "Común"},
            "+2 [CR]": {"type": "add", "value": 3, "name": "+3 [CR]", "rarity": "Común"},
            "+3 [CR]": {"type": "add", "value": 5, "name": "+5 [CR]", "rarity": "Raro"},
            "+5 [CR]": {"type": "add", "value": 7, "name": "+7 [CR]", "rarity": "Raro"},
            "+7 [CR]": {"type": "add", "value": 10, "name": "+10 [CR]", "rarity": "Épico"},
        }

        self.game_state = "menu"  # "menu" | "playing" | "game_over" | "won"
        self.main_menu_buttons = []
        self.menu_particles = []
        self._music_started = False
        self._music_current_vol = 0.0
        self._music_target_vol = 0.0
        self._dragging_slider = None
        self._play_music()

    def _start_new_game(self):
        self.game_state = "playing"
        self.menu_open = False
        self.settings_open = False
        self.init_game_data()
        self.build_ui_buttons()
        self._play_music()
        self._set_music_state(True)

    def _play_music(self):
        if self._music_started:
            return
        try:
            music_dir = os.path.join(os.path.dirname(__file__), "media", "music")
            if os.path.isdir(music_dir):
                files = [f for f in os.listdir(music_dir) if f.endswith(('.mp3', '.ogg', '.wav'))]
                if files:
                    path = os.path.join(music_dir, random.choice(files))
                    pygame.mixer.music.load(path)
                    self._music_current_vol = 0.0
                    self._set_music_state(False)
                    pygame.mixer.music.set_volume(self._music_current_vol)
                    pygame.mixer.music.play(-1, fade_ms=4000)
                    self._music_started = True
        except:
            pass

    def _set_music_state(self, in_game):
        if in_game:
            self._music_target_vol = MASTER_VOLUME * MUSIC_VOLUME * MUSIC_VOLUME_CAP * 0.85
        else:
            self._music_target_vol = MASTER_VOLUME * MUSIC_VOLUME * MUSIC_VOLUME_CAP * 0.15

    def _stop_music(self):
        self._set_music_state(False)

    def _update_music_volume(self):
        if not self._music_started:
            return
        diff = self._music_target_vol - self._music_current_vol
        if abs(diff) > 0.001:
            self._music_current_vol += diff * 0.04
            self._music_current_vol = max(0.0, min(MASTER_VOLUME * MUSIC_VOLUME * MUSIC_VOLUME_CAP, self._music_current_vol))
            pygame.mixer.music.set_volume(self._music_current_vol)

    def _draw_main_menu(self, surface):
        self.anim_tick += 0.03
        for star in self.stars:
            star["y"] += star["spd"] * 1.5
            if star["y"] > SCREEN_HEIGHT:
                star["y"] = 0
                star["x"] = random.randint(0, SCREEN_WIDTH)
        surface.fill(BG_DARK_MAIN)
        mouse_pos = pygame.mouse.get_pos()

        for star in self.stars:
            alpha = 80 + int(40 * math.sin(self.anim_tick + star["x"] * 0.01))
            pygame.draw.circle(surface, (alpha, alpha, min(255, alpha + 40)), (int(star["x"]), int(star["y"])), star["size"])

        for p in self.menu_particles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["life"] -= 0.01
            if p["life"] > 0:
                c = rainbow_color(self.anim_tick + p["offset"])
                pygame.draw.circle(surface, c, (int(p["x"]), int(p["y"])), int(p["r"] * p["life"]))
        self.menu_particles = [p for p in self.menu_particles if p["life"] > 0]
        if random.random() < 0.15:
            self.menu_particles.append({
                "x": random.randint(0, SCREEN_WIDTH), "y": SCREEN_HEIGHT + 10,
                "vx": random.uniform(-0.4, 0.4), "vy": random.uniform(-1.2, -0.5),
                "r": random.randint(2, 5), "life": 1.0, "offset": random.uniform(0, 6)
            })

        cx = SCREEN_WIDTH // 2
        title_y = int(SCREEN_HEIGHT * 0.15)
        title_colors = [rainbow_color(self.anim_tick * 0.8 + i * 0.3) for i in range(7)]
        lines = ["ROGUELIKE", "ROULETTE"]
        for li, line in enumerate(lines):
            size = scale(48 - li * 6)
            col = title_colors[li * 3]
            dark = (5, 5, 15)
            for ox in range(4, 0, -1):
                draw_text(surface, line, get_font(size + ox * 2, True), dark, cx + ox, title_y + li * (size + 4) + ox)
            for glow in range(3, 0, -1):
                g_alpha = 80 + glow * 50
                draw_text(surface, line, get_font(size + glow * 2, True), (*col, g_alpha), cx + glow, title_y + li * (size + 4) + glow)
            draw_text(surface, line, get_font(size, True), (255, 255, 255), cx, title_y + li * (size + 4))

        y_start = int(SCREEN_HEIGHT * 0.50)
        btn_w, btn_h = 220, 44
        btn_x = cx - btn_w // 2
        labels = ["NUEVA PARTIDA", "CONFIGURACION", "SALIR"]
        actions = ["new_game", "settings", "quit"]
        self.main_menu_buttons = {}
        for i, (lbl, act) in enumerate(zip(labels, actions)):
            by = y_start + i * (btn_h + 16)
            rect = pygame.Rect(btn_x, by, btn_w, btn_h)
            hover = rect.collidepoint(mouse_pos)
            col = rainbow_color(self.anim_tick * 0.5 + i * 0.5) if hover else (100, 120, 200)
            bg = (30, 35, 55) if not hover else (45, 50, 75)
            draw_panel(surface, rect, bg, col, 10, 2 if hover else 1)
            draw_text(surface, lbl, get_font(scale(15), True), (255, 255, 255) if hover else (241, 245, 249), rect.centerx, rect.centery)
            self.main_menu_buttons[act] = rect

        if self.settings_open:
            self._draw_settings_menu(surface, mouse_pos)

        draw_text(surface, "v1.0", get_font(9), (60, 72, 95), SCREEN_WIDTH - 20, SCREEN_HEIGHT - 16, "right")

    def _draw_settings_menu(self, surface, mouse_pos):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((8, 9, 15, 200))
        surface.blit(overlay, (0, 0))
        mw, mh = 360, 360
        mx = (SCREEN_WIDTH - mw) // 2
        my = (SCREEN_HEIGHT - mh) // 2
        draw_panel(surface, pygame.Rect(mx, my, mw, mh), (15, 18, 30), (100, 120, 200), 16, 2)
        draw_text(surface, "CONFIGURACION", get_font(scale(18), True), COLOR_CYAN, SCREEN_WIDTH // 2, my + 25)
        self._settings_buttons = {}
        sliders = [
            ("Volumen General", "master", MASTER_VOLUME),
            ("Volumen Efectos", "sfx", SFX_VOLUME),
            ("Volumen Musica", "music", MUSIC_VOLUME),
        ]
        bar_w, bar_h = 220, 10
        bar_x = (SCREEN_WIDTH - bar_w) // 2
        for i, (label, key, val) in enumerate(sliders):
            sy = my + 70 + i * 75
            draw_text(surface, label, get_font(scale(13), True), (241, 245, 249), SCREEN_WIDTH // 2, sy)
            bg_rect = pygame.Rect(bar_x, sy + 22, bar_w, bar_h)
            draw_panel(surface, bg_rect, (30, 35, 55), (60, 72, 95), 6)
            fill_w = int(bar_w * val)
            if fill_w > 0:
                fill_rect = pygame.Rect(bar_x, sy + 22, fill_w, bar_h)
                draw_panel(surface, fill_rect, (52, 211, 153), (52, 211, 153), 6)
            handle_cx = bar_x + fill_w
            handle_cy = sy + 22 + bar_h // 2
            pygame.draw.circle(surface, (255, 255, 255), (handle_cx, handle_cy), scale(7))
            pygame.draw.circle(surface, (52, 211, 153), (handle_cx, handle_cy), scale(4))
            self._settings_buttons[f"vol_{key}"] = bg_rect.inflate(scale(10), scale(10))
            pct_lbl = f"{int(val * 100)}%"
            draw_text(surface, pct_lbl, get_font(scale(11), True), (52, 211, 153), bar_x + bar_w + scale(18), sy + 22 + bar_h // 2)
        back_rect = pygame.Rect(SCREEN_WIDTH // 2 - 60, my + mh - 50, 120, 36)
        hover = back_rect.collidepoint(mouse_pos)
        draw_panel(surface, back_rect, (30, 35, 55) if not hover else (50, 55, 75), (100, 120, 200), 8)
        draw_text(surface, "Volver", get_font(scale(14), True), (241, 245, 249), back_rect.centerx, back_rect.centery)
        self._settings_buttons["back"] = back_rect

    def _compute_layout(self):
        margin = max(14, int(SCREEN_WIDTH * 0.015))
        self.margin = margin

        self.header_y = 10
        self.header_h = scale(76)

        self.canvas_x = margin
        self.canvas_y = self.header_y + self.header_h + 6
        self.canvas_width = SCREEN_WIDTH - margin * 2
        self.canvas_height = max(200, int(SCREEN_HEIGHT * 0.28))

        self.action_y = self.canvas_y + self.canvas_height + 8
        self.action_h = scale(50)

        self.dash_y = self.action_y + self.action_h + 6
        self.dash_h = scale(140)

        self.shelf_y = self.dash_y + self.dash_h + 6
        self.shelf_h = scale(82)

        self.shop_y = self.shelf_y + self.shelf_h + 6
        self.shop_h = SCREEN_HEIGHT - self.shop_y - margin
        self.market_y = self.shop_y + scale(42)

        self.voucher_width = max(200, int(SCREEN_WIDTH * 0.155))
        shop_inner = SCREEN_WIDTH - margin * 2
        items_area = shop_inner - self.voucher_width - scale(24)
        max_slots = 4
        gap = scale(14)
        self.box_width = max(170, (items_area - gap * (max_slots - 1)) // max_slots)
        self.box_height = max(140, self.shop_h - scale(52))
        self.v_separator_x = SCREEN_WIDTH - margin - self.voucher_width - scale(8)

        relic_area = SCREEN_WIDTH - margin * 2
        self.relic_gap = scale(14)
        self.relic_box_w = (relic_area - self.relic_gap * (self.relic_slots - 1)) // self.relic_slots
        self.relic_start_x = margin

        deck_w = int(SCREEN_WIDTH * 0.17)
        rng_w = int(SCREEN_WIDTH * 0.19)
        self.deck_w = deck_w
        self.rng_w = rng_w
        self.log_w = SCREEN_WIDTH - margin * 2 - deck_w - rng_w - scale(16)
        self.deck_x = margin
        self.log_x = margin + deck_w + scale(8)
        self.rng_x = self.log_x + self.log_w + scale(8)

    def full_reset(self):
        self.has_pack_upgrade = False
        self.has_shop_upgrade = False
        self.dual_roulette_count = 0
        self.extra_spins_per_round = 0
        self.duplicador_duplicated = set()
        self.relics = []
        self.game_over = False
        self.game_won = False
        self.has_won = False
        self.reset_hold_time = 0
        self.overlay_open = False
        self.init_game_data()
        self.build_ui_buttons()
        self.log_text = "Simulacion reiniciada. Buena suerte, operador."
        self.log_color = COLOR_CYAN

    def init_game_data(self):
        self.money = 8.0
        self.displayed_money = 8.0
        self.cash = 7.0
        self.displayed_cash = 7.0
        self.round = 1
        self.target_money = 15.0
        self.max_spins = 5 + self.extra_spins_per_round
        self.spins_left = self.max_spins
        self.reroll_cost = 1
        self.cash_bonus_chance = 0.25
        self.cash_bonus_min = 1
        self.cash_bonus_max_base = 2
        self.current_boss = NO_BOSS
        self.game_over = False
        self.game_won = False
        self.upgrade_anim = None
        self.is_spinning = False
        self.last_winners = []
        self.consecutive_negative = 0
        self.last_winner_item = {}
        self.consecutive_same_item = {}
        self.sobre_seguro_triggered = False
        self.negatives_added = set()
        self.sobre_booster_placed = False
        
        self.deck = [
            {"type": "add", "value": 2, "name": "+2 [CR]", "rarity": "Común"},
            {"type": "add", "value": 1, "name": "+1 [CR]", "rarity": "Común"},
            {"type": "add", "value": 3, "name": "+3 [CR]", "rarity": "Común"},
        ]
        self.roulette_items = [[random.choice(self.deck) for _ in range(15)]]
        self.positions = [0.0]
        self.velocities = [0.0]
        self.last_card_triggers = [-1]
        self.roulette_active = [False]
        self.shop_offers = []
        self.current_voucher = None
        self.duplicador_duplicated = set()
        self.generate_shop_offers()
        self.generate_voucher_offer()

    def calculate_probabilities(self):
        total_cards = len(self.deck)
        if total_cards == 0: return {}
        counts = {}
        for item in self.deck:
            counts[item["name"]] = counts.get(item["name"], 0) + 1
        return {name: (count / total_cards) * 100 for name, count in counts.items()}

    def get_current_shop_ratios(self):
        return {"Común": 70.9, "Raro": 20.0, "Épico": 8.0, "Legendario": 1.0, "Rainbow": 0.1}

    def is_negative(self, item):
        if item.get("is_box") or item.get("is_relic") or item.get("is_voucher"): return False
        return item["type"] in ["sub", "div", "zero"]

    def get_progressive_rarity(self):
        ratios = self.get_current_shop_ratios()
        roll = random.random() * 100
        running_sum = ratios["Rainbow"]
        if roll < running_sum: return "Rainbow"
        running_sum += ratios["Legendario"]
        if roll < running_sum: return "Legendario"
        running_sum += ratios["Épico"]
        if roll < running_sum: return "Épico"
        running_sum += ratios["Raro"]
        if roll < running_sum: return "Raro"
        return "Común"

    def get_available_vouchers(self):
        available = []
        if not self.has_pack_upgrade:
            available.append({"id": "pack_up", **{k: VOUCHER_DEFS["pack_up"][k] for k in ("name", "price", "desc")}})
        if not self.has_shop_upgrade:
            available.append({"id": "shop_up", **{k: VOUCHER_DEFS["shop_up"][k] for k in ("name", "price", "desc")}})
        if self.dual_roulette_count < 1:
            available.append({"id": "dual_roulette", **{k: VOUCHER_DEFS["dual_roulette"][k] for k in ("name", "price", "desc")}})
        if self.extra_spins_per_round < 1:
            available.append({"id": "extra_spin", **{k: VOUCHER_DEFS["extra_spin"][k] for k in ("name", "price", "desc")}})
        return available

    def generate_shop_offers(self):
        self.shop_offers = []
        is_inflated = self.current_boss["id"] == "inflation"
        slots = 4 if self.has_shop_upgrade else 3
        has_sobre_seguro = any(r["id"] == "sobre_seguro" for r in self.relics)
        
        for s in range(slots):
            rarity = self.get_progressive_rarity()
            
            # Sobre Seguro: solo la primera tienda de la ronda tiene un sobre gratis
            if has_sobre_seguro and not self.sobre_booster_placed:
                self.shop_offers.append({"name": "Sobre Gratis [M]", "price": 0, "is_box": True, "is_relic": False, "rarity": "Común"})
                self.sobre_booster_placed = True
                continue
            
            if random.random() < 0.18:
                box_price = 9
                if is_inflated: box_price = int(box_price * 1.30)
                self.shop_offers.append({"name": "Caja Sorpresa [M]", "price": box_price, "is_box": True, "is_relic": False, "rarity": "Común"})
            else:
                item = random.choice(POOL_ITEMS[rarity]).copy()
                base_price = RARITIES[item["rarity"]]["price"] + (self.round * 2)
                price = random.randint(max(1, base_price - 2), base_price + 3)
                if is_inflated: price = int(price * 1.30)
                item["price"] = price
                item["is_box"] = False
                item["is_relic"] = False
                self.shop_offers.append(item)
        self.rebuild_shop_buttons()

    def generate_voucher_offer(self):
        is_inflated = self.current_boss["id"] == "inflation"
        available = self.get_available_vouchers()
        if available:
            self.current_voucher = random.choice(available)
            if is_inflated: self.current_voucher["price"] = int(self.current_voucher["price"] * 1.30)
        else:
            self.current_voucher = None
        self.rebuild_shop_buttons()

    def build_ui_buttons(self):
        self.buttons = []
        btn_h = self.action_h - 6
        side_w = min(210, max(160, int(SCREEN_WIDTH * 0.13)))
        spin_w = min(300, max(200, SCREEN_WIDTH - self.margin * 2 - side_w * 2 - scale(40)))

        self.btn_reroll_idx = 0
        self.buttons.append(Button(
            self.margin, self.action_y + 3, side_w, btn_h,
            f"Reroll: {self.reroll_cost} $", get_font(scale(13), True),
            (30, 41, 59), (51, 65, 85), (255, 255, 255), self.trigger_reroll,
            lambda: not self.game_over and not self.game_won and not self.overlay_open and not self.is_spinning
        ))

        spin_x = self.margin + side_w + scale(20)
        self.buttons.append(Button(
            spin_x, self.action_y + 3, spin_w, btn_h,
            ">>> LANZAR <<<", get_font(scale(16), True),
            (234, 179, 8), (202, 138, 4), (15, 23, 42), self.start_spin,
            lambda: not self.game_over and not self.game_won and not self.overlay_open and not self.is_spinning,
            hotkey="ESPACIO"
        ))

        next_x = spin_x + spin_w + scale(20)
        self.buttons.append(Button(
            next_x, self.action_y + 3, side_w, btn_h,
            "Siguiente Ronda >>", get_font(scale(13), True),
            (16, 185, 129), (5, 150, 105), (15, 23, 42), self.advance_round_clean,
            lambda: (not self.game_over and not self.overlay_open and not self.is_spinning) and (not self.game_won or self.has_won),
            hotkey="N"
        ))

    def rebuild_shop_buttons(self):
        self.shop_buttons = []
        market_x = self.margin + scale(10)
        btn_h = scale(34)

        for i, item in enumerate(self.shop_offers):
            if item is None:
                continue
            bx = market_x + i * (self.box_width + scale(14))

            if item.get("is_box"):
                b_text, b_bg, b_hov = "Desplegar", (147, 51, 234), (168, 85, 247)
            elif item.get("is_relic"):
                b_text, b_bg, b_hov = "Equipar", (234, 140, 8), (250, 160, 25)
            else:
                is_neg = self.is_negative(item)
                b_text = "Asimilar" if is_neg else "Adquirir"
                if is_neg:
                    b_bg, b_hov = (220, 38, 38), (239, 68, 68)
                else:
                    rarity = item.get("rarity", "Común")
                    b_bg = RARITIES[rarity]["color"]
                    b_hov = tuple(min(255, c + 40) for c in b_bg)

            self.shop_buttons.append(Button(
                bx + 10, self.market_y + self.box_height - btn_h - 8, self.box_width - 20, btn_h,
                b_text, get_font(scale(13), True),
                b_bg, b_hov, (255, 255, 255), lambda idx=i: self.buy_item(idx),
                lambda: not self.game_over and not self.game_won and not self.overlay_open and not self.is_spinning
            ))

        if self.current_voucher:
            v_x = SCREEN_WIDTH - self.margin - self.voucher_width
            self.shop_buttons.append(Button(
                v_x + 10, self.market_y + self.box_height - btn_h - 8, self.voucher_width - 20, btn_h,
                "Adquirir Vale", get_font(scale(13), True),
                (124, 58, 237), (139, 92, 246), (255, 255, 255), self.buy_voucher,
                lambda: not self.game_over and not self.game_won and not self.overlay_open and not self.is_spinning
            ))

    def trigger_reroll(self):
        has_tarjeta = any(r["id"] == "tarjeta_clonada" for r in self.relics)
        if self.cash < self.reroll_cost:
            if not has_tarjeta or self.cash - self.reroll_cost < -15:
                self.log_text = "[ERR] CASH INSUFICIENTE PARA REROLL."
                self.log_color = (248, 113, 113)
                return
        self.cash -= self.reroll_cost
        self.reroll_cost = min(99, self.reroll_cost * 2)
        self.buttons[self.btn_reroll_idx].text = f"Reroll: {self.reroll_cost} $"
        self.generate_shop_offers()
        play_sound(SOUND_REROLL)

    def check_funds_and_spins_integrity(self):
        if self.money < 0:
            self.trigger_game_over(f"BANCARROTA CRITICA: Saldo CR inferior a 0.")
            return True
        if self.spins_left <= 0 and self.money < self.target_money:
            self.trigger_game_over(f"DERROTA: Sin giros para alcanzar {format_num(self.target_money)}.")
            return True
        return False

    def trigger_game_over(self, reason_text):
        self.game_over = True
        for i in range(len(self.velocities)):
            self.velocities[i] = 0
        self.is_spinning = False
        self.log_text = reason_text
        self.log_color = (248, 113, 113)
        play_sound(SOUND_FAIL)

    def advance_round_clean(self):
        if self.money < self.target_money:
            self.log_text = f"[BLOQUEO] ALCANZA EL OBJETIVO DE {format_num(self.target_money)} PRIMERO."
            self.log_color = (251, 146, 60)
            return

        # Base cash per round completed
        base_cash = 3 + self.round
        self.cash += base_cash
        cash_log = f"Bonificacion R{self.round}: +{base_cash} $."

        # Interest on excess CR (blocked by no_interest boss)
        if self.current_boss["id"] != "no_interest":
            if self.money > self.target_money:
                excess = self.money - self.target_money
                cash_interest = max(1, min(int(excess * 0.20), 5 + self.round * 2))
                self.cash += cash_interest
                cash_log += f" Interes CR: +{cash_interest} $."
            cr_interest = min(8, int(self.money // 4))
            if cr_interest > 0:
                self.money += cr_interest
                cash_log += f" Interes: +{cr_interest} CR."

        self.log_text = cash_log
        self.log_color = COLOR_GOLD
            
        if self.round >= VICTORY_ROUND and not self.has_won:
            self.has_won = True
            self.game_won = True
            self.log_text = f"VICTORIA RONDA {VICTORY_ROUND}! Presiona [N] para seguir en MODO INFINITO."
            self.log_color = (52, 211, 153)
            play_sound(SOUND_WIN)
            return

        self.round += 1
        # Anadir progresivamente casillas negativas al mazo segun la ronda
        for r_needed, neg_card in sorted(NEGATIVE_SCHEDULE.items()):
            if self.round >= r_needed and r_needed not in self.negatives_added:
                self.deck.append(neg_card.copy())
                self.negatives_added.add(r_needed)
        self.target_money = float(self.round ** 2.5 * 2.0 + 20 + random.randint(2, 5))
        self.current_boss = random.choice(BOSS_BLINDS) if self.round > 1 else NO_BOSS
        self.max_spins = 5 + self.extra_spins_per_round
        self.spins_left = self.max_spins - 1 if self.current_boss["id"] == "minus_spin" else self.max_spins
        self.reroll_cost = 1
        self.buttons[self.btn_reroll_idx].text = f"Reroll: {self.reroll_cost} $"
        self.last_winners = []
        self.sobre_booster_placed = False
        self.generate_shop_offers()
        self.generate_voucher_offer()
        self.generate_relic_choices()
        self.log_text = f"RONDA {self.round} INICIADA. MODIFICADORES RECALCULADOS."
        self.log_color = (52, 211, 153)
        play_sound(SOUND_NEXT_ROUND)

    def trigger_victory(self):
        self.game_won = True
        self.is_spinning = False
        for i in range(len(self.velocities)):
            self.velocities[i] = 0
        self.log_text = "VICTORIA TOTAL: Has dominado la Ruleta Zombi."
        self.log_color = (52, 211, 153)
        play_sound(SOUND_WIN)

    def start_spin(self):
        if self.game_over or self.spins_left <= 0 or self.is_spinning or self.overlay_open: return
        count = 1 + self.dual_roulette_count
        self.is_spinning = True
        self.roulette_active = [False] * count
        self.roulette_active[0] = True
        self.roulette_items = [[random.choice(self.deck).copy() for _ in range(65)]]
        self.positions = [0.0]
        self.velocities = [random.uniform(75.0, 95.0)]
        self.last_card_triggers = [-1]
        
        has_suerte_par = any(r["id"] == "suerte_par" for r in self.relics)
        cash_max = self.cash_bonus_max_base + self.round // 3
        
        for card in self.roulette_items[0]:
            if random.random() < self.cash_bonus_chance:
                cash_val = cash_max if has_suerte_par else random.randint(self.cash_bonus_min, cash_max)
                card["cash_bonus"] = cash_val
        
        for extra in range(1, count):
            self.roulette_active[extra] = True
            self.roulette_items.append([random.choice(self.deck).copy() for _ in range(65)])
            self.positions.append(0.0)
            self.velocities.append(random.uniform(70.0, 90.0))
            self.last_card_triggers.append(-1)
            for card in self.roulette_items[extra]:
                if random.random() < self.cash_bonus_chance:
                    cash_val = cash_max if has_suerte_par else random.randint(self.cash_bonus_min, cash_max)
                    card["cash_bonus"] = cash_val

    def update_physics(self, dt):
        self._update_music_volume()
        if self.game_state == "menu":
            return

        self.anim_tick += dt * 0.05
        for star in self.stars:
            star["y"] += star["spd"] * dt
            if star["y"] > SCREEN_HEIGHT:
                star["y"] = 0
                star["x"] = random.randint(0, SCREEN_WIDTH)

        alive = []
        for p in self.particles:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            if p.get("gravity"):
                p["vy"] += 0.25 * dt
            p["life"] -= p["fade_speed"] * dt
            if p["life"] > 0:
                alive.append(p)
        self.particles = alive

        if self.upgrade_anim:
            self.upgrade_anim["timer"] -= dt
            if self.upgrade_anim["timer"] <= 0:
                self.upgrade_anim = None

        if self.displayed_money != self.money:
            diff = self.money - self.displayed_money
            step = diff * 0.12 * dt
            if abs(step) < 0.01:
                self.displayed_money = self.money
            else:
                self.displayed_money += step

        if self.displayed_cash != self.cash:
            diff = self.cash - self.displayed_cash
            step = diff * 0.12 * dt
            if abs(step) < 0.01:
                self.displayed_cash = self.cash
            else:
                self.displayed_cash += step

        if self.overlay_open and self.booster_anim_progress < 1.0:
            self.booster_anim_progress += 0.03 * dt

        if self.game_over or not self.is_spinning:
            return

        current_friction = self.friction
        any_active = False

        for i in range(len(self.roulette_active)):
            if self.roulette_active[i]:
                if self.velocities[i] > self.min_velocity:
                    self.positions[i] += self.velocities[i] * dt
                    self.velocities[i] *= math.pow(current_friction, dt)
                    idx = int((self.positions[i] + (self.card_step / 2)) // self.card_step)
                    if idx != self.last_card_triggers[i]:
                        play_dynamic_click(self.velocities[i], len(self.roulette_active) > 1)
                        self.last_card_triggers[i] = idx
                else:
                    self.velocities[i] = 0
                    self.roulette_active[i] = False
            if self.roulette_active[i]:
                any_active = True

        if not any_active:
            self.is_spinning = False
            self.determine_winners_execution()

    def create_impact_particles(self, x, y, color, count=45):
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2); speed = random.uniform(4, 11)
            self.particles.append({
                "x": x, "y": y, "vx": math.cos(angle) * speed, "vy": math.sin(angle) * speed,
                "radius": random.randint(3, 5), "color": color, "life": 1.2, "gravity": True, "fade_speed": random.uniform(0.02, 0.035)
            })

    def resolve_item_effect(self, item):
        m_type, val = item.get("type", ""), item.get("value", 0)
        if m_type == "add": self.money += val
        elif m_type == "sub": self.money -= val
        elif m_type == "mult": self.money *= val
        elif m_type == "div": self.money = self.money / val if self.money > 0 else 0
        elif m_type == "pow": self.money = min(self.money ** val, 1e100) if self.money > 1 else self.money + 3
        elif m_type == "zero": self.money = 0.0
        cash_bonus = item.get("cash_bonus", 0)
        if cash_bonus:
            self.cash += cash_bonus

    def determine_winners_execution(self):
        play_sound(SOUND_WIN)
        self.last_winners = []
        old_money = self.money
        old_cash = self.cash
        log_build = ""
        has_mejora = any(r["id"] == "mejora_progresiva" for r in self.relics)
        has_recompensa = any(r["id"] == "recompensa_extra" for r in self.relics)
        has_racha = any(r["id"] == "racha_cortada" for r in self.relics)
        has_tercera = any(r["id"] == "tercera_vez" for r in self.relics)
        has_suerte_par = any(r["id"] == "suerte_par" for r in self.relics)
        upgrade_data = []
        extra_log = ""
        
        for ri in range(len(self.roulette_items)):
            idx = max(0, min(int((self.positions[ri] + (self.card_step / 2)) // self.card_step), len(self.roulette_items[ri]) - 1))
            winner = self.roulette_items[ri][idx]

            if ri == 0:
                self.resolve_item_effect(winner)
            else:
                self.resolve_item_effect(winner)
            
            # Suerte Par: todas las casillas con recompensa ya tienen el maximo asignado al generar la ruleta
            
            # Recompensa Extra: +2$ al caer en casilla negativa con recompensa
            if has_recompensa and self.is_negative(winner) and winner.get("cash_bonus", 0) > 0:
                self.cash += 2
                extra_log += " +2$ (Recompensa Extra)"
            
            self.last_winners.append(idx)
            
            # Track consecutive negative for Racha Cortada
            is_neg = self.is_negative(winner)
            if has_racha:
                if is_neg:
                    self.consecutive_negative += 1
                    if self.consecutive_negative >= 2:
                        self.money += 2
                        extra_log += " +2CR (Racha Cortada)"
                        self.consecutive_negative = 0
                else:
                    self.consecutive_negative = 0
            
            # Track same value for Tercera Vez (por cada ruleta individual)
            if has_tercera:
                item_key = (winner.get("type"), winner.get("value"))
                prev = self.last_winner_item.get(ri)
                if item_key == prev:
                    count = self.consecutive_same_item.get(ri, 0) + 1
                    self.consecutive_same_item[ri] = count
                    if count >= 3:
                        count_in_deck = sum(1 for c in self.deck if (c.get("type"), c.get("value")) == item_key)
                        prob = count_in_deck / max(1, len(self.deck))
                        if prob < 0.5:
                            extra_log += " (Tercera Vez: Sobre!)"
                            self.open_booster_pack()
                            self.consecutive_same_item[ri] = 0
                else:
                    self.consecutive_same_item[ri] = 1
                self.last_winner_item[ri] = item_key
            
            c = (248, 113, 113) if is_neg else RARITIES.get(winner["rarity"], {"color": (52, 211, 153)})["color"]
            y_pos = self.canvas_y + 50 if len(self.roulette_items) > 1 else self.canvas_y + self.canvas_height // 2
            self.create_impact_particles(self.canvas_x + self.canvas_width // 2, y_pos, c, count=40)
            
            if log_build:
                log_build += f" | [R{ri+1}]: {winner['name']}"
            else:
                log_build = f"[R1]: {winner['name']}"
            
            if has_mejora and winner["type"] == "add" and winner["rarity"] in ("Común", "Raro") and winner["name"] in self.UPGRADE_MAP:
                upgraded = self.UPGRADE_MAP[winner["name"]]
                for di, d_item in enumerate(self.deck):
                    if d_item["name"] == winner["name"]:
                        self.deck[di] = upgraded.copy()
                        break
                upgrade_color = RARITIES.get(upgraded["rarity"], {"color": (52, 211, 153)})["color"]
                self.shake_intensity = 12
                self.shake_timer = 15
                self.create_impact_particles(self.canvas_x + self.canvas_width // 2, self.canvas_y + self.canvas_height // 2, upgrade_color, count=60)
                self.create_impact_particles(self.canvas_x + self.canvas_width // 2, self.canvas_y + self.canvas_height // 2, (255, 255, 200), count=30)
                self.roulette_items[ri][idx] = upgraded.copy()
                upgrade_data.append({"idx": idx, "old_name": winner["name"], "new_name": upgraded["name"], "new_item": upgraded.copy()})
        
        delta_cr = self.money - old_money
        delta_cash = self.cash - old_cash
        log_parts = [log_build]
        if delta_cr != 0:
            sign = "+" if delta_cr >= 0 else ""
            log_parts.append(f"CR: {sign}{delta_cr:.1f}")
        if delta_cash != 0:
            sign = "+" if delta_cash >= 0 else ""
            log_parts.append(f"$: {sign}{delta_cash:.0f}")
        if extra_log:
            log_parts.append(extra_log)
        self.log_text = " >> ".join(log_parts)
        self.log_color = (52, 211, 153) if (delta_cr >= 0 and delta_cash >= 0) else (248, 113, 113)
        self.shake_intensity = 8
        self.shake_timer = 10
        
        if upgrade_data:
            self.upgrade_anim = {"data": upgrade_data, "timer": 2.5}
        
        self.spins_left -= 1
        self.check_funds_and_spins_integrity()

    def buy_item(self, idx):
        if self.game_over or self.overlay_open or self.is_spinning: return
        item = self.shop_offers[idx]
        if item is None: return
        if item.get("is_box") or item.get("is_relic") or not self.is_negative(item):
            has_tarjeta = any(r["id"] == "tarjeta_clonada" for r in self.relics)
            price = item["price"]
            if self.cash < price:
                if not has_tarjeta or self.cash - price < -15:
                    self.log_text = "[ERR] CASH INSUFICIENTE."
                    self.log_color = (248, 113, 113)
                    return
            self.cash -= price
        else:
            # Negative items pay you cash to take them
            self.cash += item["price"]

        if item.get("is_box"):
            self.shop_offers[idx] = None
            # --- CORREGIDO: Regenerar botones inmediatamente para que se limpie la interfaz al abrir ---
            self.rebuild_shop_buttons()
            self.open_booster_pack()
            return
            
        if item.get("is_relic"):
            if len(self.relics) < self.relic_slots:
                self.relics.append({"id": item["id"], "name": item["name"], "desc": item["desc"], "rarity": item["rarity"]})
                self.shop_offers[idx] = None
                self.log_text = f"[SISTEMA] RELIQUIA ADQUIRIDA: {item['name']}"
                self.log_color = COLOR_GOLD
            else:
                self.cash += item["price"]
                self.log_text = "[ERR] ESTANTERIA LLENA."
                self.log_color = (248, 113, 113)
        else:
            self.deck.append(item)
            self.shop_offers[idx] = None
            
        self.rebuild_shop_buttons()
        self.check_funds_and_spins_integrity()
        play_sound(SOUND_BUY)

    def buy_voucher(self):
        if self.game_over or not self.current_voucher or self.overlay_open or self.is_spinning: return
        has_tarjeta = any(r["id"] == "tarjeta_clonada" for r in self.relics)
        price = self.current_voucher["price"]
        if self.cash < price:
            if not has_tarjeta or self.cash - price < -15:
                return
        
        self.cash -= self.current_voucher["price"]
        v_id = self.current_voucher["id"]
        
        if v_id == "pack_up": self.has_pack_upgrade = True
        elif v_id == "shop_up": self.has_shop_upgrade = True; self.generate_shop_offers()
        elif v_id == "dual_roulette": self.dual_roulette_count += 1
        elif v_id == "extra_spin": self.extra_spins_per_round += 1; self.max_spins += 1; self.spins_left += 1
            
        self.current_voucher = None
        self.rebuild_shop_buttons()
        self.check_funds_and_spins_integrity()
        play_sound(SOUND_BUY)

    def open_booster_pack(self):
        self.overlay_open = True
        self.booster_anim_progress = 0.0
        self.selected_booster_idx = None 
        self.booster_options = []
        play_sound(SOUND_SPARKLE)
        cards_count = 4 if self.has_pack_upgrade else 3
        
        active_relic_ids = [r["id"] for r in self.relics]
        has_duplicador = "duplicador_cuantico" in active_relic_ids
        available_vouchers = self.get_available_vouchers()
        # With Duplicador Cuantico, allow ONE extra copy per voucher type in boosters
        if has_duplicador:
            extra_vouchers = []
            for vid in VOUCHER_DEFS:
                if vid in self.duplicador_duplicated:
                    continue
                vdef = VOUCHER_DEFS[vid]
                current = (self.dual_roulette_count if vid == "dual_roulette"
                           else self.extra_spins_per_round if vid == "extra_spin"
                           else (1 if self.has_pack_upgrade else 0) if vid == "pack_up"
                            else (1 if self.has_shop_upgrade else 0))
                max_allowed = 1
                if current >= 1 and current < max_allowed:
                    extra_vouchers.append({"id": vid, **{k: vdef[k] for k in ("name", "price", "desc")}})
            available_vouchers = available_vouchers + extra_vouchers
        
        while len(self.booster_options) < cards_count:
            roll = random.random()
            if roll < 0.001 and available_vouchers:
                v = random.choice(available_vouchers)
                picked = {"id": v["id"], "name": v["name"], "desc": v["desc"], "is_voucher": True, "rarity": "Rainbow", "type": "ultra"}
                available_vouchers.remove(v)
            else:
                if roll < 0.002: rarity = "Rainbow"
                elif roll < 0.012: rarity = "Legendario"
                elif roll < 0.10: rarity = "Épico"
                elif roll < 0.35: rarity = "Raro"
                else: rarity = "Común"
                picked = random.choice(POOL_ITEMS[rarity]).copy()
            
            if not self.is_negative(picked):
                self.booster_options.append({"item": picked})
        
        mw, mh = 820, 380; my = (SCREEN_HEIGHT - mh)//2
        
        self.booster_buttons = [
            Button(
                SCREEN_WIDTH//2 - 130, my + mh - 50, 120, 32, "Descartar", get_font(11, True),
                (55, 65, 81), (75, 85, 99), (243, 244, 246), self.close_booster_discard
            ),
            Button(
                SCREEN_WIDTH//2 + 10, my + mh - 50, 120, 32, "Integrar", get_font(11, True),
                (16, 185, 129), (5, 150, 105), (15, 23, 42), self.confirm_booster_selection,
                lambda: self.selected_booster_idx is not None
            )
        ]

    def close_booster_discard(self):
        self.overlay_open = False
        self.booster_options = []
        self.selected_booster_idx = None

    def confirm_booster_selection(self):
        if self.selected_booster_idx is None: return
        item = self.booster_options[self.selected_booster_idx]["item"]
        
        if item.get("is_relic"):
            if len(self.relics) < self.relic_slots:
                self.relics.append({"id": item["id"], "name": item["name"], "desc": item["desc"], "rarity": item["rarity"]})
        elif item.get("is_voucher"):
            v_id = item["id"]
            # Track Duplicador Cuantico duplicates
            if any(r["id"] == "duplicador_cuantico" for r in self.relics):
                if v_id not in self.duplicador_duplicated:
                    # Check if we already own this voucher (i.e. it's a duplicate)
                    already_owned = (
                        (v_id == "pack_up" and self.has_pack_upgrade) or
                        (v_id == "shop_up" and self.has_shop_upgrade) or
                        (v_id == "dual_roulette" and self.dual_roulette_count > 0) or
                        (v_id == "extra_spin" and self.extra_spins_per_round > 0)
                    )
                    already_in_shop = any(v["id"] == v_id for v in self.get_available_vouchers())
                    if already_owned or not already_in_shop:
                        self.duplicador_duplicated.add(v_id)
            if v_id == "pack_up": self.has_pack_upgrade = True
            elif v_id == "shop_up": self.has_shop_upgrade = True; self.generate_shop_offers()
            elif v_id == "dual_roulette": self.dual_roulette_count += 1
            elif v_id == "extra_spin": self.extra_spins_per_round += 1; self.max_spins += 1; self.spins_left += 1
        else:
            self.deck.append(item)
        
        play_sound(SOUND_BUY)
        self.overlay_open = False
        self.booster_options = []
        self.selected_booster_idx = None
        self.check_funds_and_spins_integrity()

    def handle_relic_sales(self, mouse_pos):
        if self.game_over or self.overlay_open or self.is_spinning:
            return
        for i in range(len(self.relics)):
            x_pos = self.relic_start_x + i * (self.relic_box_w + self.relic_gap)
            slot_rect = pygame.Rect(x_pos, self.shelf_y, self.relic_box_w, self.shelf_h)
            if slot_rect.collidepoint(mouse_pos):
                relic = self.relics[i]
                rar = relic["rarity"]
                rar_mult = {"Común": 0.4, "Raro": 0.5, "Épico": 0.6, "Legendario": 0.75, "Rainbow": 1.0}
                mult = rar_mult.get(rar, 0.5)
                refund = max(1, int(RELICS_POOL[relic["id"]]["price"] * mult))
                self.cash += refund
                self.relics.pop(i)
                self.rebuild_shop_buttons()
                self.check_funds_and_spins_integrity()
                break

    def generate_relic_choices(self):
        self.relic_selection_open = True
        self.relic_selection_progress = 0.0
        self.selected_relic_idx = None
        self.relic_selection_replace_mode = False
        self.relic_selection_replace_idx = -1
        self.relic_selection_options = []
        available_by_rarity = {}
        for rk in RELICS_POOL:
            if not any(r["id"] == rk for r in self.relics):
                rar = RELICS_POOL[rk]["rarity"]
                available_by_rarity.setdefault(rar, []).append(rk)
        if not available_by_rarity:
            self.relic_selection_open = False
            return
        for _ in range(3):
            rarity = self.get_progressive_rarity()
            pool = available_by_rarity.get(rarity, [])
            if not pool:
                all_available = [rk for sub in available_by_rarity.values() for rk in sub]
                if not all_available:
                    break
                rk = random.choice(all_available)
            else:
                rk = random.choice(pool)
            r_info = dict(RELICS_POOL[rk])
            r_info["id"] = rk
            self.relic_selection_options.append(r_info)
            for rar_list in available_by_rarity.values():
                if rk in rar_list:
                    rar_list.remove(rk)
                    break
    
    def confirm_relic_selection(self):
        if self.selected_relic_idx is None:
            return
        choice = self.relic_selection_options[self.selected_relic_idx]
        rk = choice["id"]
        if len(self.relics) < self.relic_slots:
            self.relics.append({"id": rk, "name": choice["name"], "desc": choice["desc"], "rarity": choice["rarity"]})
            self.log_text = f"[SISTEMA] RELIQUIA ADQUIRIDA: {choice['name']}"
            self.log_color = COLOR_GOLD
            self.relic_selection_open = False
            self.relic_selection_options = []
            self.selected_relic_idx = None
            play_sound(SOUND_RELIC)
            if rk == "sobre_seguro" and not self.sobre_booster_placed:
                self.generate_shop_offers()
        else:
            self.relic_selection_replace_mode = True

    def apply_relic_replace(self):
        if self.relic_selection_replace_idx < 0 or self.selected_relic_idx is None:
            return
        choice = self.relic_selection_options[self.selected_relic_idx]
        rk = choice["id"]
        self.relics.pop(self.relic_selection_replace_idx)
        self.relics.append({"id": rk, "name": choice["name"], "desc": choice["desc"], "rarity": choice["rarity"]})
        self.log_text = f"[SISTEMA] RELIQUIA ADQUIRIDA: {choice['name']} (reemplazada)"
        self.log_color = COLOR_GOLD
        self.relic_selection_open = False
        self.relic_selection_options = []
        self.selected_relic_idx = None
        self.relic_selection_replace_mode = False
        self.relic_selection_replace_idx = -1
        play_sound(SOUND_RELIC)
        if rk == "sobre_seguro" and not self.sobre_booster_placed:
            self.generate_shop_offers()

    def close_relic_selection(self):
        self.relic_selection_open = False
        self.relic_selection_options = []
        self.selected_relic_idx = None
        self.relic_selection_replace_mode = False
        self.relic_selection_replace_idx = -1

    def _draw_relic_selection(self, surface, mouse_pos):
        if not self.relic_selection_open:
            return
        self.relic_selection_progress += 0.025
        if self.relic_selection_progress > 1.0:
            self.relic_selection_progress = 1.0
        
        overlay_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        alpha_val = int(225 * min(1.0, self.relic_selection_progress * 1.5))
        overlay_surf.fill((8, 9, 15, alpha_val))
        surface.blit(overlay_surf, (0, 0))
        
        if self.relic_selection_replace_mode:
            self._draw_relic_replace(surface, mouse_pos)
            return
        
        mw, mh = min(900, SCREEN_WIDTH - 80), min(500, SCREEN_HEIGHT - 120)
        mx = (SCREEN_WIDTH - mw) // 2
        my = (SCREEN_HEIGHT - mh) // 2
        draw_panel(surface, pygame.Rect(mx, my, mw, mh), BG_CANVAS, (139, 92, 246), 20, 2)
        draw_text(surface, "/// SELECCIONA UNA RELIQUIA", get_font(13, True), (168, 85, 247), SCREEN_WIDTH // 2, my + 30)
        draw_text(surface, "Elige sabiamente...", get_font(11), COLOR_TEXT_MUTED, SCREEN_WIDTH // 2, my + 50)
        
        card_w, card_h = 180, min(230, mh - 190)
        total = len(self.relic_selection_options)
        total_w = total * card_w + (total - 1) * 30
        start_cx = (SCREEN_WIDTH - total_w) // 2
        
        self.relic_selection_clickable = []
        for idx, r_info in enumerate(self.relic_selection_options):
            delay = idx * 0.2
            progress = max(0.0, min(1.0, (self.relic_selection_progress - delay) * 2.5))
            ease = math.sin(progress * math.pi / 2)
            cx = start_cx + idx * (card_w + 30)
            cy = my + 80 + (1.0 - ease) * 160
            
            c_rect = pygame.Rect(cx, cy, card_w, card_h)
            self.relic_selection_clickable.append(c_rect)
            if progress > 0:
                style = RARITIES.get(r_info["rarity"], {"bg": (45, 45, 60), "color": (255, 255, 255)})
                border = style["color"]
                if r_info["rarity"] == "Rainbow":
                    border = rainbow_color(self.anim_tick * 4)
                elif r_info["rarity"] == "Legendario":
                    pulse = 0.6 + 0.4 * math.sin(self.anim_tick * 2.5)
                    border = tuple(int(c * pulse) for c in (234, 179, 8))
                
                selected = self.selected_relic_idx == idx
                draw_panel(surface, c_rect, style["bg"], COLOR_GOLD if selected else border, 12, 3 if selected else 1)
                
                pygame.draw.circle(surface, COLOR_GOLD, (c_rect.centerx, cy + 45), 24, 3)
                draw_text(surface, "R", get_font(scale(18), True), COLOR_GOLD, c_rect.centerx, cy + 45)
                draw_text(surface, r_info["name"], get_font(scale(13), True), style["color"], c_rect.centerx, cy + 80)
                draw_text(surface, r_info["rarity"], get_font(scale(11)), COLOR_TEXT_MUTED, c_rect.centerx, cy + 100)
                
                if c_rect.collidepoint(mouse_pos):
                    self.queue_tooltip(r_info["name"], r_info["desc"], mouse_pos)
        
        if self.relic_selection_progress >= 0.8:
            btn_y = my + mh - 50
            integrable = self.selected_relic_idx is not None
            int_col = (16, 185, 129) if integrable else (50, 60, 70)
            int_text = (255, 255, 255) if integrable else (100, 110, 120)
            int_rect = pygame.Rect(SCREEN_WIDTH // 2 - 110, btn_y, 100, 36)
            draw_panel(surface, int_rect, int_col, (52, 211, 153) if integrable else (70, 80, 90), 8)
            draw_text(surface, "Integrar", get_font(scale(13), True), int_text, int_rect.centerx, int_rect.centery)
            
            can_rect = pygame.Rect(SCREEN_WIDTH // 2 + 10, btn_y, 100, 36)
            hover_can = can_rect.collidepoint(mouse_pos)
            draw_panel(surface, can_rect, (50, 55, 75) if not hover_can else (70, 75, 95), (100, 120, 200), 8)
            draw_text(surface, "Cancelar", get_font(scale(13), True), (241, 245, 249), can_rect.centerx, can_rect.centery)
            
            self.relic_selection_buttons = {"integrar": int_rect, "cancelar": can_rect}

    def _draw_relic_replace(self, surface, mouse_pos):
        mw, mh = min(600, SCREEN_WIDTH - 80), min(400, SCREEN_HEIGHT - 120)
        mx = (SCREEN_WIDTH - mw) // 2
        my = (SCREEN_HEIGHT - mh) // 2
        draw_panel(surface, pygame.Rect(mx, my, mw, mh), BG_CANVAS, (239, 68, 68), 20, 2)
        draw_text(surface, "/// REEMPLAZAR RELIQUIA", get_font(14, True), (239, 68, 68), SCREEN_WIDTH // 2, my + 25)
        draw_text(surface, "Selecciona cual vender para dejar espacio:", get_font(11), COLOR_TEXT_MUTED, SCREEN_WIDTH // 2, my + 48)
        
        slot_w = min(160, (mw - 60) // self.relic_slots)
        gap = 16
        total_w = self.relic_slots * slot_w + (self.relic_slots - 1) * gap
        start_x = (SCREEN_WIDTH - total_w) // 2
        slot_h = min(180, mh - 160)
        
        self.relic_selection_clickable = []
        for i in range(self.relic_slots):
            sx = start_x + i * (slot_w + gap)
            sy = my + 70
            slot_rect = pygame.Rect(sx, sy, slot_w, slot_h)
            self.relic_selection_clickable.append(slot_rect)
            
            if i < len(self.relics):
                relic = self.relics[i]
                style = RARITIES.get(relic["rarity"], {"bg": (30, 30, 45), "color": (255, 255, 255)})
                selected = self.relic_selection_replace_idx == i
                border = (239, 68, 68) if selected else style["color"]
                draw_panel(surface, slot_rect, style["bg"], border, 10, 3 if selected else 1)
                draw_text(surface, relic["name"], get_font(scale(13), True), (255, 255, 255), slot_rect.centerx, sy + 30)
                draw_text(surface, relic["rarity"], get_font(scale(10)), COLOR_TEXT_MUTED, slot_rect.centerx, sy + 52)
                if slot_rect.collidepoint(mouse_pos):
                    self.queue_tooltip(relic["name"], relic["desc"], mouse_pos)
                desc = relic["desc"]
                draw_text(surface, (desc[:32] + "...") if len(desc) > 32 else desc, get_font(scale(10)), COLOR_TEXT_MUTED, slot_rect.centerx, sy + 75)
                if selected:
                    draw_text(surface, "VENDER", get_font(scale(12), True), (239, 68, 68), slot_rect.centerx, sy + slot_h - 30)
            else:
                draw_panel(surface, slot_rect, (14, 16, 26), (30, 36, 50), 10)
                draw_text(surface, "[ VACIO ]", get_font(scale(12), True), (60, 72, 95), slot_rect.centerx, slot_rect.centery)
        
        btn_y = my + mh - 50
        ap_rect = pygame.Rect(SCREEN_WIDTH // 2 - 110, btn_y, 100, 36)
        ap_valid = self.relic_selection_replace_idx >= 0
        ap_col = (16, 185, 129) if ap_valid else (50, 60, 70)
        ap_text = (255, 255, 255) if ap_valid else (100, 110, 120)
        draw_panel(surface, ap_rect, ap_col, (52, 211, 153) if ap_valid else (70, 80, 90), 8)
        draw_text(surface, "Aplicar", get_font(scale(13), True), ap_text, ap_rect.centerx, ap_rect.centery)
        
        can_rect = pygame.Rect(SCREEN_WIDTH // 2 + 10, btn_y, 100, 36)
        hover_can = can_rect.collidepoint(mouse_pos)
        draw_panel(surface, can_rect, (50, 55, 75) if not hover_can else (70, 75, 95), (100, 120, 200), 8)
        draw_text(surface, "Cancelar", get_font(scale(13), True), (241, 245, 249), can_rect.centerx, can_rect.centery)
        
        self.relic_selection_buttons = {"aplicar": ap_rect, "cancelar": can_rect}

    def _get_item_visual(self, item, is_blinded):
        is_neg = self.is_negative(item)
        visual = BAD_ITEM_STYLE if is_neg else RARITIES.get(item["rarity"], {"bg": (58, 58, 58), "text": (255, 255, 255), "color": (200, 200, 200)})
        bg_color = (50, 10, 15) if (is_blinded and is_neg) else visual["bg"]
        text_str = "[?] RISK" if (is_blinded and is_neg) else item["name"]
        border_color = visual.get("color", visual["text"])
        if item.get("rarity") == "Rainbow" and not is_blinded:
            border_color = rainbow_color(self.anim_tick * 3)
        return bg_color, text_str, visual["text"], border_color

    def _draw_roulette_card(self, surface, x_pos, y_pos, item, is_blinded, is_winner=False, is_upgrading=False):
        if x_pos < self.canvas_x - self.card_width or x_pos > self.canvas_x + self.canvas_width:
            return
        card_rect = pygame.Rect(x_pos, y_pos, self.card_width, self.card_height)
        bg_color, text_str, text_color, border_color = self._get_item_visual(item, is_blinded)

        # --- UPGRADE GLOW (card already shows upgraded value in roulette_items) ---
        if is_upgrading and self.upgrade_anim:
            t = self.upgrade_anim["timer"]
            draw_panel(surface, card_rect, bg_color, border_color, 10, 3)
            pulse = int(8 * math.sin(self.anim_tick * 12))
            glow = card_rect.inflate(16 + pulse, 16 + pulse)
            pygame.draw.rect(surface, (52, 211, 153), glow, width=3, border_radius=14)
            font_size = scale(14 if len(self.roulette_items) <= 1 else 13)
            draw_text(surface, text_str, get_font(font_size, True), text_color, card_rect.centerx, card_rect.centery)
            cb = item.get("cash_bonus", 0)
            if cb and not is_blinded:
                draw_text(surface, f"+{cb}$", get_font(scale(9), True), (74, 222, 128), card_rect.centerx, card_rect.top + scale(8))
            lbl = "★ MEJORADA ★" if t > 0.8 else "MEJORADA"
            lw = get_font(scale(11), True).size(lbl)[0]
            lbl_bg = pygame.Rect(0, 0, lw + 12, scale(18))
            lbl_bg.center = (card_rect.centerx, card_rect.top - scale(8))
            pygame.draw.rect(surface, (10, 12, 22), lbl_bg, border_radius=4)
            draw_text(surface, lbl, get_font(scale(11), True), (255, 255, 100), card_rect.centerx, card_rect.top - scale(8))
            return
        # --- end upgrade glow ---


        draw_panel(surface, card_rect, bg_color, border_color, 10, 2 if is_winner else 1)
        if is_winner:
            glow_rect = card_rect.inflate(6, 6)
            pygame.draw.rect(surface, COLOR_GOLD, glow_rect, width=2, border_radius=12)
        font_size = scale(14 if len(self.roulette_items) <= 1 else 13)
        draw_text(surface, text_str, get_font(font_size, True), text_color, card_rect.centerx, card_rect.centery)
        cash_bonus = item.get("cash_bonus", 0)
        if cash_bonus and not is_blinded:
            bonus_label = f"+{cash_bonus}$"
            draw_text(surface, bonus_label, get_font(scale(9), True), (74, 222, 128), card_rect.centerx, card_rect.top + scale(8))

    def _draw_roulette_track(self, surface, items, y_pos, position, winner_idx=-1):
        center_offset = self.canvas_x + (self.canvas_width / 2) - (self.card_width / 2)
        is_blinded = self.current_boss["id"] == "blind_blind"
        upgrade_idxs = set()
        if self.upgrade_anim:
            for ud in self.upgrade_anim["data"]:
                upgrade_idxs.add(ud["idx"])
        for i, item in enumerate(items):
            x_pos = (i * self.card_step) - position + center_offset
            is_winner = i == winner_idx and not self.is_spinning
            self._draw_roulette_card(surface, x_pos, y_pos, item, is_blinded, is_winner=is_winner, is_upgrading=(i in upgrade_idxs and not self.is_spinning))

    def queue_tooltip(self, name, desc, mouse_pos):
        self.tooltip_queue.append((name, desc, mouse_pos))

    def draw_queued_tooltips(self, surface):
        for name, desc, m_pos in self.tooltip_queue:
            font_title = get_font(scale(13), True)
            font_desc = get_font(scale(12))

            lines = desc.split("\n")
            line_h = scale(16)
            max_line_w = max(font_title.size(name)[0], max(font_desc.size(l)[0] for l in lines))
            tw = max_line_w + 24
            th = 28 + len(lines) * line_h
            tx = m_pos[0] + 15
            ty = m_pos[1] - 15

            if tx + tw > SCREEN_WIDTH:
                tx = m_pos[0] - tw - 10
            if ty + th > SCREEN_HEIGHT:
                ty = SCREEN_HEIGHT - th - 10

            tt_rect = pygame.Rect(tx, ty, tw, th)
            draw_panel(surface, tt_rect, (12, 15, 26), BORDER_BLUE, 8)

            draw_text(surface, name, font_title, COLOR_GOLD, tx + 12, ty + 14, "left")
            for li, line in enumerate(lines):
                draw_text(surface, line, font_desc, (226, 232, 240), tx + 12, ty + 36 + li * line_h, "left")
        self.tooltip_queue.clear()

    def draw(self, surface):
        if self.game_state == "menu":
            self._draw_main_menu(surface)
            return

        current_canvas_x = self.canvas_x
        current_canvas_y = self.canvas_y
        if self.shake_timer > 0:
            current_canvas_x += random.randint(-self.shake_intensity, self.shake_intensity)
            current_canvas_y += random.randint(-self.shake_intensity, self.shake_intensity)
            self.shake_timer -= 1

        surface.fill(BG_DARK_MAIN)
        mouse_pos = pygame.mouse.get_pos()

        for star in self.stars:
            alpha = 80 + int(40 * math.sin(self.anim_tick + star["x"] * 0.01))
            pygame.draw.circle(surface, (alpha, alpha, min(255, alpha + 40)), (int(star["x"]), int(star["y"])), star["size"])

        header_rect = pygame.Rect(self.margin, self.header_y, SCREEN_WIDTH - self.margin * 2, self.header_h)
        draw_panel(surface, header_rect, COLOR_HEADER, BORDER_BLUE, 12)

        col1 = self.margin + 16
        col2 = self.margin + int(SCREEN_WIDTH * 0.12)
        col3 = self.margin + int(SCREEN_WIDTH * 0.30)
        col4 = self.margin + int(SCREEN_WIDTH * 0.46)
        col5 = self.margin + int(SCREEN_WIDTH * 0.68)
        mid_y = self.header_y + self.header_h // 2

        ronda_txt = f"RONDA {self.round}/{VICTORY_ROUND}" if not self.has_won else f"MODO INFINITO ● RONDA {self.round}"
        draw_text(surface, ronda_txt, get_font(scale(15), True), COLOR_CYAN, col1, mid_y - 10, "left")
        # Prox. negativa
        prox = min((r for r in NEGATIVE_SCHEDULE if r not in self.negatives_added), default=None)
        if prox is not None:
            neg_txt = f"Prox. negativa: Ronda {prox}"
        else:
            neg_txt = "Todas las negativas agregadas"
        draw_text(surface, neg_txt, get_font(scale(9), True), (248, 113, 113), col1, mid_y + 10, "left")
        money_color = (52, 211, 153) if self.money >= 0 else (248, 113, 113)
        draw_text(surface, f"CR: {format_num(self.displayed_money)}", get_font(scale(15), True), money_color, col2, mid_y - 12, "left")

        target_prog = min(1.0, max(0.0, self.money / self.target_money)) if self.target_money > 0 else 0
        meta_color = (52, 211, 153) if self.money >= self.target_money else (251, 146, 60)
        draw_text(surface, f"META: {format_num(self.target_money)}", get_font(scale(12), True), meta_color, col2, mid_y + 8, "left")
        draw_progress_bar(surface, col2, mid_y + 22, int(SCREEN_WIDTH * 0.13), scale(8), target_prog, meta_color)

        cash_color = (74, 222, 128)
        draw_text(surface, f"$ {format_num(self.displayed_cash)}", get_font(scale(18), True), cash_color, col3, mid_y - 10, "left")
        draw_text(surface, "EFECTIVO", get_font(scale(11), True), (74, 222, 128), col3, mid_y + 12, "left")

        spin_prog = self.spins_left / self.max_spins if self.max_spins > 0 else 0
        draw_text(surface, f"GIROS: {max(0, self.spins_left)}/{self.max_spins}", get_font(scale(13), True), (241, 245, 249), col4, mid_y - 14, "left")
        draw_progress_bar(surface, col4, mid_y + 2, int(SCREEN_WIDTH * 0.10), scale(12), spin_prog, COLOR_CYAN)

        # Voucher inventory HUD (computed before boss to prevent overlap)
        owned_vouchers = []
        if self.has_pack_upgrade:
            owned_vouchers.append(("pack_up", VOUCHER_DEFS["pack_up"]["name"]))
        if self.has_shop_upgrade:
            owned_vouchers.append(("shop_up", VOUCHER_DEFS["shop_up"]["name"]))
        if self.dual_roulette_count > 0:
            owned_vouchers.append(("dual_roulette", VOUCHER_DEFS["dual_roulette"]["name"]))
        if self.extra_spins_per_round > 0:
            owned_vouchers.append(("extra_spin", VOUCHER_DEFS["extra_spin"]["name"]))
        voucher_area_rect = None
        if owned_vouchers:
            count_map = {}
            name_map = {}
            for vid, vname in owned_vouchers:
                if vid == "dual_roulette":
                    count_map[vid] = self.dual_roulette_count
                elif vid == "extra_spin":
                    count_map[vid] = self.extra_spins_per_round
                else:
                    count_map[vid] = 1
                name_map[vid] = vname
            icon_size = scale(28)
            gap = scale(6)
            total_w = len(count_map) * icon_size + (len(count_map) - 1) * gap
            start_x = SCREEN_WIDTH - self.margin - total_w - scale(8)
            icon_y = self.header_y + (self.header_h - icon_size) // 2
            voucher_area_rect = pygame.Rect(start_x - scale(4), icon_y - scale(2), total_w + scale(8), icon_size + scale(4))
            for vi, vid in enumerate(count_map):
                cx = start_x + vi * (icon_size + gap) + icon_size // 2
                draw_voucher_icon(surface, vid, cx, icon_y + icon_size // 2, icon_size, self.anim_tick)
                c = count_map[vid]
                if c > 1:
                    lbl = f"x{c}"
                    lw = get_font(scale(10), True).size(lbl)[0]
                    lbl_x = cx + icon_size // 2 - lw // 2 + scale(2)
                    lbl_y = icon_y - scale(2)
                    pygame.draw.rect(surface, (15, 23, 42), (lbl_x - scale(2), lbl_y, lw + scale(4), scale(14)), border_radius=3)
                    draw_text(surface, lbl, get_font(scale(10), True), COLOR_GOLD, cx + icon_size // 2 + scale(2), lbl_y + scale(7))
            if voucher_area_rect.collidepoint(mouse_pos) and not self.overlay_open:
                tooltip_lines = [f"{name_map[vid]} x{count_map[vid]}" for vid in count_map]
                self.queue_tooltip("VALES ADQUIRIDOS", "\n".join(tooltip_lines), mouse_pos)

        if self.current_boss["id"] != "none":
            draw_text(surface, f"[!] {self.current_boss['name']}", get_font(scale(12), True), (244, 63, 94), col5, mid_y - 6, "left")
            boss_rect = pygame.Rect(col5 - 5, self.header_y + 8, SCREEN_WIDTH - col5 - self.margin, self.header_h - 16)
            if boss_rect.collidepoint(mouse_pos) and (voucher_area_rect is None or not voucher_area_rect.collidepoint(mouse_pos)):
                self.queue_tooltip(self.current_boss["name"], self.current_boss["desc"], mouse_pos)

        canvas_rect = pygame.Rect(current_canvas_x, current_canvas_y, self.canvas_width, self.canvas_height)
        draw_panel(surface, canvas_rect, BG_CANVAS, BORDER_BLUE, 16)

        surface.set_clip(canvas_rect)
        n_tracks = len(self.roulette_items)
        gap = max(4, scale(6))
        total_gap = gap * (n_tracks - 1)
        track_h = (self.canvas_height - total_gap) // n_tracks
        card_h_actual = min(self.card_height, track_h - scale(4))
        for ri in range(n_tracks):
            y_center = current_canvas_y + ri * (track_h + gap) + (track_h - card_h_actual) // 2
            w_idx = self.last_winners[ri] if ri < len(self.last_winners) else -1
            self._draw_roulette_track(surface, self.roulette_items[ri], y_center, self.positions[ri], w_idx)

        mid_x = current_canvas_x + self.canvas_width // 2
        pulse = int(3 * math.sin(self.anim_tick * 4))
        for offset in range(3, 0, -1):
            alpha = 60 + offset * 30
            pygame.draw.line(surface, (250, 180, 25), (mid_x - offset, current_canvas_y), (mid_x - offset, current_canvas_y + self.canvas_height), 1)
            pygame.draw.line(surface, (250, 180, 25), (mid_x + offset, current_canvas_y), (mid_x + offset, current_canvas_y + self.canvas_height), 1)
        pygame.draw.line(surface, COLOR_GOLD, (mid_x, current_canvas_y - 4 - pulse), (mid_x, current_canvas_y + self.canvas_height + 4 + pulse), 3)
        pygame.draw.polygon(surface, COLOR_GOLD, [(mid_x, current_canvas_y - 8), (mid_x - 8, current_canvas_y + 2), (mid_x + 8, current_canvas_y + 2)])
        pygame.draw.polygon(surface, COLOR_GOLD, [(mid_x, current_canvas_y + self.canvas_height + 8), (mid_x - 8, current_canvas_y + self.canvas_height - 2), (mid_x + 8, current_canvas_y + self.canvas_height - 2)])
        surface.set_clip(None)

        action_rect = pygame.Rect(self.margin, self.action_y, SCREEN_WIDTH - self.margin * 2, self.action_h)
        draw_panel(surface, action_rect, (14, 18, 30), (35, 45, 68), 10)

        dash_y = self.dash_y
        deck_rect = pygame.Rect(self.deck_x, dash_y, self.deck_w, self.dash_h)
        draw_panel(surface, deck_rect, (18, 22, 36))
        real_deck_count = len(self.deck)
        draw_text(surface, f"MAZO [{real_deck_count}]", get_font(scale(14), True), COLOR_CYAN, deck_rect.x + 14, dash_y + 18, "left")

        total_cards = len(self.deck)
        if total_cards > 0:
            effect_counts = {}
            for item in self.deck:
                key = (item["type"], item["value"])
                effect_counts[key] = effect_counts.get(key, 0) + 1
            def sort_key(kv):
                t, v = kv[0]
                order = {"add": 0, "sub": 1, "mult": 2, "div": 3, "pow": 4, "zero": 5}.get(t, 9)
                return (order, -v if t == "add" else v)
            sorted_effects = sorted(effect_counts.items(), key=sort_key)
            max_visible = (self.dash_h - 62) // scale(14)
            hidden_count = max(0, len(sorted_effects) - max_visible)
            for i, ((t, v), count) in enumerate(sorted_effects):
                if i >= max_visible:
                    break
                if t == "add": label = f"+{int(v)} CR"
                elif t == "sub": label = f"-{int(v)} CR"
                elif t == "mult": label = f"x{v} CR"
                elif t == "div": label = f"/{v} CR"
                elif t == "pow": label = f"^{v} CR"
                elif t == "zero": label = "=0 CR"
                else: label = f"{t} {v}"
                pct = count / total_cards * 100
                line_y = dash_y + 38 + i * scale(14)
                is_neg = t in ("sub", "div", "zero")
                color = (248, 113, 113) if is_neg else COLOR_TEXT_MUTED
                draw_text(surface, f"{label}: {pct:.0f}%", get_font(scale(12)), color, deck_rect.x + 14, line_y, "left")
            if hidden_count > 0:
                more_y = dash_y + 38 + max_visible * scale(14)
                draw_text(surface, f"... +{hidden_count} mas", get_font(scale(11)), COLOR_TEXT_MUTED, deck_rect.x + 14, more_y, "left")
            shown = max_visible if hidden_count > 0 else len(sorted_effects)
            cash_y = dash_y + 38 + (shown + (1 if hidden_count > 0 else 0)) * scale(14) + scale(4)
        else:
            cash_y = dash_y + 38
        cash_max = self.cash_bonus_max_base + self.round // 3
        draw_text(surface, "$ Cash por casilla:", get_font(scale(12)), (74, 222, 128), deck_rect.x + 14, cash_y, "left")
        draw_text(surface, f"{self.cash_bonus_chance*100:.0f}% (+{self.cash_bonus_min}-{cash_max}$)", get_font(scale(12)), COLOR_TEXT_MUTED, deck_rect.x + 14, cash_y + scale(14), "left")

        if deck_rect.collidepoint(mouse_pos) and total_cards > 0:
            lines = []
            for (t, v), count in sorted_effects:
                if t == "add": lbl = f"+{int(v)} CR"
                elif t == "sub": lbl = f"-{int(v)} CR"
                elif t == "mult": lbl = f"x{v} CR"
                elif t == "div": lbl = f"/{v} CR"
                elif t == "pow": lbl = f"^{v} CR"
                elif t == "zero": lbl = "=0 CR"
                else: lbl = f"{t} {v}"
                pct = count / total_cards * 100
                lines.append(f"{lbl}: {pct:.0f}%")
            lines.append(f"---")
            lines.append(f"$ Cash: {self.cash_bonus_chance*100:.0f}% (+{self.cash_bonus_min}-{cash_max}$)")
            self.queue_tooltip("MAZO - Todas las probabilidades", "\n".join(lines), mouse_pos)

        log_rect = pygame.Rect(self.log_x, dash_y, self.log_w, self.dash_h)
        draw_panel(surface, log_rect, (15, 18, 28))
        draw_text(surface, "TERMINAL", get_font(scale(12), True), COLOR_CYAN, log_rect.x + 14, dash_y + 16, "left")
        log_display = self.log_text if len(self.log_text) <= 90 else self.log_text[:87] + "..."
        draw_text(surface, f"> {log_display}", get_font(scale(14), True), self.log_color, log_rect.x + 14, dash_y + self.dash_h // 2 + 6, "left")

        rng_rect = pygame.Rect(self.rng_x, dash_y, self.rng_w, self.dash_h)
        draw_panel(surface, rng_rect, (18, 22, 36))
        draw_text(surface, "RNG TIENDA", get_font(scale(14), True), COLOR_GOLD, rng_rect.x + 14, dash_y + 16, "left")
        ratios = self.get_current_shop_ratios()
        rng_lines = [("Común", "C"), ("Raro", "R"), ("Épico", "E"), ("Legendario", "L"), ("Rainbow", "Rain")]
        for i, (key, label) in enumerate(rng_lines):
            col = i % 2
            row = i // 2
            rx = rng_rect.x + 14 + col * (self.rng_w // 2 - 10)
            ry = dash_y + 40 + row * scale(22)
            draw_text(surface, "♦", get_font(scale(12), True), RARITIES[key]["color"], rx, ry, "left")
            pct = f"{ratios[key]:.2f}%" if key == "Rainbow" else f"{ratios[key]:.1f}%"
            draw_text(surface, f"{label}: {pct}", get_font(scale(12)), COLOR_TEXT_MUTED, rx + 16, ry, "left")

        shelf_y = self.shelf_y
        draw_text(surface, f"RELIQUIAS  {len(self.relics)}/{self.relic_slots}", get_font(scale(13), True), COLOR_CYAN, self.margin, shelf_y - 18, "left")

        for idx in range(self.relic_slots):
            rx = self.relic_start_x + idx * (self.relic_box_w + self.relic_gap)
            slot_rect = pygame.Rect(rx, shelf_y, self.relic_box_w, self.shelf_h)
            if idx < len(self.relics):
                relic_data = self.relics[idx]
                r_style = RARITIES.get(relic_data["rarity"], {"bg": (30, 30, 45), "color": (255, 255, 255)})
                if slot_rect.collidepoint(mouse_pos):
                    draw_panel(surface, slot_rect, (80, 20, 20), (239, 68, 68), 10, 2)
                    draw_text(surface, "PURGAR RELIQUIA", get_font(scale(14), True), (255, 100, 100), slot_rect.centerx, shelf_y + 28)
                    rar = relic_data["rarity"]
                    rar_mult = {"Común": 0.4, "Raro": 0.5, "Épico": 0.6, "Legendario": 0.75, "Rainbow": 1.0}
                    mult = rar_mult.get(rar, 0.5)
                    draw_text(surface, f"+{max(1, int(RELICS_POOL[relic_data['id']]['price'] * mult))} $", get_font(scale(13), True), (255, 255, 255), slot_rect.centerx, shelf_y + 52)
                    if not self.overlay_open:
                        self.queue_tooltip(relic_data["name"], relic_data["desc"], mouse_pos)
                else:
                    draw_panel(surface, slot_rect, r_style["bg"], r_style["color"], 10)
                    draw_text(surface, relic_data["name"], get_font(scale(14), True), (255, 255, 255), slot_rect.centerx, shelf_y + 24)
                    desc = relic_data["desc"]
                    draw_text(surface, (desc[:36] + "...") if len(desc) > 36 else desc, get_font(scale(11)), COLOR_TEXT_MUTED, slot_rect.centerx, shelf_y + 50)
            else:
                draw_panel(surface, slot_rect, (14, 16, 26), (30, 36, 50), 10)
                draw_text(surface, "[ SLOT VACIO ]", get_font(scale(13), True), (60, 72, 95), slot_rect.centerx, slot_rect.centery)

        shop_rect = pygame.Rect(self.margin, self.shop_y, SCREEN_WIDTH - self.margin * 2, self.shop_h)
        draw_panel(surface, shop_rect, BG_CANVAS, BORDER_BLUE, 16)
        draw_text(surface, "/// MERCADO NEGRO", get_font(scale(15), True), COLOR_GOLD, self.margin + 14, self.shop_y + 12, "left")

        market_x = self.margin + scale(10)
        pygame.draw.line(surface, BORDER_BLUE, (self.v_separator_x, self.shop_y + 6), (self.v_separator_x, self.shop_y + self.shop_h - 6), 2)

        max_slots = 4 if self.has_shop_upgrade else 3
        for i in range(max_slots):
            bx = market_x + i * (self.box_width + scale(14))
            if bx + self.box_width > self.v_separator_x - scale(8):
                continue
            box_rect = pygame.Rect(bx, self.market_y, self.box_width, self.box_height)

            if i >= len(self.shop_offers) or self.shop_offers[i] is None:
                draw_panel(surface, box_rect, (14, 16, 22), (25, 32, 45), 10)
                draw_text(surface, "[ AGOTADO ]", get_font(scale(14), True), (75, 85, 105), box_rect.centerx, box_rect.centery)
                continue

            item = self.shop_offers[i]

            is_neg = self.is_negative(item) if not item.get("is_box") and not item.get("is_relic") else False
            is_legendario = not item.get("is_box") and not item.get("is_relic") and item.get("rarity") == "Legendario"
            is_rainbow = not item.get("is_box") and not item.get("is_relic") and item.get("rarity") == "Rainbow"

            if item.get("is_box"):
                box_bg, box_border = (30, 25, 15), (251, 146, 60)
            elif item.get("is_relic"):
                box_bg, box_border = (40, 30, 10), COLOR_GOLD
            elif is_neg:
                box_bg, box_border = (50, 10, 10), (220, 38, 38)
            elif is_rainbow:
                box_bg = (40, 5, 50)
                box_border = rainbow_color(self.anim_tick * 3)
            elif is_legendario:
                pulse = 0.7 + 0.3 * math.sin(self.anim_tick * 2.5)
                box_bg = (45, 25, 5)
                box_border = tuple(int(c * pulse) for c in (234, 179, 8))
            else:
                rarity = item["rarity"]
                box_bg = RARITIES[rarity]["bg"]
                box_border = RARITIES[rarity]["color"]

            draw_panel(surface, box_rect, box_bg, box_border, 10)

            if not item.get("is_box"):
                _is_new = True
                if item.get("is_relic"):
                    _is_new = not any(r["id"] == item["id"] for r in self.relics)
                else:
                    _is_new = not any(d["name"] == item["name"] for d in self.deck)
                if _is_new:
                    draw_text(surface, "NUEVO", get_font(scale(11), True), (255, 220, 50), box_rect.centerx, self.market_y - scale(14))

            text_y = self.market_y + 24

            if item.get("is_box"):
                draw_text(surface, item["name"], get_font(scale(15), True), (251, 146, 60), box_rect.centerx, text_y)
                draw_text(surface, "Sorpresa / Pack", get_font(scale(12)), (251, 191, 36), box_rect.centerx, text_y + scale(26))
            elif item.get("is_relic"):
                draw_text(surface, item["name"], get_font(scale(15), True), COLOR_GOLD, box_rect.centerx, text_y)
                draw_text(surface, "Reliquia", get_font(scale(12)), (234, 140, 8), box_rect.centerx, text_y + scale(26))
                if box_rect.collidepoint(mouse_pos) and not self.overlay_open:
                    self.queue_tooltip(item["name"], item["desc"], mouse_pos)
            else:
                item_color = (248, 113, 113) if is_neg else RARITIES[item["rarity"]]["color"]
                draw_text(surface, item["name"], get_font(scale(16), True), item_color, box_rect.centerx, text_y)
                draw_text(surface, f"Rareza: {item['rarity']}", get_font(scale(12)), COLOR_TEXT_MUTED, box_rect.centerx, text_y + scale(26))

            draw_text(surface, f"Coste: {item['price']} $", get_font(scale(14), True), COLOR_GOLD, box_rect.centerx, self.market_y + self.box_height - scale(52))

            if is_rainbow:
                for a in range(6):
                    ang = self.anim_tick * 2.5 + a * math.pi / 3
                    dist = scale(6) + scale(3) * math.sin(self.anim_tick * 3 + a)
                    sx = box_rect.centerx + int(math.cos(ang) * dist)
                    sy = self.market_y + self.box_height // 2 + int(math.sin(ang) * dist * 0.4)
                    col = rainbow_color(self.anim_tick * 2 + a * 0.8)
                    pygame.draw.circle(surface, col, (sx, sy), max(2, scale(3)))
                for a in range(3):
                    ang = self.anim_tick * 4 + a * math.pi * 2 / 3
                    d2 = scale(12) + scale(2) * math.sin(self.anim_tick * 5 + a * 2)
                    sx = box_rect.centerx + int(math.cos(ang) * d2)
                    sy = self.market_y + self.box_height // 2 + int(math.sin(ang) * d2 * 0.3)
                    col = rainbow_color(self.anim_tick * 3 + a)
                    pygame.draw.circle(surface, (255, 255, 255), (sx, sy), max(1, scale(2)))
            elif is_legendario:
                for a in range(4):
                    ang = self.anim_tick * 2 + a * math.pi / 2
                    dx = int(math.cos(ang) * scale(8))
                    dy = int(math.sin(ang) * scale(6))
                    sx = box_rect.centerx + dx
                    sy = self.market_y + self.box_height // 2 + dy
                    alpha = int(180 + 75 * math.sin(self.anim_tick * 3 + a))
                    col = (255, min(255, alpha + 50), 50)
                    pygame.draw.circle(surface, col, (sx, sy), max(2, scale(3)))

        vx = SCREEN_WIDTH - self.margin - self.voucher_width
        v_rect = pygame.Rect(vx, self.market_y, self.voucher_width, self.box_height)
        if self.current_voucher:
            hovered = v_rect.collidepoint(mouse_pos)
            draw_voucher_card(surface, v_rect, self.current_voucher, self.anim_tick, hovered)
            if hovered and not self.overlay_open:
                self.queue_tooltip(self.current_voucher["name"], self.current_voucher["desc"], mouse_pos)
        else:
            draw_panel(surface, v_rect, (14, 16, 22), (25, 32, 45), 12)
            draw_text(surface, "VALES", get_font(scale(14), True), (75, 85, 105), v_rect.centerx, v_rect.centery - 12)
            draw_text(surface, "[ TODOS ADQUIRIDOS ]", get_font(scale(13), True), (75, 85, 105), v_rect.centerx, v_rect.centery + 14)

        for p in self.particles:
            pygame.draw.circle(surface, p["color"], (int(p["x"]), int(p["y"])), max(1, int(p["radius"] * p["life"])))

        for btn in self.buttons:
            btn.draw(surface, mouse_pos)
        for btn in self.shop_buttons:
            btn.draw(surface, mouse_pos)

        if self.overlay_open:
            overlay_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            alpha_val = int(225 * min(1.0, self.booster_anim_progress * 1.5))
            overlay_surf.fill((8, 9, 15, alpha_val))
            surface.blit(overlay_surf, (0, 0))

            mw, mh = min(900, SCREEN_WIDTH - 80), min(440, SCREEN_HEIGHT - 120)
            mx = (SCREEN_WIDTH - mw) // 2
            my = (SCREEN_HEIGHT - mh) // 2
            draw_panel(surface, pygame.Rect(mx, my, mw, mh), BG_CANVAS, (139, 92, 246), 20, 2)
            draw_text(surface, "/// TRANSFERENCIA: DESPLEGANDO SOBRE DE DATOS", get_font(13, True), (168, 85, 247), SCREEN_WIDTH // 2, my + 35)

            card_w, card_h = 160, min(220, mh - 160)
            total_cards = len(self.booster_options)
            total_w = total_cards * card_w + (total_cards - 1) * 25
            start_cx = (SCREEN_WIDTH - total_w) // 2

            self.booster_clickable_cards = []
            for idx, opt in enumerate(self.booster_options):
                card_delay = idx * 0.18
                card_progress = max(0.0, min(1.0, (self.booster_anim_progress - card_delay) * 2.5))
                ease_card = math.sin(card_progress * math.pi / 2)

                cx = start_cx + idx * (card_w + 25)
                cy = my + 95 + (1.0 - ease_card) * 140

                c_rect = pygame.Rect(cx, cy, card_w, card_h)
                self.booster_clickable_cards.append((c_rect, idx))

                if card_progress > 0:
                    item = opt["item"]
                    style = RARITIES.get(item["rarity"], {"bg": (45, 45, 60), "color": (255, 255, 255)})

                    if item.get("rarity") == "Rainbow":
                        glow_r = c_rect.inflate(scale(6), scale(6))
                        glow_c = rainbow_color(self.anim_tick * 2)
                        draw_panel(surface, glow_r, (0, 0, 0, 0), glow_c, 14, 2)
                        border = rainbow_color(self.anim_tick * 4)
                    elif item.get("rarity") == "Legendario":
                        pulse = 0.6 + 0.4 * math.sin(self.anim_tick * 2.5)
                        border = tuple(int(c * pulse) for c in (234, 179, 8))
                    else:
                        border = style["color"]

                    draw_panel(surface, c_rect, style["bg"], COLOR_GOLD if self.selected_booster_idx == idx else border, 12, 3 if self.selected_booster_idx == idx else 1)
                    draw_text(surface, item["name"], get_font(scale(13), True), style["color"], c_rect.centerx, cy + 28)

                    if item.get("is_voucher") and item.get("id"):
                        draw_voucher_icon(surface, item["id"], c_rect.centerx, cy + card_h // 2 - 10, min(90, card_w - 30), self.anim_tick)
                    elif item.get("is_relic"):
                        pygame.draw.circle(surface, COLOR_GOLD, (c_rect.centerx, cy + card_h // 2 - 10), 28, 3)
                        draw_text(surface, "R", get_font(scale(20), True), COLOR_GOLD, c_rect.centerx, cy + card_h // 2 - 10)

                    if item.get("is_relic") or item.get("is_voucher"):
                        if c_rect.collidepoint(mouse_pos):
                            self.queue_tooltip(item["name"], item["desc"], mouse_pos)

                    if item.get("type") == "ultra":
                        draw_text(surface, "ULTRA-DROP (0.1%)", get_font(scale(12), True), (244, 63, 94), c_rect.centerx, cy + card_h - 58)
                    elif not item.get("is_voucher"):
                        draw_text(surface, f"Rareza: {item['rarity']}", get_font(scale(12)), COLOR_TEXT_MUTED, c_rect.centerx, cy + card_h - 58)

                    if item.get("rarity") == "Rainbow" and card_progress > 0.5:
                        for a in range(6):
                            ang = self.anim_tick * 2 + a * math.pi / 3
                            d = scale(8) + scale(3) * math.sin(self.anim_tick * 3 + a)
                            px = c_rect.centerx + int(math.cos(ang) * d)
                            py = cy + card_h // 2 + int(math.sin(ang) * d * 0.5)
                            col = rainbow_color(self.anim_tick * 2 + a * 0.7)
                            pygame.draw.circle(surface, col, (px, py), max(2, scale(3)))
                    elif item.get("rarity") == "Legendario" and card_progress > 0.5:
                        for a in range(3):
                            ang = self.anim_tick * 2.5 + a * math.pi * 2 / 3
                            px = c_rect.centerx + int(math.cos(ang) * scale(10))
                            py = cy + card_h // 2 + int(math.sin(ang) * scale(6))
                            alpha = int(200 + 55 * math.sin(self.anim_tick * 4 + a))
                            col = (255, min(255, alpha), 40)
                            pygame.draw.circle(surface, col, (px, py), max(2, scale(3)))

                    state_txt = "Seleccionado" if self.selected_booster_idx == idx else "Marcar"
                    state_col = COLOR_GOLD if self.selected_booster_idx == idx else (52, 211, 153)
                    draw_text(surface, state_txt, get_font(scale(13), True), state_col, c_rect.centerx, cy + card_h - 28)

            if self.booster_anim_progress >= 0.8:
                for b in self.booster_buttons:
                    b.draw(surface, mouse_pos)

        if self.relic_selection_open:
            self._draw_relic_selection(surface, mouse_pos)

        if self.game_over or self.game_won:
            end_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            end_surf.fill((10, 12, 22, 240))
            surface.blit(end_surf, (0, 0))

            box_w, box_h = min(580, SCREEN_WIDTH - 100), 280
            bx = (SCREEN_WIDTH - box_w) // 2
            by = (SCREEN_HEIGHT - box_h) // 2

            if self.game_won and self.has_won:
                draw_panel(surface, pygame.Rect(bx, by, box_w, box_h), (12, 38, 28), (52, 211, 153), 16, 2)
                draw_text(surface, "SISTEMA PURGADO: VICTORIA", get_font(20, True), (52, 211, 153), SCREEN_WIDTH // 2, by + 55)
                draw_text(surface, f"Has superado {VICTORY_ROUND} rondas con {format_num(self.money)} CR!", get_font(12), (200, 230, 210), SCREEN_WIDTH // 2, by + 105)
                draw_text(surface, "[N] MODO INFINITO  |  [R] Reiniciar  |  [ESC] Salir", get_font(11, True), COLOR_GOLD, SCREEN_WIDTH // 2, by + 165)
            else:
                draw_panel(surface, pygame.Rect(bx, by, box_w, box_h), (38, 12, 16), (248, 113, 113), 16, 2)
                draw_text(surface, "CONEXION PERDIDA: GAME OVER", get_font(20, True), (248, 113, 113), SCREEN_WIDTH // 2, by + 55)
                draw_text(surface, f"No alcanzaste la meta de {format_num(self.target_money)} CR en la Ronda {self.round}.", get_font(11), (230, 200, 200), SCREEN_WIDTH // 2, by + 100)
                draw_text(surface, f"Fondos finales: {format_num(self.money)} CR", get_font(10, True), COLOR_TEXT_MUTED, SCREEN_WIDTH // 2, by + 130)

            draw_text(surface, "Mantén [R] para reiniciar  |  [ESC] para salir", get_font(10, True), COLOR_GOLD, SCREEN_WIDTH // 2, by + 200)

        if self.reset_hold_time > 0:
            bar_w, bar_h = 260, 14
            bx = (SCREEN_WIDTH - bar_w) // 2
            by = SCREEN_HEIGHT - self.margin - 30
            progress = min(1.0, self.reset_hold_time / RESET_HOLD_SECONDS)
            draw_progress_bar(surface, bx, by, bar_w, bar_h, progress, (251, 146, 60))
            draw_text(surface, "Reiniciando Terminal...", get_font(9, True), (251, 146, 60), SCREEN_WIDTH // 2, by - 12)

        draw_text(surface, "[ESC] Salir", get_font(8), (60, 72, 95), SCREEN_WIDTH - self.margin - 10, SCREEN_HEIGHT - 12, "right")
        self.draw_queued_tooltips(surface)

        if self.menu_open:
            self._draw_menu(surface, mouse_pos)

    def _draw_menu(self, surface, mouse_pos):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((8, 9, 15, 220))
        surface.blit(overlay, (0, 0))
        mw, mh = 340, 300
        mx = (SCREEN_WIDTH - mw) // 2
        my = (SCREEN_HEIGHT - mh) // 2
        draw_panel(surface, pygame.Rect(mx, my, mw, mh), (15, 18, 30), (100, 120, 200), 16, 2)

        if self.settings_open:
            mw, mh = 360, 360
            mx = (SCREEN_WIDTH - mw) // 2
            my = (SCREEN_HEIGHT - mh) // 2
            draw_panel(surface, pygame.Rect(mx, my, mw, mh), (15, 18, 30), (100, 120, 200), 16, 2)
            draw_text(surface, "CONFIGURACION", get_font(scale(18), True), COLOR_CYAN, SCREEN_WIDTH // 2, my + 25)
            self._menu_buttons = {}
            sliders = [
                ("Volumen General", "master", MASTER_VOLUME),
                ("Volumen Efectos", "sfx", SFX_VOLUME),
                ("Volumen Musica", "music", MUSIC_VOLUME),
            ]
            bar_w, bar_h = 220, 10
            bar_x = (SCREEN_WIDTH - bar_w) // 2
            for i, (label, key, val) in enumerate(sliders):
                sy = my + 70 + i * 75
                draw_text(surface, label, get_font(scale(13), True), (241, 245, 249), SCREEN_WIDTH // 2, sy)
                bg_rect = pygame.Rect(bar_x, sy + 22, bar_w, bar_h)
                draw_panel(surface, bg_rect, (30, 35, 55), (60, 72, 95), 6)
                fill_w = int(bar_w * val)
                if fill_w > 0:
                    fill_rect = pygame.Rect(bar_x, sy + 22, fill_w, bar_h)
                    draw_panel(surface, fill_rect, (52, 211, 153), (52, 211, 153), 6)
                handle_cx = bar_x + fill_w
                handle_cy = sy + 22 + bar_h // 2
                pygame.draw.circle(surface, (255, 255, 255), (handle_cx, handle_cy), scale(7))
                pygame.draw.circle(surface, (52, 211, 153), (handle_cx, handle_cy), scale(4))
                self._menu_buttons[f"vol_{key}"] = bg_rect.inflate(scale(10), scale(10))
                pct_lbl = f"{int(val * 100)}%"
                draw_text(surface, pct_lbl, get_font(scale(11), True), (52, 211, 153), bar_x + bar_w + scale(18), sy + 22 + bar_h // 2)
            back_rect = pygame.Rect(SCREEN_WIDTH // 2 - 60, my + mh - 50, 120, 36)
            hover = back_rect.collidepoint(mouse_pos)
            draw_panel(surface, back_rect, (30, 35, 55) if not hover else (50, 55, 75), (100, 120, 200), 8)
            draw_text(surface, "Volver", get_font(scale(14), True), (241, 245, 249), back_rect.centerx, back_rect.centery)
            self._menu_buttons["back"] = back_rect
        else:
            draw_text(surface, "MENU", get_font(scale(20), True), COLOR_CYAN, SCREEN_WIDTH // 2, my + 30)
            btn_w, btn_h = 200, 40
            btn_x = (SCREEN_WIDTH - btn_w) // 2
            labels = ["Continuar", "Configuracion", "Salir"]
            actions = ["continue", "settings", "quit"]
            self._menu_buttons = {}
            for i, (lbl, act) in enumerate(zip(labels, actions)):
                by = my + 90 + i * 60
                rect = pygame.Rect(btn_x, by, btn_w, btn_h)
                hover = rect.collidepoint(mouse_pos)
                draw_panel(surface, rect, (30, 35, 55) if not hover else (50, 55, 75), (100, 120, 200), 8)
                draw_text(surface, lbl, get_font(scale(15), True), (241, 245, 249), rect.centerx, rect.centery)
                self._menu_buttons[act] = rect

    def _update_volume_from_slider(self, action, mouse_x, rect):
        global MASTER_VOLUME, SFX_VOLUME, MUSIC_VOLUME
        rel_x = mouse_x - rect.x
        val = max(0.0, min(1.0, rel_x / rect.width))
        if action == "vol_master" or action == "volume":
            MASTER_VOLUME = val
        elif action == "vol_sfx":
            SFX_VOLUME = val
        elif action == "vol_music":
            MUSIC_VOLUME = val
        self._set_music_state(self.game_state == "playing")
        self._music_current_vol = self._music_target_vol
        pygame.mixer.music.set_volume(self._music_current_vol)

    def _handle_menu_click(self, mouse_pos):
        if not hasattr(self, '_menu_buttons'):
            return
        global MASTER_VOLUME, SFX_VOLUME, MUSIC_VOLUME
        for action, rect in self._menu_buttons.items():
            if rect.collidepoint(mouse_pos):
                if action == "continue":
                    self.menu_open = False
                elif action == "settings":
                    self.settings_open = True
                elif action == "quit":
                    self.menu_open = False
                    self.game_state = "menu"
                    self._stop_music()
                elif action == "back":
                    self.settings_open = False
                elif action.startswith("vol"):
                    self._update_volume_from_slider(action, mouse_pos[0], rect)
                break

    def _handle_main_menu_click(self, mouse_pos):
        if not hasattr(self, 'main_menu_buttons'):
            return
        global MASTER_VOLUME, SFX_VOLUME, MUSIC_VOLUME
        if self.settings_open:
            if hasattr(self, '_settings_buttons'):
                for action, rect in self._settings_buttons.items():
                    if rect.collidepoint(mouse_pos):
                        if action == "back":
                            self.settings_open = False
                        elif action.startswith("vol"):
                            self._update_volume_from_slider(action, mouse_pos[0], rect)
                        break
            return
        for action, rect in self.main_menu_buttons.items():
            if rect.collidepoint(mouse_pos):
                if action == "new_game":
                    self._start_new_game()
                elif action == "settings":
                    self.settings_open = True
                elif action == "quit":
                    self.running = False
                break

    def handle_global_events(self):
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if self.game_state == "menu":
                    if event.key == pygame.K_ESCAPE:
                        if self.settings_open:
                            self.settings_open = False
                        else:
                            self.running = False
                elif event.key == pygame.K_r:
                    self.r_hold_start = time.time()
                    self.r_holding = True
                elif event.key == pygame.K_ESCAPE:
                    if self.game_over or self.game_won:
                        self.game_state = "menu"
                        self.game_over = False
                        self.game_won = False
                        self._stop_music()
                    elif self.settings_open:
                        self.settings_open = False
                    elif self.menu_open:
                        self.menu_open = False
                    else:
                        self.menu_open = not self.menu_open
                elif event.key == pygame.K_SPACE:
                    if not self.menu_open:
                        self.start_spin()
                elif event.key == pygame.K_n:
                    if not self.menu_open:
                        if self.game_won and self.has_won:
                            self.game_won = False
                        self.advance_round_clean()
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_r:
                    self.r_holding = False
                    self.reset_hold_time = 0

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                buttons = None
                if self.game_state == "menu" and self.settings_open and hasattr(self, '_settings_buttons'):
                    buttons = self._settings_buttons
                elif self.menu_open and self.settings_open and hasattr(self, '_menu_buttons'):
                    buttons = self._menu_buttons
                if buttons:
                    for action, rect in buttons.items():
                        if rect.collidepoint(mouse_pos) and action.startswith("vol"):
                            self._dragging_slider = (buttons, action)
                            break
                if self.game_state == "menu":
                    self._handle_main_menu_click(mouse_pos)
                    return

                if self.menu_open:
                    self._handle_menu_click(mouse_pos)
                    return

                if self.relic_selection_open and self.relic_selection_progress >= 0.8:
                    if hasattr(self, 'relic_selection_buttons'):
                        for action, rect in self.relic_selection_buttons.items():
                            if rect.collidepoint(mouse_pos):
                                if action == "integrar":
                                    self.confirm_relic_selection()
                                elif action == "aplicar":
                                    self.apply_relic_replace()
                                elif action == "cancelar":
                                    if self.relic_selection_replace_mode:
                                        self.relic_selection_replace_mode = False
                                        self.relic_selection_replace_idx = -1
                                    else:
                                        self.close_relic_selection()
                                return
                    if hasattr(self, 'relic_selection_clickable'):
                        for idx, c_rect in enumerate(self.relic_selection_clickable):
                            if c_rect.collidepoint(mouse_pos):
                                if self.relic_selection_replace_mode:
                                    self.relic_selection_replace_idx = idx
                                else:
                                    self.selected_relic_idx = idx
                                return
                    self.close_relic_selection()
                    return

                if self.overlay_open and self.booster_anim_progress >= 0.8:
                    for c_rect, idx in self.booster_clickable_cards:
                        if c_rect.collidepoint(mouse_pos):
                            self.selected_booster_idx = idx
                            return
                    for b in self.booster_buttons:
                        b.handle_event(event, mouse_pos)
                    return

                for btn in self.buttons:
                    btn.handle_event(event, mouse_pos)
                for s_btn in self.shop_buttons:
                    s_btn.handle_event(event, mouse_pos)
                self.handle_relic_sales(mouse_pos)

            elif event.type == pygame.MOUSEMOTION:
                if self._dragging_slider is not None:
                    buttons, action = self._dragging_slider
                    if action in buttons:
                        self._update_volume_from_slider(action, event.pos[0], buttons[action])

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self._dragging_slider = None

        if self.r_holding:
            elapsed = time.time() - self.r_hold_start
            self.reset_hold_time = elapsed
            if elapsed >= RESET_HOLD_SECONDS:
                self.full_reset()
                self.r_holding = False
                self.reset_hold_time = 0
        else:
            self.reset_hold_time = 0

    def core_loop(self):
        last_time = time.time()
        while self.running:
            current_time = time.time()
            dt = (current_time - last_time) * 60.0
            last_time = current_time
            if dt > 3.0: dt = 1.0
            
            self.handle_global_events()
            self.update_physics(dt)
            self.draw(screen)
            pygame.display.flip()
            clock.tick(FPS)
            
        pygame.quit(); sys.exit()

if __name__ == "__main__":
    game_instance = PygameMathRoulette()
    game_instance.core_loop()