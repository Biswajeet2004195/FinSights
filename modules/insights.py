import tkinter as tk
from config import *
from base_dashboard import BaseDashboard

class InsightMixin(BaseDashboard):
    def show_insights(self):

        self._clear(); self._set_nav("AI Insights"); self._set_title("AI Insights")
        pg = self._scrollable(self._cf)
        self._sec(pg, "🤖 AI Financial Insights", "Smart analysis of your financial patterns")

        # Header card
        hcard = ctk.CTkFrame(pg, fg_color=BD, corner_radius=10); hcard.pack(fill="x", padx=20, pady=(0, 16))
        hci = ctk.CTkFrame(hcard, fg_color="#0d1a2e", corner_radius=10); hci.pack(padx=1, pady=1, fill="x")
        rw = ctk.CTkFrame(hci, fg_color="#0d1a2e", corner_radius=10); rw.pack(fill="x", padx=16, pady=14)
        tk.Label(rw, text="🤖", font=("Segoe UI Emoji", 30), bg="#0d1a2e", fg=CY).pack(side="left", padx=(0, 14))
        ri = ctk.CTkFrame(rw, fg_color="#0d1a2e", corner_radius=10); ri.pack(side="left")
        tk.Label(ri, text="Your Personal Financial AI", font=("Segoe UI Semibold", 14), bg="#0d1a2e", fg=TP).pack(anchor="w")
        tk.Label(ri, text="Pattern analysis powered by your transactions, budgets, goals and investments",
                 font=("Segoe UI Light", 10), bg="#0d1a2e", fg=TS).pack(anchor="w")

        for ins in self._gen_insights():
            ic = ctk.CTkFrame(pg, fg_color=BD, corner_radius=10); ic.pack(fill="x", padx=20, pady=5)
            ici = ctk.CTkFrame(ic, fg_color=ins["bg"], corner_radius=10); ici.pack(padx=1, pady=1, fill="x")
            ctk.CTkFrame(ici, fg_color=ins["border"], height=2, corner_radius=10).pack(fill="x")
            rw = ctk.CTkFrame(ici, fg_color=ins["bg"], corner_radius=10); rw.pack(fill="x", padx=14, pady=12)
            tk.Label(rw, text=ins["icon"], font=("Segoe UI Emoji", 22),
                     bg=ins["bg"]).pack(side="left", padx=(0, 12))
            ri = ctk.CTkFrame(rw, fg_color=ins["bg"], corner_radius=10); ri.pack(side="left", fill="both", expand=True)
            tk.Label(ri, text=ins["title"], font=("Segoe UI Semibold", 11),
                     bg=ins["bg"], fg=TP).pack(anchor="w")
            tk.Label(ri, text=ins["msg"], font=("Segoe UI Light", 10),
                     bg=ins["bg"], fg=TS, wraplength=860, justify="left").pack(anchor="w", pady=(2, 0))
            if ins.get("tip"):
                tk.Label(ri, text=f"💡 Tip: {ins['tip']}", font=("Segoe UI Light", 9, "italic"),
                         bg=ins["bg"], fg=CY).pack(anchor="w", pady=(4, 0))

        # Best practices
        ctk.CTkFrame(pg, fg_color=BD, height=1, corner_radius=10).pack(fill="x", padx=20, pady=16)
        tk.Label(pg, text="📚 Financial Best Practices", font=("Segoe UI Semibold", 13),
                 bg=BG, fg=TP).pack(anchor="w", padx=20, pady=(0, 8))
        tips = [
            ("50/30/20 Rule",         "Needs", "Allocate 50% to needs, 30% to wants, and 20% to savings & investments."),
            ("Emergency Fund",        "Safety", "Keep 3–6 months of expenses in a liquid, high-yield savings account."),
            ("SIP Discipline",        "Growth", "Invest monthly in index funds — consistency beats timing the market."),
            ("Avoid Lifestyle Inflation","Wealth", "As income grows, increase savings rate — not just lifestyle spending."),
        ]
        for title, badge, msg in tips:
            tf = ctk.CTkFrame(pg, fg_color=BD, corner_radius=10); tf.pack(fill="x", padx=20, pady=3)
            tfi = ctk.CTkFrame(tf, fg_color=CB2, corner_radius=10); tfi.pack(padx=1, pady=1, fill="x")
            rw = ctk.CTkFrame(tfi, fg_color=CB2, corner_radius=10); rw.pack(fill="x", padx=14, pady=10)
            tk.Label(rw, text="💡", font=("Segoe UI Emoji", 14), bg=CB2).pack(side="left", padx=(0, 10))
            ri = ctk.CTkFrame(rw, fg_color=CB2, corner_radius=10); ri.pack(side="left", fill="both")
            tk.Label(ri, text=title, font=("Segoe UI Semibold", 10), bg=CB2, fg=CY).pack(anchor="w")
            tk.Label(ri, text=msg, font=("Segoe UI Light", 9), bg=CB2, fg=TS,
                     wraplength=900, justify="left").pack(anchor="w")
        ctk.CTkFrame(pg, fg_color=BG, height=20, corner_radius=10).pack()
