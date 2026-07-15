import tkinter as tk
from tkinter import messagebox
from config import *
from base_dashboard import BaseDashboard

class ProfileMixin(BaseDashboard):
    def show_profile(self):
        self._clear()
        self._set_nav("Profile")
        self._set_title("Profile Management")
        pg = self._scrollable(self._cf)
        self._sec(pg, "👤 Profile & Settings", "Manage your account information and preferences")

        # Load users
        users = _ld_users()
        if self.email not in users:
            messagebox.showerror("Error", "User data not found!")
            return
        ud = users[self.email]

        # Calculate KPIs (Global data for now)
        trans = _ld("transactions")
        goals = _ld("goals")
        invs = _ld("investments")

        # KPI row
        r1 = ctk.CTkFrame(pg, fg_color=BG, corner_radius=10)
        r1.pack(fill="x", padx=20, pady=10)
        
        self._kpi(r1, "Transactions", str(len(trans)), "Total", AC, "📊").pack(side="left", ipadx=8, ipady=4, padx=(0, 10), expand=True, fill="both")
        self._kpi(r1, "Financial Goals", str(len(goals)), "Total", GR, "🎯").pack(side="left", ipadx=8, ipady=4, padx=(0, 10), expand=True, fill="both")
        self._kpi(r1, "Investments", str(len(invs)), "Total", CY, "📈").pack(side="left", ipadx=8, ipady=4, expand=True, fill="both")

        # Profile Details Card
        pc = ctk.CTkFrame(pg, fg_color=BD, corner_radius=10)
        pc.pack(fill="x", padx=20, pady=10)
        pci = ctk.CTkFrame(pc, fg_color=CB, corner_radius=10)
        pci.pack(padx=1, pady=1, fill="x")
        
        # Details
        r_info = ctk.CTkFrame(pci, fg_color=CB, corner_radius=10)
        r_info.pack(fill="x", padx=20, pady=20)
        tk.Label(r_info, text="Full Name:", font=("Segoe UI Semibold", 12), bg=CB, fg=TS).grid(row=0, column=0, sticky="w", pady=5)
        tk.Label(r_info, text=ud.get("name", self.username), font=("Segoe UI", 12), bg=CB, fg=TP).grid(row=0, column=1, sticky="w", padx=20, pady=5)

        tk.Label(r_info, text="Email Address:", font=("Segoe UI Semibold", 12), bg=CB, fg=TS).grid(row=1, column=0, sticky="w", pady=5)
        tk.Label(r_info, text=self.email, font=("Segoe UI", 12), bg=CB, fg=TP).grid(row=1, column=1, sticky="w", padx=20, pady=5)


        
        # Actions Row
        r_acts = ctk.CTkFrame(pci, fg_color=CB, corner_radius=10)
        r_acts.pack(fill="x", padx=20, pady=(0, 20))
        
        self._tb_btn(r_acts, "➕ Add Account", self._add_account, AC).pack(side="left", padx=(0, 10))
        self._tb_btn(r_acts, "✏ Edit Profile", self._edit_profile, AC).pack(side="left", padx=(0, 10))
        self._tb_btn(r_acts, "🔑 Change Password", self._change_password, CY).pack(side="left", padx=(0, 10))
        self._tb_btn(r_acts, "🚪 Logout", self._logout, TS).pack(side="left", padx=(0, 10))
        
        # Delete Account (Red)
        db = self._tb_btn(r_acts, "🗑 Delete Account", self._delete_account, RE)
        db.pack(side="right")
        
        # Bottom spacer
        ctk.CTkFrame(pg, fg_color=BG, height=20, corner_radius=10).pack()

    def _add_account(self):
        def save_cb(vals, dlg):
            name = vals.get("name", "").strip()
            email = vals.get("email", "").strip().lower()
            password = vals.get("password", "").strip()
            confirm = vals.get("confirm", "").strip()
            
            if not name:
                return messagebox.showerror("Error", "Name cannot be empty.")
            if "@" not in email:
                return messagebox.showerror("Error", "Invalid email address.")
                
            u = _ld_users()
            if any(k.strip().lower() == email for k in u.keys()):
                return messagebox.showerror("Error", "Email already in use.")
                
            if len(password) < 8:
                return messagebox.showerror("Error", "Password must be at least 8 characters.")
            if password != confirm:
                return messagebox.showerror("Error", "Passwords do not match.")
                
            u[email] = {
                "name": name,
                "password": hash_password(password)
            }
            _sv_users(u)
            messagebox.showinfo("Success", "New account created successfully.")
            dlg.destroy()
            self.show_profile()
            
        self._dialog("Add Account", [
            {"k": "name", "lbl": "Full Name", "type": "entry"},
            {"k": "email", "lbl": "Email Address", "type": "entry"},
            {"k": "password", "lbl": "Password", "type": "entry", "show": "*"},
            {"k": "confirm", "lbl": "Confirm Password", "type": "entry", "show": "*"},
        ], save_cb)

    def _edit_profile(self):
        users = _ld_users()
        ud = users.get(self.email, {})
        
        def save_cb(vals, dlg):
            new_name = vals.get("name", "").strip()
            new_email = vals.get("email", "").strip().lower()
            
            if not new_name:
                return messagebox.showerror("Error", "Name cannot be empty.")
            if not new_email or "@" not in new_email:
                return messagebox.showerror("Error", "Invalid email address.")
                
            u = _ld_users()
            current_email_lower = self.email.strip().lower()
            if new_email != current_email_lower and any(k.strip().lower() == new_email for k in u.keys()):
                return messagebox.showerror("Error", "Email already in use.")
                
            # Find actual key used
            old_key = next((k for k in u.keys() if k.strip().lower() == current_email_lower), self.email)
            
            # Update data
            old_data = u.pop(old_key, {})
            if old_data:
                old_data["name"] = new_name
                u[new_email] = old_data
                _sv_users(u)
            
            # Update session
            self.email = new_email
            self.username = new_name
            dlg.destroy()
            self.show_profile()
            self._update_sidebar_name()
            
        self._dialog("Edit Profile", [
            {"k": "name", "lbl": "Full Name", "type": "entry"},
            {"k": "email", "lbl": "Email Address", "type": "entry"},
        ], save_cb, defaults={"name": self.username, "email": self.email})
        
    def _update_sidebar_name(self):
        uname = self.username[:18] if len(self.username) > 18 else self.username
        if hasattr(self, "_sc"):
            self._sc.itemconfig("bottom_user", text=f"👤  {uname}")

    def _change_password(self):
        def save_cb(vals, dlg):
            cp = vals.get("curr", "").strip()
            np = vals.get("new", "").strip()
            cn = vals.get("conf", "").strip()
            
            u = _ld_users()
            current_email_lower = self.email.strip().lower()
            old_key = next((k for k in u.keys() if k.strip().lower() == current_email_lower), self.email)
            ud = u.get(old_key)
            
            if not ud or not verify_password(ud["password"], cp):
                return messagebox.showerror("Error", "Current password is incorrect.")
            if len(np) < 8:
                return messagebox.showerror("Error", "New password must be at least 8 characters.")
            if np != cn:
                return messagebox.showerror("Error", "Passwords do not match.")
                
            ud["password"] = hash_password(np)
            _sv_users(u)
            messagebox.showinfo("Success", "Password changed successfully.")
            dlg.destroy()
            
        self._dialog("Change Password", [
            {"k": "curr", "lbl": "Current Password", "type": "entry", "show": "*"},
            {"k": "new", "lbl": "New Password", "type": "entry", "show": "*"},
            {"k": "conf", "lbl": "Confirm Password", "type": "entry", "show": "*"},
        ], save_cb)

    def _logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to log out?"):
            self.root.master.deiconify()
            self.root.destroy()

    def _delete_account(self):
        msg = "Are you sure you want to permanently delete your account?\nThis action cannot be undone."
        if messagebox.askyesno("Delete Account", msg, icon="warning"):
            # Delete user
            u = _ld_users()
            if self.email in u:
                del u[self.email]
                _sv_users(u)
            
            # Clear global data mimicking user specific data deletion
            _sv("transactions", [])
            _sv("budgets", {})
            _sv("goals", [])
            _sv("investments", [])
            _sv("notifications", [])
            
            messagebox.showinfo("Account Deleted", "Your account and data have been permanently deleted.")
            self.root.master.deiconify()
            self.root.destroy()
