import tkinter as tk
from tkinter import messagebox
from collections import defaultdict
from config import *
from base_dashboard import BaseDashboard

class BudgetMixin(BaseDashboard):
    def show_budget(self):
        self._clear(); self._set_nav("Budget"); self._set_title("Budget")
        pg = self._scrollable(self._cf)
        self._sec(pg, "📊 Monthly Budget Tracker", "Set limits and monitor spending per category")

        trans = _ld("transactions"); cm = curr_m()
        budgets = _ldd("budgets")
        
        # Initialize default categories if budget data is empty
        if not budgets:
            budgets = {
                "Food": 5000.0,
                "Transportation": 3000.0,
                "Shopping": 4000.0,
                "Bills & Utilities": 6000.0,
                "Entertainment": 2000.0,
                "Healthcare": 3000.0,
                "Education": 5000.0,
                "Travel": 3000.0,
                "Savings": 10000.0,
                "Miscellaneous": 2000.0
            }
            _sv("budgets", budgets)
        spent_by = defaultdict(float)
        for r in trans:
            if r["type"] == "expense" and r["date"].startswith(cm):
                spent_by[r["category"]] += r["amount"]

        cats = list(budgets.keys())
        total_budget = sum(budgets.get(c, 0) for c in cats)
        total_spent  = sum(spent_by.get(c, 0) for c in cats)
        remaining    = total_budget - total_spent

        # Toolbar row
        tb = ctk.CTkFrame(pg, fg_color=BG, corner_radius=10); tb.pack(fill="x", padx=20, pady=(0, 8))
        
        def _add_cat():
            def _save(vals, dlg):
                name = vals.get("name", "").strip()
                amt  = vals.get("amount", "0").strip()
                if not name:
                    return messagebox.showwarning("Error", "Category name cannot be empty.")
                try:
                    val = float(amt)
                except ValueError:
                    return messagebox.showwarning("Error", "Please enter a valid amount.")
                bdgts = _ldd("budgets")
                bdgts[name] = val
                _sv("budgets", bdgts)
                dlg.destroy()
                self.show_budget()
                
            self._dialog("Add Budget Category", [
                {"k": "name",   "lbl": "Category Name", "type": "entry"},
                {"k": "amount", "lbl": "Monthly Budget Limit (₹)", "type": "entry"},
            ], _save)
            
        self._tb_btn(tb, "＋ Add Category", _add_cat, AC)

        # Summary row
        srow = ctk.CTkFrame(pg, fg_color=BG, corner_radius=10); srow.pack(fill="x", padx=20, pady=(0, 14))
        self._kpi(srow, "Total Budget",   fmt_inr(total_budget), "This month",  AC, "📊").pack(side="left", ipadx=8, ipady=4, padx=(0, 10), expand=True, fill="both")
        self._kpi(srow, "Total Spent",    fmt_inr(total_spent),  "This month",  OR, "💸").pack(side="left", ipadx=8, ipady=4, padx=(0, 10), expand=True, fill="both")
        rc = GR if remaining >= 0 else RE
        self._kpi(srow, "Remaining",      fmt_inr(remaining),    "Available",   rc, "💎").pack(side="left", ipadx=8, ipady=4, expand=True, fill="both")

        # Category cards (2 per row)
        for row_i in range(0, len(cats), 2):
            pair = cats[row_i:row_i + 2]
            rw = ctk.CTkFrame(pg, fg_color=BG, corner_radius=10); rw.pack(fill="x", padx=20, pady=5)
            for cat in pair:
                bgt   = budgets.get(cat, 0.0)
                spent = spent_by.get(cat, 0.0)
                pct   = min(1.0, spent / bgt) if bgt > 0 else (0.0 if spent == 0 else 1.0)
                bar_clr = GR if pct < 0.7 else GO if pct < 0.9 else RE
                status  = ("✅ On Track" if pct < 0.7 else "⚠️ Warning" if pct < 0.9 else "🔴 Exceeded")
                st_clr  = GR if pct < 0.7 else GO if pct < 0.9 else RE

                card = ctk.CTkFrame(rw, fg_color=BD, corner_radius=10)
                card.pack(side="left", fill="both", expand=True, padx=(0, 8) if cat == pair[0] and len(pair) > 1 else (0, 0))
                cardi = ctk.CTkFrame(card, fg_color=CB, corner_radius=10); cardi.pack(padx=1, pady=1, fill="both")
                ctk.CTkFrame(cardi, fg_color=bar_clr, height=2, corner_radius=10).pack(fill="x")

                # Header row
                hr = ctk.CTkFrame(cardi, fg_color=CB, corner_radius=10); hr.pack(fill="x", padx=14, pady=(10, 4))
                fallback_colors = ["#ff453a", "#a855f7", "#00e676", "#ff9f0a", "#ec4899", "#10b981", "#0ea5e9", "#f43f5e", "#8b5cf6", "#14b8a6", "#f59e0b", "#3b82f6"]
                cat_clr = CAT_CLR.get(cat) or fallback_colors[hash(cat) % len(fallback_colors)]
                tk.Label(hr, text="●", font=("Segoe UI Light", 14), bg=CB, fg=cat_clr).pack(side="left")
                tk.Label(hr, text=f"  {cat}", font=("Segoe UI Semibold", 11), bg=CB, fg=TP).pack(side="left")

                # Edit & Delete Buttons
                def _eb(c=cat, b=bgt):
                    self._dialog(f"Set Budget — {c}", [
                        {"k": "amount", "lbl": "Monthly Budget (₹)", "type": "entry"},
                    ], lambda vals, dlg, cat2=c: self._set_budget(cat2, vals, dlg),
                       defaults={"amount": str(b)})
                       
                def _db(c=cat):
                    if messagebox.askyesno("Confirm", f"Delete the budget category '{c}'?"):
                        bdgts = _ldd("budgets")
                        if c in bdgts:
                            del bdgts[c]
                        _sv("budgets", bdgts)
                        self.show_budget()

                btns = ctk.CTkFrame(hr, fg_color=CB, corner_radius=10)
                btns.pack(side="right")
                
                el = tk.Label(btns, text="✏ Edit", font=("Segoe UI Light", 9), bg=CB, fg=CY, cursor="hand2")
                el.pack(side="left", padx=(0, 10))
                el.bind("<Button-1>", lambda e, fn=_eb: fn())

                dl = tk.Label(btns, text="🗑 Delete", font=("Segoe UI Light", 9), bg=CB, fg=RE, cursor="hand2")
                dl.pack(side="left")
                dl.bind("<Button-1>", lambda e, fn=_db: fn())

                # Progress bar
                bc = tk.Canvas(cardi, height=14, bg=CB2, bd=0, highlightthickness=0)
                bc.pack(fill="x", padx=14, pady=(0, 4))
                
                def _draw_bar(e, canvas=bc, ratio=pct, color=bar_clr):
                    canvas.delete("bar")
                    w = e.width
                    canvas.create_rectangle(0, 0, int(w * ratio), 14, fill=color, outline="", tags="bar")
                bc.bind("<Configure>", _draw_bar)

                # Stats
                sr = ctk.CTkFrame(cardi, fg_color=CB, corner_radius=10); sr.pack(fill="x", padx=14, pady=(0, 10))
                tk.Label(sr, text=f"Spent: {fmt_inr(spent)}", font=("Segoe UI Light", 9), bg=CB, fg=TS).pack(side="left")
                tk.Label(sr, text=f"Budget: {fmt_inr(bgt)}", font=("Segoe UI Light", 9), bg=CB, fg=TH).pack(side="left", padx=14)
                tk.Label(sr, text=status, font=("Segoe UI Semibold", 9), bg=CB, fg=st_clr).pack(side="right")
        ctk.CTkFrame(pg, fg_color=BG, height=20, corner_radius=10).pack()
