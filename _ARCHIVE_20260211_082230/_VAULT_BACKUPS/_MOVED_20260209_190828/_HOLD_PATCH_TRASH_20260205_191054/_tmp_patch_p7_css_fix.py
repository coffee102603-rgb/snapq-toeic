import io, os, sys, time

path = r"""C:\Users\최정은\Desktop\snapq_toeic\app\arenas\p7_reading_arena.py"""
with open(path, "r", encoding="utf-8") as f:
    src = f.read()

needle = "def inject_css():"
i = src.find(needle)
if i < 0:
    raise SystemExit("inject_css() not found")

# inject_css() 시작부터 첫 st.markdown("<style> ...") 주입 직전까지를 안전하게 교체
# 목표:
#  - BASE CSS는 세션당 1회
#  - CRIT CSS는 매 rerun마다(짧게)
#
# 1) 함수 헤더 라인 끝 찾기
line_end = src.find("\n", i)
if line_end < 0:
    raise SystemExit("line break parse fail")

# 2) 기존 inject_css()의 맨 위 guard 블록을 제거/교체하기 위해
#    'def inject_css():' 다음 80줄 내에서 첫 'st.markdown(' 또는 'css = ' 같은 시작점을 찾는다
after = src[line_end+1:]
window = after[:8000]  # 충분히 크게
# inject_css 내부 첫 실행 코드 시작 위치(대략)
cut_candidates = []
for token in ["st.markdown(", "css = ", "CSS = ", "style = ", "st.write("]:
    p = window.find(token)
    if p >= 0:
        cut_candidates.append(p)
cut = min(cut_candidates) if cut_candidates else 0

prefix = src[:i]
rest   = after[cut:]  # 기존 본문은 유지(= 기존 CSS 문자열/내용/나머지 로직 누락 0)

# ✅ CRITICAL CSS: HUD가 깨지지 않게 하는 최소만 (짧게)
CRIT = r"""
/* P7 CRIT CSS (always) - prevents white/unstyled flashes */
.p7-hudbar{margin:0 0 6px 0!important;padding:4px 8px!important;border-radius:14px!important;}
.p7-hud-left{display:flex;gap:8px;align-items:center;flex-wrap:wrap;}
.p7-hud-gauge{height:10px;border-radius:999px;overflow:hidden;margin:6px 0 10px 0;}
.p7-hud-gauge .fill{height:100%;}
"""

new_head = f'''def inject_css():
    """
    ✅ P7 CSS injector (SAFE)
    - BASE CSS: session 1회만 주입 (크고 무거운 덩어리)
    - CRIT CSS: 매 rerun마다 주입 (짧은 최소 필수 -> 스타일 플래시 방지)
    """
    # ---- CRIT CSS (ALWAYS) ----
    st.markdown("<style>{CRIT}</style>", unsafe_allow_html=True)

    # ---- BASE CSS (ONCE per session) ----
    if st.session_state.get("_p7_base_css_once", False):
        return
    st.session_state["_p7_base_css_once"] = True

'''

patched = prefix + new_head + rest

with open(path, "w", encoding="utf-8") as f:
    f.write(patched)

print("[OK] patched inject_css(): BASE once + CRIT always")

