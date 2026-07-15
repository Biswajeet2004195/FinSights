import tkinter as tk
from tkinter import messagebox, ttk
import json, os, re, hashlib, hmac

# ── DPI Scaling (macOS crisp text quality) ────────────────────────────────────
try:
    import ctypes
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except:
        pass

from dashboard import launch_dashboard
from config import fade_color, _ld_users, _sv_users, hash_password, verify_password



# ── Paths ──────────────────────────────────────────────────────────────────────
DIR  = r"D:/infosys"
FILE = os.path.join(DIR, "users.json")
os.makedirs(DIR, exist_ok=True)
if not os.path.exists(FILE):
    json.dump({}, open(FILE, "w"))

def users():
    return _ld_users()

def save(u):
    _sv_users(u)

# ── Palette ────────────────────────────────────────────────────────────────────
BG_DARK   = "#071510"   # obsidian dark green
BG_LEFT   = "#0a1c15"   # dark forest green
CARD_BG   = "#0f261f"   # dark emerald card panel
CARD_BDR  = "#1c4437"   # Specular green border
ACCENT    = "#10b981"   # neon emerald green
ACCENT2   = "#00e676"   # neon bright green
GOLD      = "#ff9f0a"   # orange/gold
TXT_PRI   = "#ffffff"   # white
TXT_SEC   = "#8ca39b"   # pale sage
TXT_HINT  = "#5a6f66"   # muted sage
ENTRY_BG  = "#050e0a"   # deep input background
ENTRY_BDR = "#1c4437"   # green border
BTN_HVR   = "#059669"   # emerald hover
BTN2_BG   = "#15342a"   # secondary button
BTN2_HVR  = "#1c4437"   # secondary hover

# ── Window ─────────────────────────────────────────────────────────────────────
WIN_W, WIN_H = 1100, 680
try:
    import customtkinter as ctk
except ImportError:
    import subprocess, sys
    print("Installing missing dependency: customtkinter...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "customtkinter"])
    import customtkinter as ctk
root = ctk.CTk()
root.title("Finsights")
root.resizable(True, True)

s = ttk.Style()
s.theme_use("clam")
s.configure("A.TCombobox", fieldbackground=ENTRY_BG, background=ENTRY_BG, foreground=TXT_PRI, arrowcolor=ACCENT2)
s.map("A.TCombobox", fieldbackground=[("readonly", ENTRY_BG)])

# Center on screen
root.update_idletasks()
sw = root.winfo_screenwidth()
sh = root.winfo_screenheight()
x  = int((sw - WIN_W) / 2)
y  = int((sh - WIN_H) / 2)
root.geometry(f"{WIN_W}x{WIN_H}{x:+d}{y:+d}")
root.configure(fg_color=BG_DARK)

# Window transition helpers (optimized and fast)
def fade_out_window(window, callback, steps=6, delay=8):
    def step_fade(step):
        if step > steps:
            callback()
            return
        alpha = 1.0 - (step / steps)
        try:
            window.attributes("-alpha", alpha)
            window.after(delay, lambda: step_fade(step + 1))
        except Exception:
            pass
    step_fade(1)

def fade_in_window(window, steps=6, delay=8):
    window.attributes("-alpha", 0.0)
    def step_fade(step):
        if step > steps:
            window.attributes("-alpha", 1.0)
            return
        alpha = step / steps
        try:
            window.attributes("-alpha", alpha)
            window.after(delay, lambda: step_fade(step + 1))
        except Exception:
            pass
    step_fade(1)

def okmail(x):
    return re.fullmatch(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", x)

# LEFT & RIGHT CANVASES
left_canvas = tk.Canvas(root, bd=0, highlightthickness=0)
left_canvas.place(x=0, y=0)

right_canvas = tk.Canvas(root, bd=0, highlightthickness=0)

# Card Frame Dimensions
CARD_W, CARD_H = 420, 600

glow_f = ctk.CTkFrame(right_canvas, fg_color="#ffffff", corner_radius=15, bg_color="transparent")
glow_f.pack_propagate(False)
glow_f.grid_propagate(False)
card = ctk.CTkFrame(right_canvas, fg_color=CARD_BG, corner_radius=15, bg_color="transparent")
card.pack_propagate(False)
card.grid_propagate(False)
accent_bar = tk.Frame(right_canvas, bg=ACCENT, height=3)

# Initialize canvas windows
glow_win = right_canvas.create_window(0, 0, window=glow_f, state="hidden")
card_win = right_canvas.create_window(0, 0, window=card, state="hidden")
bar_win = right_canvas.create_window(0, 0, window=accent_bar, state="hidden")

# Redraw left canvas items dynamically based on size
def redraw_left_panel(w, h):
    left_canvas.delete("all")
    # Gradient background
    for i in range(h):
        t = i / h
        r = int(4 + t * 3)   # 4 -> 7
        g = int(17 + t * 16) # 17 -> 33
        b = int(11 + t * 11) # 11 -> 22
        left_canvas.create_line(0, i, w, i, fill=f"#{r:02x}{g:02x}{b:02x}")

    # Glowing decorative forest orbs
    left_canvas.create_oval(-80, -80, int(w * 0.6), int(w * 0.6), fill="#082218", outline="")
    left_canvas.create_oval(int(w * 0.3), h - int(w * 0.8), int(w * 1.1), h + int(w * 0.2), fill="#051911", outline="")
    left_canvas.create_oval(int(w * 0.6), int(h * 0.1), int(w * 1.1), int(h * 0.1) + int(w * 0.4), fill="#09281c", outline="")

    # Concentric "radar" grids for background overlays
    left_canvas.create_oval(-100, 100, int(w * 1.3), int(w * 1.3) + 200, outline="#0b2a1f", width=1)
    left_canvas.create_oval(20, 220, int(w * 0.9), int(w * 0.9) + 360, outline="#0b2a1f", width=1)

    # Thin vertical divider line on right edge of left panel
    left_canvas.create_line(w - 1, 0, w - 1, h, fill=CARD_BDR, width=1)

    # Horizontal and Vertical center coordinates
    cx = w // 2
    cy = h // 2

    # FINSIGHTS Logo (White and Amber, size 32 bold to prevent clipping)
    left_canvas.create_text(cx - 165, cy - 30, text="FIN", font=("Segoe UI", 32, "bold"), fill="#ffffff", anchor="w")
    left_canvas.create_text(cx - 78, cy - 30, text="SIGHTS", font=("Segoe UI", 32, "bold"), fill=GOLD, anchor="w")

    # Vertical gold indicator line
    left_canvas.create_line(cx - 165, cy + 25, cx - 165, cy + 65, fill=GOLD, width=3)

    # Subtitle (left-aligned next to indicator, aligned with logo boundary)
    left_canvas.create_text(
        cx - 153, cy + 45,
        text="Personal Finance & Investment Intelligence\nPlatform",
        font=("Segoe UI", 11), fill=TXT_SEC, anchor="w", justify="left"
    )

    # Badge Pills at the bottom
    left_canvas.create_rectangle(cx - 165, h - 180, cx - 65, h - 154, fill="#0b2920", outline="#1c4437", width=1)
    left_canvas.create_text(cx - 115, h - 167, text="📊 Budgeting", font=("Segoe UI", 8, "bold"), fill=ACCENT)

    left_canvas.create_rectangle(cx - 55, h - 180, cx + 55, h - 154, fill="#0b2920", outline="#1c4437", width=1)
    left_canvas.create_text(cx, h - 167, text="📈 Investments", font=("Segoe UI", 8, "bold"), fill=ACCENT)

    left_canvas.create_rectangle(cx + 65, h - 180, cx + 175, h - 154, fill="#0b2920", outline="#1c4437", width=1)
    left_canvas.create_text(cx + 120, h - 167, text="🎯 Goal Tracking", font=("Segoe UI", 8, "bold"), fill=ACCENT)

    left_canvas.create_text(
        cx, h - 24,
        text="© 2026 Finsights",
        font=("Segoe UI", 8), fill=TXT_HINT, anchor="center"
    )

# Resize callback to scale layouts dynamically
last_w, last_h = 0, 0
def on_resize(event):
    global last_w, last_h
    if event.widget != root:
        return
    w = event.width
    h = event.height
    if w == last_w and h == last_h:
        return
    last_w, last_h = w, h
    
    # Calculate panel widths
    left_w = int(w * 0.4)
    right_w = w - left_w
    
    # Place canvases
    left_canvas.place(x=0, y=0, width=left_w, height=h)
    right_canvas.place(x=left_w, y=0, width=right_w, height=h)
    
    # Redraw left canvas assets
    redraw_left_panel(left_w, h)
    
    # Redraw right canvas gradient background
    right_canvas.delete("gradient")
    for i in range(h):
        t = i / h
        r = int(5 + t * 4)   # 5 -> 9
        g = int(14 + t * 16) # 14 -> 30
        b = int(10 + t * 11) # 10 -> 21
        right_canvas.create_line(0, i, right_w, i, fill=f"#{r:02x}{g:02x}{b:02x}", tags="gradient")
    right_canvas.tag_lower("gradient")
    
    # Glow orb top-right on right canvas
    right_canvas.delete("orb")
    right_canvas.create_oval(right_w - 140, -100, right_w + 60, 100, fill="#09281c", outline="", tags="orb")
    
    # Constrain card dimensions dynamically to fit window size
    card_w = min(420, max(300, right_w - 40))
    card_h = min(600, max(400, h - 40))
    
    cx = right_w // 2
    cy = h // 2
    
    right_canvas.itemconfig(glow_win, state="normal", width=card_w + 4, height=card_h + 4)
    right_canvas.coords(glow_win, cx, cy)
    
    right_canvas.itemconfig(card_win, state="normal", width=card_w, height=card_h)
    right_canvas.coords(card_win, cx, cy)
    
    right_canvas.itemconfig(bar_win, state="normal", width=card_w, height=3)
    right_canvas.coords(bar_win, cx, cy - (card_h // 2))
    
    # Adjust padding of widgets inside card based on height
    adjust_card_spacing(h)
    
    # Update size of the current active parent page frame inside card
    if active_parent and active_parent.winfo_exists():
        active_parent.place(x=0, y=0, relwidth=1, relheight=1)

# Adjust padding recursively for widgets inside the card based on height
def adjust_card_spacing(h):
    is_small = h < 600
    pady_small_map = {
        (30, 2): (10, 2),  # Title
        (16, 4): (8, 2),   # Primary button
        (4, 4): (2, 2),    # Secondary button
        (8, 2): (4, 1),    # Labels
        (10, 2): (4, 2),   # Divider
        (4, 0): (2, 0),    # Checkbox row
        (6, 0): (2, 0),    # Link row
    }
    
    def recurse_adjust(widget):
        try:
            info = widget.pack_info()
            pady = info.get("pady")
            if pady is not None:
                if isinstance(pady, str) or isinstance(pady, int):
                    pady_tuple = (int(pady), int(pady))
                else:
                    pady_tuple = tuple(pady)
                    
                for orig, target in pady_small_map.items():
                    if pady_tuple == orig:
                        widget.pack_configure(pady=target if is_small else orig)
                        break
        except Exception:
            pass
        for child in widget.winfo_children():
            recurse_adjust(child)
            
    recurse_adjust(card)

# Bind configure event
root.bind("<Configure>", on_resize)

# ══════════════════════════════════════════════════════════════════════════════
# REUSABLE UI HELPERS  (all use grid inside a wrapper for perfect alignment)
# ══════════════════════════════════════════════════════════════════════════════
FORM_PAD = 36   # horizontal padding inside card
active_parent = None

def clear():
    pass  # handled dynamically by transition_to_form

def transition_to_form(build_func):
    global active_parent
    old_frame = active_parent if (active_parent is not None and active_parent != card) else None
    
    curr_w = card.winfo_width()
    curr_h = card.winfo_height()
    if curr_w <= 1:
        curr_w = 420
    if curr_h <= 1:
        curr_h = 600
        
    new_frame = ctk.CTkFrame(card, fg_color=CARD_BG, corner_radius=15)
    new_frame.pack_propagate(False)
    new_frame.grid_propagate(False)
    
    # Inject flexible spacers to perfectly vertically center the form inside the 600px tall card
    top_spacer = tk.Frame(new_frame, bg=CARD_BG)
    top_spacer.pack(expand=True, fill="both")
    
    active_parent = ctk.CTkFrame(new_frame, fg_color=CARD_BG)
    active_parent.pack(fill="x")
    
    bot_spacer = tk.Frame(new_frame, bg=CARD_BG)
    bot_spacer.pack(expand=True, fill="both")
    
    build_func()
    
    if not old_frame:
        new_frame.place(x=0, y=0, relwidth=1, relheight=1)
        return
        
    new_frame.place(x=curr_w, y=0, relwidth=1, relheight=1)
    
    steps = 6
    delay = 8
    
    def anim(step):
        if step > steps:
            new_frame.place(x=0, y=0, relwidth=1, relheight=1)
            if old_frame and old_frame.winfo_exists():
                old_frame.destroy()
            return
            
        t = step / steps
        ease = 1 - (1 - t) ** 3
        
        new_x = int(curr_w * (1 - ease))
        if new_frame.winfo_exists():
            new_frame.place(x=new_x, y=0, relwidth=1, relheight=1)
            
        if old_frame and old_frame.winfo_exists():
            old_frame.place(x=int(-curr_w * ease), y=0, relwidth=1, relheight=1)
            
        root.after(delay, lambda: anim(step + 1))
        
    anim(1)

def make_title(text, subtitle=""):
    tk.Label(
        active_parent, text=text,
        font=("Segoe UI", 21, "bold"),
        bg=CARD_BG, fg=TXT_PRI,
        anchor="w"
    ).pack(fill="x", padx=FORM_PAD, pady=(30, 2))

    if subtitle:
        tk.Label(
            active_parent, text=subtitle,
            font=("Segoe UI", 10),
            bg=CARD_BG, fg=TXT_HINT,
            anchor="w"
        ).pack(fill="x", padx=FORM_PAD, pady=(0, 4))

    # Accent underline
    tk.Frame(active_parent, bg=ACCENT, height=2).pack(fill="x", padx=FORM_PAD, pady=(4, 10))

def make_entry(label_text, show=""):
    """Returns the ctk.CTkEntry widget."""
    # Label
    tk.Label(
        active_parent, text=label_text,
        font=("Segoe UI", 9, "bold"),
        bg=CARD_BG, fg=TXT_SEC,
        anchor="w"
    ).pack(fill="x", padx=FORM_PAD, pady=(8, 2))

    entry = ctk.CTkEntry(
        active_parent,
        font=ctk.CTkFont("Segoe UI", 12),
        fg_color=ENTRY_BG, text_color=TXT_PRI,
        border_color=ENTRY_BDR,
        border_width=1, corner_radius=8,
        show=show
    )
    entry.pack(fill="x", ipady=4, padx=FORM_PAD, pady=(0, 2))

    entry.bind("<FocusIn>",  lambda e: fade_color(entry, None, "border_color", ACCENT2, steps=6, delay=10))
    entry.bind("<FocusOut>", lambda e: fade_color(entry, None, "border_color", ENTRY_BDR, steps=6, delay=10))
    return entry

def make_combo(label_text, options_list):
    """Returns a StringVar tied to the combobox."""
    tk.Label(
        active_parent, text=label_text,
        font=("Segoe UI", 9, "bold"),
        bg=CARD_BG, fg=TXT_SEC,
        anchor="w"
    ).pack(fill="x", padx=FORM_PAD, pady=(8, 2))

    border = tk.Frame(active_parent, bg=ENTRY_BDR, bd=0)
    border.pack(fill="x", padx=FORM_PAD, pady=(0, 0))

    inner = tk.Frame(border, bg=ENTRY_BG, bd=0)
    inner.pack(padx=1, pady=1, fill="x")

    var = tk.StringVar(value=options_list[0])
    cb = ttk.Combobox(
        inner, textvariable=var, values=options_list,
        font=("Segoe UI", 11), state="readonly",
        style="A.TCombobox"
    )
    cb.pack(fill="x", ipady=6, padx=8)
    
    cb.bind("<FocusIn>",  lambda e: border.config(bg=ACCENT2))
    cb.bind("<FocusOut>", lambda e: border.config(bg=ENTRY_BDR))
    return var

def make_show_pw(entries_list):
    v = tk.BooleanVar()
    row = tk.Frame(active_parent, bg=CARD_BG)
    row.pack(fill="x", padx=FORM_PAD, pady=(4, 0))
    tk.Checkbutton(
        row, text="Show password",
        font=("Segoe UI", 9),
        bg=CARD_BG, fg=TXT_HINT,
        selectcolor=CARD_BG,
        activebackground=CARD_BG,
        activeforeground=ACCENT2,
        variable=v, bd=0, highlightthickness=0,
        cursor="hand2",
        command=lambda: [e.configure(show="" if v.get() else "*") for e in entries_list]
    ).pack(side="left")

def make_btn_primary(text, cmd):
    """Full-width primary action button."""
    btn = ctk.CTkButton(
        active_parent, text=text,
        font=ctk.CTkFont("Segoe UI", 13, "bold"),
        fg_color=ACCENT, text_color=TXT_PRI,
        hover_color=BTN_HVR, corner_radius=8,
        command=cmd, height=40
    )
    btn.pack(fill="x", padx=FORM_PAD, pady=(16, 4))
    return btn

def make_btn_secondary(text, cmd):
    """Full-width secondary (ghost) button."""
    btn = ctk.CTkButton(
        active_parent, text=text,
        font=ctk.CTkFont("Segoe UI", 12),
        fg_color=BTN2_BG, text_color=TXT_SEC,
        hover_color=BTN2_HVR, corner_radius=8,
        command=cmd, height=36
    )
    btn.pack(fill="x", padx=FORM_PAD, pady=(4, 4))
    return btn

def make_link_row(items):
    """Row of clickable text links: items = [(text, cmd), ...]"""
    row = tk.Frame(active_parent, bg=CARD_BG)
    row.pack(fill="x", padx=FORM_PAD, pady=(6, 0))
    for text, cmd in items:
        lbl = tk.Label(
            row, text=text,
            font=("Segoe UI", 9),
            bg=CARD_BG, fg=TXT_HINT,
            cursor="hand2"
        )
        lbl.pack(side="left", padx=(0, 16))
        lbl.bind("<Button-1>", lambda e, c=cmd: c())
        lbl.bind("<Enter>", lambda e, l=lbl: fade_color(l, None, "fg", ACCENT2, steps=6, delay=10))
        lbl.bind("<Leave>", lambda e, l=lbl: fade_color(l, None, "fg", TXT_HINT, steps=6, delay=10))

def make_divider(text="— or —"):
    row = tk.Frame(active_parent, bg=CARD_BG)
    row.pack(fill="x", padx=FORM_PAD, pady=(10, 2))
    tk.Frame(row, bg=ENTRY_BDR, height=1).pack(side="left", fill="x", expand=True, pady=8)
    tk.Label(row, text=f"  {text}  ", font=("Segoe UI", 9),
             bg=CARD_BG, fg=TXT_HINT).pack(side="left")
    tk.Frame(row, bg=ENTRY_BDR, height=1).pack(side="left", fill="x", expand=True, pady=8)

# ══════════════════════════════════════════════════════════════════════════════
# PAGES
# ══════════════════════════════════════════════════════════════════════════════
# PAGES
# ══════════════════════════════════════════════════════════════════════════════
def home():
    make_title("Welcome Back", "Sign in to your account")

    # Spacer
    tk.Frame(active_parent, bg=CARD_BG, height=10).pack()

    make_btn_primary("  🔐   Sign In", lambda: transition_to_form(login))
    make_divider()
    make_btn_secondary("  ✦   Create New Account", lambda: transition_to_form(signup))

    # Decorative bottom section
    tk.Frame(active_parent, bg=ENTRY_BDR, height=1).pack(fill="x", padx=FORM_PAD, pady=(30, 10))
    tk.Label(
        active_parent,
        text="🔒  Your data is encrypted and secure",
        font=("Segoe UI", 9), bg=CARD_BG, fg=TXT_HINT, anchor="center"
    ).pack(fill="x")


def login():
    make_title("Sign In", "Enter your credentials to continue")
    e = make_entry("Email Address")
    p = make_entry("Password", "*")
    make_show_pw([p])

    def go():
        u = users()
        email_val = e.get().strip().lower()
        pass_val = p.get().strip()

        found_key = None
        for k in u.keys():
            if k.strip().lower() == email_val:
                found_key = k
                break
                
        if not found_key:
            return messagebox.showerror("Login Failed", "Invalid email or password.")
            
        user_data = u[found_key]
        pwd = user_data["password"]
        
        is_valid = verify_password(pwd, pass_val)
        
        if not is_valid:
            return messagebox.showerror("Login Failed", "Invalid email or password.")
            
        fade_out_window(root, lambda: launch_dashboard_with_fade(root, user_data["name"], found_key))

    make_btn_primary("  Sign In  →", go)
    make_link_row([("Forgot password?", lambda: transition_to_form(forgot)), ("← Home", lambda: transition_to_form(home))])


def signup():
    make_title("Create Account", "Fill in your details to get started")
    n = make_entry("Full Name")
    e = make_entry("Email Address")
    p = make_entry("Password", "*")
    c = make_entry("Confirm Password", "*")
    make_show_pw([p, c])

    def reg():
        u = users()
        name_val = n.get().strip()
        email_val = e.get().strip().lower()
        pass_val = p.get().strip()
        conf_val = c.get().strip()
        
        if not all([name_val, email_val, pass_val, conf_val]):
            return messagebox.showerror("Missing Fields", "Please fill in all fields.")
        if not okmail(email_val):
            return messagebox.showerror("Invalid Email", "Please enter a valid email address.")
        if len(pass_val) < 8:
            return messagebox.showerror("Weak Password", "Password must be at least 8 characters.")
        if pass_val != conf_val:
            return messagebox.showerror("Mismatch", "Passwords do not match.")
        
        found_key = any(k.strip().lower() == email_val for k in u.keys())
        if found_key:
            return messagebox.showerror("Duplicate", "An account with this email already exists.")
            
        u[email_val] = {
            "name": name_val,
            "password": hash_password(pass_val)
        }
        save(u)
        messagebox.showinfo("🎉 Welcome!", f"Hello {name_val}, your account is ready!")
        transition_to_form(home)

    make_btn_primary("  Create Account  →", reg)
    make_link_row([("← Back to Home", lambda: transition_to_form(home))])


def forgot():
    make_title("Reset Password", "Enter your email and a new password")
    e = make_entry("Registered Email")
    p = make_entry("New Password", "*")
    c = make_entry("Confirm New Password", "*")
    make_show_pw([p, c])

    def rst():
        u = users()
        email_val = e.get().strip().lower()
        pass_val = p.get().strip()
        conf_val = c.get().strip()
        
        found_key = None
        for k in u.keys():
            if k.strip().lower() == email_val:
                found_key = k
                break

        if not found_key:
            return messagebox.showerror("Not Found", "No account found with this email.")
        if len(pass_val) < 8:
            return messagebox.showerror("Weak Password", "Password must be at least 8 characters.")
        if pass_val != conf_val:
            return messagebox.showerror("Mismatch", "Passwords do not match.")
            
        u[found_key]["password"] = hash_password(pass_val)
        save(u)
        messagebox.showinfo("✅ Done!", "Your password has been reset successfully.")
        transition_to_form(login)

    make_btn_primary("  Reset Password  →", rst)
    make_link_row([("← Back to Login", lambda: transition_to_form(login))])


def launch_dashboard_with_fade(parent_window, name, email):
    parent_window.withdraw()
    dash = ctk.CTkToplevel()
    dash.protocol("WM_DELETE_WINDOW",
                  lambda: (dash.destroy(), parent_window.destroy()))
    dash.attributes("-alpha", 0.0)
    
    # Setup dashboard
    from dashboard import FinsightsDashboard
    FinsightsDashboard(dash, name, email)
    
    fade_in_window(dash)

# ── Launch ─────────────────────────────────────────────────────────────────────
transition_to_form(home)
root.mainloop()