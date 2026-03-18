import re

path = r"""C:\Users\최정은\Desktop\snapq_toeic\app\arenas\p7_reading_arena.py"""
src = open(path, "r", encoding="utf-8").read()

# --- find render_top_hud() ---
m = re.search(r"^def\s+render_top_hud\s*\(\s*\)\s*:\s*\n", src, flags=re.M)
if not m:
    raise SystemExit("render_top_hud() not found")

# function end
m2 = re.search(r"^\s*def\s+\w+\s*\(", src[m.end():], flags=re.M)
end = (m.end() + m2.start()) if m2 else len(src)
body = src[m.start():end]

# If already has p7_top_hud_tick, normalize it (interval=1000, key fixed) and ensure not commented
if 'key="p7_top_hud_tick"' in body:
    # normalize interval in that call (if different)
    body2 = re.sub(
        r'st_autorefresh\(\s*interval\s*=\s*\d+\s*,\s*key\s*=\s*"p7_top_hud_tick"\s*\)',
        'st_autorefresh(interval=1000, key="p7_top_hud_tick")',
        body
    )
    # if the call line is commented, uncomment it safely
    body2 = re.sub(
        r'^\s*#\s*\[.*?\]\s*st_autorefresh\(\s*interval\s*=\s*1000\s*,\s*key\s*=\s*"p7_top_hud_tick"\s*\)\s*$',
        '            st_autorefresh(interval=1000, key="p7_top_hud_tick")',
        body2,
        flags=re.M
    )
    patched = src[:m.start()] + body2 + src[end:]
    open(path, "w", encoding="utf-8").write(patched)
    print("[OK] HUD autorefresh already present -> normalized")
    raise SystemExit(0)

# Otherwise, INSERT the HUD-only autorefresh block right after tb/combo are set.
# We find the line 'combo: ComboState = st.session_state.p7_combo' and insert after it.
anchor = "combo: ComboState = st.session_state.p7_combo"
pos = body.find(anchor)
if pos < 0:
    raise SystemExit("could not find combo assignment anchor inside render_top_hud()")

line_end = body.find("\n", pos)
if line_end < 0:
    raise SystemExit("line parse fail")

INSERT = r'''
    # ✅ HUD ONLY: 1초 갱신(전투 중만) - STEP B restore
    if st.session_state.get("p7_has_started", False) and not st.session_state.get("p7_has_finished", False) and not tb.is_over:
        try:
            from streamlit_autorefresh import st_autorefresh
            st_autorefresh(interval=1000, key="p7_top_hud_tick")
        except ModuleNotFoundError:
            pass
'''

body2 = body[:line_end+1] + INSERT + body[line_end+1:]

patched = src[:m.start()] + body2 + src[end:]
open(path, "w", encoding="utf-8").write(patched)
print("[OK] inserted HUD autorefresh (p7_top_hud_tick) into render_top_hud()")

