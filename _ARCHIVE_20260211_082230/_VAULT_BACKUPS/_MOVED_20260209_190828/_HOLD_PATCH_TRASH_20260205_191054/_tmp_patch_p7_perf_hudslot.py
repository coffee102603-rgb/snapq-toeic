import re

path = r"""C:\Users\최정은\Desktop\snapq_toeic\app\arenas\p7_reading_arena.py"""
src = open(path, "r", encoding="utf-8").read()

# ------------------------------------------------------------
# 1) inject_css(): add "BASE HUD CSS once" block (do not touch CRIT always)
# ------------------------------------------------------------
def patch_inject_css(s: str) -> str:
    m = re.search(r"^def\s+inject_css\s*\(\s*\)\s*:\s*\n", s, flags=re.M)
    if not m:
        raise SystemExit("inject_css() not found")

    # If already patched, skip
    if "_p7_base_hud_css_once" in s:
        return s

    # Insert after the CRIT st.markdown(...) call block end.
    # Find first occurrence of "unsafe_allow_html=True," inside inject_css and then the following closing ")\n"
    inj_start = m.start()
    inj_body = s[inj_start:]
    # locate the first CRIT st.markdown(...) close
    close_pos = inj_body.find("unsafe_allow_html=True")
    if close_pos < 0:
        # fallback: insert right after docstring
        pass

    # safer: insert after the first CRIT block end: find first "\n    )" after unsafe_allow_html
    end_call = inj_body.find("\n    )", close_pos)
    if end_call < 0:
        # fallback: just after function header line
        insert_at = inj_start + m.end()
    else:
        insert_at = inj_start + end_call + len("\n    )")

    BASE = r"""

    # ---- BASE HUD CSS (ONCE per session) ----
    if st.session_state.get("_p7_base_hud_css_once", False):
        return
    st.session_state["_p7_base_hud_css_once"] = True

    st.markdown(
        """
        <style>
        /* ===== P7 HUD BASE (ONCE) =====
           - render_top_hud()에서 매초 style 주입하던 부분을 여기로 이동
           - rerun 비용 절감 (체감 속도 ↑)
        */
        .p7-hud-left{ display:flex; gap:8px; align-items:center; flex-wrap:wrap; }
        .p7-chip{
          display:inline-flex; align-items:center; gap:6px;
          padding:5px 9px; border-radius:999px;
          background: rgba(15,23,42,0.10);
          border: 1px solid rgba(15,23,42,0.12);
          font-weight:900; line-height:1;
        }
        .p7-hud-gauge{
          height:10px; border-radius:999px; overflow:hidden;
          background: rgba(15,23,42,0.06);
          border: 1px solid rgba(15,23,42,0.10);
          margin: 6px 0 10px 0;
        }
        .p7-hud-gauge .fill{
          height:100%;
          background: linear-gradient(90deg, rgba(34,211,238,0.95), rgba(124,58,237,0.95));
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
"""

    return s[:insert_at] + BASE + s[insert_at:]


# ------------------------------------------------------------
# 2) render_top_hud(): remove repeated <style> injection block
#    Keep: scope anchor + columns + content + gauge
# ------------------------------------------------------------
def patch_render_top_hud(s: str) -> str:
    m = re.search(r"^def\s+render_top_hud\s*\(\s*\)\s*:\s*\n", s, flags=re.M)
    if not m:
        raise SystemExit("render_top_hud() not found")

    # within render_top_hud, remove the st.markdown("""<style> ... </style> ...""", unsafe_allow_html=True) block
    # Keep the anchor div line if present.
    # We'll replace that whole st.markdown(...) call with only: st.markdown('<div id="p7hud_scope_anchor"></div>', ...)
    start = m.end()
    # find first st.markdown( """ <style> ... </style> ... <div id="p7hud_scope_anchor"> ... )
    pat = re.compile(
        r"""st\.markdown\(\s*(""" + '"""' + r""")[\s\S]*?<div id="p7hud_scope_anchor"></div>[\s\S]*?\1\s*,\s*unsafe_allow_html\s*=\s*True\s*\)""",
        re.M
    )
    # fallback if above fails: match st.markdown(""" ... <style> ... </style> ... """, unsafe_allow_html=True)
    pat2 = re.compile(
        r"""st\.markdown\(\s*(""" + '"""' + r""")[\s\S]*?<style>[\s\S]*?</style>[\s\S]*?\1\s*,\s*unsafe_allow_html\s*=\s*True\s*\)""",
        re.M
    )

    # operate only inside render_top_hud slice
    # determine function bounds
    m2 = re.search(r"^\s*def\s+\w+\s*\(", s[m.end():], flags=re.M)
    func_end = (m.end() + m2.start()) if m2 else len(s)
    body = s[m.start():func_end]

    if "p7hud_scope_anchor" in body:
        new_body = pat.sub(
            "st.markdown('<div id=\"p7hud_scope_anchor\"></div>', unsafe_allow_html=True)",
            body,
            count=1
        )
        if new_body == body:
            new_body = pat2.sub(
                "st.markdown('<div id=\"p7hud_scope_anchor\"></div>', unsafe_allow_html=True)",
                body,
                count=1
            )
    else:
        # if anchor missing, do nothing
        new_body = body

    return s[:m.start()] + new_body + s[func_end:]


# ------------------------------------------------------------
# 3) reading_arena_page(): wrap render_top_hud() call in st.empty() slot
# ------------------------------------------------------------
def patch_reading_arena_page(s: str) -> str:
    # Replace the single call line: render_top_hud()
    # with HUD slot structure (only first occurrence inside reading_arena_page)
    marker = "\n    render_top_hud()\n"
    if marker not in s:
        return s

    repl = "\n    _hud_slot = st.empty()\n    with _hud_slot.container():\n        render_top_hud()\n"
    return s.replace(marker, repl, 1)


src2 = src
src2 = patch_inject_css(src2)
src2 = patch_render_top_hud(src2)
src2 = patch_reading_arena_page(src2)

open(path, "w", encoding="utf-8").write(src2)
print("[OK] PERF PATCH applied: inject_css BASE once + render_top_hud no-repeat-style + HUD slot")

