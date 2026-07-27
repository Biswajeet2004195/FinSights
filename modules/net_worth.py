import tkinter as tk
from tkinter import ttk
from config import *
from collections import defaultdict
import datetime
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class NetWorthMixin:
    def show_net_worth(self):
        self._set_nav("Net Worth")
        self._set_title("Net Worth Tracker")
        self._clear()

        f = self._scrollable(self._active_page_frame)
        
        # Header with Add Button
        hdr = tk.Frame(f, bg=BG)
        hdr.pack(fill="x", padx=20, pady=15)
        tk.Label(hdr, text="Track Your Net Worth", font=("Segoe UI", 15, "bold"), bg=BG, fg=TP).pack(side="left")
        self._tb_btn(hdr, "+ Add Asset/Liability", self._add_net_worth_entry).pack(side="right")
        
        records = _ld("net_worth")
        
        # Calculate current net worth
        dc = GLOBAL_STATE["display_currency"]
        assets = 0
        liabilities = 0
        
        asset_cats = defaultdict(float)
        liab_cats = defaultdict(float)
        
        history = defaultdict(float) # YYYY-MM -> net worth
        
        for r in records:
            amt = convert_currency(r["amount"], r.get("currency", "INR"), dc)
            m = r.get("date", "")[:7]
            if r["type"] == "Asset":
                assets += amt
                asset_cats[r["category"]] += amt
                history[m] += amt
            else:
                liabilities += amt
                liab_cats[r["category"]] += amt
                history[m] -= amt

        net_worth = assets - liabilities
        
        # History Graph requires cumulative sum if we record changes, but here we record current absolute values for simplicity.
        # Wait, if `net_worth` JSON records exact current values of different accounts, history needs snapshots.
        # For simplicity, we just assume records are total balances at a given date.
        
        kpi_f = tk.Frame(f, bg=BG)
        kpi_f.pack(fill="x", padx=20, pady=10)
        
        self._kpi(kpi_f, "Current Net Worth", fmt_disp(net_worth), "", CY, "💎").pack(side="left", fill="x", expand=True, padx=(0, 10))
        self._kpi(kpi_f, "Total Assets", fmt_disp(assets), "", GR, "🏦").pack(side="left", fill="x", expand=True, padx=(0, 10))
        self._kpi(kpi_f, "Total Liabilities", fmt_disp(liabilities), "", RE, "💳").pack(side="left", fill="x", expand=True)

        # Charts Area
        chart_f = tk.Frame(f, bg=BG)
        chart_f.pack(fill="x", padx=20, pady=15)
        
        # History Chart
        line_card = tk.Frame(chart_f, bg=CB, bd=0)
        line_card.pack(side="left", fill="both", expand=True, padx=(0, 10))
        tk.Label(line_card, text="Net Worth History", font=("Segoe UI", 12, "bold"), bg=CB, fg=TP).pack(pady=10)
        
        fig1 = Figure(figsize=(5, 3), facecolor=CB)
        ax1 = fig1.add_subplot(111)
        ax1.set_facecolor(CB)
        ax1.tick_params(colors=TS)
        for spine in ax1.spines.values():
            spine.set_color(BD)

        if history:
            sorted_months = sorted(history.keys())
            # Convert changes to cumulative? If records are delta vs absolute
            # Let's assume records are absolute values updated on that date. We'll plot the sum per month.
            vals = [history[m] for m in sorted_months]
            ax1.plot(sorted_months, vals, color=CY, marker='o', linewidth=2)
            ax1.set_xticks(range(len(sorted_months)))
            ax1.set_xticklabels(sorted_months, rotation=45, ha='right')
        else:
            ax1.text(0.5, 0.5, "No Data", color=TS, ha='center', va='center')
            
        fig1.tight_layout()
        canvas1 = FigureCanvasTkAgg(fig1, master=line_card)
        canvas1.draw()
        canvas1.get_tk_widget().pack(fill="both", expand=True)

        # Asset Breakdown
        pie_card = tk.Frame(chart_f, bg=CB, bd=0)
        pie_card.pack(side="left", fill="both", expand=True)
        tk.Label(pie_card, text="Assets vs Liabilities", font=("Segoe UI", 12, "bold"), bg=CB, fg=TP).pack(pady=10)
        
        fig2 = Figure(figsize=(5, 3), facecolor=CB)
        ax2 = fig2.add_subplot(111)
        ax2.set_facecolor(CB)
        
        if assets > 0 or liabilities > 0:
            ax2.pie([assets, liabilities], labels=["Assets", "Liabilities"], colors=[GR, RE], autopct='%1.1f%%',
                    textprops={'color': TP, 'fontsize': 9, 'weight': 'bold'}, startangle=90)
        else:
            ax2.text(0.5, 0.5, "No Data", color=TS, ha='center', va='center')
            
        canvas2 = FigureCanvasTkAgg(fig2, master=pie_card)
        canvas2.draw()
        canvas2.get_tk_widget().pack(fill="both", expand=True)

        # Table
        tb = ctk.CTkFrame(f, fg_color=BG, corner_radius=10); tb.pack(fill="x", padx=20, pady=(20, 5))
        tk.Label(tb, text="Accounts & Debts", font=("Segoe UI", 14, "bold"), bg=BG, fg=TP).pack(side="left")
        
        def _edit():
            sel = tv.selection()
            if not sel: return tk.messagebox.showwarning("Select", "Please select a record to edit.")
            rec_id = str(sel[0])
            rec = next((r for r in _ld("net_worth") if r["id"] == rec_id), None)
            if rec:
                self._add_net_worth_entry(rec)

        def _del():
            sel = tv.selection()
            if not sel: return
            if tk.messagebox.askyesno("Confirm", "Delete this entry?"):
                rec_id = str(sel[0])
                recs = [r for r in _ld("net_worth") if r["id"] != rec_id]
                _sv("net_worth", recs)
                self.show_net_worth()
                tk.messagebox.showinfo("Deleted", "Entry deleted successfully.")
        
        self._tb_btn(tb, "✏  Edit", _edit, CB2)
        self._tb_btn(tb, "🗑  Delete", _del, CB2)
        
        tv_f, tv = self._tv(f, ("ID", "Date", "Type", "Category", "Name/Desc", "Amount"), 
                           widths=[0, 100, 80, 120, 200, 100], height=10)
        tv.column("ID", width=0, stretch=False)
        tv_f.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        rows = []
        for r in sorted(records, key=lambda x: x.get("date", ""), reverse=True):
            amt = fmt_amt(r["amount"], r.get("currency", "INR"))
            rows.append((r["id"], r.get("date", ""), r["type"], r["category"], r.get("desc", ""), amt))
            
        self._tv_fill(tv, rows)
        
        def _on_double_click(e):
            sel = tv.selection()
            if not sel: return
            rec_id = str(sel[0])
            rec = next((r for r in _ld("net_worth") if r["id"] == rec_id), None)
            if rec:
                self._add_net_worth_entry(rec)
        tv.bind("<Double-1>", _on_double_click)

    def _add_net_worth_entry(self, existing=None):
        defaults = existing or {}
        fields = [
            {"lbl": "Type (Asset/Liability)", "k": "type", "type": "combo", "opts": ["Asset", "Liability"]},
            {"lbl": "Category", "k": "category", "type": "combo", "opts": ["Cash", "Bank Account", "Investments", "Gold", "Crypto", "Other Asset", "Loan", "Credit Card", "Borrowing"]},
            {"lbl": "Name/Description", "k": "desc", "type": "text"},
            {"lbl": f"Amount ({GLOBAL_STATE['display_currency']})", "k": "amount", "type": "text"},
            {"lbl": "Date (YYYY-MM-DD)", "k": "date", "type": "text"}
        ]
        if "date" not in defaults:
            defaults["date"] = today()
            
        def _save(vals, dlg):
            if not vals["desc"].strip():
                return tk.messagebox.showerror("Error", "Name/Description cannot be empty.")
                
            try: amt = float(vals["amount"])
            except: return tk.messagebox.showerror("Error", "Amount must be a number.")
            
            if amt < 0:
                return tk.messagebox.showerror("Error", "Amount cannot be negative.")
                
            try: datetime.datetime.strptime(vals["date"], "%Y-%m-%d")
            except: return tk.messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD.")
            
            recs = _ld("net_worth")
            
            # Since these are balances, if updating an existing account on same date, we might overwrite?
            # For simplicity, we just add or update the record.
            if existing:
                for r in recs:
                    if r["id"] == existing["id"]:
                        r.update({
                            "type": vals["type"],
                            "category": vals["category"],
                            "desc": vals["desc"],
                            "amount": amt,
                            "date": vals["date"]
                        })
            else:
                recs.append({
                    "id": mk_id(),
                    "type": vals["type"],
                    "category": vals["category"],
                    "desc": vals["desc"],
                    "amount": amt,
                    "date": vals["date"],
                    "currency": GLOBAL_STATE["display_currency"]
                })
            _sv("net_worth", recs)
            dlg.destroy()
            self.show_net_worth()

        self._dialog("Add/Edit Account Balance", fields, _save, defaults)
