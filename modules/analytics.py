import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tkinter as tk
from tkinter import ttk
from collections import defaultdict
from datetime import datetime

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.ticker as mticker

from config import *


class AnalyticsMixin:
    """Full Analytics dashboard — income, expenses, savings, charts, summary."""

    # ─────────────────────────────────────────────────────────────────────────
    def show_analytics(self):
        self._set_nav("Analytics")
        self._set_title("Analytics")
        self._clear()

        pg = self._scrollable(self._active_page_frame)
        self._sec(pg, "📊 Analytics Dashboard", "Deep dive into your complete financial picture")

        # ── Load & aggregate data ──────────────────────────────────────────
        trans = _ld("transactions")
        dc    = GLOBAL_STATE["display_currency"]

        expenses  = [r for r in trans if r.get("type") == "expense"]
        incomes   = [r for r in trans if r.get("type") == "income"]

        def _conv(r):
            return convert_currency(r["amount"], r.get("currency", "INR"), dc)

        total_inc = sum(_conv(r) for r in incomes)
        total_exp = sum(_conv(r) for r in expenses)
        total_sav = total_inc - total_exp
        sav_rate  = (total_sav / total_inc * 100) if total_inc > 0 else 0.0

        # Per-category expense totals
        cat_exp = defaultdict(float)
        for r in expenses:
            cat_exp[r.get("category", "Others")] += _conv(r)

        # Per-month income & expense totals
        monthly_inc = defaultdict(float)
        monthly_exp = defaultdict(float)
        for r in incomes:
            monthly_inc[r["date"][:7]] += _conv(r)
        for r in expenses:
            monthly_exp[r["date"][:7]] += _conv(r)

        # Sorted months (union of both sets)
        all_months = sorted(set(monthly_inc) | set(monthly_exp))

        # Monthly savings
        monthly_sav = {m: monthly_inc.get(m, 0) - monthly_exp.get(m, 0)
                       for m in all_months}

        # Highest single expense transaction
        highest_tx     = None
        highest_tx_amt = 0.0
        for r in expenses:
            a = _conv(r)
            if a > highest_tx_amt:
                highest_tx     = r
                highest_tx_amt = a

        top_cat     = max(cat_exp, key=cat_exp.get) if cat_exp else "N/A"
        top_cat_amt = cat_exp.get(top_cat, 0.0)
        avg_monthly = (sum(monthly_exp.values()) / len(monthly_exp)
                       if monthly_exp else 0.0)

        # ── Row 1 — Primary KPIs ───────────────────────────────────────────
        r1 = tk.Frame(pg, bg=BG)
        r1.pack(fill="x", padx=20, pady=(6, 4))

        sav_clr  = GR if total_sav >= 0 else RE
        rate_txt = f"{sav_rate:+.1f}% savings rate"
        self._kpi(r1, "Total Income",   fmt_disp(total_inc),
                  f"{len(incomes)} transactions", GR, "💰").pack(
                      side="left", fill="both", expand=True, padx=(0, 8))
        self._kpi(r1, "Total Expenses", fmt_disp(total_exp),
                  f"{len(expenses)} transactions", RE, "💸").pack(
                      side="left", fill="both", expand=True, padx=(0, 8))
        self._kpi(r1, "Net Savings",    fmt_disp(total_sav),
                  rate_txt, sav_clr, "🏦").pack(
                      side="left", fill="both", expand=True)

        # ── Row 2 — Secondary KPIs ─────────────────────────────────────────
        r2 = tk.Frame(pg, bg=BG)
        r2.pack(fill="x", padx=20, pady=(0, 10))

        ht_desc = ""
        if highest_tx:
            raw_desc = highest_tx.get("desc", "N/A")
            ht_desc  = (raw_desc[:18] + "…") if len(raw_desc) > 18 else raw_desc

        self._kpi(r2, "Top Spending Category", top_cat,
                  fmt_disp(top_cat_amt), OR, "🏆").pack(
                      side="left", fill="both", expand=True, padx=(0, 8))
        self._kpi(r2, "Highest Single Expense", fmt_disp(highest_tx_amt),
                  ht_desc or "No expenses yet", PK, "🔥").pack(
                      side="left", fill="both", expand=True, padx=(0, 8))
        self._kpi(r2, "Avg Monthly Expense", fmt_disp(avg_monthly),
                  f"Across {len(monthly_exp)} months", BL, "📅").pack(
                      side="left", fill="both", expand=True)

        # ── Charts Row 1 — Pie + Bar ───────────────────────────────────────
        self._ana_pie_and_bar(pg, cat_exp, all_months, monthly_inc, monthly_exp)

        # ── Charts Row 2 — Savings Trend ──────────────────────────────────
        self._ana_savings_trend(pg, all_months, monthly_sav)

        # ── Recent Financial Summary ───────────────────────────────────────
        self._ana_summary_table(pg, all_months, monthly_inc, monthly_exp, monthly_sav)

        # Bottom spacer
        tk.Frame(pg, bg=BG, height=24).pack()

    # ─────────────────────────────────────────────────────────────────────────
    # Pie Chart (Category Spend) + Grouped Bar Chart (Income vs Expense)
    # ─────────────────────────────────────────────────────────────────────────
    def _ana_pie_and_bar(self, parent, cat_exp, all_months,
                         monthly_inc, monthly_exp):
        row = tk.Frame(parent, bg=BG)
        row.pack(fill="x", padx=20, pady=(0, 10))

        # ── Pie ──────────────────────────────────────────────────────────
        pie_card = tk.Frame(row, bg=CB)
        pie_card.pack(side="left", fill="both", expand=True, padx=(0, 8))
        tk.Frame(pie_card, bg=CY, height=2).pack(fill="x")
        tk.Label(pie_card, text="Spending by Category",
                 font=("Segoe UI", 12, "bold"), bg=CB, fg=TP).pack(pady=(10, 4))

        fig1 = Figure(figsize=(4.8, 3.8), facecolor=CB)
        ax1  = fig1.add_subplot(111)
        ax1.set_facecolor(CB)

        if cat_exp:
            labels = list(cat_exp.keys())
            sizes  = list(cat_exp.values())

            fallback = [GR, RE, BL, OR, PK, CY, PR, GO, TS,
                        "#f43f5e", "#14b8a6", "#8b5cf6"]
            colors = []
            for i, cat in enumerate(labels):
                c = CAT_CLR.get(cat)
                colors.append(c if c else fallback[i % len(fallback)])

            wedges, _, autotexts = ax1.pie(
                sizes, labels=None, colors=colors,
                autopct="%1.0f%%", startangle=90,
                textprops={"color": TP, "fontsize": 8, "weight": "bold"},
                pctdistance=0.72, wedgeprops={"linewidth": 0.5, "edgecolor": CB}
            )
            ax1.legend(
                wedges, labels,
                title="Categories",
                loc="center left",
                bbox_to_anchor=(0.88, 0.5),
                fontsize=7,
                title_fontsize=7,
                facecolor=CB, edgecolor=BD, labelcolor=TP
            )
            fig1.subplots_adjust(right=0.60, left=0.05, top=0.95, bottom=0.05)
        else:
            ax1.text(0.5, 0.5, "No expense data",
                     color=TS, ha="center", va="center", fontsize=11)
            ax1.axis("off")

        c1 = FigureCanvasTkAgg(fig1, master=pie_card)
        c1.draw()
        c1.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=(0, 10))

        # ── Grouped Bar Chart — Income vs Expense per month ──────────────
        bar_card = tk.Frame(row, bg=CB)
        bar_card.pack(side="left", fill="both", expand=True)
        tk.Frame(bar_card, bg=AC, height=2).pack(fill="x")
        tk.Label(bar_card, text="Monthly Income vs Expense",
                 font=("Segoe UI", 12, "bold"), bg=CB, fg=TP).pack(pady=(10, 4))

        fig2 = Figure(figsize=(5.6, 3.8), facecolor=CB)
        ax2  = fig2.add_subplot(111)
        ax2.set_facecolor(CB)
        ax2.tick_params(colors=TS, labelsize=8)
        for sp in ax2.spines.values():
            sp.set_color(BD)
        ax2.yaxis.set_major_formatter(
            mticker.FuncFormatter(lambda v, _: self._short_num(v))
        )

        if all_months:
            # Show last 12 months max to keep chart readable
            show_months = all_months[-12:]
            xs   = list(range(len(show_months)))
            inc_ = [monthly_inc.get(m, 0) for m in show_months]
            exp_ = [monthly_exp.get(m, 0) for m in show_months]
            w    = 0.35
            ax2.bar([x - w / 2 for x in xs], inc_, w,
                    color=GR, label="Income", alpha=0.9)
            ax2.bar([x + w / 2 for x in xs], exp_, w,
                    color=RE, label="Expense", alpha=0.9)
            ax2.set_xticks(xs)
            # Short month labels e.g. "Jan'25"
            short = [datetime.strptime(m, "%Y-%m").strftime("%b'%y")
                     for m in show_months]
            ax2.set_xticklabels(short, rotation=40, ha="right", fontsize=7)
            leg = ax2.legend(facecolor=CB, edgecolor=BD, labelcolor=TP,
                             fontsize=8)
            ax2.grid(axis="y", color=BD, linewidth=0.5, linestyle="--", alpha=0.7)
            fig2.subplots_adjust(bottom=0.22, top=0.95, left=0.12, right=0.97)
        else:
            ax2.text(0.5, 0.5, "No data yet",
                     color=TS, ha="center", va="center", fontsize=11)
            ax2.axis("off")

        c2 = FigureCanvasTkAgg(fig2, master=bar_card)
        c2.draw()
        c2.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=(0, 10))

    # ─────────────────────────────────────────────────────────────────────────
    # Monthly Savings Trend (line chart)
    # ─────────────────────────────────────────────────────────────────────────
    def _ana_savings_trend(self, parent, all_months, monthly_sav):
        card = tk.Frame(parent, bg=CB)
        card.pack(fill="x", padx=20, pady=(0, 10))
        tk.Frame(card, bg=CY, height=2).pack(fill="x")
        tk.Label(card, text="Monthly Savings Trend",
                 font=("Segoe UI", 12, "bold"), bg=CB, fg=TP).pack(
                     anchor="w", padx=14, pady=(10, 4))

        fig = Figure(figsize=(10, 2.8), facecolor=CB)
        ax  = fig.add_subplot(111)
        ax.set_facecolor(CB)
        ax.tick_params(colors=TS, labelsize=8)
        for sp in ax.spines.values():
            sp.set_color(BD)
        ax.yaxis.set_major_formatter(
            mticker.FuncFormatter(lambda v, _: self._short_num(v))
        )

        if all_months:
            show_months = all_months[-18:]
            vals = [monthly_sav.get(m, 0) for m in show_months]
            xs   = list(range(len(show_months)))

            # Colour-fill: positive savings = green, negative = red
            pos_vals = [max(v, 0) for v in vals]
            neg_vals = [min(v, 0) for v in vals]

            ax.bar(xs, pos_vals, color=GR, alpha=0.55, label="Savings")
            ax.bar(xs, neg_vals, color=RE, alpha=0.55, label="Deficit")
            ax.plot(xs, vals, color=CY, linewidth=2, marker="o",
                    markersize=4, zorder=5)
            ax.axhline(0, color=BD, linewidth=0.8, linestyle="--")

            short = [datetime.strptime(m, "%Y-%m").strftime("%b'%y")
                     for m in show_months]
            ax.set_xticks(xs)
            ax.set_xticklabels(short, rotation=40, ha="right", fontsize=7)
            ax.legend(facecolor=CB, edgecolor=BD, labelcolor=TP, fontsize=8)
            ax.grid(axis="y", color=BD, linewidth=0.5, linestyle="--", alpha=0.6)
            fig.subplots_adjust(bottom=0.22, top=0.94, left=0.08, right=0.98)
        else:
            ax.text(0.5, 0.5, "No transaction data yet",
                    color=TS, ha="center", va="center", fontsize=12)
            ax.axis("off")

        canvas = FigureCanvasTkAgg(fig, master=card)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True,
                                    padx=8, pady=(0, 10))

    # ─────────────────────────────────────────────────────────────────────────
    # Recent Financial Summary Table
    # ─────────────────────────────────────────────────────────────────────────
    def _ana_summary_table(self, parent, all_months,
                           monthly_inc, monthly_exp, monthly_sav):
        self._sec(parent, "Recent Financial Summary",
                  "Month-by-month breakdown (latest first)")

        if not all_months:
            tk.Label(parent, text="No transaction data yet.",
                     font=("Segoe UI", 11), bg=BG, fg=TS).pack(pady=20)
            return

        cols    = ["Month", "Income", "Expenses", "Savings", "Savings %"]
        widths  = [140, 160, 160, 160, 120]
        tf, tv  = self._tv(parent, cols, widths, height=min(12, len(all_months)))
        tf.pack(fill="both", expand=True, padx=20, pady=(0, 8))

        tv.tag_configure("pos_sav", foreground=GR)
        tv.tag_configure("neg_sav", foreground=RE)

        rows = []
        for m in reversed(all_months):
            inc  = monthly_inc.get(m, 0.0)
            exp  = monthly_exp.get(m, 0.0)
            sav  = monthly_sav.get(m, 0.0)
            rate = (sav / inc * 100) if inc > 0 else 0.0
            label = datetime.strptime(m, "%Y-%m").strftime("%B %Y")
            tag   = "pos_sav" if sav >= 0 else "neg_sav"
            rows.append((
                m, label,
                fmt_disp(inc),
                fmt_disp(exp),
                fmt_disp(sav),
                f"{rate:+.1f}%",
                tag
            ))

        # Custom insert (tag is the 7th element, values are elements 1-5)
        tv.delete(*tv.get_children())
        for i, row in enumerate(rows):
            iid    = row[0]
            vals   = row[1:6]
            tag    = row[6]
            zebra  = "odd" if i % 2 else "even"
            tv.insert("", "end", iid=iid, values=vals, tags=(zebra, tag))

    # ─────────────────────────────────────────────────────────────────────────
    # Utility: compact number formatter for chart axes
    # ─────────────────────────────────────────────────────────────────────────
    def _short_num(self, v):
        sym = get_currency_symbol(GLOBAL_STATE.get("display_currency", "INR"))
        av  = abs(v)
        if av >= 1_00_00_000:      # ≥ 1 Cr
            return f"{sym}{v/1_00_00_000:.1f}Cr"
        elif av >= 1_00_000:       # ≥ 1 L
            return f"{sym}{v/1_00_000:.1f}L"
        elif av >= 1_000:          # ≥ 1 K
            return f"{sym}{v/1_000:.0f}K"
        else:
            return f"{sym}{v:.0f}"
