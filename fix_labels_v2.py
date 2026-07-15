import glob

def fix_all_labels():
    files = glob.glob("modules/*.py")
    for f in files:
        with open(f, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        new_lines = []
        for line in lines:
            if 'tk.Label(' in line:
                # Replace CTk properties with standard Tkinter properties for tk.Label
                line = line.replace('fg_color=', 'bg=')
                line = line.replace('text_color=', 'fg=')
            if '.config(' in line:
                # Also ensure .config uses the correct property names.
                # If it's configuring a CTkFrame (like title_bdr), it should use fg_color=...
                pass
            new_lines.append(line)
            
        with open(f, 'w', encoding='utf-8') as file:
            file.writelines(new_lines)

    print("All labels accurately fixed line-by-line!")

if __name__ == "__main__":
    fix_all_labels()
