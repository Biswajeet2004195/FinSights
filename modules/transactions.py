import tkinter as tk
from tkinter import ttk, messagebox
from config import *
from base_dashboard import BaseDashboard

class TransactionsMixin(BaseDashboard):
    def show_transactions(self):
        self._clear()
        self._set_nav("Transactions")
        self._set_title("All Transactions")
        pg = self._scrollable(self._cf)
        
        trans = _ld("transactions")
        cm = curr_m()
        dc = GLOBAL_STATE["display_currency"]
        
        tot_inc = sum(convert_currency(r["amount"], r.get("currency", "INR"), dc) for r in trans if r["type"] == "income")
        tot_exp = sum(convert_currency(r["amount"], r.get("currency", "INR"), dc) for r in trans if r["type"] == "expense")
        net_bal = tot_inc - tot_exp
        
        top = ctk.CTkFrame(pg, fg_color=BG, corner_radius=10)
        top.pack(fill="x", padx=20, pady=(14, 8))
        self._kpi(top, "Total Income (+)", fmt_disp(tot_inc), "All-time income", GR, "💰").pack(side="left", ipadx=8, ipady=4, padx=(0, 10))
        self._kpi(top, "Total Expense (-)", fmt_disp(tot_exp), "All-time expenses", RE, "💸").pack(side="left", ipadx=8, ipady=4, padx=(0, 10))
        self._kpi(top, "Net Balance", fmt_disp(net_bal), "Income - Expense", CY if net_bal >= 0 else RE, "📊").pack(side="left", ipadx=8, ipady=4)
        
        tb = ctk.CTkFrame(pg, fg_color=BG, corner_radius=10)
        tb.pack(fill="x", padx=20, pady=(0, 8))
        
        # Filter controls
        tk.Label(tb, text="Type:", bg=BG, fg=TS, font=("Segoe UI", 10)).pack(side="left", padx=(10, 5))
        type_var = tk.StringVar(value="All")
        type_cb = ttk.Combobox(tb, textvariable=type_var, values=["All", "Income (+)", "Expense (-)"], state="readonly", width=12, style="A.TCombobox")
        type_cb.pack(side="left", padx=5)
        
        tk.Label(tb, text="Search:", bg=BG, fg=TS, font=("Segoe UI", 10)).pack(side="left", padx=(15, 5))
        f_var = tk.StringVar()
        f_ent = tk.Entry(tb, textvariable=f_var, bg=CB2, fg=TP, insertbackground=CY, bd=0, font=("Segoe UI", 10))
        f_ent.pack(side="left", padx=5, ipady=4)
        
        cols = ["Type", "Date", "Description", "Category", "Amount", "Notes"]
        tf, tv = self._tv(pg, cols, [80, 110, 220, 160, 140, 200], height=20)
        tf.pack(fill="both", expand=True, padx=20, pady=(0, 16))
        
        # Format rows with + for income and - for expense
        recs = sorted(trans, key=lambda r: r["date"], reverse=True)
        
        def _apply_filter(*args):
            q = f_var.get().lower()
            t_sel = type_var.get()
            filtered = []
            for r in recs:
                is_inc = (r["type"] == "income")
                if t_sel == "Income (+)" and not is_inc: continue
                if t_sel == "Expense (-)" and is_inc: continue
                
                if q in r["date"].lower() or q in r["desc"].lower() or q in r["category"].lower() or q in str(r["amount"]).lower():
                    sign = "+" if is_inc else "-"
                    amt_str = f"{sign}{fmt_amt(r['amount'], r.get('currency', 'INR'))}"
                    type_str = "Income (+)" if is_inc else "Expense (-)"
                    tag = "income" if is_inc else "expense"
                    filtered.append((r["id"], type_str, r["date"], r["desc"], r["category"], amt_str, r.get("notes", ""), tag))
            self._tv_fill(tv, filtered)
            
        f_var.trace("w", _apply_filter)
        type_cb.bind("<<ComboboxSelected>>", _apply_filter)
        _apply_filter()
