import os
import glob
import re

def migrate():
    files = glob.glob("modules/*.py")
    for f in files:
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Replace tk.Frame with ctk.CTkFrame and bg= with fg_color=
        def repl(match):
            inner = match.group(1)
            inner = inner.replace('bg=', 'fg_color=')
            if 'corner_radius' not in inner:
                inner += ', corner_radius=10'
            return f'ctk.CTkFrame({inner})'
            
        new_content = re.sub(r'tk\.Frame\((.*?)\)', repl, content)
        
        # Ensure config import pulls ctk (it does via 'from config import *')
        # We also need to fix tk.Button -> ctk.CTkButton, tk.Entry -> ctk.CTkEntry
        def repl_btn(match):
            inner = match.group(1)
            inner = inner.replace('bg=', 'fg_color=').replace('fg=', 'text_color=').replace('bd=0', 'border_width=0')
            if 'corner_radius' not in inner:
                inner += ', corner_radius=8'
            return f'ctk.CTkButton({inner})'
            
        new_content = re.sub(r'tk\.Button\((.*?)\)', repl_btn, new_content)
        
        def repl_entry(match):
            inner = match.group(1)
            inner = inner.replace('bg=', 'fg_color=').replace('fg=', 'text_color=').replace('bd=0', 'border_width=0')
            if 'corner_radius' not in inner:
                inner += ', corner_radius=8'
            return f'ctk.CTkEntry({inner})'
            
        new_content = re.sub(r'tk\.Entry\((.*?)\)', repl_entry, new_content)
        
        # In custom tkinter, width and height of frames can be tricky if they were packing with 1px width.
        # But let's apply the changes and see.
        
        with open(f, 'w', encoding='utf-8') as file:
            file.write(new_content)
            
    print("Migration complete!")

if __name__ == "__main__":
    migrate()
