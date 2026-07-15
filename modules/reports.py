import tkinter as tk
from tkinter import filedialog, messagebox
import csv
from datetime import datetime, timedelta
from collections import defaultdict
from config import *
from base_dashboard import BaseDashboard

class ReportMixin(BaseDashboard):
    def show_reports(self):

        self._clear(); self._set_nav("Reports"); self._set_title("Reports")
        pg = self._scrollable(self._cf)
        self._sec(pg, "📋 Financial Reports", "Monthly analysis and data export")

        trans = _ld("transactions"); cm = curr_m()
        mi = sum(r["amount"] for r in trans if r["type"] == "income"  and r["date"].startswith(cm))
        me = sum(r["amount"] for r in trans if r["type"] == "expense" and r["date"].startswith(cm))
        ms = mi - me; sr = ms / mi * 100 if mi else 0

        srow = ctk.CTkFrame(pg, fg_color=BG, corner_radius=10); srow.pack(fill="x", padx=20, pady=(4, 12))
        self._kpi(srow, "Income",   fmt_inr(mi), "This month",     GR, "💰").pack(side="left", ipadx=8, ipady=4, padx=(0, 10), expand=True, fill="both")
        self._kpi(srow, "Expenses", fmt_inr(me), "This month",     RE, "💸").pack(side="left", ipadx=8, ipady=4, padx=(0, 10), expand=True, fill="both")
        self._kpi(srow, "Savings",  fmt_inr(ms), f"Rate: {sr:.0f}%", CY, "💎").pack(side="left", ipadx=8, ipady=4, expand=True, fill="both")

        # Bar chart card
        ccard = ctk.CTkFrame(pg, fg_color=BD, corner_radius=10); ccard.pack(fill="x", padx=20, pady=(0, 12))
        ccardi = ctk.CTkFrame(ccard, fg_color=CB, corner_radius=10); ccardi.pack(padx=1, pady=1, fill="x")
        ctk.CTkFrame(ccardi, fg_color=AC, height=3, corner_radius=10).pack(fill="x")
        tk.Label(ccardi, text="📊  Income vs Expenses — Last 6 Months",
                 font=("Segoe UI", 11, "bold"), bg=CB, fg=TP).pack(anchor="w", padx=14, pady=(10, 4))

        months_data = []
        for mo in range(5, -1, -1):
            d = datetime.now() - timedelta(days=30 * mo)
            ym = d.strftime("%Y-%m"); lbl = d.strftime("%b")
            inc = sum(r["amount"] for r in trans if r["type"] == "income"  and r["date"].startswith(ym))
            exp = sum(r["amount"] for r in trans if r["type"] == "expense" and r["date"].startswith(ym))
            months_data.append((lbl, inc, exp))

        bc = tk.Canvas(ccardi, height=240, bg=CB, bd=0, highlightthickness=0)
        bc.pack(fill="x", padx=14, pady=(4, 8))
        self.root.after(80, lambda: self._draw_bar_chart(bc, months_data))
        bc.bind("<Configure>", lambda e, c=bc, d=months_data: self._draw_bar_chart(c, d))

        leg = ctk.CTkFrame(ccardi, fg_color=CB, corner_radius=10); leg.pack(padx=14, pady=(0, 12))
        ctk.CTkFrame(leg, fg_color=GR, width=18, height=10, corner_radius=10).pack(side="left", pady=4)
        tk.Label(leg, text=" Income", font=("Segoe UI Light", 9), bg=CB, fg=TS).pack(side="left")
        ctk.CTkFrame(leg, fg_color=RE, width=18, height=10, corner_radius=10).pack(side="left", padx=(20, 0), pady=4)
        tk.Label(leg, text=" Expenses", font=("Segoe UI Light", 9), bg=CB, fg=TS).pack(side="left")

        # Category table
        tk.Label(pg, text="📊  Category Breakdown — Current Month",
                 font=("Segoe UI Semibold", 12), bg=BG, fg=TP).pack(anchor="w", padx=20, pady=(8, 4))
        cols = ["Category", "Transactions", "Total Spent", "Budget", "% of Budget"]
        tf, tv = self._tv(pg, cols, [200, 120, 140, 140, 120], height=10)
        tf.pack(fill="x", padx=20, pady=(0, 12))
        
        budgets = _ldd("budgets")
        cats = list(budgets.keys())
        cat_data = defaultdict(lambda: {"count": 0, "total": 0.0})
        for r in trans:
            if r["type"] == "expense" and r["date"].startswith(cm):
                cat_data[r["category"]]["count"]  += 1
                cat_data[r["category"]]["total"]  += r["amount"]
        rows = []
        for cat in cats:
            d  = cat_data[cat]; bgt = budgets.get(cat, 0)
            pct = d["total"] / bgt * 100 if bgt else 0
            rows.append((cat, cat, str(d["count"]), fmt_inr(d["total"]),
                         fmt_inr(bgt), f"{pct:.0f}%"))
        self._tv_fill(tv, rows)

        # Export
        ew = ctk.CTkFrame(pg, fg_color=BG, corner_radius=10); ew.pack(fill="x", padx=20, pady=(4, 20))

        def _export_all():
            fn = filedialog.asksaveasfilename(
                defaultextension=".csv", filetypes=[("CSV files", "*.csv")],
                initialfile="finsights_all_transactions.csv")
            if not fn: return
            with open(fn, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["Date", "Type", "Description", "Category", "Amount", "Notes"])
                for r in sorted(trans, key=lambda x: x["date"], reverse=True):
                    w.writerow([r["date"], r["type"], r["desc"],
                                r["category"], r["amount"], r.get("notes", "")])
            messagebox.showinfo("✅ Exported", f"Full report saved to:\n{fn}")

        self._tb_btn(ew, "⬇  Export PDF Report", lambda: self._export_pdf_report(cm_only=True), GR)
        self._tb_btn(ew, "📊  Export Excel Report", lambda: self._export_excel_report(cm_only=True), CY)
        self._tb_btn(ew, "📁  Export All Data (CSV)", _export_all, CB2)

    def _export_pdf_report(self, cm_only=True):
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib import colors
        except ImportError:
            try:
                import subprocess, sys
                subprocess.check_call([sys.executable, "-m", "pip", "install", "reportlab"])
                from reportlab.lib.pagesizes import letter
                from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
                from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
                from reportlab.lib import colors
            except Exception as ex:
                return messagebox.showerror("Error", f"ReportLab is not installed and could not be automatically installed.\nDetail: {ex}")

        fn = filedialog.asksaveasfilename(
            defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")],
            initialfile=f"finsights_{curr_m() if cm_only else 'all'}.pdf")
        if not fn: return
            
        doc = SimpleDocTemplate(fn, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        story = []
        
        styles = getSampleStyleSheet()
        
        primary_color = colors.HexColor("#0a84ff")
        secondary_color = colors.HexColor("#30d158")
        dark_neutral = colors.HexColor("#161617")
        light_neutral = colors.HexColor("#f4f4f5")
        text_color = colors.HexColor("#272728")
        
        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontSize=22,
            textColor=primary_color,
            spaceAfter=6
        )
        
        subtitle_style = ParagraphStyle(
            'SubtitleStyle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor("#8e8e93"),
            spaceAfter=15
        )
        
        heading_style = ParagraphStyle(
            'HeadingStyle',
            parent=styles['Heading2'],
            fontSize=13,
            textColor=dark_neutral,
            spaceBefore=14,
            spaceAfter=8
        )
        
        body_style = ParagraphStyle(
            'BodyStyle',
            parent=styles['Normal'],
            fontSize=9,
            textColor=text_color
        )
        
        body_header_style = ParagraphStyle(
            'BodyHeaderStyle',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.white,
            fontName="Helvetica-Bold"
        )
        
        story.append(Paragraph("Finsights — Financial Statement", title_style))
        scope_text = f"Report for month: {curr_m()}" if cm_only else "All-time financial report"
        story.append(Paragraph(f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}  •  {scope_text}", subtitle_style))
        story.append(Spacer(1, 10))
        
        trans = _ld("transactions")
        if cm_only:
            trans = [r for r in trans if r["date"].startswith(curr_m())]
            
        mi = sum(r["amount"] for r in trans if r["type"] == "income")
        me = sum(r["amount"] for r in trans if r["type"] == "expense")
        ms = mi - me
        sr = ms / mi * 100 if mi else 0
        
        summary_data = [
            [Paragraph("Total Income", body_header_style), Paragraph("Total Expenses", body_header_style), 
             Paragraph("Net Savings", body_header_style), Paragraph("Savings Rate", body_header_style)],
            [fmt_inr(mi), fmt_inr(me), fmt_inr(ms), f"{sr:.1f}%"]
        ]
        
        summary_table = Table(summary_data, colWidths=[135]*4)
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), primary_color),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BOTTOMPADDING', (0,0), (-1,0), 6),
            ('TOPPADDING', (0,0), (-1,0), 6),
            ('BACKGROUND', (0,1), (-1,1), light_neutral),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e4e4e7")),
            ('FONTSIZE', (0,1), (-1,1), 11),
            ('BOTTOMPADDING', (0,1), (-1,1), 8),
            ('TOPPADDING', (0,1), (-1,1), 8),
        ]))
        
        story.append(Paragraph("Financial Summary", heading_style))
        story.append(summary_table)
        story.append(Spacer(1, 12))
        
        # Category breakdown
        budgets = _ldd("budgets")
        spent_by = defaultdict(float)
        trans_count = defaultdict(int)
        for r in trans:
            if r["type"] == "expense":
                spent_by[r["category"]] += r["amount"]
                trans_count[r["category"]] += 1
                
        breakdown_data = [[
            Paragraph("Category", body_header_style), 
            Paragraph("Transactions", body_header_style), 
            Paragraph("Total Spent", body_header_style), 
            Paragraph("Budget Limit", body_header_style), 
            Paragraph("Utilization", body_header_style)
        ]]
        
        for cat in budgets.keys():
            spent = spent_by.get(cat, 0.0)
            count = trans_count.get(cat, 0)
            bgt = budgets.get(cat, 0.0)
            pct = spent / bgt * 100 if bgt else 0
            
            breakdown_data.append([
                cat,
                str(count),
                fmt_inr(spent),
                fmt_inr(bgt) if bgt else "No Limit",
                f"{pct:.1f}%" if bgt else "N/A"
            ])
            
        bd_table = Table(breakdown_data, colWidths=[160, 80, 100, 100, 100])
        bd_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), dark_neutral),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e4e4e7")),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, light_neutral]),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('TOPPADDING', (0,0), (-1,-1), 5),
        ]))
        
        story.append(Paragraph("Category Spending Breakdown", heading_style))
        story.append(bd_table)
        story.append(Spacer(1, 12))
        
        # Transactions list
        story.append(Paragraph("Recent Transactions", heading_style))
        tx_data = [[
            Paragraph("Date", body_header_style),
            Paragraph("Type", body_header_style),
            Paragraph("Description", body_header_style),
            Paragraph("Category", body_header_style),
            Paragraph("Amount", body_header_style)
        ]]
        
        sorted_tx = sorted(trans, key=lambda x: x["date"], reverse=True)
        for r in sorted_tx[:45]:
            sign = "+" if r["type"] == "income" else "−"
            amt_str = f"{sign}{fmt_inr(r['amount'])}"
            amt_color = secondary_color.hexval() if r["type"] == "income" else "#ff453a"
            
            tx_data.append([
                r["date"],
                r["type"].capitalize(),
                r["desc"][:25],
                r["category"],
                Paragraph(f"<font color='{amt_color}'><b>{amt_str}</b></font>", body_style)
            ])
            
        tx_table = Table(tx_data, colWidths=[80, 70, 160, 110, 120])
        tx_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), dark_neutral),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e4e4e7")),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, light_neutral]),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('TOPPADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(tx_table)
        if len(sorted_tx) > 45:
            story.append(Spacer(1, 4))
            story.append(Paragraph(f"<i>* Showing latest 45 of {len(sorted_tx)} transactions.</i>", subtitle_style))
            
        doc.build(story)
        messagebox.showinfo("✅ Exported", f"PDF report saved to:\n{fn}")

    def _export_excel_report(self, cm_only=True):
        try:
            import openpyxl
            from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
        except ImportError:
            try:
                import subprocess, sys
                subprocess.check_call([sys.executable, "-m", "pip", "install", "openpyxl"])
                import openpyxl
                from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
            except Exception as ex:
                return messagebox.showerror("Error", f"Could not load or install openpyxl.\nDetail: {ex}")
        
        fn = filedialog.asksaveasfilename(
            defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")],
            initialfile=f"finsights_{curr_m() if cm_only else 'all'}.xlsx")
        if not fn: return
            
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Transactions"
        
        title_font = Font(name="Segoe UI", size=16, bold=True, color="0A84FF")
        header_font = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
        bold_font = Font(name="Segoe UI", size=11, bold=True)
        regular_font = Font(name="Segoe UI", size=11)
        
        header_fill = PatternFill(start_color="161617", end_color="161617", fill_type="solid")
        
        thin_side = Side(border_style="thin", color="E4E4E7")
        border_all = Border(left=thin_side, right=thin_side, top=thin_side, bottom=thin_side)
        
        ws.merge_cells("A1:F1")
        ws["A1"] = "Finsights — Financial Transactions Statement"
        ws["A1"].font = title_font
        ws.row_dimensions[1].height = 30
        
        headers = ["Date", "Type", "Description", "Category", "Amount (₹)", "Notes"]
        for col_idx, h in enumerate(headers, 1):
            cell = ws.cell(row=3, column=col_idx, value=h)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center" if col_idx in [1, 2] else ("right" if col_idx == 5 else "left"))
            cell.border = border_all
        ws.row_dimensions[3].height = 24
        
        trans = _ld("transactions")
        if cm_only:
            trans = [r for r in trans if r["date"].startswith(curr_m())]
        sorted_tx = sorted(trans, key=lambda x: x["date"], reverse=True)
        
        row_idx = 4
        for r in sorted_tx:
            ws.cell(row=row_idx, column=1, value=r["date"]).alignment = Alignment(horizontal="center")
            ws.cell(row=row_idx, column=2, value=r["type"].capitalize()).alignment = Alignment(horizontal="center")
            ws.cell(row=row_idx, column=3, value=r["desc"])
            ws.cell(row=row_idx, column=4, value=r["category"])
            
            amt_cell = ws.cell(row=row_idx, column=5, value=r["amount"])
            amt_cell.number_format = '₹#,##0.00'
            amt_cell.font = Font(name="Segoe UI", size=11, color="30D158" if r["type"] == "income" else "FF453A")
            
            ws.cell(row=row_idx, column=6, value=r.get("notes", ""))
            
            for col_idx in range(1, 7):
                c = ws.cell(row=row_idx, column=col_idx)
                if col_idx != 5:
                    c.font = regular_font
                c.border = border_all
                
            row_idx += 1
            
        for col in ws.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            col_letter = openpyxl.utils.get_column_letter(col[0].column)
            ws.column_dimensions[col_letter].width = max(max_len + 3, 12)
            
        ws2 = wb.create_sheet(title="Summary & Budgets")
        ws2.merge_cells("A1:E1")
        ws2["A1"] = "Finsights — Summary & Budget Report"
        ws2["A1"].font = title_font
        ws2.row_dimensions[1].height = 30
        
        ws2["A3"] = "Metric"
        ws2["B3"] = "Amount (₹)"
        for cell in [ws2["A3"], ws2["B3"]]:
            cell.font = header_font
            cell.fill = header_fill
            cell.border = border_all
            
        mi = sum(r["amount"] for r in trans if r["type"] == "income")
        me = sum(r["amount"] for r in trans if r["type"] == "expense")
        ms = mi - me
        sr = ms / mi * 100 if mi else 0
        
        metrics = [
            ("Total Income", mi),
            ("Total Expenses", me),
            ("Net Savings", ms),
            ("Savings Rate (%)", sr / 100)
        ]
        
        for idx, (m, val) in enumerate(metrics, 4):
            ws2.cell(row=idx, column=1, value=m).font = bold_font
            ws2.cell(row=idx, column=1).border = border_all
            
            val_cell = ws2.cell(row=idx, column=2, value=val)
            val_cell.border = border_all
            if m == "Savings Rate (%)":
                val_cell.number_format = '0.0%'
                val_cell.font = bold_font
            else:
                val_cell.number_format = '₹#,##0.00'
                val_cell.font = Font(name="Segoe UI", size=11, bold=True, color="30D158" if val >= 0 else "FF453A")
                
        ws2["A10"] = "Category"
        ws2["B10"] = "Transactions"
        ws2["C10"] = "Spent (₹)"
        ws2["D10"] = "Budget (₹)"
        ws2["E10"] = "Utilization"
        
        for col_idx, h in enumerate(["Category", "Transactions", "Spent (₹)", "Budget (₹)", "Utilization"], 1):
            cell = ws2.cell(row=10, column=col_idx, value=h)
            cell.font = header_font
            cell.fill = header_fill
            cell.border = border_all
            
        budgets = _ldd("budgets")
        spent_by = defaultdict(float)
        trans_count = defaultdict(int)
        for r in trans:
            if r["type"] == "expense":
                spent_by[r["category"]] += r["amount"]
                trans_count[r["category"]] += 1
                
        row_idx = 11
        for cat in budgets.keys():
            spent = spent_by.get(cat, 0.0)
            count = trans_count.get(cat, 0)
            bgt = budgets.get(cat, 0.0)
            pct = spent / bgt if bgt else 0
            
            ws2.cell(row=row_idx, column=1, value=cat).font = regular_font
            ws2.cell(row=row_idx, column=2, value=count).font = regular_font
            
            spent_cell = ws2.cell(row=row_idx, column=3, value=spent)
            spent_cell.number_format = '₹#,##0.00'
            spent_cell.font = regular_font
            
            bgt_cell = ws2.cell(row=row_idx, column=4, value=bgt)
            bgt_cell.number_format = '₹#,##0.00'
            bgt_cell.font = regular_font
            
            pct_cell = ws2.cell(row=row_idx, column=5, value=pct)
            pct_cell.number_format = '0.0%'
            pct_cell.font = Font(name="Segoe UI", size=11, bold=True, color="FF453A" if pct >= 0.9 else ("FF9F0A" if pct >= 0.7 else "30D158"))
            
            for col_idx in range(1, 6):
                ws2.cell(row=row_idx, column=col_idx).border = border_all
                
            row_idx += 1
            
        for col in ws2.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            col_letter = openpyxl.utils.get_column_letter(col[0].column)
            ws2.column_dimensions[col_letter].width = max(max_len + 3, 14)
            
        wb.save(fn)
        messagebox.showinfo("✅ Exported", f"Excel report saved to:\n{fn}")
