import re

path = r"""C:\Users\최정은\Desktop\snapq_toeic\app\arenas\p7_reading_arena.py"""
src = open(path, "r", encoding="utf-8").read()

# ------------------------------------------------------------
# A) inject_css(): add TIMER FX CSS (small, safe)
# ------------------------------------------------------------
def patch_inject_css(s: str) -> str:
    m = re.search(r"^def\s+inject_css\s*\(\s*\)\s*:\s*\n", s, flags=re.M)
    if not m:
        raise SystemExit("inject_css() not found")

    if "P7_TIMER_FX__V1" in s:
        return s  # already patched

    # Insert right AFTER the first st.markdown("""<style> ... </style>""", unsafe_allow_html=True) in inject_css
    inj_start = m.start()
    inj_slice = s[inj_start:]
    pos = inj_slice.find("unsafe_allow_html=True")
    if pos < 0:
        # fallback: insert right after def line
        insert_at = inj_start + m.end()
    else:
        # find the close of that st.markdown call: the next "\n    )"
        end_call = inj_slice.find("\n    )", pos)
        insert_at = (inj_start + end_call + len("\n    )")) if end_call >= 0 else (inj_start + m.end())

    add = r"""

    # ---- P7 TIMER FX (ALWAYS) ----
    st.markdown(
        r"""
        <style>
        /* P7_TIMER_FX__V1 */
        .p7-time-chip{
          font-size: 16px !important;
          font-weight: 900 !important;
          letter-spacing: 0.3px;
        }
        .p7-time-chip b{
          font-size: 18px !important;
          font-weight: 1000 !important;
        }

        /* 부드러운 좌우 움직임(요란함) */
        @keyframes p7_time_wiggle {
          0% { transform: translateX(0px); }
          25% { transform: translateX(-2px); }
          50% { transform: translateX(0px); }
          75% { transform: translateX(2px); }
          100% { transform: translateX(0px); }
        }

        /* 경고 펄스 */
        @keyframes p7_time_pulse {
          0% { box-shadow: 0 0 0 rgba(255,193,7,0.0); }
          50% { box-shadow: 0 0 18px rgba(255,193,7,0.35); }
          100% { box-shadow: 0 0 0 rgba(255,193,7,0.0); }
        }

        /* 위험(빨강) 깜빡 + 더 강한 흔들림 */
        @keyframes p7_time_flash {
          0% { filter: brightness(1.0); }
          50% { filter: brightness(1.55); }
          100% { filter: brightness(1.0); }
        }

        @keyframes p7_time_shake {
          0% { transform: translateX(0px); }
          20% { transform: translateX(-3px); }
          40% { transform: translateX(3px); }
          60% { transform: translateX(-2px); }
          80% { transform: translateX(2px); }
          100% { transform: translateX(0px); }
        }

        /* 상태별 색/연출 */
        .p7-time-ok{
          background: rgba(255,255,255,0.10) !important;
        }

        .p7-time-warn{
          border-color: rgba(255,193,7,0.55) !important;
          background: rgba(255,193,7,0.12) !important;
          animation: p7_time_wiggle 0.9s linear infinite, p7_time_pulse 1.0s ease-in-out infinite;
        }

        .p7-time-danger{
          border-color: rgba(255,45,45,0.70) !important;
          background: rgba(255,45,45,0.14) !important;
          animation: p7_time_wiggle 0.55s linear infinite, p7_time_flash 0.55s ease-in-out infinite;
        }

        .p7-time-final{
          border-color: rgba(255,0,0,0.90) !important;
          background: rgba(255,0,0,0.18) !important;
          animation: p7_time_shake 0.35s linear infinite, p7_time_flash 0.25s ease-in-out infinite;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
"""
    return s[:insert_at] + add + s[insert_at:]


# ------------------------------------------------------------
# B) render_top_hud(): add stage class to TIME chip
#   - Find the TIME chip HTML line and replace with staged class
# ------------------------------------------------------------
def patch_render_top_hud(s: str) -> str:
    m = re.search(r"^def\s+render_top_hud\s*\(\s*\)\s*:\s*\n", s, flags=re.M)
    if not m:
        raise SystemExit("render_top_hud() not found")

    # function bounds
    m2 = re.search(r"^\s*def\s+\w+\s*\(", s[m.end():], flags=re.M)
    end = (m.end() + m2.start()) if m2 else len(s)
    body = s[m.start():end]

    if "time_stage =" in body and "p7-time-chip" in body:
        return s  # already staged

    # Insert time_stage computation after remaining is defined
    # We assume remaining variable exists in function.
    insert_point = body.find("remaining =")
    if insert_point < 0:
        return s

    # Find line end after remaining assignment
    line_end = body.find("\n", insert_point)
    if line_end < 0:
        return s

    stage_block = """
    # --- TIME FX STAGE (UI ONLY) ---
    time_stage = "p7-time-ok"
    if remaining <= 10:
        time_stage = "p7-time-final"
    elif remaining <= 30:
        time_stage = "p7-time-danger"
    elif remaining <= 60:
        time_stage = "p7-time-warn"
"""

    body2 = body[:line_end+1] + stage_block + body[line_end+1:]

    # Replace TIME chip span (keep text same)
    body2 = body2.replace(
        '<span class="p7-chip">⏱ TIME <b>{get_time_display(remaining)}</b></span>',
        '<span class="p7-chip p7-time-chip {time_stage}">⏱ TIME <b>{get_time_display(remaining)}</b></span>'
    )

    return s[:m.start()] + body2 + s[end:]


src2 = src
src2 = patch_inject_css(src2)
src2 = patch_render_top_hud(src2)

open(path, "w", encoding="utf-8").write(src2)
print("[OK] STEP A applied: Timer drama CSS + staged TIME chip")

