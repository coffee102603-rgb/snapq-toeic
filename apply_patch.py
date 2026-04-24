# -*- coding: utf-8 -*-
"""
SnapQ 데일리 게이트 패치 (2026-04-24)
  ① 헤더 복구: 🌅 오늘의 워밍업 · Day N + 문항 1/5 (CSS 공간 복원)
  ② 타이머 추가: 데일리 120초 (30초 이하 빨간색 깜빡임 + 자동 완료)
  ③ 상수 재정의: DAILY_GATE_TIME_SEC=120, MILESTONE_GATE_TIME_SEC=900

실행:
    cd C:\\Users\\최정은\\Desktop\\snapq_toeic_V3
    python apply_patch.py
"""
import shutil
import sys
from datetime import datetime
from pathlib import Path

# ─── stdout UTF-8 (윈도우 콘솔 한글 출력용) ───
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

FILE = Path("app/core/pretest_gate.py")
BACKUP_DIR = Path("backup_2026-04-27")
BACKUP_DIR.mkdir(exist_ok=True)

if not FILE.exists():
    print(f"❌ 파일 없음: {FILE.resolve()}")
    print("   → 프로젝트 루트(snapq_toeic_V3)에서 실행했는지 확인하세요.")
    sys.exit(1)

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_path = BACKUP_DIR / f"pretest_gate.py.pre_timer.{stamp}.bak"
shutil.copy(FILE, backup_path)
print(f"✅ 백업: {backup_path}")

content = FILE.read_text(encoding="utf-8")
original = content
patches_applied = 0

# ════════════════════════════════════════════════════════════
# 패치 ①-a : block-container padding-top 확대 (헤더 공간 확보)
# ════════════════════════════════════════════════════════════
old_1a = '    .block-container {{ max-width: 600px !important; margin: 0 auto !important; padding: 1rem 1rem 2rem 1rem !important; }}'
new_1a = '    .block-container {{ max-width: 600px !important; margin: 0 auto !important; padding: 2.5rem 1rem 2rem 1rem !important; }}'
if old_1a in content:
    content = content.replace(old_1a, new_1a)
    print("✅ 패치 ①-a: padding-top 1rem → 2.5rem (헤더 공간 확보)")
    patches_applied += 1
else:
    print("⚠️  패치 ①-a: 원본 못 찾음 (이미 적용됐거나 코드 변경됨)")

# ════════════════════════════════════════════════════════════
# 패치 ①-b : header display:none → visibility:hidden
# (공간은 유지하되 Streamlit 기본 메뉴/햄버거만 숨김)
# ════════════════════════════════════════════════════════════
old_1b = '    #MainMenu {{ display: none !important; }} footer {{ display: none !important; }} header {{ display: none !important; }} [data-testid="stHeader"] {{ display: none !important; }} [data-testid="stToolbar"] {{ display: none !important; }}'
new_1b = '    #MainMenu {{ display: none !important; }} footer {{ display: none !important; }} header {{ visibility: hidden !important; }} [data-testid="stHeader"] {{ visibility: hidden !important; }} [data-testid="stToolbar"] {{ display: none !important; }}'
if old_1b in content:
    content = content.replace(old_1b, new_1b)
    print("✅ 패치 ①-b: header visibility:hidden (공간 유지)")
    patches_applied += 1
else:
    print("⚠️  패치 ①-b: 원본 못 찾음")

# ════════════════════════════════════════════════════════════
# 패치 ② : 타이머 상수 추가 (DAILY 120초, MILESTONE 900초)
# ════════════════════════════════════════════════════════════
old_2 = "DAILY_GATE_QUESTIONS = 5     # 매일 아침 첫 접속 시 5문항\nDAILY_GATE_SECONDS   = 20    # 문항당 20초"
new_2 = (
    "DAILY_GATE_QUESTIONS     = 5     # 매일 아침 첫 접속 시 5문항\n"
    "DAILY_GATE_TIME_SEC      = 120   # ⭐ 데일리 총 제한: 2분\n"
    "DAILY_GATE_SECONDS       = 20    # (레거시, 참고용)\n"
    "MILESTONE_GATE_QUESTIONS = 30    # ⭐ 관문검사 30문항\n"
    "MILESTONE_GATE_TIME_SEC  = 900   # ⭐ 관문검사 총 제한: 15분"
)
if old_2 in content:
    content = content.replace(old_2, new_2)
    print("✅ 패치 ②: DAILY_GATE_TIME_SEC=120, MILESTONE_GATE_TIME_SEC=900")
    patches_applied += 1
else:
    print("⚠️  패치 ②: 원본 못 찾음")

# ════════════════════════════════════════════════════════════
# 패치 ③ : 데일리 게이트 헤더 직전에 타이머 삽입
#         + 시간 초과 서버측 자동 완료
# ════════════════════════════════════════════════════════════
old_3 = '''    q = questions[qi]
    day = _get_user_day(nickname, month_key)

    # 헤더
    st.markdown(f"""
    <div style="text-align:center;margin-top:8px;margin-bottom:20px;">
        <div style="font-size:22px;color:#3B82F6;font-weight:900;margin-bottom:4px;">
            🌅 오늘의 워밍업 · Day {day}
        </div>
        <div style="font-size:13px;color:rgba(255,255,255,0.5);">
            문항 {qi+1} / {DAILY_GATE_QUESTIONS}
        </div>
    </div>
    """, unsafe_allow_html=True)
'''

new_3 = '''    q = questions[qi]
    day = _get_user_day(nickname, month_key)

    # ─── ⏱ 타이머 시작 시각 (오늘 날짜 key: 매일 자동 리셋) ───
    _today_key = date.today().isoformat()
    _ts_key = f"daily_gate_start_ts_{_today_key}"
    if _ts_key not in st.session_state:
        st.session_state[_ts_key] = time.time()
    _elapsed = time.time() - st.session_state[_ts_key]
    _remaining = max(0, DAILY_GATE_TIME_SEC - int(_elapsed))

    # ─── 시간 초과 → 서버측 강제 완료 (JS 실패해도 안전장치) ───
    if _remaining <= 0:
        st.session_state.daily_time_spent_sec = int(_elapsed)
        st.session_state.daily_qi = DAILY_GATE_QUESTIONS
        st.rerun()

    # ─── 헤더 ───
    st.markdown(f"""
    <div style="text-align:center;margin-top:8px;margin-bottom:12px;">
        <div style="font-size:22px;color:#3B82F6;font-weight:900;margin-bottom:4px;">
            🌅 오늘의 워밍업 · Day {day}
        </div>
        <div style="font-size:13px;color:rgba(255,255,255,0.5);">
            문항 {qi+1} / {DAILY_GATE_QUESTIONS}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ─── ⏱ JS 카운트다운 타이머 (30초 이하 빨간 깜빡임) ───
    import streamlit.components.v1 as _components
    _m, _s = divmod(_remaining, 60)
    _components.html(f"""
    <div style="text-align:center;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
      <div id="snapq-timer-box" style="
           font-size:22px;font-weight:900;color:#3B82F6;
           padding:8px 22px;border-radius:24px;display:inline-block;
           background:rgba(59,130,246,0.12);
           border:1.5px solid rgba(59,130,246,0.4);
           transition:all 0.3s ease;">
        ⏱ <span id="snapq-time">{_m}:{_s:02d}</span>
      </div>
    </div>
    <script>
    (function() {{
        let remaining = {_remaining};
        const timeEl = document.getElementById('snapq-time');
        const boxEl  = document.getElementById('snapq-timer-box');
        if (!timeEl || !boxEl) return;
        function render() {{
            const m = Math.floor(remaining / 60);
            const s = remaining % 60;
            timeEl.textContent = m + ':' + (s < 10 ? '0' : '') + s;
            if (remaining <= 30) {{
                boxEl.style.color = '#EF4444';
                boxEl.style.background = 'rgba(239,68,68,0.15)';
                boxEl.style.borderColor = 'rgba(239,68,68,0.6)';
                boxEl.style.animation = 'snapq-pulse 0.9s ease-in-out infinite';
            }}
        }}
        render();
        const iv = setInterval(function() {{
            remaining -= 1;
            if (remaining < 0) {{
                clearInterval(iv);
                try {{ window.parent.location.reload(); }} catch(e) {{ location.reload(); }}
                return;
            }}
            render();
        }}, 1000);
    }})();
    </script>
    <style>
    @keyframes snapq-pulse {{
        0%, 100% {{ opacity: 1; transform: scale(1); }}
        50%      {{ opacity: 0.55; transform: scale(1.04); }}
    }}
    body {{ margin:0; padding:0; background:transparent; }}
    </style>
    """, height=70)
'''

if old_3 in content:
    content = content.replace(old_3, new_3)
    print("✅ 패치 ③: 데일리 헤더 + JS 타이머 + 서버 자동완료")
    patches_applied += 1
else:
    print("⚠️  패치 ③: 원본 못 찾음 ← 가장 중요! 다음 창에서 수동 확인 필요")

# ════════════════════════════════════════════════════════════
# 저장
# ════════════════════════════════════════════════════════════
print("")
if content == original:
    print("❌ 변경된 내용 없음. 원본 그대로 유지.")
    sys.exit(1)
else:
    FILE.write_text(content, encoding="utf-8")
    print(f"✅ 저장 완료 ({patches_applied}/4 패치 적용)")
    print(f"📁 원본 백업: {backup_path}")
    print("")
    print("🧪 다음 단계:")
    print("   streamlit run main.py")
    print("   → 데일리 게이트 접속해서 타이머 + 헤더 확인")
