import tkinter as tk
from tkinter import messagebox
from config import *
from base_dashboard import BaseDashboard

class InvestmentMixin(BaseDashboard):
    def show_investments(self):

        self._clear(); self._set_nav("Investments"); self._set_title("Investments")
        pg = self._scrollable(self._cf)
        invs = _ld("investments")
        total_val  = sum(i["qty"] * i["current_price"] for i in invs)
        total_cost = sum(i["qty"] * i["buy_price"]     for i in invs)
        total_pl   = total_val - total_cost
        pl_pct     = total_pl / total_cost * 100 if total_cost else 0

        top = ctk.CTkFrame(pg, fg_color=BG, corner_radius=10); top.pack(fill="x", padx=20, pady=(14, 8))
        self._kpi(top, "Portfolio Value", fmt_inr(total_val),  "Current",   AC,              "📈").pack(side="left", ipadx=8, ipady=4, padx=(0, 10))
        self._kpi(top, "Total Invested",  fmt_inr(total_cost), "Cost basis", CY,             "💰").pack(side="left", ipadx=8, ipady=4, padx=(0, 10))
        pl_clr = GR if total_pl >= 0 else RE
        self._kpi(top, "Total P&L",  fmt_inr(total_pl), f"{pl_pct:+.1f}%", pl_clr,          "💹").pack(side="left", ipadx=8, ipady=4, padx=(0, 10))
        self._kpi(top, "Holdings",   str(len(invs)),      "Assets",          GO,              "🗂️").pack(side="left", ipadx=8, ipady=4)

        tb = ctk.CTkFrame(pg, fg_color=BG, corner_radius=10); tb.pack(fill="x", padx=20, pady=(0, 8))

        def _add():
            self._dialog("Add Investment", [
                {"k": "name",          "lbl": "Asset Name",         "type": "entry"},
                {"k": "symbol",        "lbl": "Symbol / Ticker",    "type": "entry"},
                {"k": "type",          "lbl": "Type",               "type": "combo", "opts": INV_TYPES},
                {"k": "qty",           "lbl": "Quantity",           "type": "entry"},
                {"k": "buy_price",     "lbl": "Buy Price (₹)",      "type": "entry"},
                {"k": "current_price", "lbl": "Current Price (₹)",  "type": "entry"},
                {"k": "notes",         "lbl": "Notes",              "type": "entry"},
            ], self._save_inv_cb)

        def _edit():
            sel = tv.selection()
            if not sel: return messagebox.showwarning("Select", "Select an investment to edit.")
            inv = next((i for i in _ld("investments") if i["id"] == sel[0]), None)
            if not inv: return
            self._dialog("Edit Investment", [
                {"k": "name",          "lbl": "Asset Name",         "type": "entry"},
                {"k": "symbol",        "lbl": "Symbol / Ticker",    "type": "entry"},
                {"k": "type",          "lbl": "Type",               "type": "combo", "opts": INV_TYPES},
                {"k": "qty",           "lbl": "Quantity",           "type": "entry"},
                {"k": "buy_price",     "lbl": "Buy Price (₹)",      "type": "entry"},
                {"k": "current_price", "lbl": "Current Price (₹)",  "type": "entry"},
                {"k": "notes",         "lbl": "Notes",              "type": "entry"},
            ], lambda vals, dlg: self._upd_inv(sel[0], vals, dlg),
               defaults={k: str(inv.get(k, "")) for k in
                         ["name", "symbol", "type", "qty", "buy_price", "current_price", "notes"]})

        def _del():
            sel = tv.selection()
            if not sel: return
            if messagebox.askyesno("Confirm", "Delete this investment?"):
                invs2 = [i for i in _ld("investments") if i["id"] != sel[0]]
                _sv("investments", invs2); self.show_investments()

        self._tb_btn(tb, "＋  Add Investment", _add, AC)
        self._tb_btn(tb, "✏  Edit",            _edit, CB2)
        self._tb_btn(tb, "🗑  Delete",          _del,  CB2)

        cols = ["Asset", "Symbol", "Type", "Qty", "Buy Price", "Curr Price", "Value", "P&L", "P&L %"]
        tf, tv = self._tv(pg, cols, [150, 90, 110, 65, 110, 110, 120, 110, 80], height=20)
        tf.pack(fill="both", expand=True, padx=20, pady=(0, 16))
        tv.tag_configure("pl_pos", foreground=GR)
        tv.tag_configure("pl_neg", foreground=RE)

        tv.delete(*tv.get_children())
        for i2, inv in enumerate(invs):
            val  = inv["qty"] * inv["current_price"]
            cost = inv["qty"] * inv["buy_price"]
            pl   = val - cost
            plp  = pl / cost * 100 if cost else 0
            tag  = "pl_pos" if pl >= 0 else "pl_neg"
            tv.insert("", "end", iid=inv["id"], tags=(tag,),
                      values=(inv["name"], inv["symbol"], inv["type"],
                              str(inv["qty"]), fmt_inr(inv["buy_price"]),
                              fmt_inr(inv["current_price"]),
                              fmt_inr(val), fmt_inr(pl), f"{plp:+.1f}%"))
