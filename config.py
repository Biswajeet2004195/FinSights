import os
import json
from datetime import datetime
import customtkinter as ctk
import hashlib
import hmac

# Set global ctk appearance
ctk.set_appearance_mode("dark")
try:
    ctk.set_window_scaling(1.0)
    ctk.set_widget_scaling(1.0)
except Exception:
    pass

# Global Corner Radius Constants
CR_CARD = 15
CR_BTN = 8
CR_ENT = 8

__all__ = [
    '_p', '_ld', '_ldd', '_sv', '_seed',
    'BG', 'SB', 'CB', 'CB2', 'BD', 'AC', 'CY', 'GO', 'GR', 'RE', 'OR', 'PK', 'BL', 'PR', 'TP', 'TS', 'TH', 'EN',
    'SIDE_W', 'HEAD_H', 'WIN_W', 'WIN_H',
    'EXPENSE_CATS', 'INCOME_CATS', 'INV_TYPES', 'CAT_CLR',
    'fmt_inr', 'mk_id', 'today', 'curr_m', 'now_ts',
    '_ld_users', '_sv_users', 'fade_color',
    'ctk', 'CR_CARD', 'CR_BTN', 'CR_ENT',
    'hash_password', 'verify_password'
]

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

USER_FILE = r"D:/infosys/users.json"

def _ld_users():
    if os.path.exists(USER_FILE):
        try:
            with open(USER_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def _sv_users(u):
    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump(u, f, indent=4)

def _p(n):    return os.path.join(DATA_DIR, f"{n}.json")

def _ld(n):
    if os.path.exists(_p(n)):
        try:
            with open(_p(n), "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []

def _ldd(n):
    if os.path.exists(_p(n)):
        try:
            with open(_p(n), "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def _sv(n, d):
    with open(_p(n), "w", encoding="utf-8") as f:
        json.dump(d, f, indent=2)

# ── Colour Tokens ─────────────────────────────────────────────────────────────
BG  = "#071510";  SB  = "#0a1c15";  CB  = "#0f261f";  CB2 = "#15342a"
BD  = "#1c4437";  AC  = "#10b981";  CY  = "#00e676";  GO  = "#ff9f0a"
GR  = "#10b981";  RE  = "#ff453a";  OR  = "#ff9f0a";  PK  = "#ec4899"
BL  = "#0ea5e9";  PR  = "#a855f7"
TP  = "#ffffff";  TS  = "#8ca39b";  TH  = "#5a6f66";  EN  = "#050e0a"

SIDE_W = 220;  HEAD_H = 64;  WIN_W = 1280;  WIN_H = 760

EXPENSE_CATS = ["Food & Dining", "Rent/Housing", "Transport", "Entertainment",
                "Shopping", "Healthcare", "Utilities", "Education", "Others"]
INCOME_CATS  = ["Salary", "Freelance", "Business", "Investment Returns", "Rental", "Other"]
INV_TYPES    = ["Stocks", "Mutual Fund", "Crypto", "ETF", "Bond", "Gold", "FD", "Other"]

CAT_CLR = {
    "Food & Dining": RE,  "Rent/Housing": PR,  "Transport": CY,
    "Entertainment": GO,  "Shopping": PK,       "Healthcare": GR,
    "Utilities": OR,      "Education": BL,      "Others": TS,
    "Salary": GR,         "Freelance": CY,       "Business": GO,
    "Investment Returns": PR, "Rental": PK,      "Other": TS,
}

def fmt_inr(n):
    n = float(n); neg = n < 0; n = abs(n)
    return f"{'−' if neg else ''}₹{n:,.0f}"

def mk_id():
    import time, random
    return f"{int(time.time()*1000)}{random.randint(100, 999)}"

def today():   return datetime.now().strftime("%Y-%m-%d")
def curr_m():  return datetime.now().strftime("%Y-%m")
def now_ts():  return datetime.now().strftime("%Y-%m-%d %H:%M")

def _seed():
    """Create empty data stores on first run. No pre-loaded values."""
    if not os.path.exists(_p("transactions")):
        _sv("transactions", [])
    if not os.path.exists(_p("budgets")):
        _sv("budgets", {})
    if not os.path.exists(_p("investments")):
        _sv("investments", [])
    if not os.path.exists(_p("goals")):
        _sv("goals", [])
    if not os.path.exists(_p("notifications")):
        _sv("notifications", [])

_seed()

# ── Color Fading Hover Animation Engine ──────────────────────────────────────
_active_fades = {}

def fade_color(widget_or_canvas, item_id, attribute, target_hex, steps=4, delay=8, is_canvas_item=False):
    def hex_to_rgb(hex_str):
        hex_str = hex_str.lstrip('#')
        if len(hex_str) == 3:
            hex_str = "".join(x*2 for x in hex_str)
        return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

    def rgb_to_hex(rgb):
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"

    fade_key = f"{id(widget_or_canvas)}_{item_id}_{attribute}"
    run_id = _active_fades.get(fade_key, 0) + 1
    _active_fades[fade_key] = run_id

    try:
        if is_canvas_item:
            current_hex = widget_or_canvas.itemcget(item_id, attribute)
        else:
            current_hex = widget_or_canvas.cget(attribute)
    except Exception:
        current_hex = "#ffffff"

    color_map = {
        "white": "#ffffff", "black": "#000000", "gray": "#808080",
        "red": "#ff0000", "green": "#00ff00", "blue": "#0000ff"
    }
    if not current_hex.startswith('#'):
        current_hex = color_map.get(current_hex.lower(), "#ffffff")
    if not target_hex.startswith('#'):
        target_hex = color_map.get(target_hex.lower(), "#ffffff")

    try:
        c_rgb = hex_to_rgb(current_hex)
        t_rgb = hex_to_rgb(target_hex)
    except Exception:
        try:
            if is_canvas_item:
                widget_or_canvas.itemconfig(item_id, **{attribute: target_hex})
            else:
                widget_or_canvas.configure(**{attribute: target_hex})
        except:
            pass
        return

    def step_fade(step, current_run_id):
        if _active_fades.get(fade_key) != current_run_id:
            return
        if step > steps:
            try:
                if is_canvas_item:
                    widget_or_canvas.itemconfig(item_id, **{attribute: target_hex})
                else:
                    widget_or_canvas.configure(**{attribute: target_hex})
            except Exception:
                pass
            return

        factor = step / steps
        r = int(c_rgb[0] + (t_rgb[0] - c_rgb[0]) * factor)
        g = int(c_rgb[1] + (t_rgb[1] - c_rgb[1]) * factor)
        b = int(c_rgb[2] + (t_rgb[2] - c_rgb[2]) * factor)
        next_hex = rgb_to_hex((r, g, b))

        try:
            if is_canvas_item:
                widget_or_canvas.itemconfig(item_id, **{attribute: next_hex})
            else:
                widget_or_canvas.configure(**{attribute: next_hex})
        except Exception:
            return

        try:
            widget_or_canvas.after(delay, lambda: step_fade(step + 1, current_run_id))
        except Exception:
            pass

    try:
        step_fade(1, run_id)
    except Exception:
        pass


def hash_password(password):
    try:
        import bcrypt
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    except Exception:
        salt = os.urandom(16)
        hashed = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        return f"pbkdf2:${salt.hex()}:${hashed.hex()}"

def verify_password(stored_password_hash, input_password):
    if not stored_password_hash.startswith('$2') and not stored_password_hash.startswith('pbkdf2:$'):
        return False
    if stored_password_hash.startswith('pbkdf2:$'):
        try:
            parts = stored_password_hash.split(':$')
            salt = bytes.fromhex(parts[1])
            expected = bytes.fromhex(parts[2])
            hashed = hashlib.pbkdf2_hmac('sha256', input_password.encode('utf-8'), salt, 100000)
            return hmac.compare_digest(expected, hashed)
        except Exception:
            return False
    try:
        import bcrypt
        return bcrypt.checkpw(input_password.encode('utf-8'), stored_password_hash.encode('utf-8'))
    except Exception:
        return False

