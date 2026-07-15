import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from config import *
from base_dashboard import BaseDashboard

class GoalMixin(BaseDashboard):
    def show_goals(self):
        self._clear(); self._set_nav("Goals"); self._set_title("Goals")
        pg = self._scrollable(self._cf)
        self._sec(pg, "🎯 Financial Goals", "Track progress towards your savings goals")

        tb = ctk.CTkFrame(pg, fg_color=BG, corner_radius=10); tb.pack(fill="x", padx=20, pady=(0, 12))

        def _add():
            self._dialog("Add New Goal", [
                {"k": "name",     "lbl": "Goal Name",                 "type": "entry"},
                {"k": "target",   "lbl": "Target Amount (₹)",         "type": "entry"},
                {"k": "saved",    "lbl": "Already Saved (₹)",         "type": "entry"},
                {"k": "deadline", "lbl": "Target Date (YYYY-MM-DD)",  "type": "entry"},
            ], self._save_goal_cb, defaults={"saved": "0"})

        self._tb_btn(tb, "＋  Add Goal", _add, AC)

        goals = _ld("goals")
        if not goals:
            tk.Label(pg, text="No goals yet. Add your first financial goal!",
                     font=("Segoe UI", 13), bg=BG, fg=TS).pack(pady=60)
            return

        # 2-column grid using pairs
        for i in range(0, len(goals), 2):
            pair = goals[i:i + 2]
            rw = ctk.CTkFrame(pg, fg_color=BG, corner_radius=10); rw.pack(fill="x", padx=20, pady=6)
            for g in pair:
                tgt    = float(g["target"]); saved = float(g["saved"])
                pct    = min(1.0, saved / tgt) if tgt > 0 else 0
                try:
                    dl         = datetime.strptime(g["deadline"], "%Y-%m-%d")
                    days_left  = (dl - datetime.now()).days
                    months_left = max(1, days_left // 30)
                    mneed      = (tgt - saved) / months_left if months_left > 0 else 0
                except Exception:
                    days_left = months_left = mneed = 0

                bar_clr = GR if pct >= 1 else CY if pct > 0.6 else AC

                card = ctk.CTkFrame(rw, fg_color=BD, corner_radius=10)
                card.pack(side="left", fill="both", expand=True, padx=(0, 8) if g == pair[0] and len(pair) > 1 else (0, 0))
                cardi = ctk.CTkFrame(card, fg_color=CB, corner_radius=10); cardi.pack(padx=1, pady=1, fill="both")
                ctk.CTkFrame(cardi, fg_color=bar_clr, height=3, corner_radius=10).pack(fill="x")

                cont = ctk.CTkFrame(cardi, fg_color=CB, corner_radius=10); cont.pack(fill="x", padx=14, pady=12)

                # Progress ring
                rc = tk.Canvas(cont, width=90, height=90, bg=CB, bd=0, highlightthickness=0)
                rc.pack(side="left")
                self._draw_ring(rc, 45, 45, 36, pct, bar_clr)

                # Details
                ri = ctk.CTkFrame(cont, fg_color=CB, corner_radius=10); ri.pack(side="left", fill="both", expand=True, padx=14)
                tk.Label(ri, text=f"{g['name']}",
                         font=("Segoe UI", 13, "bold"), bg=CB, fg=TP).pack(anchor="w")
                tk.Label(ri, text=f"Target: {fmt_inr(tgt)}",
                         font=("Segoe UI", 10), bg=CB, fg=TS).pack(anchor="w", pady=(4, 0))
                tk.Label(ri, text=f"Saved: {fmt_inr(saved)}  ({int(pct*100)}%)",
                         font=("Segoe UI", 10, "bold"), bg=CB, fg=bar_clr).pack(anchor="w")
                tk.Label(ri, text=f"Deadline: {g['deadline']}  •  {max(0, days_left)} days left",
                         font=("Segoe UI", 9), bg=CB, fg=TH).pack(anchor="w", pady=(2, 0))
                if mneed > 0 and pct < 1:
                    tk.Label(ri, text=f"Need {fmt_inr(mneed)}/month to hit goal",
                             font=("Segoe UI", 9), bg=CB, fg=CY).pack(anchor="w")

                # Edit/Delete
                br = ctk.CTkFrame(cardi, fg_color=CB, corner_radius=10); br.pack(fill="x", padx=14, pady=(0, 10))

                def _edit_g(gid=g["id"], gd=dict(g)):
                    self._dialog("Edit Goal", [
                        {"k": "name",     "lbl": "Goal Name",                "type": "entry"},
                        {"k": "target",   "lbl": "Target (₹)",               "type": "entry"},
                        {"k": "saved",    "lbl": "Saved (₹)",                "type": "entry"},
                        {"k": "deadline", "lbl": "Deadline (YYYY-MM-DD)",    "type": "entry"},
                    ], lambda vals, dlg: self._upd_goal(gid, vals, dlg),
                       defaults={k: str(gd[k]) for k in ["name", "target", "saved", "deadline"]})

                def _del_g(gid=g["id"]):
                    if messagebox.askyesno("Delete", "Delete this goal?"):
                        gs = [x for x in _ld("goals") if x["id"] != gid]
                        _sv("goals", gs); self.show_goals()

                el = tk.Label(br, text="✏ Edit",   font=("Segoe UI Light", 9), bg=CB, fg=CY, cursor="hand2")
                el.pack(side="left"); el.bind("<Button-1>", lambda e, fn=_edit_g: fn())
                dl2 = tk.Label(br, text="🗑 Delete", font=("Segoe UI Light", 9), bg=CB, fg=RE, cursor="hand2")
                dl2.pack(side="left", padx=12); dl2.bind("<Button-1>", lambda e, fn=_del_g: fn())
        ctk.CTkFrame(pg, fg_color=BG, height=20, corner_radius=10).pack()
