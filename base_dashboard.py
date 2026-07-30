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
        s.map("A.TCombobox", fieldbackground=[("readonly", EN)], foreground=[("readonly", TP)])

    def refresh_theme(self):
        self.root.configure(bg=BG)
        self._setup_styles()
        if hasattr(self, "_right_panel") and self._right_panel:
            try:
                self._right_panel.configure(fg_color=BG)
            except Exception:
                pass
        if hasattr(self, "_cf") and self._cf:
            try:
                self._cf.configure(fg_color=BG)
            except Exception:
                pass
        if hasattr(self, "_sc") and self._sc:
            self._sc.configure(bg=SB)
            self._sc.itemconfig("bottom_line", fill=BD)
            self._sc.itemconfig("bottom_user", fill=TS)
            self._sc.itemconfig("bottom_copy", fill=TH)
            self._sc.itemconfig("logo_line", fill=BD)
            self._sc.itemconfig("right_border", fill=BD)
            self._sc.event_generate("<Configure>")
        if hasattr(self, "_hc") and self._hc:
            self._hc.configure(bg=BG)
            self._hc.itemconfig(self._htitle, fill=TP)
            self._hc.itemconfig(self._date_txt, fill=TS)
            self._hc.itemconfig(self._bell_icon, fill=TP)
            self._hc.itemconfig(self._month_btn, fill=TP)
            if hasattr(self, "search_entry"):
                self.search_entry.configure(bg=EN, fg=TP, insertbackground=CY)
                if hasattr(self.search_entry, "master"):
                    self.search_entry.master.configure(bg=EN)
            self._hc.event_generate("<Configure>")
            
        self._set_nav(self.active_nav)
        
        # Re-render active view
        nav_map = {name: cmd for icon, name, cmd in self._nav_data if cmd is not None}
        if self.active_nav in nav_map:
            nav_map[self.active_nav]()

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
            ("🔄", "Transactions",  getattr(self, "show_transactions", None)),
            ("💰", "Income",        self.show_income),
            ("💸", "Expenses",      self.show_expenses),
            ("📉", "Analytics",     getattr(self, "show_analytics", None)),
            ("💎", "Net Worth",     getattr(self, "show_net_worth", None)),
            ("🔮", "Forecast",      getattr(self, "show_forecast", None)),
            ("🔁", "Recurring",     getattr(self, "show_recurring", None)),
            ("📊", "Budget",        self.show_budget),
            ("📈", "Investments",   self.show_investments),
            ("🎯", "Goals",         self.show_goals),
            ("🤖", "AI Insights",   self.show_insights),
            ("📋", "Reports",       self.show_reports),
            ("🔔", "Notifications", self.show_notifications),
            ("⚙️", "Settings",      getattr(self, "show_settings", None)),
            ("💾", "Backup",        getattr(self, "show_backup", None)),
            ("👤", "Profile",       self.show_profile),
        ]

            
        self._nav_hl = []
        for i, (icon, label, cmd) in enumerate(self._nav_data):
            y = 80 + i * 36
            hl  = sc.create_rectangle(0, y, SIDE_W, y + 32, fill=CB2, outline="", state="hidden")
            bar = sc.create_rectangle(0, y, 3, y + 32, fill=CY, outline="", state="hidden")
            ico = sc.create_text(30, y + 16, text=icon, font=("Segoe UI Emoji", 13), fill=TP, anchor="center")
            lbl = sc.create_text(58, y + 16, text=label, font=("Segoe UI", 10), fill=TS, anchor="w")
            area = sc.create_rectangle(0, y, SIDE_W, y + 32, fill="", outline="", tags=f"nv{i}")
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
            sc.create_rectangle(0, 0, SIDE_W, h, fill=SB, outline="", tags="gradient")
            sc.tag_lower("gradient")
            
            sc.delete("orb")
            if GLOBAL_STATE.get("theme", "dark") == "dark":
                sc.create_oval(-50, -50, 190, 190, fill="#071a12", outline="", tags="orb")
                sc.create_oval(50, h - 200, 290, h + 50, fill="#05150e", outline="", tags="orb")
            else:
                sc.create_oval(-50, -50, 190, 190, fill="#d5e3df", outline="", tags="orb")
                sc.create_oval(50, h - 200, 290, h + 50, fill="#cce0db", outline="", tags="orb")
            sc.tag_lower("orb")
            sc.tag_lower("gradient")
            
            sc.delete("right_border")
            sc.create_line(SIDE_W - 1, 0, SIDE_W - 1, h, fill=BD, width=1, tags="right_border")
            
            sc.coords("bottom_line", 16, h - 76, SIDE_W - 16, h - 76)
            sc.coords("bottom_user", SIDE_W // 2, h - 50)
            sc.coords("bottom_copy", SIDE_W // 2, h - 26)
            
            sc.delete("logo_line")
            sc.create_line(16, 82, SIDE_W - 16, 82, fill=BD, width=1, tags="logo_line")
            
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
        
        # Smart Search
        search_f = tk.Frame(hc, bg=EN, bd=0)
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(search_f, textvariable=self.search_var, bg=EN, fg=TP, font=("Segoe UI", 10), insertbackground=CY, relief="flat", bd=0, width=20)
        self.search_entry.pack(side="left", fill="both", expand=True, padx=(10, 5), pady=4)
        self.search_entry.insert(0, "Search...")
        
        def _on_focus_in(e):
            if self.search_entry.get() == "Search...":
                self.search_entry.delete(0, "end")
        def _on_focus_out(e):
            if not self.search_entry.get():
                self.search_entry.insert(0, "Search...")
        def _on_search(e):
            q = self.search_var.get().lower().strip()
            if q and q != "search...":
                self._show_search_results(q)
                
        self.search_entry.bind("<FocusIn>", _on_focus_in)
        self.search_entry.bind("<FocusOut>", _on_focus_out)
        self.search_entry.bind("<Return>", _on_search)
        self._search_window = hc.create_window(0, HEAD_H // 2, window=search_f, anchor="center", tags="search_bar")

        # Currency Selector
        self.currency_var = tk.StringVar(value=GLOBAL_STATE.get("display_currency", "INR"))
        self.curr_cb = ttk.Combobox(hc, textvariable=self.currency_var, values=SUPPORTED_CURRENCIES, 
                                    state="readonly", width=5, style="A.TCombobox")
        self.curr_cb.bind("<<ComboboxSelected>>", self._on_currency_change)
        self._curr_cb_window = hc.create_window(0, HEAD_H // 2, window=self.curr_cb, anchor="center", tags="curr_cb")
        
        # Month Selector
        import datetime
        sm = GLOBAL_STATE.get("selected_month", datetime.datetime.now().strftime("%Y-%m"))
        sm_lbl = datetime.datetime.strptime(sm, "%Y-%m").strftime("%B %Y")
        self._month_btn = hc.create_text(0, HEAD_H // 2, text=f"📅 {sm_lbl} ▼", font=("Segoe UI", 10, "bold"), fill=TP, anchor="center", tags="month_sel")
        hc.tag_bind("month_sel", "<Button-1>", lambda e: self._show_month_picker())
        hc.tag_bind("month_sel", "<Enter>",  lambda e: hc.config(cursor="hand2"))
        hc.tag_bind("month_sel", "<Leave>",  lambda e: hc.config(cursor=""))
        
        # Date & Bell (repositioned on resize)
        self._date_txt = hc.create_text(0, HEAD_H // 2, text=datetime.datetime.now().strftime("%a, %d %b %Y"), font=("Segoe UI", 10), fill=TS, anchor="center", tags="date")
        self._bell_icon = hc.create_text(0, HEAD_H // 2, text="🔔", font=("Segoe UI Emoji", 16), fill=TP, tags="bell")
        
        hc.tag_bind("bell", "<Button-1>", lambda e: self.show_notifications())
        hc.tag_bind("bell", "<Enter>",  lambda e: hc.config(cursor="hand2"))
        hc.tag_bind("bell", "<Leave>",  lambda e: hc.config(cursor=""))
        
        self._bell_x = WIN_W - SIDE_W - 60
        self._update_bell()

        def _on_hc_resize(e):
            w = e.width
            hc.delete("gradient")
            hc.create_rectangle(0, 0, w, HEAD_H, fill=BG, outline="", tags="gradient")
            hc.tag_lower("gradient")
            
            hc.delete("border")
            hc.create_line(0, HEAD_H - 1, w, HEAD_H - 1, fill=BD, width=1, tags="border")
            
            hc.coords("search_bar", w - 620, HEAD_H // 2)
            hc.coords("curr_cb", w - 460, HEAD_H // 2)
            hc.coords("month_sel", w - 320, HEAD_H // 2)
            hc.coords("date", w - 160, HEAD_H // 2)
            hc.coords("bell", w - 40, HEAD_H // 2)
            self._bell_x = w - 40
            self._update_bell()
            
        hc.bind("<Configure>", _on_hc_resize)

    def _on_currency_change(self, e=None):
        new_curr = self.currency_var.get()
        GLOBAL_STATE["display_currency"] = new_curr
        
        users = _ld_users()
        if self.email in users:
            users[self.email]["display_currency"] = new_curr
            _sv_users(users)
            
        # Refresh current page
        nav_map = {name: cmd for icon, name, cmd in self._nav_data}
        if self.active_nav in nav_map:
            nav_map[self.active_nav]()

    def _show_month_picker(self):
        dlg = tk.Toplevel(self.root)
        dlg.title("Select Month")
        dlg.geometry("300x260")
        dlg.configure(bg=BG)
        dlg.transient(self.root)
        dlg.grab_set()
        
        sel_m = GLOBAL_STATE.get("selected_month", datetime.now().strftime("%Y-%m"))
        y_str, m_str = sel_m.split('-')
        current_year = tk.IntVar(value=int(y_str))
        
        hf = tk.Frame(dlg, bg=BG)
        hf.pack(fill="x", pady=15)
        
        tk.Button(hf, text="<", bg=CB2, fg=TP, bd=0, width=3, cursor="hand2", command=lambda: current_year.set(current_year.get() - 1)).pack(side="left", padx=20)
        tk.Label(hf, textvariable=current_year, font=("Segoe UI", 12, "bold"), bg=BG, fg=TP).pack(side="left", expand=True)
        tk.Button(hf, text=">", bg=CB2, fg=TP, bd=0, width=3, cursor="hand2", command=lambda: current_year.set(current_year.get() + 1)).pack(side="right", padx=20)
        
        grid_f = tk.Frame(dlg, bg=BG)
        grid_f.pack(expand=True, fill="both", padx=15, pady=(0, 15))
        
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        
        def _apply_month(m_idx):
            new_m = f"{current_year.get()}-{m_idx:02d}"
            GLOBAL_STATE["selected_month"] = new_m
            import datetime
            d = datetime.datetime.strptime(new_m, "%Y-%m")
            self._hc.itemconfig("month_sel", text=f"📅 {d.strftime('%B %Y')} ▼")
            dlg.destroy()
            
            nav_map = {name: cmd for icon, name, cmd in self._nav_data}
            if self.active_nav in nav_map:
                nav_map[self.active_nav]()
                
        for i, m_name in enumerate(months):
            r, c = divmod(i, 4)
            btn = tk.Button(grid_f, text=m_name, font=("Segoe UI", 10), bg=CB, fg=TP, bd=0, cursor="hand2",
                            command=lambda idx=i+1: _apply_month(idx))
            btn.grid(row=r, column=c, padx=3, pady=3, sticky="nsew")
            grid_f.grid_columnconfigure(c, weight=1)
            grid_f.grid_rowconfigure(r, weight=1)

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

    def _show_search_results(self, query):
        dlg = tk.Toplevel(self.root)
        dlg.title(f"Search Results: '{query}'")
        dlg.geometry("700x500")
        dlg.configure(bg=BG)
        dlg.transient(self.root)
        dlg.grab_set()
        
        tk.Label(dlg, text=f"Search Results for '{query}'", font=("Segoe UI", 16, "bold"), bg=BG, fg=TP).pack(pady=(15, 5))
        
        f = tk.Frame(dlg, bg=CB)
        f.pack(fill="both", expand=True, padx=20, pady=15)
        
        tv = ttk.Treeview(f, columns=("Type", "Name/Desc", "Date/Detail", "Amount"), show="headings", style="D.Treeview", height=15)
        tv.heading("Type", text="Type"); tv.column("Type", width=100, anchor="w")
        tv.heading("Name/Desc", text="Name/Desc"); tv.column("Name/Desc", width=250, anchor="w")
        tv.heading("Date/Detail", text="Date/Detail"); tv.column("Date/Detail", width=150, anchor="w")
        tv.heading("Amount", text="Amount"); tv.column("Amount", width=100, anchor="w")
        
        sb = ttk.Scrollbar(f, orient="vertical", command=tv.yview)
        tv.configure(yscrollcommand=sb.set)
        tv.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        
        results = []
        # Search transactions
        for t in _ld("transactions"):
            if query in t.get("desc", "").lower() or query in t.get("category", "").lower():
                results.append(("Transaction", t.get("desc", ""), t.get("date", ""), fmt_amt(t.get("amount", 0), t.get("currency", "INR"))))
        
        # Search Budgets
        for b in get_all_budgets():
            if query in b.get("category", "").lower():
                results.append(("Budget", b.get("category", ""), b.get("month", ""), fmt_amt(b.get("amount", 0), b.get("currency", "INR"))))
                
        # Search Goals
        for g in _ld("goals"):
            if query in g.get("name", "").lower():
                results.append(("Goal", g.get("name", ""), g.get("deadline", ""), fmt_disp(g.get("target", 0))))
                
        # Search Investments
        for i in _ld("investments"):
            if query in i.get("name", "").lower() or query in i.get("symbol", "").lower():
                results.append(("Investment", i.get("name", ""), i.get("type", ""), fmt_amt(i.get("qty", 0) * i.get("buy_price", 0), i.get("currency", "INR"))))
                
        for idx, r in enumerate(results):
            tv.insert("", "end", values=r, tags=("odd" if idx % 2 else "even",))
            
        tv.tag_configure("odd", background="#1d1d1f")
        tv.tag_configure("even", background=CB)
        
        tk.Button(dlg, text="Close", font=("Segoe UI", 10), bg=BD, fg=TP, bd=0, cursor="hand2", command=dlg.destroy).pack(pady=(0, 15))

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
        tv.tag_configure("income", foreground=GR)
        tv.tag_configure("expense", foreground=RE)
        return f, tv

    def _tv_fill(self, tv, rows):
        """rows = list of tuples; first element is the iid, rest are values. Optionally last element can be a tag tuple or tag string if row length exceeds columns+1."""
        tv.delete(*tv.get_children())
        num_cols = len(tv["columns"])
        for i, row in enumerate(rows):
            item_id = str(row[0]) if not tv.exists(str(row[0])) else None
            # Check if custom tags were appended at end of row tuple
            row_tags = ["odd" if i % 2 else "even"]
            if len(row) > num_cols + 1:
                extra_tag = row[-1]
                if isinstance(extra_tag, (list, tuple)):
                    row_tags.extend(extra_tag)
                elif isinstance(extra_tag, str):
                    row_tags.append(extra_tag)
                vals = row[1:-1]
            else:
                vals = row[1:]
            
            if item_id:
                tv.insert("", "end", iid=item_id, values=vals, tags=tuple(row_tags))
            else:
                tv.insert("", "end", values=vals, tags=tuple(row_tags))

    def _dialog(self, title, fields, on_save, defaults=None):
        """Generic modal dialog — fully scrollable with fixed button bar."""
        dlg = tk.Toplevel(self.root)
        dlg.title(title)
        dlg.configure(bg=CB)
        dlg.grab_set()
        dlg.resizable(False, True)
        DW = 460
        # Fixed height: 64px header + 80px buttons + up to 6 fields at 74px each;
        # cap at 640 so it always fits on screen while still scrolling when needed.
        DH = min(640, 64 + len(fields) * 74 + 80)
        DH = max(DH, 280)   # minimum usable height
        dlg.geometry(f"{DW}x{DH}")
        dlg.update_idletasks()
        x = (dlg.winfo_screenwidth() - DW) // 2
        y = max(40, (dlg.winfo_screenheight() - DH) // 2)
        dlg.geometry(f"{DW}x{DH}+{x}+{y}")

        # ── Top accent + title (fixed, never scrolls) ──────────────────────────
        tk.Frame(dlg, bg=AC, height=3).pack(fill="x")
        tk.Label(dlg, text=title, font=("Segoe UI Semibold", 13),
                 bg=CB, fg=TP).pack(padx=20, pady=(14, 2), anchor="w")
        tk.Frame(dlg, bg=BD, height=1).pack(fill="x", padx=20, pady=(0, 4))

        # ── Button row (packed at bottom BEFORE the canvas so it never clips) ──
        brow = tk.Frame(dlg, bg=CB)
        brow.pack(fill="x", padx=20, pady=12, side="bottom")
        tk.Frame(dlg, bg=BD, height=1).pack(fill="x", padx=20, side="bottom")

        # ── Scrollable field area ───────────────────────────────────────────────
        sc_cont = tk.Frame(dlg, bg=CB)
        sc_cont.pack(fill="both", expand=True)

        cv = tk.Canvas(sc_cont, bg=CB, bd=0, highlightthickness=0)
        sb = ttk.Scrollbar(sc_cont, orient="vertical", command=cv.yview,
                           style="Vertical.TScrollbar")
        cv.configure(yscrollcommand=sb.set)
        cv.pack(side="left", fill="both", expand=True)

        body = tk.Frame(cv, bg=CB)
        bw = cv.create_window(0, 0, anchor="nw", window=body)

        sb_shown = [False]

        def _show_sb():
            cv.update_idletasks()
            bbox = cv.bbox("all")
            if bbox and bbox[3] > cv.winfo_height():
                if not sb_shown[0]:
                    sb.pack(side="right", fill="y")
                    sb_shown[0] = True
            else:
                if sb_shown[0]:
                    sb.pack_forget()
                    sb_shown[0] = False

        def _cfg(e):
            cv.configure(scrollregion=cv.bbox("all"))
            sc_cont.after_idle(_show_sb)

        def _resize(e):
            cv.itemconfig(bw, width=e.width)
            sc_cont.after_idle(_show_sb)

        body.bind("<Configure>", _cfg)
        cv.bind("<Configure>", _resize)
        cv.bind("<MouseWheel>", lambda e: cv.yview_scroll(int(-1 * (e.delta / 40)), "units"))

        # ── Build fields ────────────────────────────────────────────────────────
        widgets = {}
        for fd in fields:
            tk.Label(body, text=fd["lbl"], font=("Segoe UI Semibold", 9),
                     bg=CB, fg=TS).pack(padx=20, pady=(10, 2), anchor="w")
            if fd["type"] == "combo":
                var = tk.StringVar()
                opts = fd.get("opts", [])
                default_val = (defaults or {}).get(fd["k"], opts[0] if opts else "")
                var.set(default_val)
                cb = ttk.Combobox(body, textvariable=var, values=opts,
                                  font=("Segoe UI Light", 11), state="readonly",
                                  style="A.TCombobox")
                cb.pack(fill="x", padx=20, ipady=5, pady=(0, 4))
                widgets[fd["k"]] = var
            else:
                bdr = tk.Frame(body, bg=BD)
                bdr.pack(fill="x", padx=20, pady=(0, 4))
                inn = tk.Frame(bdr, bg=EN)
                inn.pack(padx=1, pady=1, fill="x")
                # Support optional show="*" for password fields
                show_char = fd.get("show", "")
                e = tk.Entry(inn, font=("Segoe UI Light", 11), bg=EN, fg=TP,
                             insertbackground=CY, relief="flat", bd=0,
                             show=show_char)
                e.pack(fill="x", ipady=8, padx=10)
                if defaults and fd["k"] in defaults:
                    e.insert(0, str(defaults[fd["k"]]))
                e.bind("<FocusIn>",  lambda ev, b=bdr: b.config(bg=CY))
                e.bind("<FocusOut>", lambda ev, b=bdr: b.config(bg=BD))
                widgets[fd["k"]] = e

        # Spacer at bottom of field list so last field isn't cramped
        tk.Frame(body, bg=CB, height=8).pack()

        # ── Button callbacks ────────────────────────────────────────────────────
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
        dt = vals.get("date", default_date())
        recs.append({"id": mk_id(), "type": ttype,
                     "date": dt,
                     "month": dt[:7],
                     "desc": vals["desc"],
                     "category": vals.get("category", ""),
                     "currency": vals.get("currency", GLOBAL_STATE.get("display_currency", "INR")),
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
                dt = vals["date"]
                r.update({"date": dt, "month": dt[:7], "desc": vals["desc"],
                           "category": vals["category"],
                           "currency": vals.get("currency", r.get("currency", GLOBAL_STATE.get("display_currency", "INR"))),
                           "amount": amt,
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
                     "currency": vals.get("currency", GLOBAL_STATE.get("display_currency", "INR")),
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
                           "type": vals["type"],
                           "currency": vals.get("currency", i.get("currency", GLOBAL_STATE.get("display_currency", "INR"))),
                           "qty": qty,
                           "buy_price": bp, "current_price": cp,
                           "notes": vals.get("notes", "")})
        _sv("investments", invs); dlg.destroy(); self.show_investments()

    def _set_budget(self, cat, vals, dlg):
        try:   amt = float(vals["amount"])
        except: return messagebox.showerror("Error", "Amount must be a number.")
        save_budget_for_month(curr_m(), cat, amt, vals.get("currency", "INR"))
        dlg.destroy(); self.show_budget()

    def _save_goal_cb(self, vals, dlg):
        try:   tgt = float(vals["target"]); saved = float(vals["saved"])
        except: return messagebox.showerror("Error", "Target and saved amounts must be numbers.")
        if not vals.get("name", "").strip():
            return messagebox.showerror("Error", "Goal name is required.")
        goals = _ld("goals")
        goals.append({"id": mk_id(), "name": vals["name"],
                      "currency": vals.get("currency", GLOBAL_STATE.get("display_currency", "INR")),
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
                           "currency": vals.get("currency", g.get("currency", GLOBAL_STATE.get("display_currency", "INR"))),
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
        trans = _ld("transactions"); budgets = get_budgets_for_month(curr_m()); cm = curr_m()
        dc = GLOBAL_STATE["display_currency"]
        spent_by = defaultdict(float)
        for r in trans:
            if r["type"] == "expense" and r["date"].startswith(cm):
                spent_by[r["category"]] += convert_currency(r["amount"], r.get("currency", "INR"), dc)
        ns = _ld("notifications")
        existing = {n["title"] for n in ns}
        for cat, b_val in budgets.items():
            if isinstance(b_val, (int, float)): b_val = {"amount": float(b_val), "currency": "INR"}
            bgt = convert_currency(b_val["amount"], b_val["currency"], dc)
            spent = spent_by.get(cat, 0); pct = spent / bgt if bgt else 0
            title = f"Budget Alert: {cat}"
            if pct >= 0.9 and title not in existing:
                ns.append({"id": mk_id(), "type": "warning", "title": title,
                            "msg": f"{cat} spending at {int(pct*100)}% of {fmt_disp(bgt)} budget",
                            "read": False, "ts": now_ts()})
        _sv("notifications", ns); self._update_bell()

    # ── Calculation & Drawing Helpers ─────────────────────────────────────────────
    def _calc_health(self):
        trans   = _ld("transactions"); budgets = get_budgets_for_month(curr_m())
        goals   = _ld("goals");        invs    = _ld("investments"); cm = curr_m()
        dc = GLOBAL_STATE["display_currency"]
        mi = sum(convert_currency(r["amount"], r.get("currency", "INR"), dc) for r in trans if r["type"] == "income"  and r["date"].startswith(cm))
        me = sum(convert_currency(r["amount"], r.get("currency", "INR"), dc) for r in trans if r["type"] == "expense" and r["date"].startswith(cm))
        sr     = (mi - me) / mi if mi > 0 else 0
        pts_sr = min(30.0, max(0.0, sr * 150))
        spent_by = defaultdict(float)
        for r in trans:
            if r["type"] == "expense" and r["date"].startswith(cm):
                spent_by[r["category"]] += convert_currency(r["amount"], r.get("currency", "INR"), dc)
        cats_ok = 0
        for c, b_val in budgets.items():
            if isinstance(b_val, (int, float)): b_val = {"amount": float(b_val), "currency": "INR"}
            b = convert_currency(b_val["amount"], b_val["currency"], dc)
            if spent_by.get(c, 0) <= b: cats_ok += 1
        pts_bgt  = (cats_ok / len(budgets) * 25) if budgets else 0
        if goals:
            avg_p = sum(min(1.0, float(g["saved"]) / float(g["target"])) for g in goals if float(g["target"]) > 0) / len(goals)
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
        trans = _ld("transactions"); budgets = get_budgets_for_month(curr_m())
        goals = _ld("goals");        invs    = _ld("investments"); cm = curr_m()
        insights = []
        dc = GLOBAL_STATE["display_currency"]
        mi = sum(convert_currency(r["amount"], r.get("currency", "INR"), dc) for r in trans if r["type"] == "income"  and r["date"].startswith(cm))
        me = sum(convert_currency(r["amount"], r.get("currency", "INR"), dc) for r in trans if r["type"] == "expense" and r["date"].startswith(cm))
        
        # Savings Rate Insight
        if mi > 0:
            sr = (mi - me) / mi * 100
            if sr >= 20:
                insights.append({"icon": "✅", "title": "Great Savings Rate!",
                    "msg": f"You're saving {sr:.1f}% of your income this month — above the 20% target.",
                    "tip": "Keep it up! Invest your surplus in SIPs or index funds.",
                    "bg": "#1c2c1c", "border": GR, "priority": "Positive"})
            elif sr > 0:
                insights.append({"icon": "⚠️", "title": "Savings Rate Needs Work",
                    "msg": f"Savings rate is {sr:.1f}% this month. Target is 20% ({fmt_disp(mi*0.2)}).",
                    "tip": "Try the 50/30/20 rule: 50% needs, 30% wants, 20% savings.",
                    "bg": "#2c2a1c", "border": GO, "priority": "Warning"})
            else:
                insights.append({"icon": "🔴", "title": "Spending Exceeds Income!",
                    "msg": f"Spent {fmt_disp(me)} vs income of {fmt_disp(mi)} — deficit of {fmt_disp(me - mi)}.",
                    "tip": "Review discretionary spending and cut non-essentials immediately.",
                    "bg": "#2c1c1c", "border": RE, "priority": "Critical"})
                    
        # Expense Analysis
        spent_by = defaultdict(float)
        prev_spent = defaultdict(float)
        y, m = map(int, cm.split('-'))
        pm = f"{y-1}-12" if m == 1 else f"{y}-{m-1:02d}"
        
        for r in trans:
            if r["type"] == "expense":
                amt = convert_currency(r["amount"], r.get("currency", "INR"), dc)
                if r["date"].startswith(cm):
                    spent_by[r["category"]] += amt
                elif r["date"].startswith(pm):
                    prev_spent[r["category"]] += amt
                    
        if spent_by:
            top_cat = max(spent_by, key=spent_by.get)
            top_amt = spent_by[top_cat]
            b_val = budgets.get(top_cat, {"amount": 0, "currency": "INR"})
            if isinstance(b_val, (int, float)): b_val = {"amount": float(b_val), "currency": "INR"}
            bgt = convert_currency(b_val["amount"], b_val["currency"], dc)
            pct_b   = top_amt / bgt * 100 if bgt else 0
            insights.append({"icon": "📊", "title": f"Top Expense: {top_cat}",
                "msg": f"Highest spending: {top_cat} at {fmt_disp(top_amt)} ({pct_b:.0f}% of budget).",
                "tip": f"Look for small ways to reduce {top_cat} spending next month.",
                "bg": "#1c222c", "border": AC, "priority": "Normal"})
                
        # Month-over-month spending increases
        for cat, amt in spent_by.items():
            if cat in prev_spent and prev_spent[cat] > 0:
                pct_change = (amt - prev_spent[cat]) / prev_spent[cat] * 100
                if pct_change > 15: # 15% increase threshold
                    insights.append({"icon": "📈", "title": f"Spending Spike: {cat}",
                        "msg": f"{cat} spending increased by {pct_change:.1f}% compared to last month.",
                        "tip": f"Review your {cat.lower()} expenses to ensure this spike was planned.",
                        "bg": "#2c1c1c", "border": OR, "priority": "Warning"})
                        
        # Budget Alerts
        for cat, b_val in budgets.items():
            if isinstance(b_val, (int, float)): b_val = {"amount": float(b_val), "currency": "INR"}
            bgt = convert_currency(b_val["amount"], b_val["currency"], dc)
            spent = spent_by.get(cat, 0); pct = spent / bgt if bgt else 0
            if pct > 0.9:
                insights.append({"icon": "⚠️", "title": f"Budget Alert: {cat}",
                    "msg": f"Used {int(pct*100)}% of {cat} budget. Spent {fmt_disp(spent)} of {fmt_disp(bgt)}.",
                    "tip": "Pause non-essential spending in this category for the rest of the month.",
                    "bg": "#2c2a1c", "border": GO, "priority": "Critical" if pct > 1.0 else "Warning"})
                    
        # Goals Progress
        for g in goals[:2]:
            tgt = convert_currency(float(g["target"]), g.get("currency", "INR"), dc)
            saved = convert_currency(float(g["saved"]), g.get("currency", "INR"), dc)
            pct = saved / tgt * 100 if tgt else 0
            insights.append({"icon": g.get("icon", "🎯"), "title": f"Goal: {g['name']}",
                "msg": f"{g['name']} is {pct:.0f}% complete. {fmt_disp(saved)} of {fmt_disp(tgt)} saved.",
                "tip": f"Need {fmt_disp(tgt-saved)} more by {g.get('deadline', 'target date')}.",
                "bg": "#1c2c2c", "border": CY, "priority": "Positive"})
                
        # Investments Analysis
        if invs:
            pf_val  = sum(convert_currency(i["qty"] * i["current_price"], i.get("currency", "INR"), dc) for i in invs)
            pf_cost = sum(convert_currency(i["qty"] * i["buy_price"], i.get("currency", "INR"), dc) for i in invs)
            
            # Concentration Risk
            asset_types = defaultdict(float)
            for i in invs:
                asset_types[i["type"]] += convert_currency(i["qty"] * i["current_price"], i.get("currency", "INR"), dc)
            
            if pf_val > 0:
                for a_type, val in asset_types.items():
                    conc = val / pf_val * 100
                    if conc > 40: # 40% concentration threshold
                        insights.append({"icon": "⚖️", "title": "Portfolio Concentration",
                            "msg": f"Your portfolio is heavily concentrated in {a_type} ({conc:.0f}%).",
                            "tip": "Diversify your investments across different asset classes to reduce risk.",
                            "bg": "#2c2a1c", "border": GO, "priority": "Warning"})
                        break
                        
            # Performance
            pl      = pf_val - pf_cost; plp = pl / pf_cost * 100 if pf_cost else 0
            direction = "up" if pl >= 0 else "down"
            clr  = GR if pl >= 0 else RE; bg = "#1c2c1c" if pl >= 0 else "#2c1c1c"
            icon = "📈" if pl >= 0 else "📉"
            insights.append({"icon": icon, "title": "Portfolio Performance",
                "msg": f"Portfolio is {direction} {fmt_disp(abs(pl))} ({plp:+.1f}%) overall. Total value: {fmt_disp(pf_val)}.",
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

        dc_sym = get_currency_symbol(GLOBAL_STATE.get("display_currency", "INR"))
        for i in range(5):
            y = pad_t + int(ch * (1 - i / 4))
            canvas.create_line(pad_l, y, W - pad_r, y, fill=CB2, dash=(4, 4))
            val = int(max_val * i / 4)
            lbl = f"{dc_sym}{val//1000}k" if val >= 1000 else f"{dc_sym}{val}"
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
