# FinSights: Premium Personal Finance Manager

FinSights is a feature-rich, premium desktop-based personal finance management application built using Python and CustomTkinter. Designed with modern UX/UI guidelines (including full dark/light theme styling, dynamic responsiveness, and high DPI support), the application provides a modular, production-grade architecture that makes it perfect as an internship showcase project.

---

## 🚀 Key Features

The application leverages a modular, mixin-based Python architecture to support a wide range of modules:

### 1. Secure Authentication & Onboarding (`regform.py`)
- **Credentials Security:** Secure passwords storage using salt-based HMAC-SHA256 encryption.
- **Robust Validation:** Real-time client-side checks for email formats, password strength, and duplicate usernames.
- **Fluid UI:** Custom transition animations (fade-in/fade-out) between login, registration, and onboarding panels.

### 2. Multi-Currency & Live Exchange Rates (`currency_utils.py`)
- **Live Rates Fetching:** Interacts with external exchange rate APIs to grab live conversions (INR, USD, EUR, etc.).
- **Smart Fallback:** Caching mechanism that falls back to pre-defined exchange rates if the API request times out or is offline.

### 3. Core Dashboard Modules (`modules/`)
- **Overview:** Dynamic KPI cards (Income, Expense, Savings Rate, Net Worth) with interactive recent transactions list.
- **Income & Expense Tracker:** Easy forms for recording financial events, categorizing, and editing entries.
- **Analytics & Trends:** Interactive charts and breakdowns powered by Matplotlib.
- **Budgeting & Savings Goals:** Define spending limits per category, track goal progress with dynamic progress bars.
- **Investments & Net Worth:** Track investment portfolios, assets vs liabilities, and net worth growth history.
- **Recurring Transactions:** Automate scheduled expenses and income with automatic background processing.
- **Forecasts:** Predictive models forecasting cash flows and future budget limits.
- **AI Insights:** Rule-based analytics generating personalized financial advice and health tips.
- **Financial Health Score:** Multi-dimensional algorithm evaluating debt-to-income ratios, savings rates, and budget discipline.
- **Notifications & Alerts:** Smart reminders for recurring events, budget warnings, and goal achievements.
- **Reports Export (`reports.py`):**
  - Generate visual, print-ready PDF statements using **ReportLab**.
  - Export structured raw spreadsheets using **OpenPyXL**.

---

## 🛠️ Technology Stack

- **Core Logic:** Python 3.8+
- **GUI Framework:** CustomTkinter (modern tk styling), Tkinter
- **Visualization:** Matplotlib, NumPy
- **Spreadsheets & Docs:** OpenPyXL, ReportLab
- **Security:** `hmac`, `hashlib` (standard library encryption)
- **Networking:** `urllib` (lightweight API calling)

---

## 📂 Project Architecture

```
Finsights/
│
├── regform.py                 # Entry point: Sign in / Registration forms
├── dashboard.py               # Main Dashboard application class coordinating all Mixins
├── base_dashboard.py          # Shell layout (sidebar, header, content area, dynamic scrolling canvas)
├── config.py                  # Colors, dark/light theme definitions, global state, paths, and caching
├── currency_utils.py          # Currency converter with exchange API logic
├── requirements.txt           # Python library dependencies
│
├── modules/                   # Componentized features (Mixin architecture)
│   ├── __init__.py
│   ├── admin.py               # System diagnostics & admin features
│   ├── analytics.py           # Charts, graph plotting, trends
│   ├── backup.py              # Exporting/importing database files
│   ├── budget.py              # Custom category budgets
│   ├── expenses.py            # Expense list & form handlers
│   ├── forecast.py            # Financial projections
│   ├── goals.py               # Savings targets
│   ├── health.py              # Financial Health Score calculation
│   ├── income.py              # Income tracker list & forms
│   ├── insights.py            # AI advisory & tips
│   ├── investments.py         # Investment tracking
│   ├── net_worth.py           # Balance sheet calculation
│   ├── notifications.py       # Notification center
│   ├── overview.py            # Core summary landing screen
│   ├── profile.py             # User profile details
│   ├── recurring.py           # Scheduled payments processor
│   ├── reports.py             # Report generation (PDF & Excel)
│   └── settings.py            # Theme selectors & preferences
│
└── data/                      # Local JSON database storage (auto-generated)
```

---

## 💻 Installation & Setup

1. **Clone the Repository**
   ```bash
   git clone <repository_url>
   cd Finsights
   ```

2. **Set Up a Virtual Environment (Recommended)**
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # macOS/Linux:
   source .venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**
   ```bash
   python regform.py
   ```

---

## 💡 Key Coding Best Practices Demonstrated

- **Design Patterns (Mixins):** The project avoids a massive single-file dashboard by using a Mixin-based class architecture, making the application modular, readable, and highly maintainable.
- **Secure Storage:** Storing passwords using secure hash functions (`sha256`) and dynamic user-specific salt keys.
- **Dynamic Layout & DPI Awareness:** Embedded OS scaling detection for crisp display render on high-resolution screens (4k, Retina displays).
- **Graceful Error Handling:** Fallback rates for offline usage, clean handling of empty fields, and verification alerts.
- **Responsive CustomTkinter UI:** Utilization of grid weight distributions, matching color cards, and modern glassmorphism aesthetic guidelines.
