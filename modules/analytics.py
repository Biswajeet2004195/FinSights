import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from config import *
from collections import defaultdict

class AnalyticsMixin:
    def show_analytics(self):
        self._set_nav("Analytics")
        self._set_title("Expense Analytics")
        self._clear()

        f = self._scrollable(self._active_page_frame)

        # Header
        self._sec(f, "Analytics Dashboard", "Deep dive into your financial data")

        # Top KPIs frame
        kpi_f = tk.Frame(f, bg=BG)
        kpi_f.pack(fill="x", padx=20, pady=10)

        # Load data
        trans = _ld("transactions")

        # Calculate metrics
        expenses = [r for r in trans if r["type"] == "expense"]
        incomes = [r for r in trans if r["type"] == "income"]

        dc = GLOBAL_STATE["display_currency"]
        total_exp = sum(convert_currency(r["amount"], r.get("currency", "INR"), dc) for r in expenses)
        total_inc = sum(convert_currency(r["amount"], r.get("currency", "INR"), dc) for r in incomes)

        cat_exp = defaultdict(float)
        monthly_exp = defaultdict(float)

        highest_tx = None
        highest_amt_conv = 0
        
        for r in expenses:
            amt_conv = convert_currency(r["amount"], r.get("currency", "INR"), dc)
            cat_exp[r["category"]] += amt_conv
            m = r["date"][:7] # YYYY-MM
            monthly_exp[m] += amt_conv
            if not highest_tx or amt_conv > highest_amt_conv:
                highest_tx = r
                highest_amt_conv = amt_conv
        
        top_cat = max(cat_exp, key=cat_exp.get) if cat_exp else "N/A"
        top_cat_amt = cat_exp.get(top_cat, 0)
        
        avg_monthly = sum(monthly_exp.values()) / len(monthly_exp) if monthly_exp else 0
        
        # Display KPIs
        self._kpi(kpi_f, "Top Category", top_cat, fmt_disp(top_cat_amt), RE, "🏆").pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        highest_amt = highest_amt_conv if highest_tx else 0
        highest_desc = highest_tx["desc"][:15] + "..." if highest_tx and len(highest_tx["desc"]) > 15 else (highest_tx["desc"] if highest_tx else "N/A")
        self._kpi(kpi_f, "Highest Txn", fmt_disp(highest_amt), highest_desc, OR, "🔥").pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self._kpi(kpi_f, "Avg Monthly", fmt_disp(avg_monthly), "All-time", BL, "📅").pack(side="left", fill="x", expand=True)

        # Charts Area (Pie and Line)
        chart_f1 = tk.Frame(f, bg=BG)
        chart_f1.pack(fill="x", padx=20, pady=10)

        # Pie Chart: Category Distribution
        pie_card = tk.Frame(chart_f1, bg=CB, bd=0)
        pie_card.pack(side="left", fill="both", expand=True, padx=(0, 10))
        tk.Label(pie_card, text="Category Distribution", font=("Segoe UI", 12, "bold"), bg=CB, fg=TP).pack(pady=10)
        
        fig1 = Figure(figsize=(5, 4), facecolor=CB)
        ax1 = fig1.add_subplot(111)
        ax1.set_facecolor(CB)
        
        if cat_exp:
            labels = list(cat_exp.keys())
            sizes = list(cat_exp.values())
            
            CUSTOM_PIE_COLORS = {
                "Food": GR,
                "Food & Dining": GR,
                "Transport": BL,
                "Entertainment": OR,
                "Healthcare": PR,
                "Education": CY,
                "Shopping": PK,
                "Rent/Housing": GO,
                "Utilities": "#facc15",
                "Others": TS
            }
            
            colors = []
            import matplotlib.cm as cm
            try:
                cmap = cm.get_cmap('tab20')
            except AttributeError:
                cmap = cm.tab20
                
            for i, cat in enumerate(labels):
                if cat in CUSTOM_PIE_COLORS:
                    colors.append(CUSTOM_PIE_COLORS[cat])
                elif cat in CAT_CLR:
                    colors.append(CAT_CLR[cat])
                else:
                    colors.append(cmap(i % 20))

            wedges, texts, autotexts = ax1.pie(
                sizes, 
                labels=None, 
                colors=colors, 
                autopct='%1.1f%%', 
                startangle=90, 
                textprops={'color': TP, 'fontsize': 9, 'weight': 'bold'},
                pctdistance=0.7
            )
            
            ax1.legend(
                wedges, labels,
                title="Categories",
                loc="center left",
                bbox_to_anchor=(0.9, 0.5),
                facecolor=CB, edgecolor=BD, labelcolor=TP
            )
            fig1.subplots_adjust(right=0.6) # Make room for legend
        else:
            ax1.text(0.5, 0.5, "No Expense Data", color=TS, ha='center', va='center')
        
        canvas1 = FigureCanvasTkAgg(fig1, master=pie_card)
        canvas1.draw()
        canvas1.get_tk_widget().pack(fill="both", expand=True)

        # Line Chart: Monthly Trend
        line_card = tk.Frame(chart_f1, bg=CB, bd=0)
        line_card.pack(side="left", fill="both", expand=True)
        tk.Label(line_card, text="Monthly Expense Trend", font=("Segoe UI", 12, "bold"), bg=CB, fg=TP).pack(pady=10)
        
        fig2 = Figure(figsize=(5, 4), facecolor=CB)
        ax2 = fig2.add_subplot(111)
        ax2.set_facecolor(CB)
        ax2.tick_params(colors=TS)
        for spine in ax2.spines.values():
            spine.set_color(BD)

        if monthly_exp:
            sorted_months = sorted(monthly_exp.keys())
            vals = [monthly_exp[m] for m in sorted_months]
            ax2.plot(sorted_months, vals, color=CY, marker='o', linewidth=2)
            ax2.set_xticks(range(len(sorted_months)))
            ax2.set_xticklabels(sorted_months, rotation=45, ha='right')
        else:
            ax2.text(0.5, 0.5, "No Data", color=TS, ha='center', va='center')
            
        fig2.tight_layout()
        canvas2 = FigureCanvasTkAgg(fig2, master=line_card)
        canvas2.draw()
        canvas2.get_tk_widget().pack(fill="both", expand=True)

        # Bar Chart: Income vs Expenses
        chart_f2 = tk.Frame(f, bg=BG)
        chart_f2.pack(fill="x", padx=20, pady=20)
        
        bar_card = tk.Frame(chart_f2, bg=CB, bd=0)
        bar_card.pack(fill="both", expand=True)
        tk.Label(bar_card, text="Income vs Expenses (All Time)", font=("Segoe UI", 12, "bold"), bg=CB, fg=TP).pack(pady=10)

        fig3 = Figure(figsize=(10, 4), facecolor=CB)
        ax3 = fig3.add_subplot(111)
        ax3.set_facecolor(CB)
        ax3.tick_params(colors=TS)
        for spine in ax3.spines.values():
            spine.set_color(BD)
            
        bar_labels = ['Total']
        income_vals = [total_inc]
        expense_vals = [total_exp]
        
        x = range(len(bar_labels))
        width = 0.35
        
        ax3.bar([p - width/2 for p in x], income_vals, width, label='Income', color=GR)
        ax3.bar([p + width/2 for p in x], expense_vals, width, label='Expense', color=RE)
        
        ax3.set_xticks(x)
        ax3.set_xticklabels(bar_labels)
        
        # Style the legend to match the theme
        legend = ax3.legend(facecolor=CB, edgecolor=BD, labelcolor=TP)
        
        canvas3 = FigureCanvasTkAgg(fig3, master=bar_card)
        canvas3.draw()
        canvas3.get_tk_widget().pack(fill="both", expand=True, pady=(0, 20))
