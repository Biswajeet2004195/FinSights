import re
with open("regform.py", "r", encoding="utf-8") as f:
    content = f.read()

# Remove root.mainloop()
content = content.replace("root.mainloop()", "print('Init complete!')")

with open("test_regform.py", "w", encoding="utf-8") as f:
    f.write(content)
