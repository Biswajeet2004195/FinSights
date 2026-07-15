import tkinter as tk
from config import *
from base_dashboard import BaseDashboard

class HealthMixin(BaseDashboard):
    def show_health(self):

        self._clear(); self._set_nav("Health Score"); self._set_title("Financial Health Score")
        pg = self._scrollable(self._cf)
        self._sec(pg, "❤️ Financial Health Score", "Your comprehensive financial wellness rating (0–100)")

        score, breakdown = self._calc_health()
        grade      = "A" if score >= 80 else "B" if score >= 65 else "C" if score >= 50 else "D" if score >= 35 else "F"
        grade_clr  = GR  if score >= 80 else CY  if score >= 65 else GO  if score >= 50 else OR  if score >= 35 else RE
        grade_desc = {
            "A": "Excellent — top-tier financial health!",
            "B": "Good — a few areas to polish.",
            "C": "Fair — noticeable room for improvement.",
            "D": "Poor — needs significant attention.",
            "F": "Critical — take immediate corrective steps.",
        }[grade]

        # Main card
        mc = ctk.CTkFrame(pg, fg_color=BD, corner_radius=10); mc.pack(fill="x", padx=20, pady=(8, 16))
        mci = ctk.CTkFrame(mc, fg_color=CB, corner_radius=10); mci.pack(padx=1, pady=1, fill="x")
        ctk.CTkFrame(mci, fg_color=grade_clr, height=3, corner_radius=10).pack(fill="x")
        inner = ctk.CTkFrame(mci, fg_color=CB, corner_radius=10); inner.pack(fill="x", padx=20, pady=20)

        # Arc gauge (left)
        lg = ctk.CTkFrame(inner, fg_color=CB, corner_radius=10); lg.pack(side="left", padx=(20, 50))
        canvas = tk.Canvas(lg, width=280, height=240, bg=CB, bd=0, highlightthickness=0)
        canvas.pack()
        self._draw_gauge(canvas, 140, 140, 110, score, big=True)
        tk.Label(lg, text=f"Grade  {grade}", font=("Segoe UI", 20, "bold"),
                 bg=CB, fg=grade_clr).pack()
        tk.Label(lg, text=grade_desc, font=("Segoe UI Light", 9),
                 bg=CB, fg=TS).pack(pady=(2, 0))

        # Breakdown (right)
        labels_map = {
            "Savings Rate":      ("How much of your income you save monthly",      GO),
            "Budget Compliance": ("How well you stay within your budget limits",    CY),
            "Goal Progress":     ("Average progress across your financial goals",   GR),
            "Invest Diversity":  ("Diversity of your investment portfolio",          AC),
        }
        rg = ctk.CTkFrame(inner, fg_color=CB, corner_radius=10); rg.pack(side="left", fill="both", expand=True)
        tk.Label(rg, text="Score Breakdown", font=("Segoe UI Semibold", 13),
                 bg=CB, fg=TP).pack(anchor="w", pady=(0, 12))

        for cat, (pts, max_pts) in breakdown.items():
            pct = pts / max_pts if max_pts else 0
            clr = GR if pct > 0.7 else GO if pct > 0.4 else RE
            desc, cat_clr = labels_map.get(cat, ("", CY))

            cf2 = ctk.CTkFrame(rg, fg_color=CB2, corner_radius=10); cf2.pack(fill="x", pady=5)
            ctk.CTkFrame(cf2, fg_color=CB2, height=2, corner_radius=10).pack()
            hr = ctk.CTkFrame(cf2, fg_color=CB2, corner_radius=10); hr.pack(fill="x", padx=12, pady=(4, 2))
            tk.Label(hr, text=cat, font=("Segoe UI Semibold", 10), bg=CB2, fg=TP).pack(side="left")
            tk.Label(hr, text=f"{int(pts)} / {max_pts} pts", font=("Segoe UI Semibold", 10),
                     bg=CB2, fg=clr).pack(side="right")
            bc = tk.Canvas(cf2, height=12, bg=BD, bd=0, highlightthickness=0)
            bc.pack(fill="x", padx=12, pady=(0, 2))
            bc.update_idletasks()
            w = bc.winfo_width() or 400
            bc.create_rectangle(0, 0, int(w * pct), 12, fill=clr, outline="")
            tk.Label(cf2, text=desc, font=("Segoe UI Light", 8), bg=CB2, fg=TH
                     ).pack(anchor="w", padx=12, pady=(0, 6))

        # Improvement tips
        tk.Label(pg, text="📈 How to Improve Your Score", font=("Segoe UI Semibold", 13),
                 bg=BG, fg=TP).pack(anchor="w", padx=20, pady=(8, 8))
        tips = []
        bd = breakdown
        if bd.get("Savings Rate",      (0, 30))[0] < 20:
            tips.append(("💰", "Boost Savings Rate",    "Save at least 20% of monthly income. Set an auto-transfer on payday."))
        if bd.get("Budget Compliance", (0, 25))[0] < 18:
            tips.append(("📊", "Improve Budget Compliance", "Overspending in some categories. Adjust limits or cut discretionary spend."))
        if bd.get("Goal Progress",     (0, 25))[0] < 15:
            tips.append(("🎯", "Accelerate Goal Savings",   "Increase monthly contributions — even ₹500 extra/month compounds significantly."))
        if bd.get("Invest Diversity",  (0, 20))[0] < 12:
            tips.append(("📈", "Diversify Portfolio",        "Add asset classes like index funds, gold, or bonds to reduce concentration risk."))
        if not tips:
            tips.append(("⭐", "Keep It Up!",               "You have excellent financial habits. Maintain discipline and stay the course."))

        for icon, title, msg in tips:
            tf = ctk.CTkFrame(pg, fg_color=BD, corner_radius=10); tf.pack(fill="x", padx=20, pady=4)
            tfi = ctk.CTkFrame(tf, fg_color=CB2, corner_radius=10); tfi.pack(padx=1, pady=1, fill="x")
            rw = ctk.CTkFrame(tfi, fg_color=CB2, corner_radius=10); rw.pack(fill="x", padx=14, pady=12)
            tk.Label(rw, text=icon, font=("Segoe UI Emoji", 16), bg=CB2).pack(side="left", padx=(0, 12))
            ri = ctk.CTkFrame(rw, fg_color=CB2, corner_radius=10); ri.pack(side="left", fill="both")
            tk.Label(ri, text=title, font=("Segoe UI Semibold", 10), bg=CB2, fg=CY).pack(anchor="w")
            tk.Label(ri, text=msg, font=("Segoe UI Light", 9), bg=CB2, fg=TS,
                     wraplength=900, justify="left").pack(anchor="w")
        ctk.CTkFrame(pg, fg_color=BG, height=20, corner_radius=10).pack()
