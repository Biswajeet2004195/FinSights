import tkinter as tk
from tkinter import messagebox
from collections import defaultdict
from config import *
from base_dashboard import BaseDashboard

class ExpenseMixin(BaseDashboard):
    def show_expenses(self):
        self._clear(); self._set_nav("Expenses"); self._set_title("Expenses")
        pg = self._scrollable(self._cf)
        trans = _ld("transactions"); cm = curr_m()
        dc = GLOBAL_STATE["display_currency"]
        me = sum(convert_currency(r["amount"], r.get("currency", "INR"), dc) for r in trans if r["type"] == "expense" and r["date"].startswith(cm))
        ae = sum(convert_currency(r["amount"], r.get("currency", "INR"), dc) for r in trans if r["type"] == "expense")

        top = ctk.CTkFrame(pg, fg_color=BG, corner_radius=10); top.pack(fill="x", padx=20, pady=(14, 8))
        self._kpi(top, "Monthly Expenses",  fmt_disp(me), "Current month", RE, "💸").pack(side="left", ipadx=8, ipady=4, padx=(0, 10))
        self._kpi(top, "All-time Expenses", fmt_disp(ae), "Total",         OR, "📊").pack(side="left", ipadx=8, ipady=4, padx=(0, 10))
        mi = sum(convert_currency(r["amount"], r.get("currency", "INR"), dc) for r in trans if r["type"] == "income" and r["date"].startswith(cm))
        ratio = me / mi * 100 if mi else 0
        self._kpi(top, "Expense Ratio", f"{ratio:.0f}%", "vs this month income", PK, "📉").pack(side="left", ipadx=8, ipady=4)

        tb = ctk.CTkFrame(pg, fg_color=BG, corner_radius=10); tb.pack(fill="x", padx=20, pady=(0, 8))

        def _add():
            self._dialog("Add Expense", [
                {"k": "date",     "lbl": "Date (YYYY-MM-DD)", "type": "entry"},
                {"k": "desc",     "lbl": "Description",       "type": "entry"},
                {"k": "category", "lbl": "Category",          "type": "combo", "opts": list(_ldd("budgets").keys())},
                {"k": "currency", "lbl": "Currency",          "type": "combo", "opts": SUPPORTED_CURRENCIES},
                {"k": "amount",   "lbl": "Amount",            "type": "entry"},
                {"k": "notes",    "lbl": "Notes",             "type": "entry"},
            ], lambda vals, dlg: self._save_trans(vals, "expense", dlg, self.show_expenses),
               defaults={"date": today(), "currency": GLOBAL_STATE["display_currency"]})

        def _edit():
            sel = tv.selection()
            if not sel: return messagebox.showwarning("Select", "Please select a record to edit.")
            rec = next((r for r in _ld("transactions") if r["id"] == sel[0]), None)
            if not rec: return
            self._dialog("Edit Expense", [
                {"k": "date",     "lbl": "Date (YYYY-MM-DD)", "type": "entry"},
                {"k": "desc",     "lbl": "Description",       "type": "entry"},
                {"k": "category", "lbl": "Category",          "type": "combo", "opts": list(_ldd("budgets").keys())},
                {"k": "currency", "lbl": "Currency",          "type": "combo", "opts": SUPPORTED_CURRENCIES},
                {"k": "amount",   "lbl": "Amount",            "type": "entry"},
                {"k": "notes",    "lbl": "Notes",             "type": "entry"},
            ], lambda vals, dlg: self._upd_trans(sel[0], vals, dlg, self.show_expenses),
               defaults={"date": rec["date"], "desc": rec["desc"], "category": rec["category"],
                         "currency": rec.get("currency", "INR"), "amount": str(rec["amount"]), "notes": rec.get("notes", "")})

        def _del():
            sel = tv.selection()
            if not sel: return
            if messagebox.askyesno("Confirm", "Delete this expense?"):
                recs = [r for r in _ld("transactions") if r["id"] != sel[0]]
                _sv("transactions", recs); self.show_expenses()

        self._tb_btn(tb, "＋  Add Expense", _add, AC)
        self._tb_btn(tb, "✏  Edit",        _edit, CB2)
        self._tb_btn(tb, "🗑  Delete",     _del,  CB2)

        # Content Frame
        split = ctk.CTkFrame(pg, fg_color=BG, corner_radius=10); split.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        # Table
        cols = ["Date", "Description", "Category", "Amount", "Notes"]
        tf, tv = self._tv(split, cols, [120, 220, 180, 140, 340], height=18)
        tf.pack(side="top", fill="both", expand=True)
        recs = sorted([r for r in trans if r["type"] == "expense"],
                      key=lambda r: r["date"], reverse=True)
        self._tv_fill(tv, [(r["id"], r["date"], r["desc"], r["category"],
                            fmt_amt(r["amount"], r.get("currency", "INR")), r.get("notes", "")) for r in recs])
