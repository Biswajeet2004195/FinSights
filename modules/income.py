import tkinter as tk
from tkinter import messagebox
from config import *
from base_dashboard import BaseDashboard

class IncomeMixin(BaseDashboard):
    def show_income(self):
        self._clear(); self._set_nav("Income"); self._set_title("Income")
        pg = self._scrollable(self._cf)
        trans = _ld("transactions"); cm = curr_m()
        mi = sum(r["amount"] for r in trans if r["type"] == "income" and r["date"].startswith(cm))
        ai = sum(r["amount"] for r in trans if r["type"] == "income")

        top = ctk.CTkFrame(pg, fg_color=BG, corner_radius=10); top.pack(fill="x", padx=20, pady=(14, 8))
        self._kpi(top, "Monthly Income",   fmt_inr(mi), "Current month", GR, "💰").pack(side="left", ipadx=8, ipady=4, padx=(0, 10))
        self._kpi(top, "All-time Income",  fmt_inr(ai), "Total",         CY, "📊").pack(side="left", ipadx=8, ipady=4, padx=(0, 10))
        count = sum(1 for r in trans if r["type"] == "income" and r["date"].startswith(cm))
        self._kpi(top, "Entries This Month", str(count), "Income records", GO, "📋").pack(side="left", ipadx=8, ipady=4)

        tb = ctk.CTkFrame(pg, fg_color=BG, corner_radius=10); tb.pack(fill="x", padx=20, pady=(0, 8))

        def _add():
            self._dialog("Add Income Entry", [
                {"k": "date",     "lbl": "Date (YYYY-MM-DD)", "type": "entry"},
                {"k": "desc",     "lbl": "Description",       "type": "entry"},
                {"k": "category", "lbl": "Category",          "type": "combo", "opts": INCOME_CATS},
                {"k": "amount",   "lbl": "Amount (₹)",        "type": "entry"},
                {"k": "notes",    "lbl": "Notes",             "type": "entry"},
            ], lambda vals, dlg: self._save_trans(vals, "income", dlg, self.show_income),
               defaults={"date": today()})

        def _edit():
            sel = tv.selection()
            if not sel: return messagebox.showwarning("Select", "Please select a record to edit.")
            rec = next((r for r in _ld("transactions") if r["id"] == sel[0]), None)
            if not rec: return
            self._dialog("Edit Income Entry", [
                {"k": "date",     "lbl": "Date (YYYY-MM-DD)", "type": "entry"},
                {"k": "desc",     "lbl": "Description",       "type": "entry"},
                {"k": "category", "lbl": "Category",          "type": "combo", "opts": INCOME_CATS},
                {"k": "amount",   "lbl": "Amount (₹)",        "type": "entry"},
                {"k": "notes",    "lbl": "Notes",             "type": "entry"},
            ], lambda vals, dlg: self._upd_trans(sel[0], vals, dlg, self.show_income),
               defaults={"date": rec["date"], "desc": rec["desc"], "category": rec["category"],
                         "amount": str(rec["amount"]), "notes": rec.get("notes", "")})

        def _del():
            sel = tv.selection()
            if not sel: return
            if messagebox.askyesno("Confirm", "Delete this income entry?"):
                recs = [r for r in _ld("transactions") if r["id"] != sel[0]]
                _sv("transactions", recs); self.show_income()

        self._tb_btn(tb, "＋  Add Income", _add, AC)
        self._tb_btn(tb, "✏  Edit",       _edit, CB2)
        self._tb_btn(tb, "🗑  Delete",    _del,  CB2)

        cols = ["Date", "Description", "Category", "Amount", "Notes"]
        tf, tv = self._tv(pg, cols, [110, 220, 160, 130, 200], height=20)
        tf.pack(fill="both", expand=True, padx=20, pady=(0, 16))
        recs = sorted([r for r in trans if r["type"] == "income"],
                      key=lambda r: r["date"], reverse=True)
        self._tv_fill(tv, [(r["id"], r["date"], r["desc"], r["category"],
                            fmt_inr(r["amount"]), r.get("notes", "")) for r in recs])
