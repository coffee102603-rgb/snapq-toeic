import re

path = r"""C:\Users\최정은\Desktop\snapq_toeic\app\arenas\p7_reading_arena.py"""
src = open(path, "r", encoding="utf-8").read()

# ------------------------------------------------------------
# 1) inject_css(): add TIMER FX CSS if missing
# ------------------------------------------------------------
def ensure_timer_fx(s: str) -> str:
    if "P7_TIMER_FX__LOCK_V3" in s:
        return s

    m = re.search(r"^def\s+inject_css\s*\(\s*\)\s*:\s*\n", s, flags=re.M)
    if not m:
        raise SystemExit("inject_css() not found")

    inj_start = m.start()
    inj_slice = s[inj_start:]
    # insert after first st.markdown(... unsafe_allow_html=True ...) close
    pos = inj_slice.find("unsafe_allow_html=True")
    end_call = inj_slice.find("\n    )", pos) if pos >= 0 else -1
    insert_at = (inj_start + end_call + len("\n    )")) if end_call >= 0 else (inj_start + m.end())

    fx = r"""

    # ---- P7 TIMER FX (ALWAYS) ----
    st.markdown(
        r"""
        <style>
        /* P7_TIMER_FX__LOCK_V3 */
        .p7-time-chip{ font-weight: 1000 !important; }
        .p7-time-chip b{ font-size: 20px !important; font-weight: 1100 !important; }

        @keyframes p7_wiggle {
          0%{transform:translateX(0)}
          25%{transform:translateX(-2px)}
          50%{transform:translateX(0)}
          75%{transform:translateX(2px)}
          100%{transform:translateX(0)}
        }
        @keyframes p7_pulse_y {
          0%{box-shadow:0 0 0 rgba(255,193,7,0)}
          50%{box-shadow:0 0 24px rgba(255,193,7,0.45)}
          100%{box-shadow:0 0 0 rgba(255,193,7,0)}
        }
        @keyframes p7_flash_r {
          0%{filter:brightness(1.0)}
          50%{filter:brightness(1.7)}
          100%{filter:brightness(1.0)}
        }
        @keyframes p7_shake {
          0%{transform:translateX(0)}
          20%{transform:translateX(-4px)}
          40%{transform:translateX(4px)}
          60%{transform:translateX(-3px)}
          80%{transform:translateX(3px)}
          100%{transform:translateX(0)}
        }
        @keyframes p7_heartbeat {
          0%{transform:scale(1)}
          50%{transform:scale(1.06)}
          100%{transform:scale(1)}
        }

        /* 60초 이하 */
        .p7-time-warn{
          border-color: rgba(255,193,7,0.65) !important;
          background: rgba(255,193,7,0.16) !important;
          animation: p7_wiggle 0.9s linear infinite, p7_pulse_y 0.95s ease-in-out infinite;
        }
        /* 30초 이하 */
        .p7-time-danger{
          border-color: rgba(255,45,45,0.80) !important;
          background: rgba(255,45,45,0.18) !important;
          animation: p7_wiggle 0.55s linear infinite, p7_flash_r 0.55s ease-in-out infinite;
        }
        /* 10초 이하 */
        .p7-time-final{
          border-color: rgba(255,0,0,0.95) !important;
          background: rgba(255,0,0,0.22) !important;
          animation: p7_shake 0.32s linear infinite, p7_flash_r 0.22s ease-in-out infinite, p7_heartbeat 0.32s ease-in-out infinite;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
"""
    return s[:insert_at] + fx + s[insert_at:]


# ------------------------------------------------------------
# 2) render_top_hud(): add time_stage + apply classes to TIME span
# ------------------------------------------------------------
def patch_render_top_hud(s: str) -> str:
    m = re.search(r"^def\s+render_top_hud\s*\(\s*\)\s*:\s*\n", s, flags=re.M)
    if not m:
        raise SystemExit("render_top_hud() not found")

    m2 = re.search(r"^\s*def\s+\w+\s*\(", s[m.end():], flags=re.M)
    end = (m.end() + m2.start()) if m2 else len(s)
    body = s[m.start():end]

    # if already staged, skip
    if "time_stage = " in body and "p7-time-chip" in body:
        return s

    # Insert stage right after remaining defined
    # find line: remaining = ...
    mm = re.search(r"^\s*remaining\s*=\s*max\([^\n]+\)\s*$", body, flags=re.M)
    if not mm:
        return s
    line_end = body.find("\n", mm.end())
    if line_end < 0:
        return s

    stage = """
    # --- TIME FX STAGE (UI ONLY) ---
    time_stage = "p7-time-ok"
    if remaining <= 10:
        time_stage = "p7-time-final"
    elif remaining <= 30:
        time_stage = "p7-time-danger"
    elif remaining <= 60:
        time_stage = "p7-time-warn"
"""
    body2 = body[:mm.end()] + "\n" + stage + body[mm.end():]

    # Replace the TIME span line (current file uses p7-chip only)
    body2 = body2.replace(
        '<span class="p7-chip">⏱ TIME <b>{get_time_display(remaining)}</b></span>',
        '<span class="p7-chip p7-time-chip {time_stage}">⏱ TIME <b>{get_time_display(remaining)}</b></span>'
    )

    return s[:m.start()] + body2 + s[end:]


src2 = ensure_timer_fx(src)
src2 = patch_render_top_hud(src2)

open(path, "w", encoding="utf-8").write(src2)
print("[OK] TIMER DRAMA APPLY done (TIME span class + FX CSS)")

