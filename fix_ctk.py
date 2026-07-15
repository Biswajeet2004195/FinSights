import glob
import re

def fix():
    files = glob.glob("modules/*.py")
    for f in files:
        with open(f, 'r', encoding='utf-8') as file:
            c = file.read()
            
        # Fix CTkEntry
        # ctk.CTkEntry(a, font=("A", 10, corner_radius=8)), b) -> ctk.CTkEntry(a, font=("A", 10), corner_radius=8, b)
        # Actually it's easier to find: `corner_radius=8)), ` and move `corner_radius=8` to the end of the line.
        # Let's fix CTkFrame first:
        # ctk.CTkFrame(a, font=("A", 10, corner_radius=10)), b) 
        
        # We need a robust regex to fix the dangling parentheses and arguments.
        
        # 1. CTkEntry
        def fix_entry(match):
            pre = match.group(1)
            font_name = match.group(2)
            font_size = match.group(3)
            post = match.group(4)
            # Reconstruct correctly
            post = post.replace('bg=', 'fg_color=').replace('fg=', 'text_color=').replace('bd=0', 'border_width=0')
            return f'ctk.CTkEntry({pre}, font=("{font_name}", {font_size}), {post}, corner_radius=8)'
            
        c = re.sub(r'ctk\.CTkEntry\((.*?), font=\("(.*?)", (.*?)[,\s]*corner_radius=8\)\), (.*?)\)', fix_entry, c)
        
        # 2. CTkButton
        def fix_btn(match):
            pre = match.group(1)
            font_name = match.group(2)
            font_size = match.group(3)
            post = match.group(4)
            post = post.replace('bg=', 'fg_color=').replace('fg=', 'text_color=').replace('bd=0', 'border_width=0')
            return f'ctk.CTkButton({pre}, font=("{font_name}", {font_size}), {post}, corner_radius=8)'
            
        c = re.sub(r'ctk\.CTkButton\((.*?), font=\("(.*?)", (.*?)[,\s]*corner_radius=8\)\), (.*?)\)', fix_btn, c)
        
        # 3. CTkFrame might not have font=, so the regex `tk.Frame((.*?))` probably matched to the end `)` perfectly because it has no inner `)`. 
        # But let's check if there are any dangling `))` for CTkFrame.
        def fix_frame(match):
            pre = match.group(1)
            font_name = match.group(2)
            font_size = match.group(3)
            post = match.group(4)
            post = post.replace('bg=', 'fg_color=').replace('fg=', 'text_color=').replace('bd=0', 'border_width=0')
            return f'ctk.CTkFrame({pre}, font=("{font_name}", {font_size}), {post}, corner_radius=10)'
            
        c = re.sub(r'ctk\.CTkFrame\((.*?), font=\("(.*?)", (.*?)[,\s]*corner_radius=10\)\), (.*?)\)', fix_frame, c)
        
        # Now fix remaining bg= and fg= that the first script missed because it matched the wrong )
        c = c.replace('bg=', 'fg_color=')
        c = c.replace('fg=', 'text_color=')
        
        # ctk.CTkFrame(..., corner_radius=10)), fg_color=X)
        # Wait, if tk.Frame(...) had no inner parens, the first script worked perfectly for it!
        # Let's do a sanity check to see if there are any `)), ` 
        c = re.sub(r'corner_radius=(\d+)\)\), (.*?)\)', r'\2, corner_radius=\1)', c)
        
        # Write back
        with open(f, 'w', encoding='utf-8') as file:
            file.write(c)

    print("Fix complete!")

if __name__ == "__main__":
    fix()
