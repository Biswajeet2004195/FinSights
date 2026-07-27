import tkinter as tk
from tkinter import filedialog, messagebox
from config import *
import os
import shutil
import zipfile
import datetime

class BackupMixin:
    def show_backup(self):
        self._set_nav("Backup")
        self._set_title("Data Backup & Restore")
        self._clear()

        f = self._scrollable(self._active_page_frame)
        self._sec(f, "Data Management", "Backup or restore your Finsights data securely.")
        
        form_f = tk.Frame(f, bg=CB)
        form_f.pack(fill="x", padx=20, pady=10)
        
        # Backup section
        tk.Label(form_f, text="Manual Backup", font=("Segoe UI Semibold", 12), bg=CB, fg=TP).pack(anchor="w", padx=20, pady=(20, 5))
        tk.Label(form_f, text="Export all your financial data into a compressed ZIP file.", font=("Segoe UI", 10), bg=CB, fg=TS).pack(anchor="w", padx=20)
        
        btn_f1 = tk.Frame(form_f, bg=CB)
        btn_f1.pack(fill="x", padx=20, pady=15)
        self._tb_btn(btn_f1, "Export Backup", self._export_backup, GR).pack(side="left")
        
        tk.Frame(form_f, bg=BD, height=1).pack(fill="x", padx=20, pady=10)
        
        # Restore section
        tk.Label(form_f, text="Restore Backup", font=("Segoe UI Semibold", 12), bg=CB, fg=TP).pack(anchor="w", padx=20, pady=(10, 5))
        tk.Label(form_f, text="Import a previously saved ZIP backup. WARNING: This will overwrite current data.", font=("Segoe UI", 10), bg=CB, fg=OR).pack(anchor="w", padx=20)
        
        btn_f2 = tk.Frame(form_f, bg=CB)
        btn_f2.pack(fill="x", padx=20, pady=15)
        self._tb_btn(btn_f2, "Import Backup", self._import_backup, RE).pack(side="left")

    def _export_backup(self):
        default_name = f"finsights_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        save_path = filedialog.asksaveasfilename(
            parent=self.root,
            title="Save Backup As",
            initialfile=default_name,
            defaultextension=".zip",
            filetypes=[("ZIP Archives", "*.zip"), ("All Files", "*.*")]
        )
        
        if not save_path:
            return
            
        try:
            with zipfile.ZipFile(save_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(DATA_DIR):
                    for file in files:
                        if file.endswith('.json'):
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, start=DATA_DIR)
                            zipf.write(file_path, arcname)
            messagebox.showinfo("Backup Successful", f"Data successfully backed up to:\n{save_path}")
        except Exception as e:
            messagebox.showerror("Backup Failed", f"An error occurred during backup:\n{e}")

    def _import_backup(self):
        open_path = filedialog.askopenfilename(
            parent=self.root,
            title="Select Backup File",
            filetypes=[("ZIP Archives", "*.zip"), ("All Files", "*.*")]
        )
        
        if not open_path:
            return
            
        confirm = messagebox.askyesno("Confirm Restore", "Are you sure you want to restore this backup? ALL current data will be overwritten and cannot be recovered.")
        if not confirm:
            return
            
        try:
            # Create a temporary extraction directory
            temp_dir = os.path.join(BASE_DIR, "temp_restore")
            os.makedirs(temp_dir, exist_ok=True)
            
            with zipfile.ZipFile(open_path, 'r') as zipf:
                zipf.extractall(temp_dir)
                
            # Move files to DATA_DIR
            for file in os.listdir(temp_dir):
                if file.endswith('.json'):
                    shutil.move(os.path.join(temp_dir, file), os.path.join(DATA_DIR, file))
                    
            shutil.rmtree(temp_dir)
            
            # Clear caches
            _DATA_CACHE.clear()
            
            messagebox.showinfo("Restore Successful", "Data has been successfully restored. The dashboard will now refresh.")
            self.show_overview()
            
        except Exception as e:
            messagebox.showerror("Restore Failed", f"An error occurred during restore:\n{e}")
