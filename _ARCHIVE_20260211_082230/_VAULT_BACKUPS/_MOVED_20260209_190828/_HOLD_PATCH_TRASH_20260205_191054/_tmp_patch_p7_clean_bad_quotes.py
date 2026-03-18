import re

path = r"""C:\Users\최정은\Desktop\snapq_toeic\app\arenas\p7_reading_arena.py"""
src = open(path, "r", encoding="utf-8").read()

# remove the exact broken pattern that causes SyntaxError
src2 = re.sub(r'^\s*time_stage\s*=\s*\\\"p7-time-warn\\\".*$', '    time_stage = "p7-time-warn"  # [CLEANED]', src, flags=re.M)

# also normalize any accidental \" inside time_stage assignment
src2 = re.sub(r'(time_stage\s*=\s*)\\\"([^\\\"]+)\\\"', r'\1"\2"', src2)

open(path, "w", encoding="utf-8").write(src2)
print("[OK] cleaned bad escaped quotes (if existed)")

