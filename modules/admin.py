import tkinter as tk
from tkinter import ttk, messagebox
from config import *
from base_dashboard import BaseDashboard

class AdminMixin(BaseDashboard):
    def show_admin(self):
        self._clear()
        self._set_nav("Admin Panel")
        self._set_title("Admin Console")
        pg = self._scrollable(self._cf)
        
        self._sec(pg, "👑 Admin Management Console", "Manage system users and send broadcast alerts")
        
        # Split: Users Table (left) + Broadcast Alert Form (right)
        split = ctk.CTkFrame(pg, fg_color=BG, corner_radius=10)
        split.pack(fill="both", expand=True, padx=20, pady=(4, 20))
        
        # Broadcast Panel (Right)
        bf = ctk.CTkFrame(split, fg_color=BD, width=320, corner_radius=10)
        bf.pack(side="right", fill="y", padx=(10, 0))
        bf.pack_propagate(False)
        bfi = ctk.CTkFrame(bf, fg_color=CB, corner_radius=10); bfi.pack(padx=1, pady=1, fill="both", expand=True)
        ctk.CTkFrame(bfi, fg_color=AC, height=3, corner_radius=10).pack(fill="x")
        
        tk.Label(bfi, text="📢 Broadcast System Alert", font=("Segoe UI Semibold", 12), bg=CB, fg=TP).pack(anchor="w", padx=14, pady=(14, 4))
        
        tk.Label(bfi, text="Title", font=("Segoe UI Semibold", 9), bg=CB, fg=TS).pack(anchor="w", padx=14, pady=(8, 2))
        title_bdr = ctk.CTkFrame(bfi, fg_color=BD, corner_radius=10); title_bdr.pack(fill="x", padx=14)
        title_inn = ctk.CTkFrame(title_bdr, fg_color=EN, corner_radius=10); title_inn.pack(padx=1, pady=1, fill="x")
        title_e = ctk.CTkEntry(title_inn, font=ctk.CTkFont("Segoe UI", 12), fg_color=EN, text_color=TP, corner_radius=8)
        title_e.pack(fill="x", ipady=6, padx=8)
        
        title_e.bind("<FocusIn>",  lambda e: title_bdr.configure(fg_color=CY))
        title_e.bind("<FocusOut>", lambda e: title_bdr.configure(fg_color=BD))
        
        tk.Label(bfi, text="Message", font=("Segoe UI Semibold", 9), bg=CB, fg=TS).pack(anchor="w", padx=14, pady=(8, 2))
        msg_bdr = ctk.CTkFrame(bfi, fg_color=BD, corner_radius=10); msg_bdr.pack(fill="x", padx=14)
        msg_inn = ctk.CTkFrame(msg_bdr, fg_color=EN, corner_radius=10); msg_inn.pack(padx=1, pady=1, fill="x")
        msg_e = ctk.CTkEntry(msg_inn, font=ctk.CTkFont("Segoe UI", 12), fg_color=EN, text_color=TP, corner_radius=8)
        msg_e.pack(fill="x", ipady=6, padx=8)
        
        msg_e.bind("<FocusIn>",  lambda e: msg_bdr.configure(fg_color=CY))
        msg_e.bind("<FocusOut>", lambda e: msg_bdr.configure(fg_color=BD))
        
        tk.Label(bfi, text="Alert Type", font=("Segoe UI Semibold", 9), bg=CB, fg=TS).pack(anchor="w", padx=14, pady=(8, 2))
        type_var = tk.StringVar(value="info")
        type_cb = ttk.Combobox(bfi, textvariable=type_var, values=["info", "success", "warning", "error"], state="readonly", style="A.TCombobox")
        type_cb.pack(fill="x", padx=14, ipady=4)
        
        def broadcast():
            t = title_e.get().strip()
            m = msg_e.get().strip()
            if not t or not m:
                return messagebox.showwarning("Broadcast", "Please fill in title and message.")
            
            # Save to notifications
            ns = _ld("notifications")
            ns.append({
                "id": mk_id(),
                "type": type_var.get(),
                "title": f"[Broadcast] {t}",
                "msg": m,
                "read": False,
                "ts": now_ts()
            })
            _sv("notifications", ns)
            self._update_bell()
            messagebox.showinfo("Broadcast", "System notification broadcasted to all users!")
            title_e.delete(0, tk.END)
            msg_e.delete(0, tk.END)
            
        send_btn = tk.Label(bfi, text="  Broadcast Alert  ", font=("Segoe UI Semibold", 10), bg=AC, fg=TP, cursor="hand2", pady=8, anchor="center")
        send_btn.pack(fill="x", padx=14, pady=20)
        send_btn.bind("<Button-1>", lambda e: broadcast())
        send_btn.bind("<Enter>", lambda e: fade_color(send_btn, None, "bg", "#006ee6", steps=6, delay=10))
        send_btn.bind("<Leave>", lambda e: fade_color(send_btn, None, "bg", AC, steps=6, delay=10))
        
        # Users Table (Left)
        tf, tv = self._tv(split, ["Email", "Name"], [280, 260], height=18)
        tf.pack(side="left", fill="both", expand=True)
        
        def refresh_table():
            u = _ld_users()
            rows = []
            for email, info in u.items():
                rows.append((email, email, info.get("name", "")))
            self._tv_fill(tv, rows)
            
        refresh_table()
        

