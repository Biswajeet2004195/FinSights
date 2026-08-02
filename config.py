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
    'ENTRY_BG', 'ENTRY_BDR', 'CARD_BG', 'CARD_BDR', 'CHART_BG', 'CHART_FG', 'CHART_GRID', 'CHART_LINE',
    'HOV', 'SEL',
    'SIDE_W', 'HEAD_H', 'WIN_W', 'WIN_H',
    'EXPENSE_CATS', 'INCOME_CATS', 'INV_TYPES', 'CAT_CLR',
    'fmt_inr', 'fmt_amt', 'fmt_disp', 'GLOBAL_STATE', 'SUPPORTED_CURRENCIES', 'convert_currency', 'get_currency_symbol',
    'mk_id', 'today', 'curr_m', 'now_ts',
    'get_all_budgets', 'get_budgets_for_month', 'save_budget_for_month', 'delete_budget_for_month',
    '_ld_users', '_sv_users', 'fade_color',
    'ctk', 'CR_CARD', 'CR_BTN', 'CR_ENT',
    'hash_password', 'verify_password',
    'BASE_DIR', 'DATA_DIR', '_DATA_CACHE', 'default_date',
    'get_user_key', 'get_user_dir', 'set_current_user', 'init_user_data',
    'THEMES', 'apply_theme', 'get_system_theme', 'insight_colors'
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

_DATA_CACHE = {}

GLOBAL_STATE = {
    "display_currency": "INR",
    "selected_month": datetime.now().strftime("%Y-%m"),
    "current_user": "",
    "theme": "dark"
}

THEMES = {
    "dark": {
        "BG": "#071510",
        "SB": "#0a1c15",
        "CB": "#0f261f",
        "CB2": "#15342a",
        "BD": "#1c4437",
        "AC": "#10b981",
        "CY": "#00e676",
        "GO": "#ff9f0a",
        "GR": "#10b981",
        "RE": "#ff453a",
        "OR": "#ff9f0a",
        "PK": "#ec4899",
        "BL": "#0ea5e9",
        "PR": "#a855f7",
        "TP": "#ffffff",
        "TS": "#8ca39b",
        "TH": "#5a6f66",
        "EN": "#050e0a",
        "ENTRY_BG": "#050e0a",
        "ENTRY_BDR": "#1c4437",
        "CARD_BG": "#0f261f",
        "CARD_BDR": "#1c4437",
        "CHART_BG": "#0f261f",
        "CHART_FG": "#ffffff",
        "CHART_GRID": "#1c4437",
        "CHART_LINE": "#10b981",
        "HOV": "#15342a",
        "SEL": "#1c4437",
    },
    "light": {
        "BG": "#F8FAFC",
        "SB": "#FFFFFF",
        "CB": "#FFFFFF",
        "CB2": "#DBEAFE",
        "BD": "#CBD5E1",
        "AC": "#2563EB",
        "CY": "#2563EB",
        "GO": "#F59E0B",
        "GR": "#16A34A",
        "RE": "#DC2626",
        "OR": "#F59E0B",
        "PK": "#DB2777",
        "BL": "#2563EB",
        "PR": "#7C3AED",
        "TP": "#0F172A",
        "TS": "#475569",
        "TH": "#64748B",
        "EN": "#FFFFFF",
        "ENTRY_BG": "#FFFFFF",
        "ENTRY_BDR": "#CBD5E1",
        "CARD_BG": "#FFFFFF",
        "CARD_BDR": "#CBD5E1",
        "CHART_BG": "#FFFFFF",
        "CHART_FG": "#0F172A",
        "CHART_GRID": "#E2E8F0",
        "CHART_LINE": "#16A34A",
        "HOV": "#DBEAFE",
        "SEL": "#BFDBFE",
    }
}


def get_system_theme():
    """Detect the OS-level dark/light preference. Returns 'dark' or 'light'."""
    try:
        import darkdetect
        mode = darkdetect.theme()
        return "light" if mode == "Light" else "dark"
    except Exception:
        pass
    # Windows Registry fallback
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
        )
        val, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
        winreg.CloseKey(key)
        return "light" if val == 1 else "dark"
    except Exception:
        pass
    return "dark"  # safe fallback


def insight_colors(priority):
    """Return (bg, border) for an insight card based on current theme."""
    is_dark = GLOBAL_STATE.get("theme", "dark") == "dark"
    mapping = {
        "Positive":  ("#1c2c1c" if is_dark else "#F0FFF4", GR),
        "Warning":   ("#2c2a1c" if is_dark else "#FFFBEB", GO),
        "Critical":  ("#2c1c1c" if is_dark else "#FFF1F2", RE),
        "Normal":    ("#1c222c" if is_dark else "#EFF6FF", AC),
    }
    return mapping.get(priority, (CB2, BD))

# Initial Default Tokens (Dark)
BG = THEMES["dark"]["BG"]
SB = THEMES["dark"]["SB"]
CB = THEMES["dark"]["CB"]
CB2 = THEMES["dark"]["CB2"]
BD = THEMES["dark"]["BD"]
AC = THEMES["dark"]["AC"]
CY = THEMES["dark"]["CY"]
GO = THEMES["dark"]["GO"]
GR = THEMES["dark"]["GR"]
RE = THEMES["dark"]["RE"]
OR = THEMES["dark"]["OR"]
PK = THEMES["dark"]["PK"]
BL = THEMES["dark"]["BL"]
PR = THEMES["dark"]["PR"]
TP = THEMES["dark"]["TP"]
TS = THEMES["dark"]["TS"]
TH = THEMES["dark"]["TH"]
EN = THEMES["dark"]["EN"]
ENTRY_BG = THEMES["dark"]["ENTRY_BG"]
ENTRY_BDR = THEMES["dark"]["ENTRY_BDR"]
CARD_BG = THEMES["dark"]["CARD_BG"]
CARD_BDR = THEMES["dark"]["CARD_BDR"]
CHART_BG = THEMES["dark"]["CHART_BG"]
CHART_FG = THEMES["dark"]["CHART_FG"]
CHART_GRID = THEMES["dark"]["CHART_GRID"]
CHART_LINE = THEMES["dark"]["CHART_LINE"]
HOV = THEMES["dark"]["HOV"]
SEL = THEMES["dark"]["SEL"]

def apply_theme(theme_name="Dark"):
    """Apply a named theme ('Dark', 'Light', 'System') and update all global tokens."""
    theme_key = str(theme_name).strip().lower()
    if theme_key == "system":
        theme_key = get_system_theme()
    if theme_key not in THEMES:
        theme_key = "dark"

    theme_data = THEMES[theme_key]
    GLOBAL_STATE["theme"] = theme_key

    gl = globals()
    for key, val in theme_data.items():
        gl[key] = val

    # Propagate style tokens dynamically to all modules that imported config variables
    import sys
    for mod_name, module in list(sys.modules.items()):
        if module and mod_name not in ('sys', 'os', 'json', 'datetime', 'config'):
            m_dict = getattr(module, '__dict__', None)
            if m_dict:
                if 'BG' in m_dict and m_dict.get('BASE_DIR') == BASE_DIR:
                    for k, v in theme_data.items():
                        if k in m_dict:
                            m_dict[k] = v

    ctk.set_appearance_mode("light" if theme_key == "light" else "dark")

    try:
        from tkinter import ttk
        s = ttk.Style()
        s.theme_use("clam")
        s.configure("A.TCombobox",
                    fieldbackground=theme_data["EN"],
                    background=theme_data["EN"],
                    foreground=theme_data["TP"],
                    arrowcolor=theme_data["AC"])
        s.map("A.TCombobox",
              fieldbackground=[("readonly", theme_data["EN"])],
              foreground=[("readonly", theme_data["TP"])])
        # Treeview (D.Treeview) full restyle
        s.configure("D.Treeview",
                    background=theme_data["CB"],
                    foreground=theme_data["TP"],
                    fieldbackground=theme_data["CB"],
                    rowheight=34,
                    font=("Segoe UI", 10))
        s.configure("D.Treeview.Heading",
                    background=theme_data["CB2"],
                    foreground=theme_data["AC"],
                    font=("Segoe UI", 10, "bold"),
                    relief="flat")
        s.map("D.Treeview",
              background=[("selected", theme_data["AC"])],
              foreground=[("selected", theme_data["TP"])])
        s.configure("Vertical.TScrollbar",
                    background=theme_data["BD"],
                    troughcolor=theme_data["CB"],
                    borderwidth=0,
                    arrowcolor=theme_data["TS"],
                    width=8)
    except Exception:
        pass

def get_user_key(email=None):
    if not email:
        email = GLOBAL_STATE.get("current_user", "")
    if not email:
        return "default"
    import re
    return re.sub(r'[^a-zA-Z0-9_-]', '_', email.strip().lower())

def get_user_dir(email=None):
    key = get_user_key(email)
    user_dir = os.path.join(DATA_DIR, "users", key)
    os.makedirs(user_dir, exist_ok=True)
    return user_dir

def init_user_data(email):
    """Initialize empty data files for a brand-new user.
    Safe to call even if the directory already has files — only missing files are created.
    Never touches any other user's data.
    """
    import re as _re
    key = _re.sub(r'[^a-zA-Z0-9_-]', '_', email.strip().lower())
    user_dir = os.path.join(DATA_DIR, "users", key)
    os.makedirs(user_dir, exist_ok=True)
    data_files = ["transactions", "budgets", "investments", "goals",
                  "notifications", "net_worth", "recurring", "settings"]
    for fname in data_files:
        path = os.path.join(user_dir, f"{fname}.json")
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as fp:
                json.dump({} if fname == "settings" else [], fp)

def set_current_user(email):
    email_clean = email.strip().lower() if email else ""
    GLOBAL_STATE["current_user"] = email_clean
    _DATA_CACHE.clear()

    # Ensure directory exists and seed any missing data files with empty defaults.
    # Legacy root-level files (data/*.json) are deliberately NOT copied here —
    # every user starts with their own clean, empty data.
    get_user_dir(email_clean)  # creates directory if needed
    _seed()
    _migrate_transactions()

    # Apply the user's saved theme
    settings = _ldd("settings")
    user_theme = settings.get("theme", "Dark")
    apply_theme(user_theme)

def _p(n):
    return os.path.join(get_user_dir(), f"{n}.json")

def _ld(n):
    if n in _DATA_CACHE:
        return _DATA_CACHE[n]
    if os.path.exists(_p(n)):
        try:
            with open(_p(n), "r", encoding="utf-8") as f:
                data = json.load(f)
                _DATA_CACHE[n] = data
                return data
        except Exception:
            pass
    return []

def _ldd(n):
    if n in _DATA_CACHE:
        return _DATA_CACHE[n]
    if os.path.exists(_p(n)):
        try:
            with open(_p(n), "r", encoding="utf-8") as f:
                data = json.load(f)
                _DATA_CACHE[n] = data
                return data
        except Exception:
            pass
    return {}

def _sv(n, d):
    _DATA_CACHE[n] = d
    with open(_p(n), "w", encoding="utf-8") as f:
        json.dump(d, f, indent=2)

# ── Colour Tokens — always reflect current theme (set by apply_theme) ─────────
# Do not hard-reset these here; they are managed by apply_theme()

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

from currency_utils import format_amount, convert_currency, SUPPORTED_CURRENCIES, get_currency_symbol

from datetime import datetime


def fmt_amt(n, from_curr="INR"):
    converted = convert_currency(n, from_curr, GLOBAL_STATE["display_currency"])
    return format_amount(converted, GLOBAL_STATE["display_currency"])

def fmt_disp(n):
    # For amounts already converted to display_currency
    return format_amount(n, GLOBAL_STATE["display_currency"])

def fmt_inr(n):
    # Alias for backward compatibility if I miss some replacements
    return fmt_amt(n, "INR")

def mk_id():
    import time, random
    return f"{int(time.time()*1000)}{random.randint(100, 999)}"

def today():   return datetime.now().strftime("%Y-%m-%d")
def curr_m():  return GLOBAL_STATE.get("selected_month", datetime.now().strftime("%Y-%m"))
def default_date():
    sys_m = datetime.now().strftime("%Y-%m")
    sel_m = GLOBAL_STATE.get("selected_month", sys_m)
    return today() if sel_m == sys_m else f"{sel_m}-01"

def now_ts():  return datetime.now().strftime("%Y-%m-%d %H:%M")

def get_all_budgets():
    if not os.path.exists(_p("budgets")):
        return []
    with open(_p("budgets"), "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except Exception:
            return []
            
    if isinstance(data, dict):
        new_data = []
        cm = curr_m()
        for cat, val in data.items():
            amt = val["amount"] if isinstance(val, dict) else float(val)
            curr = val["currency"] if isinstance(val, dict) else "INR"
            new_data.append({
                "month": cm,
                "category": cat,
                "amount": amt,
                "currency": curr
            })
        _sv("budgets", new_data)
        return new_data
    return data if isinstance(data, list) else []

def get_budgets_for_month(month):
    all_b = get_all_budgets()
    res = {}
    for b in all_b:
        if b.get("month") == month:
            res[b["category"]] = {"amount": float(b.get("amount", 0)), "currency": b.get("currency", "INR")}
    return res

def save_budget_for_month(month, category, amount, currency="INR"):
    all_b = get_all_budgets()
    found = False
    for b in all_b:
        if b.get("month") == month and b.get("category") == category:
            b["amount"] = float(amount)
            b["currency"] = currency
            found = True
            break
    if not found:
        all_b.append({
            "month": month,
            "category": category,
            "amount": float(amount),
            "currency": currency
        })
    _sv("budgets", all_b)

def delete_budget_for_month(month, category):
    all_b = get_all_budgets()
    all_b = [b for b in all_b if not (b.get("month") == month and b.get("category") == category)]
    _sv("budgets", all_b)

def _seed():
    """Create empty data stores on first run. No pre-loaded values."""
    files_to_seed = ["transactions", "budgets", "investments", "goals", "notifications", "net_worth", "recurring", "settings"]
    for f in files_to_seed:
        if not os.path.exists(_p(f)):
            if f == "settings":
                _sv(f, {})
            else:
                _sv(f, [])

def _migrate_transactions():
    """Add 'month' field to any transaction missing it."""
    try:
        trans = _ld("transactions")
        if trans:
            modified = False
            for r in trans:
                if "month" not in r:
                    r["month"] = r["date"][:7] if "date" in r else datetime.now().strftime("%Y-%m")
                    modified = True
            if modified:
                _sv("transactions", trans)
    except Exception:
        pass

_seed()
_migrate_transactions()

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

