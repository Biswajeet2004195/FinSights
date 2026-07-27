import tkinter as tk
from tkinter import ttk
from config import *
from collections import defaultdict
import datetime

class ForecastMixin:
    def show_forecast(self):
        self._set_nav("Forecast")
        self._set_title("Financial Forecast")
        self._clear()

        f = self._scrollable(self._active_page_frame)
        self._sec(f, "AI Forecast", "Predictive insights based on your past transactions.")

        trans = _ld("transactions")
        if not trans:
            tk.Label(f, text="Not enough data to generate forecast.", font=("Segoe UI", 12), bg=BG, fg=TS).pack(pady=40)
            return

        # Group data by month
        dc = GLOBAL_STATE["display_currency"]
        monthly_inc = defaultdict(float)
        monthly_exp = defaultdict(float)

        for r in trans:
            m = r.get("month", r.get("date", "")[:7])
            amt = convert_currency(r["amount"], r.get("currency", "INR"), dc)
            if r["type"] == "income":
                monthly_inc[m] += amt
            elif r["type"] == "expense":
                monthly_exp[m] += amt

        months = sorted(set(monthly_inc.keys()).union(monthly_exp.keys()))
        if len(months) < 2:
            tk.Label(f, text="Need at least 2 months of data for a reliable forecast.", font=("Segoe UI", 12), bg=BG, fg=TS).pack(pady=40)
            return

        def _predict(data_dict, months_list):
            vals = [data_dict[m] for m in months_list]
            if not vals: return 0, "→", "Low"
            
            # Simple Moving Average (last 3 months)
            if len(vals) <= 3:
                pred = sum(vals) / len(vals)
                trend = "↑" if len(vals) >= 2 and vals[-1] > vals[-2] else ("↓" if len(vals) >= 2 and vals[-1] < vals[-2] else "→")
                conf = "Medium" if len(vals) == 3 else "Low"
                return pred, trend, conf
            
            # Linear Regression for > 3 months
            n = len(vals)
            x_mean = sum(range(n)) / n
            y_mean = sum(vals) / n
            
            num = sum((i - x_mean) * (vals[i] - y_mean) for i in range(n))
            den = sum((i - x_mean)**2 for i in range(n))
            
            m = num / den if den != 0 else 0
            c = y_mean - m * x_mean
            
            pred = m * n + c
            pred = max(0, pred)
            
            trend = "↑" if m > 0.05 * y_mean else ("↓" if m < -0.05 * y_mean else "→")
            
            # Calculate variance for confidence
            variance = sum((vals[i] - y_mean)**2 for i in range(n)) / n
            if y_mean > 0:
                cv = (variance ** 0.5) / y_mean
                conf = "High" if cv < 0.2 else ("Medium" if cv < 0.5 else "Low")
            else:
                conf = "Low"
                
            return pred, trend, conf

        pred_inc, trend_inc, conf_inc = _predict(monthly_inc, months)
        pred_exp, trend_exp, conf_exp = _predict(monthly_exp, months)
        pred_sav = pred_inc - pred_exp
        trend_sav = "↑" if pred_sav > (monthly_inc[months[-1]] - monthly_exp[months[-1]]) else "↓"

        # Cards Frame
        cards_f = tk.Frame(f, bg=BG)
        cards_f.pack(fill="x", padx=20, pady=10)
        
        nxt_m = (datetime.datetime.now().replace(day=28) + datetime.timedelta(days=4)).strftime("%B %Y")
        tk.Label(cards_f, text=f"Predictions for {nxt_m}", font=("Segoe UI", 12, "bold"), bg=BG, fg=TS).pack(anchor="w", pady=(0, 10))
        
        row_f = tk.Frame(cards_f, bg=BG)
        row_f.pack(fill="x")

        self._kpi(row_f, "Expected Income", f"{fmt_disp(pred_inc)} {trend_inc}", f"Confidence: {conf_inc}", GR, "💰").pack(side="left", fill="x", expand=True, padx=(0, 10))
        self._kpi(row_f, "Expected Expense", f"{fmt_disp(pred_exp)} {trend_exp}", f"Confidence: {conf_exp}", RE, "💸").pack(side="left", fill="x", expand=True, padx=(0, 10))
        self._kpi(row_f, "Expected Savings", f"{fmt_disp(pred_sav)} {trend_sav}", "Based on income vs expense", BL, "🏦").pack(side="left", fill="x", expand=True)

        # Cash Balance and Budget Utilization
        row2_f = tk.Frame(cards_f, bg=BG)
        row2_f.pack(fill="x", pady=20)
        
        avg_exp = sum([monthly_exp[m] for m in months[-3:]]) / min(3, len(months))
        total_bgt = sum([b["amount"] for b in get_all_budgets() if b["month"] == months[-1]])
        if total_bgt > 0:
            util = (pred_exp / total_bgt) * 100
        else:
            util = 0
            
        self._kpi(row2_f, "Expected Budget Utilization", f"{util:.1f}%", f"Avg past exp: {fmt_disp(avg_exp)}", OR, "📊").pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        curr_cash = sum([i["qty"]*i["current_price"] for i in _ld("investments") if i["type"] == "Cash"]) # Approximate cash
        # Assuming current net cash = total all time income - total all time expense + net worth cash
        all_inc = sum(monthly_inc.values())
        all_exp = sum(monthly_exp.values())
        est_balance = all_inc - all_exp
        
        self._kpi(row2_f, "Est. Cash Balance", f"{fmt_disp(est_balance + pred_sav)}", "End of next month", CY, "💵").pack(side="left", fill="x", expand=True)
