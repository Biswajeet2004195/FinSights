import tkinter as tk
from datetime import datetime
from collections import defaultdict
from config import *
from base_dashboard import BaseDashboard

class OverviewMixin(BaseDashboard):
    def show_overview(self):
        self._clear()
        self._set_nav("Overview")
        self._set_title("Overview")
        pg = self._scrollable(self._cf)

        # ── Welcome banner ───────────────────────────────────────────────────────
        banner = ctk.CTkFrame(pg, fg_color=CB2, corner_radius=10)
        banner.pack(fill="x", padx=20, pady=(16, 8))
        ctk.CTkFrame(banner, fg_color=AC, width=4, corner_radius=10).pack(side="left", fill="y")
        bi = ctk.CTkFrame(banner, fg_color=CB2, corner_radius=10)
        bi.pack(side="left", fill="both", expand=True, padx=14, pady=14)
        tk.Label(bi, text=f"Welcome back, {self.username}! 👋",
                 font=("Segoe UI Semibold", 16), bg=CB2, fg=TP).pack(anchor="w")
        tk.Label(bi,
                 text=f"{datetime.now().strftime('%B %Y')}  •  Click any module below to dive in",
                 font=("Segoe UI Light", 10), bg=CB2, fg=TS).pack(anchor="w", pady=(2, 0))

        # ── KPI row ──────────────────────────────────────────────────────────────
        trans = _ld("transactions"); cm = curr_m()
        dc = GLOBAL_STATE["display_currency"]
        mi = sum(convert_currency(r["amount"], r.get("currency", "INR"), dc) for r in trans if r["type"] == "income"  and r["date"].startswith(cm))
        me = sum(convert_currency(r["amount"], r.get("currency", "INR"), dc) for r in trans if r["type"] == "expense" and r["date"].startswith(cm))
        ms = mi - me
        invs = _ld("investments")
        pv = sum(convert_currency(i["qty"] * i["current_price"], i.get("currency", "INR"), dc) for i in invs)

        krow = ctk.CTkFrame(pg, fg_color=BG, corner_radius=10)
        krow.pack(fill="x", padx=20, pady=(0, 10))
        for title, val, sub, clr, ico, cmd in [
            ("Total Income",    fmt_disp(mi), "This month", GR, "💰", self.show_income),
            ("Total Expenses",  fmt_disp(me), "This month", RE, "💸", self.show_expenses),
            ("Net Savings",     fmt_disp(ms), "This month", CY, "💎", self.show_budget),
            ("Portfolio Value", fmt_disp(pv), "All investments", GO, "📈", self.show_investments),
        ]:
            k = self._kpi(krow, title, val, sub, color=clr, icon=ico, cmd=cmd)
            k.pack(side="left", fill="both", expand=True, padx=(0, 10), ipady=4)

        # ── Quick Access grid ────────────────────────────────────────────────────
        ctk.CTkFrame(pg, fg_color=BD, height=1, corner_radius=10).pack(fill="x", padx=20, pady=(4, 12))
        hdr_row = ctk.CTkFrame(pg, fg_color=BG, corner_radius=10); hdr_row.pack(fill="x", padx=20, pady=(0, 10))
        tk.Label(hdr_row, text="⚡  Quick Access",
                 font=("Segoe UI Semibold", 13), bg=BG, fg=TP).pack(side="left")
        tk.Label(hdr_row, text="Click any module to open it",
                 font=("Segoe UI Light", 9), bg=BG, fg=TH).pack(side="left", padx=(10, 0), pady=2)

        quick_items = [
            ("💰", "Income",       "Add & track all income sources",   GR,  self.show_income),
            ("💸", "Expenses",     "Log and categorise your spending",  RE,  self.show_expenses),
            ("📊", "Budget",       "Set & monitor spending limits",     CY,  self.show_budget),
            ("📈", "Investments",  "Track your portfolio & P&L",        GO,  self.show_investments),
            ("🎯", "Goals",        "Plan and reach savings goals",      AC,  self.show_goals),
            ("🤖", "AI Insights",  "Smart spending analysis",           PR,  self.show_insights),
            ("❤️", "Health Score", "Your financial wellness rating",    PK,  self.show_health),
            ("📋", "Reports",      "View trends & export to CSV",       OR,  self.show_reports),
        ]
        for i in range(0, len(quick_items), 4):
            qrow = ctk.CTkFrame(pg, fg_color=BG, corner_radius=10)
            qrow.pack(fill="x", padx=20, pady=(0, 8))
            for icon, name, desc, clr, cmd in quick_items[i:i + 4]:
                self._quick_card(qrow, icon, name, desc, clr, cmd)

        # ── At a Glance ──────────────────────────────────────────────────────────
        ctk.CTkFrame(pg, fg_color=BD, height=1, corner_radius=10).pack(fill="x", padx=20, pady=(4, 12))
        tk.Label(pg, text="📊  At a Glance", font=("Segoe UI Semibold", 13),
                 bg=BG, fg=TP).pack(anchor="w", padx=20, pady=(0, 8))
        mid = ctk.CTkFrame(pg, fg_color=BG, corner_radius=10)
        mid.pack(fill="x", padx=20, pady=(0, 10))

        # Health Score mini
        hf = ctk.CTkFrame(mid, fg_color=BD, corner_radius=10)
        hf.pack(side="left", fill="both", expand=True, padx=(0, 8))
        hfi = ctk.CTkFrame(hf, fg_color=CB, corner_radius=10); hfi.pack(padx=1, pady=1, fill="both", expand=True)
        ctk.CTkFrame(hfi, fg_color=AC, height=3, corner_radius=10).pack(fill="x")
        tk.Label(hfi, text="❤️  Financial Health Score", font=("Segoe UI Semibold", 11),
                 bg=CB, fg=TP).pack(anchor="w", padx=14, pady=(10, 0))
        score, breakdown = self._calc_health()
        gc = tk.Canvas(hfi, width=220, height=160, bg=CB, bd=0, highlightthickness=0)
        gc.pack(pady=(4, 0))
        self._draw_gauge(gc, 110, 90, 72, score)
        for cat, (pts, max_pts) in breakdown.items():
            pct2 = pts / max_pts if max_pts else 0
            rw = ctk.CTkFrame(hfi, fg_color=CB, corner_radius=10); rw.pack(fill="x", padx=14, pady=2)
            tk.Label(rw, text=cat[:16], font=("Segoe UI Light", 8), bg=CB, fg=TS,
                     width=18, anchor="w").pack(side="left")
            bc = tk.Canvas(rw, width=100, height=10, bg=CB2, bd=0, highlightthickness=0)
            bc.pack(side="left", padx=4)
            clr2 = GR if pct2 > 0.7 else GO if pct2 > 0.4 else RE
            bc.create_rectangle(0, 0, int(100 * pct2), 10, fill=clr2, outline="")
            tk.Label(rw, text=f"{int(pts)}/{max_pts}", font=("Segoe UI", 8),
                     bg=CB, fg=TH).pack(side="left")
        hl = tk.Label(hfi, text="View full score →", font=("Segoe UI Light", 8, "italic"),
                      bg=CB, fg=CY, cursor="hand2")
        hl.pack(padx=14, pady=(4, 10), anchor="w")
        hl.bind("<Button-1>", lambda e: self.show_health())

        # Budget Status
        bf = ctk.CTkFrame(mid, fg_color=BD, corner_radius=10)
        bf.pack(side="left", fill="both", expand=True, padx=(0, 8))
        bfi = ctk.CTkFrame(bf, fg_color=CB, corner_radius=10); bfi.pack(padx=1, pady=1, fill="both", expand=True)
        ctk.CTkFrame(bfi, fg_color=CY, height=3, corner_radius=10).pack(fill="x")
        tk.Label(bfi, text="📊  Budget Status", font=("Segoe UI Semibold", 11),
                 bg=CB, fg=TP).pack(anchor="w", padx=14, pady=(10, 4))
        budgets = get_budgets_for_month(curr_m())
        spent_by = defaultdict(float)
        for r in trans:
            if r["type"] == "expense" and r["date"].startswith(cm):
                spent_by[r["category"]] += convert_currency(r["amount"], r.get("currency", "INR"), dc)
        for cat in EXPENSE_CATS[:6]:
            b_val = budgets.get(cat, {"amount": 5000.0, "currency": "INR"})
            bgt = convert_currency(b_val["amount"], b_val["currency"], dc)
            spent = spent_by.get(cat, 0)
            pct3 = min(1, spent / bgt) if bgt else 0
            clr3 = GR if pct3 < 0.7 else GO if pct3 < 0.9 else RE
            rw = ctk.CTkFrame(bfi, fg_color=CB, corner_radius=10); rw.pack(fill="x", padx=14, pady=3)
            tk.Label(rw, text=cat[:14], font=("Segoe UI Light", 9), bg=CB, fg=TS,
                     width=14, anchor="w").pack(side="left")
            bc = tk.Canvas(rw, width=120, height=10, bg=CB2, bd=0, highlightthickness=0)
            bc.pack(side="left", padx=4)
            bc.create_rectangle(0, 0, int(120 * pct3), 10, fill=clr3, outline="")
            tk.Label(rw, text=f"{int(pct3*100)}%", font=("Segoe UI", 8),
                     bg=CB, fg=TH, width=4).pack(side="left")
        bl = tk.Label(bfi, text="Manage budgets →", font=("Segoe UI Light", 8, "italic"),
                      bg=CB, fg=CY, cursor="hand2")
        bl.pack(padx=14, pady=(4, 10), anchor="w")
        bl.bind("<Button-1>", lambda e: self.show_budget())

        # Recent Transactions
        rf = ctk.CTkFrame(mid, fg_color=BD, corner_radius=10)
        rf.pack(side="left", fill="both", expand=True)
        rfi = ctk.CTkFrame(rf, fg_color=CB, corner_radius=10); rfi.pack(padx=1, pady=1, fill="both", expand=True)
        ctk.CTkFrame(rfi, fg_color=GO, height=3, corner_radius=10).pack(fill="x")
        tk.Label(rfi, text="🕐  Recent Transactions", font=("Segoe UI Semibold", 11),
                 bg=CB, fg=TP).pack(anchor="w", padx=14, pady=(10, 4))
        recent = sorted(trans, key=lambda r: r["date"], reverse=True)[:9]
        if recent:
            for r in recent:
                rw = ctk.CTkFrame(rfi, fg_color=CB, corner_radius=10); rw.pack(fill="x", padx=10, pady=2)
                clr4 = GR if r["type"] == "income" else RE
                sign = "+" if r["type"] == "income" else "−"
                tk.Label(rw, text=r["date"][5:], font=("Segoe UI", 8),
                         bg=CB, fg=TH, width=5).pack(side="left")
                tk.Label(rw, text=r["desc"][:20], font=("Segoe UI", 9),
                         bg=CB, fg=TS).pack(side="left", padx=4)
                converted_amt = convert_currency(r["amount"], r.get("currency", "INR"), dc)
                tk.Label(rw, text=f"{sign}{fmt_disp(converted_amt)}",
                         font=("Segoe UI", 9, "bold"), bg=CB, fg=clr4
                         ).pack(side="right", padx=4)
        else:
            ctk.CTkFrame(rfi, fg_color=CB, height=16, corner_radius=10).pack()
            tk.Label(rfi, text="No transactions yet", font=("Segoe UI", 10),
                     bg=CB, fg=TH).pack()
            tk.Label(rfi,
                     text="Use  💰 Income  or  💸 Expenses\nto add your first entry",
                     font=("Segoe UI", 9), bg=CB, fg=TH, justify="center").pack(pady=(4, 0))
        ctk.CTkFrame(rfi, fg_color=CB, height=6, corner_radius=10).pack()

        # ── Financial Forecast ───────────────────────────────────────────────────
        ctk.CTkFrame(pg, fg_color=BD, height=1, corner_radius=10).pack(fill="x", padx=20, pady=(4, 12))
        tk.Label(pg, text="🔮  Financial Forecast", font=("Segoe UI Semibold", 13),
                 bg=BG, fg=TP).pack(anchor="w", padx=20, pady=(0, 8))
        
        ff = ctk.CTkFrame(pg, fg_color=BG, corner_radius=10)
        ff.pack(fill="x", padx=20, pady=(0, 10))

        today_dt = datetime.now()
        import calendar
        _, last_day = calendar.monthrange(today_dt.year, today_dt.month)
        current_day = today_dt.day
        remaining_days = last_day - current_day
        
        if current_day > 0 and me > 0:
            avg_daily = me / current_day
            forecast_remaining = avg_daily * remaining_days
            total_expected_expenses = me + forecast_remaining
            expected_savings = mi - total_expected_expenses
            confidence = min(99, int((current_day / last_day) * 100))
        else:
            total_expected_expenses = 0
            expected_savings = mi
            confidence = 0
            
        for title, val, sub, clr, ico in [
            ("Forecasted Expenses", fmt_disp(total_expected_expenses), f"By month end", OR, "📈"),
            ("Expected Savings", fmt_disp(expected_savings), f"By month end", BL, "💎"),
            ("Forecast Confidence", f"{confidence}%", f"Based on {current_day} days data", PR, "🎯"),
        ]:
            k = self._kpi(ff, title, val, sub, color=clr, icon=ico)
            k.pack(side="left", fill="both", expand=True, padx=(0, 10) if title != "Forecast Confidence" else 0, ipady=4)

        # ── Quick AI Insights ────────────────────────────────────────────────────
        ctk.CTkFrame(pg, fg_color=BD, height=1, corner_radius=10).pack(fill="x", padx=20, pady=(4, 10))
        insights = self._gen_insights()
        if insights:
            tk.Label(pg, text="🤖  Quick AI Insights", font=("Segoe UI", 12, "bold"),
                     bg=BG, fg=TP).pack(anchor="w", padx=20, pady=(0, 8))
            for ins in insights[:3]:
                ic = ctk.CTkFrame(pg, fg_color=BD, corner_radius=10); ic.pack(fill="x", padx=20, pady=3)
                ici = ctk.CTkFrame(ic, fg_color=ins["bg"], corner_radius=10); ici.pack(padx=1, pady=1, fill="x")
                rw = ctk.CTkFrame(ici, fg_color=ins["bg"], corner_radius=10); rw.pack(fill="x", padx=14, pady=8)
                tk.Label(rw, text=ins["icon"], font=("Segoe UI Emoji", 14),
                         bg=ins["bg"], fg=TP).pack(side="left", padx=(0, 10))
                ri = ctk.CTkFrame(rw, fg_color=ins["bg"], corner_radius=10); ri.pack(side="left", fill="both", expand=True)
                tk.Label(ri, text=ins["title"], font=("Segoe UI", 10, "bold"),
                         bg=ins["bg"], fg=TP).pack(anchor="w")
                tk.Label(ri, text=ins["msg"], font=("Segoe UI", 9),
                         bg=ins["bg"], fg=TS, wraplength=900, justify="left").pack(anchor="w")
        else:
            emp = ctk.CTkFrame(pg, fg_color=BD, corner_radius=10); emp.pack(fill="x", padx=20, pady=4)
            empi = ctk.CTkFrame(emp, fg_color=CB2, corner_radius=10); empi.pack(padx=1, pady=1, fill="x")
            rw = ctk.CTkFrame(empi, fg_color=CB2, corner_radius=10); rw.pack(fill="x", padx=16, pady=14)
            tk.Label(rw, text="🤖", font=("Segoe UI Emoji", 20), bg=CB2).pack(side="left", padx=(0, 12))
            ri = ctk.CTkFrame(rw, fg_color=CB2, corner_radius=10); ri.pack(side="left")
            tk.Label(ri, text="AI Insights will appear here",
                     font=("Segoe UI", 11, "bold"), bg=CB2, fg=TP).pack(anchor="w")
            tk.Label(ri, text="Add income & expenses to get personalised financial analysis",
                     font=("Segoe UI", 9), bg=CB2, fg=TS).pack(anchor="w", pady=(2, 0))
        ctk.CTkFrame(pg, fg_color=BG, height=20, corner_radius=10).pack()
