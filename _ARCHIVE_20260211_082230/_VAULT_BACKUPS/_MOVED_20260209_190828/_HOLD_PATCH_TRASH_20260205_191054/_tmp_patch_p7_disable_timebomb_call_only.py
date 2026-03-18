import re

path = r"""C:\Users\최정은\Desktop\snapq_toeic\app\arenas\p7_reading_arena.py"""
src = open(path, "r", encoding="utf-8").read()

# Replace ONLY the call line for key="p7_timebomb_tick" (do NOT touch import line)
# Keep indentation same as original call line.
def repl(m):
    indent = m.group("indent")
    return indent + "pass  # [AUTO-DISABLED duplicate P7 timebomb tick]\n"

pattern = re.compile(r'^(?P<indent>\s*)st_autorefresh\(\s*interval\s*=\s*1000\s*,\s*key\s*=\s*"p7_timebomb_tick"\s*\)\s*$', re.M)
src2, n = pattern.subn(repl, src)

print(f"[OK] replaced timebomb tick calls: {n}")
open(path, "w", encoding="utf-8").write(src2)

