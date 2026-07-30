import tkinter as tk
from tkinter import ttk
from config import *
import os

class SettingsMixin:
    def show_settings(self):
        self._set_nav("Settings")
        self._set_title("Application Settings")
        self._clear()

        f = self._scrollable(self._active_page_frame)
        self._sec(f, "Preferences", "Customize your Finsights experience.")
        
        settings = _ldd("settings")
        
        form_f = tk.Frame(f, bg=CB)
        form_f.pack(fill="x", padx=20, pady=10)
        
        # Default Currency
        tk.Label(form_f, text="Default Currency", font=("Segoe UI Semibold", 10), bg=CB, fg=TS).grid(row=0, column=0, sticky="w", padx=20, pady=(20, 10))
        self.def_curr_var = tk.StringVar(value=settings.get("default_currency", GLOBAL_STATE["display_currency"]))
        curr_cb2 = ttk.Combobox(form_f, textvariable=self.def_curr_var, values=SUPPORTED_CURRENCIES, state="readonly", style="A.TCombobox")
        curr_cb2.grid(row=0, column=1, sticky="w", padx=20, pady=(20, 10))
        
        # Language
        tk.Label(form_f, text="Language", font=("Segoe UI Semibold", 10), bg=CB, fg=TS).grid(row=1, column=0, sticky="w", padx=20, pady=10)
        self.lang_var = tk.StringVar(value=settings.get("language", "English"))
        lang_cb = ttk.Combobox(form_f, textvariable=self.lang_var, values=["English"], state="disabled", style="A.TCombobox")
        lang_cb.grid(row=1, column=1, sticky="w", padx=20, pady=10)
        
        # Auto Backup
        tk.Label(form_f, text="Automatic Backups", font=("Segoe UI Semibold", 10), bg=CB, fg=TS).grid(row=2, column=0, sticky="w", padx=20, pady=10)
        self.auto_backup_var = tk.BooleanVar(value=settings.get("auto_backup", False))
        auto_chk = tk.Checkbutton(form_f, variable=self.auto_backup_var, bg=CB, fg=TP, activebackground=CB, selectcolor=BG, bd=0)
        auto_chk.grid(row=2, column=1, sticky="w", padx=16, pady=10)
        
        # Notification Settings
        tk.Label(form_f, text="Enable Budget Alerts", font=("Segoe UI Semibold", 10), bg=CB, fg=TS).grid(row=3, column=0, sticky="w", padx=20, pady=10)
        self.notif_var = tk.BooleanVar(value=settings.get("enable_alerts", True))
        notif_chk = tk.Checkbutton(form_f, variable=self.notif_var, bg=CB, fg=TP, activebackground=CB, selectcolor=BG, bd=0)
        notif_chk.grid(row=3, column=1, sticky="w", padx=16, pady=10)
        
        def _save_settings():
            new_s = {
                "theme": settings.get("theme", "Dark"),  # preserve existing theme value
                "default_currency": self.def_curr_var.get(),
                "language": self.lang_var.get(),
                "auto_backup": self.auto_backup_var.get(),
                "enable_alerts": self.notif_var.get()
            }
            _sv("settings", new_s)
            
            # Apply currency change globally if changed
            if new_s["default_currency"] != GLOBAL_STATE["display_currency"]:
                self.currency_var.set(new_s["default_currency"])
                self._on_currency_change()
            else:
                self.show_settings()
                
            tk.messagebox.showinfo("Settings", "Settings saved successfully.")
            
        sv_btn = tk.Button(form_f, text="Save Preferences", font=("Segoe UI", 10, "bold"), bg=AC, fg=TP, bd=0, cursor="hand2", command=_save_settings, padx=15, pady=8)
        sv_btn.grid(row=4, column=0, columnspan=2, sticky="w", padx=20, pady=(20, 20))
        
        # App Info
        self._sec(f, "About Finsights", "Application Information")
        info_f = tk.Frame(f, bg=BG)
        info_f.pack(fill="x", padx=20, pady=10)
        
        tk.Label(info_f, text="Finsights Premium Dashboard", font=("Segoe UI", 11, "bold"), bg=BG, fg=TP).pack(anchor="w")
        tk.Label(info_f, text="Version: 2.5 (Milestone 4)", font=("Segoe UI", 10), bg=BG, fg=TS).pack(anchor="w", pady=(2, 0))
        tk.Label(info_f, text=f"Data Directory: {DATA_DIR}", font=("Segoe UI", 9), bg=BG, fg=TS).pack(anchor="w", pady=(2, 0))
        tk.Label(info_f, text="Developed with CustomTkinter & Matplotlib", font=("Segoe UI", 9), bg=BG, fg=TS).pack(anchor="w", pady=(2, 0))
