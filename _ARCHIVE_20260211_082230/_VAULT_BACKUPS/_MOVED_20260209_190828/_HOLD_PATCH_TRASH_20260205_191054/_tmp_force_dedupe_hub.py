import re, sys
from pathlib import Path

path = Path(sys.argv[1])
txt = path.read_text(encoding="utf-8", errors="ignore")

# protect auto nav block
m = re.search(r"(?s)# --- SNAPQ_MAIN_HUB_NAV \(auto\) ---.*?# --- /SNAPQ_MAIN_HUB_NAV ---", txt)
auto = ""
if m:
    auto = m.group(0)
    txt = txt.replace(auto, "__AUTO_HUB_BLOCK__")

# remove any OTHER st.button blocks containing MAIN HUB (keep auto)
# covers: "🏠 MAIN HUB", "🏠 MAIN\nHUB", "MAIN HUB" etc.
pat = r"(?s)\n[ \t]*if[ \t]+st\.button\([^\)]*(MAIN\s*HUB|MAIN\\nHUB)[^\)]*\)[ \t]*:[ \t]*\n(?:[ \t]+.*\n)+"
txt2 = re.sub(pat, "\n", txt)

# restore auto block
txt2 = txt2.replace("__AUTO_HUB_BLOCK__", auto)

path.write_text(txt2, encoding="utf-8-sig")
print("OK:", path)