import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from collections import defaultdict
from config import *

class BaseDashboard:
    # ── Window Setup ─────────────────────────────────────────────────────────────
    def _setup_win(self):
        self.root.title("Finsights — Dashboard")
        self.root.configure(bg=BG)
        self.root.minsize(1100, 680)
        self.root.resizable(True, True)
        self.root.update_idletasks()
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        ww = int(sw * 0.85)
        wh = int(sh * 0.85)
        self.root.geometry(f"{ww}x{wh}+{(sw-ww)//2}+{(sh-wh)//2}")

    def _setup_styles(self):
        s = ttk.Style()
        s.theme_use("clam")
        s.configure("D.Treeview",
                    background=CB, foreground=TP, fieldbackground=CB,
                    borderwidth=0, rowheight=34, font=("Segoe UI", 10))
        s.configure("D.Treeview.Heading",
                    background=CB2, foreground=CY,
                    font=("Segoe UI", 10, "bold"), borderwidth=0, relief="flat")
        s.map("D.Treeview",
              background=[("selected", AC)], foreground=[("selected", TP)])
        s.configure("Vertical.TScrollbar",
                    background=BD, troughcolor=CB,
                    borderwidth=0, arrowcolor=TS, width=8)
        s.configure("A.TCombobox",
                    fieldbackground=EN, background=EN,
                    foreground=TP, arrowcolor=CY,
                    selectbackground=AC, selectforeground=TP)
        s.map("A.TCombobox", fieldbackground=[("readonly", EN)])

    def _setup_wheel(self):
        # Bind MouseWheel exactly once globally to prevent memory leaks and locks
        def _on_wheel(e):
            if hasattr(self, "_active_canvas") and self._active_canvas:
                c = self._active_canvas
                if c.winfo_exists():
                    w = e.widget
                    while w:
                        if w == c:
                            c.yview_scroll(int(-1 * (e.delta / 40)), "units")
                            break
                        p = w.winfo_parent()
                        if not p:
                            break
                        try:
                            w = self.root.nametowidget(p)
                        except:
                            break
        self.root.bind_all("<MouseWheel>", _on_wheel)

    # ── Sidebar ──────────────────────────────────────────────────────────────────
    def _build_sidebar(self):
        sc = tk.Canvas(self.root, width=SIDE_W, bg=SB, bd=0, highlightthickness=0)
        sc.pack(side="left", fill="y")
        self._sc = sc
        # FINSIGHTS Logo (White and Amber, unified single word appearance)
        logo_cx = 90  # Shifted left from SIDE_W // 2 (110)
        sc.create_text(logo_cx - 2, 36, text="FIN", font=("Segoe UI", 20, "bold"), fill="#ffffff", anchor="e", tags="logo")
        sc.create_text(logo_cx + 2, 36, text="SIGHTS", font=("Segoe UI", 20, "bold"), fill=GO, anchor="w", tags="logo")

        # Nav items
        self._nav_data = [
            ("🏠", "Overview",      self.show_overview),
            ("💰", "Income",        self.show_income),
            ("💸", "Expenses",      self.show_expenses),
            ("📊", "Budget",        self.show_budget),
            ("📈", "Investments",   self.show_investments),
            ("🎯", "Goals",         self.show_goals),
            ("🤖", "AI Insights",   self.show_insights),
            ("❤️", "Health Score",  self.show_health),
            ("📋", "Reports",       self.show_reports),
            ("🔔", "Notifications", self.show_notifications),
            ("👤", "Profile",       self.show_profile),
        ]

            
        self._nav_hl = []
        for i, (icon, label, cmd) in enumerate(self._nav_data):
            y = 96 + i * 50
            hl  = sc.create_rectangle(0, y, SIDE_W, y + 44, fill=CB2, outline="", state="hidden")
            bar = sc.create_rectangle(0, y, 3, y + 44, fill=CY, outline="", state="hidden")
            ico = sc.create_text(30, y + 22, text=icon, font=("Segoe UI Emoji", 14), fill=TP, anchor="center")
            lbl = sc.create_text(58, y + 22, text=label, font=("Segoe UI", 11), fill=TS, anchor="w")
            area = sc.create_rectangle(0, y, SIDE_W, y + 44, fill="", outline="", tags=f"nv{i}")
            self._nav_hl.append((hl, bar, ico, lbl))
            sc.tag_bind(f"nv{i}", "<Button-1>", lambda e, c=cmd: c())
            sc.tag_bind(f"nv{i}", "<Enter>",
                lambda e, l=lbl, ic=ico: (
                    fade_color(sc, l, "fill", TP, steps=5, delay=10, is_canvas_item=True),
                    fade_color(sc, ic, "fill", CY, steps=5, delay=10, is_canvas_item=True)
                ))
            sc.tag_bind(f"nv{i}", "<Leave>",
                lambda e, idx2=i, l=lbl, ic=ico: (
                    fade_color(sc, l, "fill", TP if self.active_nav == self._nav_data[idx2][1] else TS, steps=5, delay=10, is_canvas_item=True),
                    fade_color(sc, ic, "fill", CY if self.active_nav == self._nav_data[idx2][1] else TP, steps=5, delay=10, is_canvas_item=True)
                ))
        
        # User info at bottom
        uname = self.username[:18] if len(self.username) > 18 else self.username
        sc.create_line(16, 0, SIDE_W - 16, 0, fill=BD, width=1, tags="bottom_line")
        sc.create_text(SIDE_W // 2, 0, text=f"👤  {uname}", font=("Segoe UI", 9), fill=TS, anchor="center", tags="bottom_user")
        sc.create_text(SIDE_W // 2, 0, text="© 2026 Finsights", font=("Segoe UI", 8), fill=TH, anchor="center", tags="bottom_copy")

        def _on_sc_resize(e):
            h = e.height
            sc.delete("gradient")
            # Sidebar gradient using SB green tones: from #0a1c15 (10, 28, 21) to #050f0b (5, 15, 11)
            for j in range(h):
                t = j / max(1, h)
                r = int(10 - t * 5)
                g = int(28 - t * 13)
                b = int(21 - t * 10)
                sc.create_line(0, j, SIDE_W, j, fill=f"#{r:02x}{g:02x}{b:02x}", tags="gradient")
            sc.tag_lower("gradient")
            
            sc.delete("orb")
            sc.create_oval(-50, -50, 190, 190, fill="#071a12", outline="", tags="orb")
            sc.create_oval(50, h - 200, 290, h + 50, fill="#05150e", outline="", tags="orb")
            sc.tag_lower("orb")
            sc.tag_lower("gradient")
            
            sc.delete("right_border")
            sc.create_line(SIDE_W - 1, 0, SIDE_W - 1, h, fill=BD, width=1, tags="right_border")
            
            sc.coords("bottom_line", 16, h - 76, SIDE_W - 16, h - 76)
            sc.coords("bottom_user", SIDE_W // 2, h - 50)
            sc.coords("bottom_copy", SIDE_W // 2, h - 26)
            
            sc.delete("logo_line")
            sc.create_line(16, 82, SIDE_W - 16, 82, fill=BD, width=1, tags="logo_line")
            
            # Raise the FINSIGHTS logo so it is never hidden
            sc.tag_raise("logo")
            sc.tag_raise("logo_line")

        sc.bind("<Configure>", _on_sc_resize)

    def _set_nav(self, name):
        self.active_nav = name
        sc = self._sc
        for i, (hl, bar, ico, lbl) in enumerate(self._nav_hl):
            if self._nav_data[i][1] == name:
                sc.itemconfig(hl, state="normal")
                sc.itemconfig(bar, state="normal")
                sc.itemconfig(lbl, fill=TP, font=("Segoe UI", 11, "bold"))
                sc.itemconfig(ico, fill=CY)
            else:
                sc.itemconfig(hl, state="hidden")
                sc.itemconfig(bar, state="hidden")
                sc.itemconfig(lbl, fill=TS, font=("Segoe UI", 11))
                sc.itemconfig(ico, fill=TP)

    # ── Header ───────────────────────────────────────────────────────────────────
    def _build_header(self):
        hc = tk.Canvas(self._right_panel, height=HEAD_H, bg=BG, bd=0, highlightthickness=0)
        hc.pack(side="top", fill="x")
        self._hc = hc
        # Page title
        self._htitle = hc.create_text(
            24, HEAD_H // 2, text="Overview",
            font=("Segoe UI", 18, "bold"), fill=TP, anchor="w"
        )
        # Date & Bell (repositioned on resize)
        self._date_txt = hc.create_text(0, HEAD_H // 2, text=datetime.now().strftime("%a, %d %b %Y"), font=("Segoe UI", 10), fill=TS, anchor="center", tags="date")
        self._bell_icon = hc.create_text(0, HEAD_H // 2, text="🔔", font=("Segoe UI Emoji", 16), fill=TP, tags="bell")
        
        hc.tag_bind("bell", "<Button-1>", lambda e: self.show_notifications())
        hc.tag_bind("bell", "<Enter>",  lambda e: hc.config(cursor="hand2"))
        hc.tag_bind("bell", "<Leave>",  lambda e: hc.config(cursor=""))
        
        self._bell_x = WIN_W - SIDE_W - 60
        self._update_bell()

        def _on_hc_resize(e):
            w = e.width
            hc.delete("gradient")
            for j in range(HEAD_H):
                t = j / HEAD_H
                r = int(22 + t * 10); g = int(22 + t * 10); b = int(23 + t * 10)
                hc.create_line(0, j, w, j, fill=f"#{r:02x}{g:02x}{b:02x}", tags="gradient")
            hc.tag_lower("gradient")
            
            hc.delete("border")
            hc.create_line(0, HEAD_H - 1, w, HEAD_H - 1, fill=BD, width=1, tags="border")
            
            hc.coords("date", w - 160, HEAD_H // 2)
            hc.coords("bell", w - 60, HEAD_H // 2)
            self._bell_x = w - 60
            self._update_bell()
            
        hc.bind("<Configure>", _on_hc_resize)

    def _update_bell(self):
        hc = self._hc
        hc.delete("nbadge")
        notifs = _ld("notifications")
        unread = sum(1 for n in notifs if not n.get("read"))
        if unread:
            bx = self._bell_x + 6; by = HEAD_H // 2 - 18
            hc.create_oval(bx, by, bx + 16, by + 16, fill=RE, outline="", tags="nbadge")
            hc.create_text(bx + 8, by + 8, text=str(unread),
                           font=("Segoe UI", 7, "bold"), fill=TP, tags="nbadge")

    def _set_title(self, t):
        self._hc.itemconfig(self._htitle, text=t)

    # ── Content Area ──────────────────────────────────────────────────────────────
    def _build_content(self):
        self._cf = ctk.CTkFrame(self._right_panel, fg_color=BG, corner_radius=0)
        self._cf.pack(side="top", fill="both", expand=True)

    def _clear(self):
        self._active_canvas = None
        self._old_page_frame = getattr(self, "_active_page_frame", None)
        self._active_page_frame = ctk.CTkFrame(self._cf, fg_color=BG, corner_radius=0)
        
        if not self._old_page_frame:
            self._active_page_frame.pack(fill="both", expand=True)
        else:
            w = self._cf.winfo_width()
            if w <= 1:
                w = WIN_W - SIDE_W
            self._active_page_frame.place(x=w, y=0, relwidth=1, relheight=1)
            self.root.after(10, self._animate_page_transition)

    def _animate_page_transition(self):
        old_frame = getattr(self, "_old_page_frame", None)
        new_frame = getattr(self, "_active_page_frame", None)
        if not new_frame:
            return
        w = self._cf.winfo_width()
        if w <= 1:
            w = WIN_W - SIDE_W
        
        steps = 6
        delay = 8
        
        def step_anim(step):
            if step > steps:
                if new_frame.winfo_exists():
                    new_frame.place_forget()
                    new_frame.pack(fill="both", expand=True)
                if old_frame and old_frame.winfo_exists():
                    old_frame.destroy()
                self._old_page_frame = None
                return
                
            t = step / steps
            ease = 1 - (1 - t) ** 3
            
            new_x = int(w * (1 - ease))
            if new_frame.winfo_exists():
                new_frame.place(x=new_x, y=0, relwidth=1, relheight=1)
                
            if old_frame and old_frame.winfo_exists():
                try:
                    old_frame.pack_forget()
                except:
                    pass
                old_frame.place(x=int(-w * ease), y=0, relwidth=1, relheight=1)
                
            self.root.after(delay, lambda: step_anim(step + 1))
            
        step_anim(1)



    def _scrollable(self, parent):
        """Return a scrollable inner frame placed inside parent."""
        if parent == self._cf:
            parent = getattr(self, "_active_page_frame", self._cf)
        c = tk.Canvas(parent, bg=BG, bd=0, highlightthickness=0)
        self._active_canvas = c  # Register as the current active scrollable canvas
        sb = ttk.Scrollbar(parent, orient="vertical", command=c.yview, style="Vertical.TScrollbar")
        c.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        c.pack(fill="both", expand=True)
        f = tk.Frame(c, bg=BG)
        fw = c.create_window(0, 0, anchor="nw", window=f)
        def _cfg(e):  c.configure(scrollregion=c.bbox("all"))
        def _resize(e): c.itemconfig(fw, width=e.width)
        f.bind("<Configure>", _cfg)
        c.bind("<Configure>", _resize)
        return f

    # ── Widget Helpers ────────────────────────────────────────────────────────────
    def _kpi(self, parent, title, value, sub="", color=CY, icon="💡", cmd=None):
        cur = "hand2" if cmd else ""
        outer = tk.Frame(parent, bg=BD, cursor=cur)
        inner = tk.Frame(outer, bg=CB, cursor=cur)
        inner.pack(padx=1, pady=1, fill="both", expand=True)
        tk.Frame(inner, bg=color, height=3).pack(fill="x")
        lbl_title = tk.Label(inner, text=f"{icon}  {title}", font=("Segoe UI", 9), bg=CB, fg=TS, cursor=cur)
        lbl_title.pack(anchor="w", padx=14, pady=(10, 2))
        lbl_val = tk.Label(inner, text=value, font=("Segoe UI", 17, "bold"), bg=CB, fg=color, cursor=cur)
        lbl_val.pack(anchor="w", padx=14)
        lbl_sub = tk.Label(inner, text=sub, font=("Segoe UI", 9), bg=CB, fg=TH, cursor=cur)
        lbl_sub.pack(anchor="w", padx=14, pady=(2, 12))
        if cmd:
            for w in [outer, inner, lbl_title, lbl_val, lbl_sub]:
                w.bind("<Button-1>", lambda e: cmd())
        return outer

    def _tv(self, parent, cols, widths=None, height=12):
        """Dark-styled Treeview with scrollbar."""
        f = tk.Frame(parent, bg=CB)
        tv = ttk.Treeview(f, columns=cols, show="headings",
                          style="D.Treeview", selectmode="browse", height=height)
        sb = ttk.Scrollbar(f, orient="vertical", command=tv.yview)
        tv.configure(yscrollcommand=sb.set)
        for i, col in enumerate(cols):
            tv.heading(col, text=col)
            tv.column(col, width=widths[i] if widths else 120, minwidth=60, anchor="w")
        tv.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        tv.tag_configure("odd",  background="#1d1d1f")
        tv.tag_configure("even", background=CB)
        return f, tv

    def _tv_fill(self, tv, rows):
        """rows = list of tuples; first element is the iid, rest are values."""
        tv.delete(*tv.get_children())
        for i, row in enumerate(rows):
            tv.insert("", "end", iid=row[0], values=row[1:],
                      tags=("odd" if i % 2 else "even",))

    def _dialog(self, title, fields, on_save, defaults=None):
        """Generic modal dialog."""
        dlg = tk.Toplevel(self.root)
        dlg.title(title)
        dlg.configure(bg=CB)
        dlg.grab_set()
        dlg.resizable(False, False)
        DW = 440
        DH = min(700, 90 + len(fields) * 74 + 80)
        dlg.geometry(f"{DW}x{DH}")
        dlg.update_idletasks()
        x = (dlg.winfo_screenwidth() - DW) // 2
        y = (dlg.winfo_screenheight() - DH) // 2
        dlg.geometry(f"{DW}x{DH}+{x}+{y}")

        tk.Frame(dlg, bg=AC, height=3).pack(fill="x")
        tk.Label(dlg, text=title, font=("Segoe UI Semibold", 13),
                 bg=CB, fg=TP).pack(padx=20, pady=(14, 2), anchor="w")
        tk.Frame(dlg, bg=BD, height=1).pack(fill="x", padx=20, pady=(0, 6))

        widgets = {}
        for fd in fields:
            tk.Label(dlg, text=fd["lbl"], font=("Segoe UI Semibold", 9),
                     bg=CB, fg=TS).pack(padx=20, pady=(8, 2), anchor="w")
            if fd["type"] == "combo":
                var = tk.StringVar()
                opts = fd.get("opts", [])
                default_val = (defaults or {}).get(fd["k"], opts[0] if opts else "")
                var.set(default_val)
                cb = ttk.Combobox(dlg, textvariable=var, values=opts,
                                  font=("Segoe UI Light", 11), state="readonly",
                                  style="A.TCombobox")
                cb.pack(fill="x", padx=20, ipady=5)
                widgets[fd["k"]] = var
            else:
                bdr = tk.Frame(dlg, bg=BD)
                bdr.pack(fill="x", padx=20)
                inn = tk.Frame(bdr, bg=EN)
                inn.pack(padx=1, pady=1, fill="x")
                e = tk.Entry(inn, font=("Segoe UI Light", 11), bg=EN, fg=TP,
                             insertbackground=CY, relief="flat", bd=0)
                e.pack(fill="x", ipady=8, padx=10)
                if defaults and fd["k"] in defaults:
                    e.insert(0, str(defaults[fd["k"]]))
                e.bind("<FocusIn>",  lambda ev, b=bdr: b.config(bg=CY))
                e.bind("<FocusOut>", lambda ev, b=bdr: b.config(bg=BD))
                widgets[fd["k"]] = e

        brow = tk.Frame(dlg, bg=CB)
        brow.pack(fill="x", padx=20, pady=16, side="bottom")

        def _ok():
            vals = {k: (w.get() if isinstance(w, tk.StringVar) else w.get())
                    for k, w in widgets.items()}
            on_save(vals, dlg)

        sv = tk.Label(brow, text="  Save  ", font=("Segoe UI", 11, "bold"),
                      bg=AC, fg=TP, cursor="hand2", pady=9, padx=18)
        sv.pack(side="left")
        sv.bind("<Button-1>", lambda e: _ok())
        sv.bind("<Enter>", lambda e: fade_color(sv, None, "bg", "#6d28d9", steps=6, delay=10))
        sv.bind("<Leave>", lambda e: fade_color(sv, None, "bg", AC, steps=6, delay=10))

        cn = tk.Label(brow, text="  Cancel  ", font=("Segoe UI", 11),
                      bg=CB2, fg=TS, cursor="hand2", pady=9, padx=18)
        cn.pack(side="left", padx=(10, 0))
        cn.bind("<Button-1>", lambda e: dlg.destroy())
        cn.bind("<Enter>", lambda e: fade_color(cn, None, "bg", BD, steps=6, delay=10))
        cn.bind("<Leave>", lambda e: fade_color(cn, None, "bg", CB2, steps=6, delay=10))

    def _tb_btn(self, parent, text, cmd, color=AC):
        """Toolbar button."""
        b = tk.Label(parent, text=text, font=("Segoe UI", 10, "bold"),
                     bg=color, fg=TP, cursor="hand2", padx=14, pady=7)
        b.pack(side="left", padx=(0, 8))
        b.bind("<Button-1>", lambda e: cmd())
        hov = "#6d28d9" if color == AC else ("#263147" if color == CB2 else "#0e7c59")
        b.bind("<Enter>", lambda e: fade_color(b, None, "bg", hov, steps=6, delay=10))
        b.bind("<Leave>", lambda e: fade_color(b, None, "bg", color, steps=6, delay=10))
        return b

    def _quick_card(self, parent, icon, name, desc, color, cmd):
        """Clickable quick-access card for the Overview panel."""
        HOV = "#32386a"
        outer = tk.Frame(parent, bg=BD, cursor="hand2")
        outer.pack(side="left", fill="both", expand=True, padx=(0, 8))
        inner = tk.Frame(outer, bg=CB2, cursor="hand2")
        inner.pack(padx=1, pady=1, fill="both")
        tk.Frame(inner, bg=color, height=3).pack(fill="x")
        body = tk.Frame(inner, bg=CB2, cursor="hand2")
        body.pack(fill="both", padx=12, pady=10)
        ico_lbl  = tk.Label(body, text=icon, font=("Segoe UI Emoji", 24),
                            bg=CB2, fg=TP, cursor="hand2")
        ico_lbl.pack(anchor="w")
        name_lbl = tk.Label(body, text=name, font=("Segoe UI", 11, "bold"),
                            bg=CB2, fg=TP, cursor="hand2")
        name_lbl.pack(anchor="w", pady=(4, 0))
        desc_lbl = tk.Label(body, text=desc, font=("Segoe UI", 9),
                            bg=CB2, fg=TS, cursor="hand2")
        desc_lbl.pack(anchor="w")
        arr_lbl  = tk.Label(body, text="→", font=("Segoe UI", 13, "bold"),
                            bg=CB2, fg=color, cursor="hand2")
        arr_lbl.pack(anchor="e", pady=(6, 0))
        all_w = [inner, body, ico_lbl, name_lbl, desc_lbl, arr_lbl]
        def _click(e): cmd()
        def _enter(e):
            for w in all_w: fade_color(w, None, "bg", HOV, steps=5, delay=10)
        def _leave(e):
            for w in all_w: fade_color(w, None, "bg", CB2, steps=5, delay=10)
        for w in [outer] + all_w:
            w.bind("<Button-1>", _click)
        for w in all_w:
            w.bind("<Enter>", _enter)
            w.bind("<Leave>", _leave)
        return outer

    def _sec(self, parent, title, sub=""):
        tk.Label(parent, text=title, font=("Segoe UI", 15, "bold"),
                 bg=BG, fg=TP).pack(anchor="w", padx=20, pady=(16, 2))
        if sub:
            tk.Label(parent, text=sub, font=("Segoe UI", 9),
                     bg=BG, fg=TH).pack(anchor="w", padx=20, pady=(0, 8))

    # ── Transaction & Data Utilities ──────────────────────────────────────────────
    def _save_trans(self, vals, ttype, dlg, refresh):
        try:   amt = float(vals["amount"])
        except: return messagebox.showerror("Error", "Amount must be a number.")
        if not vals.get("desc", "").strip():
            return messagebox.showerror("Error", "Description is required.")
        recs = _ld("transactions")
        recs.append({"id": mk_id(), "type": ttype,
                     "date": vals.get("date", today()),
                     "desc": vals["desc"],
                     "category": vals.get("category", ""),
                     "amount": amt,
                     "notes": vals.get("notes", "")})
        _sv("transactions", recs); dlg.destroy()
        self._auto_notif(); refresh()

    def _upd_trans(self, iid, vals, dlg, refresh):
        try:   amt = float(vals["amount"])
        except: return messagebox.showerror("Error", "Amount must be a number.")
        recs = _ld("transactions")
        for r in recs:
            if r["id"] == iid:
                r.update({"date": vals["date"], "desc": vals["desc"],
                           "category": vals["category"], "amount": amt,
                           "notes": vals.get("notes", "")})
        _sv("transactions", recs); dlg.destroy(); refresh()

    def _save_inv_cb(self, vals, dlg):
        try:
            qty = float(vals["qty"])
            bp  = float(vals["buy_price"])
            cp  = float(vals["current_price"])
        except: return messagebox.showerror("Error", "Qty, buy price and current price must be numbers.")
        if not vals.get("name", "").strip():
            return messagebox.showerror("Error", "Asset name is required.")
        invs = _ld("investments")
        invs.append({"id": mk_id(), "name": vals["name"],
                     "symbol": vals["symbol"], "type": vals["type"],
                     "qty": qty, "buy_price": bp, "current_price": cp,
                     "notes": vals.get("notes", "")})
        _sv("investments", invs); dlg.destroy(); self.show_investments()

    def _upd_inv(self, iid, vals, dlg):
        try:
            qty = float(vals["qty"])
            bp  = float(vals["buy_price"])
            cp  = float(vals["current_price"])
        except: return messagebox.showerror("Error", "Qty, buy price and current price must be numbers.")
        invs = _ld("investments")
        for i in invs:
            if i["id"] == iid:
                i.update({"name": vals["name"], "symbol": vals["symbol"],
                           "type": vals["type"], "qty": qty,
                           "buy_price": bp, "current_price": cp,
                           "notes": vals.get("notes", "")})
        _sv("investments", invs); dlg.destroy(); self.show_investments()

    def _set_budget(self, cat, vals, dlg):
        try:   amt = float(vals["amount"])
        except: return messagebox.showerror("Error", "Amount must be a number.")
        b = _ldd("budgets")
        b[cat] = amt; _sv("budgets", b); dlg.destroy(); self.show_budget()

    def _save_goal_cb(self, vals, dlg):
        try:   tgt = float(vals["target"]); saved = float(vals["saved"])
        except: return messagebox.showerror("Error", "Target and saved amounts must be numbers.")
        if not vals.get("name", "").strip():
            return messagebox.showerror("Error", "Goal name is required.")
        goals = _ld("goals")
        goals.append({"id": mk_id(), "name": vals["name"],
                      "target": tgt, "saved": saved,
                      "deadline": vals.get("deadline", "")})
        _sv("goals", goals); dlg.destroy(); self.show_goals()

    def _upd_goal(self, gid, vals, dlg):
        try:   tgt = float(vals["target"]); saved = float(vals["saved"])
        except: return messagebox.showerror("Error", "Target and saved amounts must be numbers.")
        goals = _ld("goals")
        for g in goals:
            if g["id"] == gid:
                g.update({"name": vals["name"],
                           "target": tgt, "saved": saved,
                           "deadline": vals.get("deadline", "")})
        _sv("goals", goals); dlg.destroy(); self.show_goals()

    def _save_notif_cb(self, vals, dlg):
        ns = _ld("notifications")
        ns.append({"id": mk_id(), "type": vals.get("type", "info"),
                   "title": vals.get("title", ""), "msg": vals.get("msg", ""),
                   "read": False, "ts": now_ts()})
        _sv("notifications", ns); self._update_bell(); dlg.destroy()
        self.show_notifications()

    def _auto_notif(self):
        """Generate budget-exceeded notifications automatically."""
        trans = _ld("transactions"); budgets = _ldd("budgets"); cm = curr_m()
        spent_by = defaultdict(float)
        for r in trans:
            if r["type"] == "expense" and r["date"].startswith(cm):
                spent_by[r["category"]] += r["amount"]
        ns = _ld("notifications")
        existing = {n["title"] for n in ns}
        for cat, bgt in budgets.items():
            spent = spent_by.get(cat, 0); pct = spent / bgt if bgt else 0
            title = f"Budget Alert: {cat}"
            if pct >= 0.9 and title not in existing:
                ns.append({"id": mk_id(), "type": "warning", "title": title,
                            "msg": f"{cat} spending at {int(pct*100)}% of {fmt_inr(bgt)} budget",
                            "read": False, "ts": now_ts()})
        _sv("notifications", ns); self._update_bell()

    # ── Calculation & Drawing Helpers ─────────────────────────────────────────────
    def _calc_health(self):
        trans   = _ld("transactions"); budgets = _ldd("budgets")
        goals   = _ld("goals");        invs    = _ld("investments"); cm = curr_m()
        mi = sum(r["amount"] for r in trans if r["type"] == "income"  and r["date"].startswith(cm))
        me = sum(r["amount"] for r in trans if r["type"] == "expense" and r["date"].startswith(cm))
        sr     = (mi - me) / mi if mi > 0 else 0
        pts_sr = min(30.0, max(0.0, sr * 150))
        spent_by = defaultdict(float)
        for r in trans:
            if r["type"] == "expense" and r["date"].startswith(cm):
                spent_by[r["category"]] += r["amount"]
        cats_ok  = sum(1 for c, b in budgets.items() if spent_by.get(c, 0) <= b)
        pts_bgt  = (cats_ok / len(budgets) * 25) if budgets else 0
        if goals:
            avg_p = sum(min(1.0, g["saved"] / g["target"]) for g in goals if g["target"] > 0) / len(goals)
            pts_g = avg_p * 25
        else:
            pts_g = 0.0
        inv_types = len({i["type"] for i in invs})
        pts_i     = min(20.0, inv_types * 5)
        total = pts_sr + pts_bgt + pts_g + pts_i
        breakdown = {
            "Savings Rate":      (round(pts_sr),  30),
            "Budget Compliance": (round(pts_bgt), 25),
            "Goal Progress":     (round(pts_g),   25),
            "Invest Diversity":  (round(pts_i),   20),
        }
        return round(total), breakdown

    def _gen_insights(self):
        trans = _ld("transactions"); budgets = _ldd("budgets")
        goals = _ld("goals");        invs    = _ld("investments"); cm = curr_m()
        insights = []
        mi = sum(r["amount"] for r in trans if r["type"] == "income"  and r["date"].startswith(cm))
        me = sum(r["amount"] for r in trans if r["type"] == "expense" and r["date"].startswith(cm))
        if mi > 0:
            sr = (mi - me) / mi * 100
            if sr >= 20:
                insights.append({"icon": "✅", "title": "Great Savings Rate!",
                    "msg": f"You're saving {sr:.1f}% of your income this month — above the 20% target.",
                    "tip": "Keep it up! Invest your surplus in SIPs or index funds.",
                    "bg": "#1c2c1c", "border": GR})
            elif sr > 0:
                insights.append({"icon": "⚠️", "title": "Savings Rate Needs Work",
                    "msg": f"Savings rate is {sr:.1f}% this month. Target is 20% ({fmt_inr(mi*0.2)}).",
                    "tip": "Try the 50/30/20 rule: 50% needs, 30% wants, 20% savings.",
                    "bg": "#2c2a1c", "border": GO})
            else:
                insights.append({"icon": "🔴", "title": "Spending Exceeds Income!",
                    "msg": f"Spent {fmt_inr(me)} vs income of {fmt_inr(mi)} — deficit of {fmt_inr(me - mi)}.",
                    "tip": "Review discretionary spending and cut non-essentials immediately.",
                    "bg": "#2c1c1c", "border": RE})
        spent_by = defaultdict(float)
        for r in trans:
            if r["type"] == "expense" and r["date"].startswith(cm):
                spent_by[r["category"]] += r["amount"]
        if spent_by:
            top_cat = max(spent_by, key=spent_by.get)
            top_amt = spent_by[top_cat]
            bgt     = budgets.get(top_cat, 0)
            pct_b   = top_amt / bgt * 100 if bgt else 0
            insights.append({"icon": "📊", "title": f"Top Expense: {top_cat}",
                "msg": f"Highest spending: {top_cat} at {fmt_inr(top_amt)} ({pct_b:.0f}% of budget).",
                "tip": f"Look for small ways to reduce {top_cat} spending next month.",
                "bg": "#1c222c", "border": AC})
        for cat, bgt in budgets.items():
            spent = spent_by.get(cat, 0); pct = spent / bgt if bgt else 0
            if pct > 0.9:
                insights.append({"icon": "⚠️", "title": f"Budget Alert: {cat}",
                    "msg": f"Used {int(pct*100)}% of {cat} budget. Spent {fmt_inr(spent)} of {fmt_inr(bgt)}.",
                    "tip": "Pause non-essential spending in this category for the rest of the month.",
                    "bg": "#2c2a1c", "border": GO})
        for g in goals[:2]:
            tgt = g["target"]; saved = g["saved"]; pct = saved / tgt * 100 if tgt else 0
            insights.append({"icon": g.get("icon", "🎯"), "title": f"Goal: {g['name']}",
                "msg": f"{g['name']} is {pct:.0f}% complete. {fmt_inr(saved)} of {fmt_inr(tgt)} saved.",
                "tip": f"Need {fmt_inr(tgt-saved)} more by {g['deadline']}.",
                "bg": "#1c2c2c", "border": CY})
        if invs:
            pf_val  = sum(i["qty"] * i["current_price"] for i in invs)
            pf_cost = sum(i["qty"] * i["buy_price"]     for i in invs)
            pl      = pf_val - pf_cost; plp = pl / pf_cost * 100 if pf_cost else 0
            direction = "up" if pl >= 0 else "down"
            clr  = GR if pl >= 0 else RE; bg = "#1c2c1c" if pl >= 0 else "#2c1c1c"
            icon = "📈" if pl >= 0 else "📉"
            insights.append({"icon": icon, "title": "Portfolio Performance",
                "msg": f"Portfolio is {direction} {fmt_inr(abs(pl))} ({plp:+.1f}%) overall. Total value: {fmt_inr(pf_val)}.",
                "tip": "Rebalance if any single asset exceeds 30% of portfolio." if pl > 0 else "Consider rupee-cost averaging during downturns.",
                "bg": bg, "border": clr})
        return insights

    def _draw_gauge(self, canvas, cx, cy, r, score, big=False):
        clr = GR if score >= 80 else CY if score >= 65 else GO if score >= 50 else OR if score >= 35 else RE
        lw  = 16 if big else 12
        canvas.create_arc(cx - r, cy - r, cx + r, cy + r,
                          start=220, extent=-260,
                          style="arc", outline=CB2, width=lw)
        ext = -260 * score / 100
        canvas.create_arc(cx - r, cy - r, cx + r, cy + r,
                          start=220, extent=ext,
                          style="arc", outline=clr, width=lw)
        fs = 26 if big else 20
        canvas.create_text(cx, cy - 14, text=str(int(score)),
                           font=("Segoe UI", fs, "bold"), fill=clr, anchor="center")
        canvas.create_text(cx, cy + 14, text="/ 100",
                           font=("Segoe UI", 9 if big else 8), fill=TS, anchor="center")

    def _draw_ring(self, canvas, cx, cy, r, pct, color):
        """Circular progress ring for goals."""
        canvas.create_oval(cx - r, cy - r, cx + r, cy + r, outline=CB2, width=8)
        if pct > 0:
            ext = -360 * pct
            canvas.create_arc(cx - r, cy - r, cx + r, cy + r,
                              start=90, extent=ext,
                              style="arc", outline=color, width=8)
        canvas.create_text(cx, cy, text=f"{int(pct*100)}%",
                           font=("Segoe UI", 12, "bold"), fill=color, anchor="center")

    def _draw_pie(self, canvas, cx, cy, r, data):
        """Pie chart. data = [(label, value, color), ...]"""
        if not data: return
        total = sum(v for _, v, _ in data)
        if total == 0: return
        start = 90
        for _, val, clr in data:
            ext = -360 * val / total
            canvas.create_arc(cx - r, cy - r, cx + r, cy + r,
                              start=start, extent=ext,
                              fill=clr, outline=CB, width=2)
            start += ext

    def _draw_bar_chart(self, canvas, data):
        """Bar chart for income vs expenses."""
        canvas.delete("all")
        W = canvas.winfo_width(); H = canvas.winfo_height()
        if W < 20 or H < 20 or not data: return

        pad_l = 52; pad_r = 20; pad_t = 16; pad_b = 36
        cw = W - pad_l - pad_r; ch = H - pad_t - pad_b

        max_val = max(max(d[1], d[2]) for d in data) or 1
        n = len(data); slot_w = cw // n; bar_w = max(12, slot_w // 3)

        for i in range(5):
            y = pad_t + int(ch * (1 - i / 4))
            canvas.create_line(pad_l, y, W - pad_r, y, fill=CB2, dash=(4, 4))
            val = int(max_val * i / 4)
            lbl = f"₹{val//1000}k" if val >= 1000 else f"₹{val}"
            canvas.create_text(pad_l - 4, y, text=lbl, font=("Segoe UI", 7), fill=TH, anchor="e")

        for i, (label, income, expense) in enumerate(data):
            x0 = pad_l + i * slot_w + slot_w // 5
            h1 = int(ch * income / max_val)
            canvas.create_rectangle(x0, pad_t + ch - h1, x0 + bar_w, pad_t + ch,
                                    fill=GR, outline="")
            h2 = int(ch * expense / max_val)
            canvas.create_rectangle(x0 + bar_w + 4, pad_t + ch - h2,
                                    x0 + bar_w * 2 + 4, pad_t + ch,
                                    fill=RE, outline="")
            canvas.create_text(x0 + bar_w + 2, pad_t + ch + 16, text=label,
                                font=("Segoe UI", 9), fill=TS, anchor="center")
