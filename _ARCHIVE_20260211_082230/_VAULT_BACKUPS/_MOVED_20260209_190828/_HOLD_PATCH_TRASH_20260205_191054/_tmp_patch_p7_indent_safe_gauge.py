import re

path = r"""C:\Users\최정은\Desktop\snapq_toeic\app\arenas\p7_reading_arena.py"""
src = open(path, "r", encoding="utf-8").read()

# ---------- A) inject_css: add readability CSS inside function (idempotent) ----------
MARK = "P7_READABILITY_V2"
if MARK not in src:
    m = re.search(r"^def\s+inject_css\s*\(\s*\)\s*:\s*\n", src, flags=re.M)
    if not m:
        raise SystemExit("inject_css() not found")
    m2 = re.search(r"^\s*def\s+\w+\s*\(", src[m.end():], flags=re.M)
    inj_end = (m.end() + m2.start()) if m2 else len(src)
    body = src[m.start():inj_end]

    add = r'''
    # ---- P7 READABILITY V2 ----
    st.markdown(
        r"""
        <style>
        /* ''' + MARK + r''' */
        .p7-opt-wrap div[data-testid="stButton"] > button,
        .p7-opt-wrap div[data-testid="stButton"] > button *{
          color:#0B1020 !important;
          text-shadow:none !important;
        }
        .p7-opt-wrap div[data-testid="stButton"] > button{
          font-size:22px !important;
          font-weight:950 !important;
        }
        .p7-opt-wrap div[data-testid="stButton"] > button:hover,
        .p7-opt-wrap div[data-testid="stButton"] > button:hover *{
          color:#ffffff !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
'''
    # append near end of inject_css
    body2 = body.rstrip() + "\n\n" + add + "\n"
    src = src[:m.start()] + body2 + src[inj_end:]
    print("[OK] readability CSS injected")

# ---------- B) render_top_hud: indent-safe gauge drama injection ----------
m = re.search(r"^def\s+render_top_hud\s*\(\s*\)\s*:\s*\n", src, flags=re.M)
if not m:
    open(path, "w", encoding="utf-8").write(src)
    raise SystemExit("[WARN] render_top_hud not found")

m2 = re.search(r"^\s*def\s+\w+\s*\(", src[m.end():], flags=re.M)
end = (m.end() + m2.start()) if m2 else len(src)
body = src[m.start():end]

# if already has stage/last60, skip
if "gauge_cls = f\"p7-hud-gauge stage" not in body:
    # find the gauge st.markdown block that prints p7-hud-gauge
    # We'll capture its indent from the line containing st.markdown(
    pat = re.compile(r'^(?P<indent>\s*)st\.markdown\(\s*f?"""[\s\S]*?class="p7-hud-gauge[\s\S]*?unsafe_allow_html\s*=\s*True[\s\S]*?\)\s*', re.M)
    mm = pat.search(body)
    if not mm:
        # maybe gauge already uses {gauge_cls}; then search that
        pat2 = re.compile(r'^(?P<indent>\s*)st\.markdown\(\s*f?"""[\s\S]*?class="\{gauge_cls\}"[\s\S]*?unsafe_allow_html\s*=\s*True[\s\S]*?\)\s*', re.M)
        mm = pat2.search(body)

    if mm:
        indent = mm.group("indent")
        block = mm.group(0)

        # ensure f-string
        if not block.lstrip().startswith("st.markdown(f"):
            block = block.replace("st.markdown(", "st.markdown(f", 1)

        # ensure class uses {gauge_cls}
        block = block.replace('class="p7-hud-gauge"', 'class="{gauge_cls}"')

        gauge_code = (
            indent + "# ---- Gauge Drama Classes (30s stage + last60/last30/final) ----\n" +
            indent + "stage = int(remaining // 30)  # 0~5 (150초 기준)\n" +
            indent + "gauge_cls = f\"p7-hud-gauge stage{stage}\"\n" +
            indent + "if remaining <= 60:\n" +
            indent + "    gauge_cls += \" last60\"\n" +
            indent + "if remaining <= 30:\n" +
            indent + "    gauge_cls += \" last30\"\n" +
            indent + "if remaining <= 10:\n" +
            indent + "    gauge_cls += \" final\"\n"
        )

        body = body[:mm.start()] + gauge_code + block + body[mm.end():]
        print("[OK] gauge drama injected with indent-safe method")

patched = src[:m.start()] + body + src[end:]
open(path, "w", encoding="utf-8").write(patched)
print("[DONE] patched safely")

