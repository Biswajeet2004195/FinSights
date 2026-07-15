import glob

def fix_multiline():
    files = glob.glob("modules/*.py")
    for f in files:
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # We will iterate through characters. When we see 'tk.Label(' or 'tk.Canvas(', 
        # we track parentheses depth until depth reaches 0.
        # Within that range, we replace 'fg_color=' with 'bg=' and 'text_color=' with 'fg='
        
        out = []
        i = 0
        while i < len(content):
            found_label = content.startswith('tk.Label(', i)
            found_canvas = content.startswith('tk.Canvas(', i)
            if found_label or found_canvas:
                start_idx = i
                # find the end of the call
                depth = 0
                j = i
                started = False
                while j < len(content):
                    if content[j] == '(':
                        depth += 1
                        started = True
                    elif content[j] == ')':
                        depth -= 1
                    j += 1
                    if started and depth == 0:
                        break
                
                # Now we have the chunk from i to j
                chunk = content[i:j]
                chunk = chunk.replace('fg_color=', 'bg=').replace('text_color=', 'fg=')
                out.append(chunk)
                i = j
            else:
                out.append(content[i])
                i += 1
                
        with open(f, 'w', encoding='utf-8') as file:
            file.write("".join(out))

    print("Multiline fix complete!")

if __name__ == "__main__":
    fix_multiline()
