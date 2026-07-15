import glob
import re

def fix_labels():
    files = glob.glob("modules/*.py")
    for f in files:
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # We need to revert fg_color -> bg and text_color -> fg ONLY inside tk.Label(...)
        def repl(match):
            inner = match.group(1)
            inner = inner.replace('fg_color=', 'bg=').replace('text_color=', 'fg=')
            return f'tk.Label({inner})'
            
        content = re.sub(r'tk\.Label\((.*?)\)', repl, content)
        
        # Also fix fade_color arguments that might have been incorrectly replaced back from fg_color to bg for tk.Labels?
        # Actually it's easier to just run this and see.
        
        with open(f, 'w', encoding='utf-8') as file:
            file.write(content)

    print("tk.Label fix complete!")

if __name__ == "__main__":
    fix_labels()
