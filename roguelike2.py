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

def play_dynamic_click(velocity, is_dual=False):
    factor = max(0.75, min(1.2, velocity / 40.0))
    pool = CLICK_POOL_DUAL if is_dual else CLICK_POOL_SINGLE
    sound = random.choice(pool)
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
        self.has_dual_roulette = False
        self.extra_spins_per_round = 0
        
        self.is_spinning = False
        self.roulette_1_active = False
        self.roulette_2_active = False
        
        self.relic_slots = 3
        self._compute_layout()
        self.card_width = max(120, min(165, int(SCREEN_WIDTH * 0.095)))
        self.card_height = max(95, min(120, int(self.canvas_height * 0.52)))
        self.card_step = self.card_width + CARD_SPACING
        
        self.position = 0.0
        self.velocity = 0.0
        self.last_card_trigger = -1
        
        self.position_dual = 0.0
        self.velocity_dual = 0.0
        self.last_card_trigger_dual = -1
        
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
        self.booster_options = []       
        self.booster_buttons = []
        self.booster_clickable_cards = []
        self.booster_anim_progress = 0.0
        self.selected_booster_idx = None
        
        self.relics = []
        self.has_won = False
        self.upgrade_anim = None
        self.RELICS_POOL = {
            "tarjeta_clonada": {"name": "Tarjeta Clonada", "desc": "Permite saldo negativo de hasta -15 CR.", "price": 12, "rarity": "Raro"},
            "segunda_oportunidad": {"name": "Segunda Oportunidad", "desc": "10% de probabilidad de evadir una casilla negativa y repetir el giro sin coste.", "price": 20, "rarity": "Épico"},
            "mejora_progresiva": {"name": "Mejora Progresiva", "desc": "Al tocar una casilla positiva Común o Raro, mejora permanentemente al siguiente escalón.", "price": 28, "rarity": "Épico"}
        }
        self.UPGRADE_MAP = {
            "+1 [CR]": {"type": "add", "value": 2, "name": "+2 [CR]", "rarity": "Común"},
            "+2 [CR]": {"type": "add", "value": 3, "name": "+3 [CR]", "rarity": "Común"},
            "+3 [CR]": {"type": "add", "value": 5, "name": "+5 [CR]", "rarity": "Raro"},
            "+5 [CR]": {"type": "add", "value": 7, "name": "+7 [CR]", "rarity": "Raro"},
            "+7 [CR]": {"type": "add", "value": 10, "name": "+10 [CR]", "rarity": "Épico"},
        }
        
        self.init_game_data()
        self.build_ui_buttons()

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
        self.dash_h = scale(118)

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
        self.has_dual_roulette = False
        self.extra_spins_per_round = 0
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
        self.money = 6.0
        self.displayed_money = 6.0
        self.cash = 5.0
        self.displayed_cash = 5.0
        self.round = 1
        self.target_money = 18.0
        self.max_spins = 5 + self.extra_spins_per_round
        self.spins_left = self.max_spins
        self.reroll_cost = 1
        self.current_boss = NO_BOSS
        self.game_over = False
        self.game_won = False
        self.upgrade_anim = None
        self.is_spinning = False
        self.last_winners = []
        
        self.deck = [
            {"type": "add", "value": 2, "name": "+2 [CR]", "rarity": "Común"},
            {"type": "add", "value": 1, "name": "+1 [CR]", "rarity": "Común"},
            {"type": "add", "value": 3, "name": "+3 [CR]", "rarity": "Común"},
            {"type": "sub", "value": 1, "name": "-1 [CR]", "rarity": "Común"},
        ]
        self.roulette_items_top = [random.choice(self.deck) for _ in range(15)]
        self.roulette_items_dual = [random.choice(self.deck) for _ in range(15)]
        self.shop_offers = []
        self.current_voucher = None
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
        r = self.round
        p_rainbow = min(0.008 + (r * 0.004), 0.05)
        p_legendario = min(0.04 + (r * 0.015), 0.15)
        p_epico = min(0.10 + (r * 0.02), 0.25)
        p_raro = min(0.20 + (r * 0.025), 0.35)
        p_comun = 1.0 - (p_rainbow + p_legendario + p_epico + p_raro)
        return {"Común": p_comun*100, "Raro": p_raro*100, "Épico": p_epico*100, "Legendario": p_legendario*100, "Rainbow": p_rainbow*100}

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
        if not self.has_dual_roulette:
            available.append({"id": "dual_roulette", **{k: VOUCHER_DEFS["dual_roulette"][k] for k in ("name", "price", "desc")}})
        if self.extra_spins_per_round < 3:
            available.append({"id": "extra_spin", **{k: VOUCHER_DEFS["extra_spin"][k] for k in ("name", "price", "desc")}})
        return available

    def generate_shop_offers(self):
        self.shop_offers = []
        is_inflated = self.current_boss["id"] == "inflation"
        slots = 4 if self.has_shop_upgrade else 3
        
        available_relics = [rk for rk in self.RELICS_POOL.keys() if not any(r["id"] == rk for r in self.relics)]
        
        for s in range(slots):
            rarity = self.get_progressive_rarity()
            
            _try_relic = False
            if rarity in ["Legendario", "Rainbow"]:
                _try_relic = random.random() < 0.5
            elif rarity == "Épico":
                _try_relic = random.random() < 0.35
            
            if _try_relic and available_relics:
                rk = random.choice(available_relics)
                r_info = self.RELICS_POOL[rk]
                price = r_info["price"] + (self.round * 2)
                if is_inflated: price = int(price * 1.30)
                self.shop_offers.append({
                    "id": rk, "name": r_info["name"], "desc": r_info["desc"], 
                    "price": price, "is_relic": True, "is_box": False, "rarity": rarity
                })
                available_relics.remove(rk)
            elif random.random() < 0.18:
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
        if self.cash < self.reroll_cost:
            self.log_text = "[ERR] CASH INSUFICIENTE PARA REROLL."
            self.log_color = (248, 113, 113)
            return
        self.cash -= self.reroll_cost
        self.reroll_cost = min(99, self.reroll_cost * 2)
        self.buttons[self.btn_reroll_idx].text = f"Reroll: {self.reroll_cost} $"
        self.generate_shop_offers()

    def check_funds_and_spins_integrity(self):
        has_tarjeta = any(r["id"] == "tarjeta_clonada" for r in self.relics)
        floor_limit = -15.0 if has_tarjeta else 0.0

        if self.money < floor_limit:
            self.trigger_game_over(f"BANCARROTA CRITICA: Saldo CR inferior a {floor_limit}.")
            return True
        if self.spins_left <= 0 and self.money < self.target_money:
            self.trigger_game_over(f"DERROTA: Sin giros para alcanzar {format_num(self.target_money)}.")
            return True
        return False

    def trigger_game_over(self, reason_text):
        self.game_over = True
        self.velocity = 0; self.velocity_dual = 0; self.is_spinning = False
        self.log_text = reason_text
        self.log_color = (248, 113, 113)
        SOUND_FAIL.play()

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
                cash_interest = max(1, int(excess * 0.20))
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
            SOUND_WIN.play()
            return

        self.round += 1
        self.target_money = float(self.round * 16 + random.randint(3, 8))
        self.current_boss = random.choice(BOSS_BLINDS) if self.round > 1 else NO_BOSS
        self.max_spins = 5 + self.extra_spins_per_round
        self.spins_left = self.max_spins - 1 if self.current_boss["id"] == "minus_spin" else self.max_spins
        self.reroll_cost = 1
        self.buttons[self.btn_reroll_idx].text = f"Reroll: {self.reroll_cost} $"
        self.last_winners = []
        self.generate_shop_offers()
        self.generate_voucher_offer()
        self.log_text = f"RONDA {self.round} INICIADA. MODIFICADORES RECALCULADOS."
        self.log_color = (52, 211, 153)

    def trigger_victory(self):
        self.game_won = True
        self.is_spinning = False
        self.velocity = 0
        self.velocity_dual = 0
        self.log_text = "VICTORIA TOTAL: Has dominado la Ruleta Zombi."
        self.log_color = (52, 211, 153)
        SOUND_WIN.play()

    def start_spin(self):
        if self.game_over or self.spins_left <= 0 or self.is_spinning or self.overlay_open: return
        self.is_spinning = True; self.roulette_1_active = True
        self.roulette_items_top = [random.choice(self.deck).copy() for _ in range(65)]
        self.position = 0.0; self.velocity = random.uniform(75.0, 95.0)
        self.last_card_trigger = -1
        
        for card in self.roulette_items_top:
            if random.random() < 0.22:
                cash_val = random.randint(1, 2 + self.round // 3)
                card["cash_bonus"] = cash_val
        
        if self.has_dual_roulette:
            self.roulette_2_active = True
            self.roulette_items_dual = [random.choice(self.deck).copy() for _ in range(65)]
            self.position_dual = 0.0; self.velocity_dual = random.uniform(70.0, 90.0)
            self.last_card_trigger_dual = -1
            
            for card in self.roulette_items_dual:
                if random.random() < 0.22:
                    cash_val = random.randint(1, 2 + self.round // 3)
                    card["cash_bonus"] = cash_val
        else: self.roulette_2_active = False

    def update_physics(self, dt):
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

        if self.roulette_1_active:
            if self.velocity > self.min_velocity:
                self.position += self.velocity * dt
                self.velocity *= math.pow(current_friction, dt)
                idx = int((self.position + (self.card_step / 2)) // self.card_step)
                if idx != self.last_card_trigger:
                    play_dynamic_click(self.velocity, self.has_dual_roulette)
                    self.last_card_trigger = idx
            else:
                self.velocity = 0
                self.roulette_1_active = False

        if self.roulette_2_active and self.has_dual_roulette:
            if self.velocity_dual > self.min_velocity:
                self.position_dual += self.velocity_dual * dt
                self.velocity_dual *= math.pow(current_friction, dt)
                idx = int((self.position_dual + (self.card_step / 2)) // self.card_step)
                if idx != self.last_card_trigger_dual:
                    play_dynamic_click(self.velocity_dual, True)
                    self.last_card_trigger_dual = idx
            else:
                self.velocity_dual = 0
                self.roulette_2_active = False

        if not self.roulette_1_active and not (self.roulette_2_active and self.has_dual_roulette):
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
        elif m_type == "pow": self.money = min(self.money ** val, 1e12) if self.money > 1 else self.money + 3
        elif m_type == "zero": self.money = 0.0
        cash_bonus = item.get("cash_bonus", 0)
        if cash_bonus:
            self.cash += cash_bonus

    def determine_winners_execution(self):
        SOUND_WIN.play()
        self.last_winners = []
        
        w1_idx = max(0, min(int((self.position + (self.card_step / 2)) // self.card_step), len(self.roulette_items_top) - 1))
        winner1 = self.roulette_items_top[w1_idx]
        old_money = self.money
        old_cash = self.cash
        self.resolve_item_effect(winner1)
        self.last_winners.append(w1_idx)
        
        has_segunda = any(r["id"] == "segunda_oportunidad" for r in self.relics)
        if has_segunda and self.is_negative(winner1) and random.random() < 0.10:
            self.money = old_money
            self.cash = old_cash
            if self.has_dual_roulette:
                old_dual = self.money
                old_cash_dual = self.cash
                w2_temp = max(0, min(int((self.position_dual + (self.card_step / 2)) // self.card_step), len(self.roulette_items_dual) - 1))
                self.resolve_item_effect(self.roulette_items_dual[w2_temp])
                self.money = old_dual
                self.cash = old_cash_dual
            self.log_text = "¡SEGUNDA OPORTUNIDAD! Casilla negativa evadida. Gira de nuevo."
            self.log_color = (52, 211, 153)
            y_emit = self.canvas_y + 50 if self.has_dual_roulette else self.canvas_y + self.canvas_height // 2
            self.create_impact_particles(self.canvas_x + self.canvas_width // 2, y_emit, (52, 211, 153), count=50)
            return
        
        c1 = (248, 113, 113) if self.is_negative(winner1) else RARITIES.get(winner1["rarity"], {"color": (52, 211, 153)})["color"]
        y_emit_1 = self.canvas_y + 50 if self.has_dual_roulette else self.canvas_y + self.canvas_height // 2
        self.create_impact_particles(self.canvas_x + self.canvas_width // 2, y_emit_1, c1, count=40)
        
        log_build = f"[R1]: {winner1['name']}"
        if self.has_dual_roulette:
            w2_idx = max(0, min(int((self.position_dual + (self.card_step / 2)) // self.card_step), len(self.roulette_items_dual) - 1))
            winner2 = self.roulette_items_dual[w2_idx]
            old2 = self.money
            old_cash2 = self.cash
            self.resolve_item_effect(winner2)
            if has_segunda and self.is_negative(winner2) and random.random() < 0.10:
                self.money = old_money
                self.cash = old_cash
                self.log_text = "¡SEGUNDA OPORTUNIDAD! Casilla negativa evadida. Gira de nuevo."
                self.log_color = (52, 211, 153)
                self.create_impact_particles(self.canvas_x + self.canvas_width // 2, self.canvas_y + self.canvas_height - 50, (52, 211, 153), count=50)
                return
            self.last_winners.append(w2_idx)
            c2 = (248, 113, 113) if self.is_negative(winner2) else RARITIES.get(winner2["rarity"], {"color": (34, 211, 238)})["color"]
            self.create_impact_particles(self.canvas_x + self.canvas_width // 2, self.canvas_y + self.canvas_height - 50, c2, count=40)
            log_build += f" | [R2]: {winner2['name']}"
            
        delta_cr = self.money - old_money
        delta_cash = self.cash - old_cash
        log_parts = [log_build]
        if delta_cr != 0:
            sign = "+" if delta_cr >= 0 else ""
            log_parts.append(f"CR: {sign}{delta_cr:.1f}")
        if delta_cash != 0:
            sign = "+" if delta_cash >= 0 else ""
            log_parts.append(f"$: {sign}{delta_cash:.0f}")
        self.log_text = " >> ".join(log_parts)
        self.log_color = (52, 211, 153) if (delta_cr >= 0 and delta_cash >= 0) else (248, 113, 113)
        self.shake_intensity = 8
        self.shake_timer = 10
        
        has_mejora = any(r["id"] == "mejora_progresiva" for r in self.relics)
        upgrade_data = []
        for ii, w_item in enumerate([(w1_idx, winner1)] + ([(w2_idx, winner2)] if self.has_dual_roulette else [])):
            w_idx, w_item_data = w_item
            if has_mejora and w_item_data["type"] == "add" and w_item_data["rarity"] in ("Común", "Raro") and w_item_data["name"] in self.UPGRADE_MAP:
                upgraded = self.UPGRADE_MAP[w_item_data["name"]]
                for i, d_item in enumerate(self.deck):
                    if d_item["name"] == w_item_data["name"]:
                        self.deck[i] = upgraded.copy()
                        break
                upgrade_color = RARITIES.get(upgraded["rarity"], {"color": (52, 211, 153)})["color"]
                self.shake_intensity = 12
                self.shake_timer = 15
                self.create_impact_particles(self.canvas_x + self.canvas_width // 2, self.canvas_y + self.canvas_height // 2, upgrade_color, count=60)
                self.create_impact_particles(self.canvas_x + self.canvas_width // 2, self.canvas_y + self.canvas_height // 2, (255, 255, 200), count=30)
                # Replace the card in the roulette track immediately so it shows the new value
                if ii == 0:
                    self.roulette_items_top[w_idx] = upgraded.copy()
                elif ii == 1 and self.has_dual_roulette:
                    self.roulette_items_dual[w_idx] = upgraded.copy()
                upgrade_data.append({"idx": w_idx, "old_name": w_item_data["name"], "new_name": upgraded["name"], "new_item": upgraded.copy()})
        if upgrade_data:
            self.upgrade_anim = {"data": upgrade_data, "timer": 2.5}
        
        self.spins_left -= 1
        self.check_funds_and_spins_integrity()

    def buy_item(self, idx):
        if self.game_over or self.overlay_open or self.is_spinning: return
        item = self.shop_offers[idx]
        if item is None: return
        if item.get("is_box") or item.get("is_relic") or not self.is_negative(item):
            if self.cash < item["price"]:
                self.log_text = "[ERR] CASH INSUFICIENTE."
                self.log_color = (248, 113, 113)
                return
            self.cash -= item["price"]
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
                self.log_text = f"[SISTEMA] PASIVO ADQUIRIDO: {item['name']}"
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

    def buy_voucher(self):
        if self.game_over or not self.current_voucher or self.overlay_open or self.is_spinning: return
        if self.cash < self.current_voucher["price"]:
            return
        
        self.cash -= self.current_voucher["price"]
        v_id = self.current_voucher["id"]
        
        if v_id == "pack_up": self.has_pack_upgrade = True
        elif v_id == "shop_up": self.has_shop_upgrade = True; self.generate_shop_offers()
        elif v_id == "dual_roulette": self.has_dual_roulette = True
        elif v_id == "extra_spin": self.extra_spins_per_round += 1; self.max_spins += 1; self.spins_left += 1
            
        self.current_voucher = None
        self.rebuild_shop_buttons()
        self.check_funds_and_spins_integrity()

    def open_booster_pack(self):
        self.overlay_open = True
        self.booster_anim_progress = 0.0
        self.selected_booster_idx = None 
        self.booster_options = []
        cards_count = 4 if self.has_pack_upgrade else 3
        
        active_relic_ids = [r["id"] for r in self.relics]
        available_relics = [rk for rk in self.RELICS_POOL.keys() if rk not in active_relic_ids]
        available_vouchers = self.get_available_vouchers()
        
        while len(self.booster_options) < cards_count:
            roll = random.random()
            if roll < 0.001 and (available_relics or available_vouchers):
                choice = random.choice(["relic", "voucher"] if (available_relics and available_vouchers) else (["relic"] if available_relics else ["voucher"]))
                if choice == "relic":
                    rk = random.choice(available_relics)
                    r_info = self.RELICS_POOL[rk]
                    picked = {"id": rk, "name": r_info["name"], "desc": r_info["desc"], "is_relic": True, "rarity": "Rainbow", "type": "ultra"}
                    available_relics.remove(rk)
                else:
                    v = random.choice(available_vouchers)
                    picked = {"id": v["id"], "name": v["name"], "desc": v["desc"], "is_voucher": True, "rarity": "Rainbow", "type": "ultra"}
                    available_vouchers.remove(v)
            else:
                if roll < 0.004: rarity = "Rainbow"
                elif roll < 0.015: rarity = "Legendario"
                elif roll < 0.15: rarity = "Épico"
                elif roll < 0.45: rarity = "Raro"
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
            if v_id == "pack_up": self.has_pack_upgrade = True
            elif v_id == "shop_up": self.has_shop_upgrade = True; self.generate_shop_offers()
            elif v_id == "dual_roulette": self.has_dual_roulette = True
            elif v_id == "extra_spin": self.extra_spins_per_round += 1; self.max_spins += 1; self.spins_left += 1
        else:
            self.deck.append(item)
            
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
                base_val = self.RELICS_POOL[relic["id"]]["price"]
                refund = max(1, base_val // 2)
                self.cash += refund
                self.relics.pop(i)
                self.rebuild_shop_buttons()
                self.check_funds_and_spins_integrity()
                break

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
            font_size = scale(14 if not self.has_dual_roulette else 13)
            draw_text(surface, text_str, get_font(font_size, True), text_color, card_rect.centerx, card_rect.centery)
            cb = item.get("cash_bonus", 0)
            if cb and not is_blinded:
                draw_text(surface, f"+{cb}$", get_font(scale(9), True), (74, 222, 128), card_rect.centerx, card_rect.bottom - scale(8))
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
        font_size = scale(14 if not self.has_dual_roulette else 13)
        draw_text(surface, text_str, get_font(font_size, True), text_color, card_rect.centerx, card_rect.centery)
        cash_bonus = item.get("cash_bonus", 0)
        if cash_bonus and not is_blinded:
            bonus_label = f"+{cash_bonus}$"
            draw_text(surface, bonus_label, get_font(scale(9), True), (74, 222, 128), card_rect.centerx, card_rect.bottom - scale(8))

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

            tw = max(font_title.size(name)[0], font_desc.size(desc)[0]) + 24
            th = 58
            tx = m_pos[0] + 15
            ty = m_pos[1] - 15

            if tx + tw > SCREEN_WIDTH:
                tx = m_pos[0] - tw - 10
            if ty + th > SCREEN_HEIGHT:
                ty = SCREEN_HEIGHT - th - 10

            tt_rect = pygame.Rect(tx, ty, tw, th)
            draw_panel(surface, tt_rect, (12, 15, 26), BORDER_BLUE, 8)

            draw_text(surface, name, font_title, COLOR_GOLD, tx + 12, ty + 14, "left")
            draw_text(surface, desc, font_desc, (226, 232, 240), tx + 12, ty + 36, "left")
        self.tooltip_queue.clear()

    def draw(self, surface):
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

        if self.current_boss["id"] != "none":
            draw_text(surface, f"[!] {self.current_boss['name']}", get_font(scale(12), True), (244, 63, 94), col5, mid_y - 6, "left")
            boss_rect = pygame.Rect(col5 - 5, self.header_y + 8, SCREEN_WIDTH - col5 - self.margin, self.header_h - 16)
            if boss_rect.collidepoint(mouse_pos):
                self.queue_tooltip(self.current_boss["name"], self.current_boss["desc"], mouse_pos)

        canvas_rect = pygame.Rect(current_canvas_x, current_canvas_y, self.canvas_width, self.canvas_height)
        draw_panel(surface, canvas_rect, BG_CANVAS, BORDER_BLUE, 16)

        surface.set_clip(canvas_rect)
        w1 = self.last_winners[0] if len(self.last_winners) > 0 else -1
        w2 = self.last_winners[1] if len(self.last_winners) > 1 else -1
        if not self.has_dual_roulette:
            y_top = current_canvas_y + (self.canvas_height - self.card_height) // 2
            self._draw_roulette_track(surface, self.roulette_items_top, y_top, self.position, w1)
        else:
            y_top_1 = current_canvas_y + 10
            y_top_2 = current_canvas_y + self.canvas_height - self.card_height - 10
            self._draw_roulette_track(surface, self.roulette_items_top, y_top_1, self.position, w1)
            self._draw_roulette_track(surface, self.roulette_items_dual, y_top_2, self.position_dual, w2)

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

        probs = self.calculate_probabilities()
        sorted_probs = sorted(probs.items(), key=lambda x: x[1], reverse=True)[:6]
        for i, (name, prob) in enumerate(sorted_probs):
            line_y = dash_y + 40 + i * scale(14)
            if line_y < dash_y + self.dash_h - 8:
                draw_text(surface, f"{name}: {prob:.0f}%", get_font(scale(12)), COLOR_TEXT_MUTED, deck_rect.x + 14, line_y, "left")

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
        draw_text(surface, f"PASIVOS  {len(self.relics)}/{self.relic_slots}", get_font(scale(13), True), COLOR_CYAN, self.margin, shelf_y - 18, "left")

        for idx in range(self.relic_slots):
            rx = self.relic_start_x + idx * (self.relic_box_w + self.relic_gap)
            slot_rect = pygame.Rect(rx, shelf_y, self.relic_box_w, self.shelf_h)
            if idx < len(self.relics):
                relic_data = self.relics[idx]
                r_style = RARITIES.get(relic_data["rarity"], {"bg": (30, 30, 45), "color": (255, 255, 255)})
                if slot_rect.collidepoint(mouse_pos):
                    draw_panel(surface, slot_rect, (80, 20, 20), (239, 68, 68), 10, 2)
                    draw_text(surface, "PURGAR PASIVO", get_font(scale(14), True), (255, 100, 100), slot_rect.centerx, shelf_y + 28)
                    draw_text(surface, f"+{max(1, self.RELICS_POOL[relic_data['id']]['price'] // 2)} $", get_font(scale(13), True), (255, 255, 255), slot_rect.centerx, shelf_y + 52)
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
                draw_text(surface, "Pasivo / Reliquia", get_font(scale(12)), (234, 140, 8), box_rect.centerx, text_y + scale(26))
                if box_rect.collidepoint(mouse_pos):
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
            if hovered:
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

    def handle_global_events(self):
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.r_hold_start = time.time()
                    self.r_holding = True
                elif event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    self.start_spin()
                elif event.key == pygame.K_n:
                    if self.game_won and self.has_won:
                        self.game_won = False
                    self.advance_round_clean()
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_r:
                    self.r_holding = False
                    self.reset_hold_time = 0

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
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