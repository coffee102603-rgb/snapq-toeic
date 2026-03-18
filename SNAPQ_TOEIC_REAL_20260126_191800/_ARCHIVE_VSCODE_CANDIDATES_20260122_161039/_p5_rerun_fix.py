from pathlib import Path
import re

p = Path(r"C:\Users\최정은\Desktop\SNAPQ_TOEIC\app\arenas\p5_timebomb_arena.py")
t = p.read_text(encoding="utf-8", errors="ignore")

t2 = re.sub(r"\bst\.experimental_rerun\s*\(\s*\)", "st.rerun()", t)
p.write_text(t2, encoding="utf-8")

print("[OK] replaced:", (t != t2))
