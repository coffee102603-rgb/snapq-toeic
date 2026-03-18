import re

path = r"""C:\Users\최정은\Desktop\snapq_toeic\app\arenas\p7_reading_arena.py"""
src  = open(path, "r", encoding="utf-8").read()
lines = src.splitlines(True)

CSS_MARK = "P7_FORCE_TOP_V1"
WRAP_MARK = "P7_FORCE_TOP_WRAP_V1"

# -----------------------------
# A) inject_css(): add CSS once
# -----------------------------
if CSS_MARK not in src:
    idx_def = next((i for i,l in enumerate(lines) if l.startswith("def inject_css()")), None)
    if idx_def is None:
        raise SystemExit("inject_css() not found")

    idx_next = next((i for i in range(idx_def+1, len(lines)) if lines[i].startswith("def ") and not lines[i].startswith("def inject_css()")), len(lines))

    indent = "    "
    css_block = [
        "\n",
        f"{indent}# ---- {CSS_MARK} ----\n",
        f"{indent}st.markdown(\n",
        f"{indent}    r\"\"\"\n",
        f"{indent}    <style>\n",
        f"{indent}    /* {CSS_MARK} : pull HUD+gauge up (do NOT touch passage/question/options) */\n",
        f"{indent}    .p7-force-top{{ margin-top:-28px !important; }}\n",
        f"{indent}    </style>\n",
        f"{indent}    \"\"\",\n",
        f"{indent}    unsafe_allow_html=True,\n",
        f"{indent})\n",
    ]
    lines[idx_next:idx_next] = css_block

# refresh src after edit
src2 = "".join(lines)
lines = src2.splitlines(True)

# -----------------------------------------
# B) Wrap the first render_top_hud() call
# -----------------------------------------
if WRAP_MARK not in src2:
    # find first line that contains render_top_hud()
    target_idx = None
    for i,l in enumerate(lines):
        if "render_top_hud()" in l and not l.lstrip().startswith("#"):
            target_idx = i
            break

    if target_idx is None:
        open(path, "w", encoding="utf-8").write("".join(lines))
        raise SystemExit("render_top_hud() call not found")

    # keep same indentation as that call line
    indent = re.match(r"^\s*", lines[target_idx]).group(0)

    open_tag = [
        f"{indent}# ---- {WRAP_MARK} ----\n",
        f"{indent}st.markdown(\"\"\"<div class='p7-force-top'>\"\"\", unsafe_allow_html=True)\n",
    ]
    close_tag = [
        f"{indent}st.markdown(\"\"\"</div>\"\"\", unsafe_allow_html=True)\n",
    ]

    # insert open_tag right before the call, close_tag right after the call line
    lines[target_idx:target_idx] = open_tag
    target_idx = target_idx + len(open_tag)
    lines[target_idx+1:target_idx+1] = close_tag

open(path, "w", encoding="utf-8").write("".join(lines))
print("[OK] FORCE TOP applied (CSS + wrapper)")

