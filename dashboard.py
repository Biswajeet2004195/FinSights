"""
Finsights Premium Dashboard  ·  dashboard.py
All 10 modules: Overview, Income, Expenses, Budget, Investments, Goals,
                AI Insights, Health Score, Notifications, Reports
"""
# ── DPI Scaling (macOS crisp text quality) ────────────────────────────────────
try:
    import ctypes
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except:
        pass

import tkinter as tk
from config import *
from base_dashboard import BaseDashboard
from modules.overview import OverviewMixin
from modules.income import IncomeMixin
from modules.expenses import ExpenseMixin
from modules.budget import BudgetMixin
from modules.investments import InvestmentMixin
from modules.goals import GoalMixin
from modules.insights import InsightMixin
from modules.health import HealthMixin
from modules.notifications import NotificationMixin
from modules.reports import ReportMixin
from modules.admin import AdminMixin
from modules.profile import ProfileMixin

# ═══════════════════════════════════════════════════════════════════════════════
class FinsightsDashboard(
    OverviewMixin,
    IncomeMixin,
    ExpenseMixin,
    BudgetMixin,
    InvestmentMixin,
    GoalMixin,
    InsightMixin,
    HealthMixin,
    NotificationMixin,
    ReportMixin,
    AdminMixin,
    ProfileMixin,
    BaseDashboard
):
# ═══════════════════════════════════════════════════════════════════════════════
    def __init__(self, root, username="User", email="test@test.com"):
        self.root = root
        self.username = username
        self.email = email
        self.active_nav = ""
        self._active_canvas = None
        self._setup_win()
        self._setup_styles()
        self._setup_wheel()
        self._build_sidebar()
        self._right_panel = ctk.CTkFrame(self.root, fg_color=BG, corner_radius=0)
        self._right_panel.pack(side="right", fill="both", expand=True)
        self._build_header()
        self._build_content()
        self.show_overview()

# ═══════════════════════════════════════════════════════════════════════════════
def launch_dashboard(parent_window, username, email):
    """
    Call from regform.py after a successful login.
    Hides the login window and opens the dashboard.
    """
    parent_window.withdraw()
    dash = tk.Toplevel()
    dash.protocol("WM_DELETE_WINDOW",
                  lambda: (dash.destroy(), parent_window.destroy()))
    FinsightsDashboard(dash, username, email)

# Stand-alone entry point (for direct testing)
if __name__ == "__main__":
    root = ctk.CTk()
    FinsightsDashboard(root, "Demo User")
    root.mainloop()
