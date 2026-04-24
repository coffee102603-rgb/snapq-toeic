# -*- coding: utf-8 -*-
"""
SnapQ 연구 설계 재조정 + 관문검사 타이머 v2 (2026-04-24)
═══════════════════════════════════════════════════════════

변경 내용:
  ① Day 1  = 사전 설문 A~F만 (검사 X, 10분)
  ② Day 2  = pretest baseline (관문 30문항, 15분 타이머) ⭐ NEW
  ③ Day 11 = midtest (관문 30문항, 15분 타이머)
  ④ Day 20 = posttest (관문 30 + 사후 설문 G, 15분 타이머)
  ⑤ 그 외 = 데일리 5문항만 (게이트 없이 자유 입장)

이유:
  - 선생님 현장 관찰: Day 1~20이 학원 안정 구간
  - Day 21~28 (토익 시험 전후) = 대규모 이탈
  - 첫날 부담 최소화(10분) → 이탈률 ↓

실행:
    cd C:\\Users\\최정은\\Desktop\\snapq_toeic_V3
    python apply_patch_v2.py
"""
import shutil
import sys
from datetime import datetime
from pathlib import Path

# Windows 콘솔 UTF-8
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

FILE = Path("app/core/pretest_gate.py")
BACKUP_DIR = Path("backup_2026-04-27")
BACKUP_DIR.mkdir(exist_ok=True)

if not FILE.exists():
    print(f"❌ 파일 없음: {FILE.resolve()}")
    sys.exit(1)

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_path = BACKUP_DIR / f"pretest_gate.py.v2_design.{stamp}.bak"
shutil.copy(FILE, backup_path)
print(f"✅ 백업: {backup_path}")

# ━━━ 파일 읽기: CRLF/BOM 보존 ━━━
raw = FILE.read_bytes()
had_bom = raw.startswith(b"\xef\xbb\xbf")
if had_bom:
    raw = raw[3:]
text = raw.decode("utf-8")

original_crlf = "\r\n" in text
# 내부 처리는 \n 통일
content = text.replace("\r\n", "\n")
original = content
patches = 0

# ═══════════════════════════════════════════════════════════
# 패치 ① : 상수 재정의
# ═══════════════════════════════════════════════════════════
old_1 = """# --- 관문검사 (Milestone) ---
PRE_DAY          = 1     # Day 1: 사전 (검사 + 설문 A~F)
MILESTONE_EVERY  = 10    # 10일마다 관문검사 (Day 1, 11, 21, 31...)
POST_SURVEY_DAY  = 21    # Day 21 이상부터 사후 설문 G 추가"""

new_1 = """# --- 관문검사 (Milestone) — 재설계 2026.04.24 ---
# 학원 월 사이클(안정 20일)에 맞춘 3회 고정 측정
PRE_SURVEY_DAY   = 1     # ⭐ Day 1:  사전 설문 A~F만 (검사 X, 온보딩)
PRETEST_DAY      = 2     # ⭐ Day 2:  pretest baseline (검사 30만)
MIDTEST_DAY      = 11    # ⭐ Day 11: midtest (검사 30만)
POSTTEST_DAY     = 20    # ⭐ Day 20: posttest (검사 30 + 사후 설문 G)
MILESTONE_DAYS   = {PRETEST_DAY, MIDTEST_DAY, POSTTEST_DAY}  # {2, 11, 20}

# 레거시 호환 (기존 코드/로그에서 참조)
PRE_DAY          = PRE_SURVEY_DAY
MILESTONE_EVERY  = 10
POST_SURVEY_DAY  = POSTTEST_DAY"""

if old_1 in content:
    content = content.replace(old_1, new_1)
    print("✅ 패치 ①: 상수 재정의 (Day 1=설문만, Day 2/11/20=관문)")
    patches += 1
else:
    print("⚠️  패치 ①: 원본 못 찾음")

# ═══════════════════════════════════════════════════════════
# 패치 ② : is_milestone_day + get_milestone_round
# ═══════════════════════════════════════════════════════════
old_2 = """def is_milestone_day(day: int) -> bool:
    \"\"\"개인 Day가 관문검사 날인지 판정. Day 1, 11, 21, 31... = True\"\"\"
    if day < 1:
        return False
    return (day - 1) % MILESTONE_EVERY == 0


def get_milestone_round(day: int) -> int:
    \"\"\"관문검사 회차 계산 (Day 1=1회, Day 11=2회, Day 21=3회...)\"\"\"
    if not is_milestone_day(day):
        return 0
    return ((day - 1) // MILESTONE_EVERY) + 1"""

new_2 = """def is_milestone_day(day: int) -> bool:
    \"\"\"개인 Day가 관문검사 날인지 판정. Day 2, 11, 20 = True\"\"\"
    return day in MILESTONE_DAYS


def get_milestone_round(day: int) -> int:
    \"\"\"관문검사 회차 계산 (Day 2=1회 pretest, Day 11=2회 mid, Day 20=3회 post)\"\"\"
    mapping = {PRETEST_DAY: 1, MIDTEST_DAY: 2, POSTTEST_DAY: 3}
    return mapping.get(day, 0)"""

if old_2 in content:
    content = content.replace(old_2, new_2)
    print("✅ 패치 ②: is_milestone_day + get_milestone_round (Set 기반)")
    patches += 1
else:
    print("⚠️  패치 ②: 원본 못 찾음")

# ═══════════════════════════════════════════════════════════
# 패치 ③ : _get_required_stage() 재작성
# ═══════════════════════════════════════════════════════════
old_3 = """def _get_required_stage(nickname: str = \"\", month_key: str = \"\") -> Optional[int]:
    \"\"\"개인 Day 기준으로 필요한 관문검사 단계 반환.

    옵션 A 설계:
        Day 1  → stage 1 (사전검사 + 사전 설문 A~F)
        Day 11, 21, 31, 41... (is_milestone_day=True) → stage 2 (검사만)
        Day 21 이상 milestone → stage 3 (검사 + 사후 설문 G, 최초 1회만)
        기타 → None (자유 입장)
    \"\"\"
    day = _get_user_day(nickname, month_key)

    # Day 1: 사전 (설문 + 검사)
    if day == PRE_DAY:
        return 1

    # 관문검사 날이 아니면 게이트 없음
    if not is_milestone_day(day):
        return None

    # Day 11 이후 milestone → stage 2 (검사만)
    # 단, 사후 설문 아직 안 했으면 Day 21 이상에서 stage 3 처리
    if day >= POST_SURVEY_DAY:
        # 이미 사후 설문을 했는지 확인
        try:
            student_tests = _get_student_tests(nickname, month_key)
            if not student_tests.get(\"survey_post\"):
                return 3  # 아직 사후 설문 미완료 → stage 3
        except Exception:
            pass

    return 2  # 관문검사만"""

new_3 = """def _get_required_stage(nickname: str = \"\", month_key: str = \"\") -> Optional[int]:
    \"\"\"개인 Day 기준 필요한 stage 반환. — 재설계 2026.04.24

        Day 1  → stage 1 (사전 설문 A~F만, 검사 X)
        Day 2  → stage 2 (pretest baseline 30문항)
        Day 11 → stage 2 (midtest 30문항)
        Day 20 → stage 3 (posttest 30문항 + 사후 설문 G)
        그 외  → None (게이트 없이 자유 입장, 데일리 5문항만)
    \"\"\"
    day = _get_user_day(nickname, month_key)

    # Day 1: 사전 설문만 (관문검사 없음)
    if day == PRE_SURVEY_DAY:
        return 1

    # Day 20: posttest (관문 + 사후 설문 G)
    if day == POSTTEST_DAY:
        return 3

    # Day 2, 11: 관문검사만
    if day in (PRETEST_DAY, MIDTEST_DAY):
        return 2

    return None"""

if old_3 in content:
    content = content.replace(old_3, new_3)
    print("✅ 패치 ③: _get_required_stage() 재작성 (Day 2/11/20)")
    patches += 1
else:
    print("⚠️  패치 ③: 원본 못 찾음")

# ═══════════════════════════════════════════════════════════
# 패치 ④ : require_pretest_gate() - Stage 1에서 검사 흐름 제거
# ═══════════════════════════════════════════════════════════
old_4 = """    if required_stage == 1:
        survey_done = student_tests.get(\"survey_pre\") is not None
        if stage_done and survey_done:
            return  # 둘 다 완료
    elif required_stage == 3:"""

new_4 = """    if required_stage == 1:
        # ⭐ 재설계: Day 1은 설문만. 검사 없음.
        survey_done = student_tests.get(\"survey_pre\") is not None
        if survey_done:
            return  # 설문 완료 → 입장
    elif required_stage == 3:"""

if old_4 in content:
    content = content.replace(old_4, new_4)
    print("✅ 패치 ④-a: Stage 1 완료 조건 = 설문만")
    patches += 1
else:
    print("⚠️  패치 ④-a: 원본 못 찾음")

# Stage 1 흐름에서 "pre_test"로 전환하는 로직 제거 (설문 끝 = 입장)
old_5 = """    # --- STAGE 1: 사전 설문 → 검사 ---
    if flow == \"pre_survey\":
        if st.session_state.get(\"_survey_pre_done\"):
            # 설문 완료 → 검사로 전환
            st.session_state.current_gate_flow = \"pre_test\"
            st.session_state.test_qi = 0
            st.session_state.test_answers = []
            st.session_state.test_start = time.time()
            st.session_state.test_phase = \"quiz\"
            st.rerun()
        else:
            _render_survey(\"pre\", nickname, month_key)
            st.stop()

    if flow == \"pre_test\":
        if st.session_state.get(\"test_phase\") in (\"quiz\", \"result\"):
            _render_test(stage, nickname, month_key)
            st.stop()
        else:
            return  # 검사 완료 → 입장"""

new_5 = """    # --- STAGE 1: 사전 설문만 (검사 없음) — 재설계 2026.04.24 ---
    if flow == \"pre_survey\":
        if st.session_state.get(\"_survey_pre_done\"):
            return  # 설문 완료 → 바로 입장 (검사 X)
        else:
            _render_survey(\"pre\", nickname, month_key)
            st.stop()

    # flow == \"pre_test\" 레거시 경로: 혹시 남은 세션 있으면 통과 처리
    if flow == \"pre_test\":
        return"""

if old_5 in content:
    content = content.replace(old_5, new_5)
    print("✅ 패치 ④-b: pre_survey 완료 = 바로 입장 (pre_test 흐름 제거)")
    patches += 1
else:
    print("⚠️  패치 ④-b: 원본 못 찾음")

# ═══════════════════════════════════════════════════════════
# 패치 ⑤ : _render_test()에 15분 JS 타이머 + 자동완료
# ═══════════════════════════════════════════════════════════
old_6 = """def _render_test(stage: int, nickname: str, month_key: str) -> None:
    color = _stage_color(stage)
    name = _stage_name(stage)
    _inject_gate_css(color)

    # 초기화
    if \"test_qi\" not in st.session_state:
        st.session_state.test_qi = 0
        st.session_state.test_answers = []
        st.session_state.test_start = time.time()
        st.session_state.test_phase = \"quiz\"

    if st.session_state.get(\"test_phase\") == \"result\":
        _render_result(stage, nickname, month_key)
        return

    qi = st.session_state.test_qi
    total = len(TEST_QUESTIONS)

    # 헤더
    st.markdown(f\"\"\"
    <div style=\"text-align:center;padding:16px 0 12px;\">
        <div style=\"font-size:12px;font-weight:700;color:{color};letter-spacing:4px;margin-bottom:4px;\">
            SnapQ TOEIC · {name}
        </div>
        <div style=\"font-size:24px;font-weight:900;color:#fff;\">
            {qi + 1} / {total}
        </div>
        <div style=\"background:rgba(255,255,255,0.1);border-radius:999px;height:6px;margin:8px 0;\">
            <div style=\"background:{color};height:6px;border-radius:999px;
                        width:{int((qi / total) * 100)}%;transition:width 0.3s;\"></div>
        </div>
        <div style=\"font-size:12px;color:rgba(255,255,255,0.4);\">
            ⏱ 약 3분 · 편하게 풀어보세요
        </div>
    </div>
    \"\"\", unsafe_allow_html=True)"""

new_6 = """def _render_test(stage: int, nickname: str, month_key: str) -> None:
    color = _stage_color(stage)
    name = _stage_name(stage)
    _inject_gate_css(color)

    # 초기화
    if \"test_qi\" not in st.session_state:
        st.session_state.test_qi = 0
        st.session_state.test_answers = []
        st.session_state.test_start = time.time()
        st.session_state.test_phase = \"quiz\"

    # ─── ⏱ 시간 초과 → 서버측 강제 완료 (JS 실패해도 안전) ───
    _ts_start = st.session_state.get(\"test_start\", time.time())
    _test_elapsed = time.time() - _ts_start
    _test_remaining = max(0, MILESTONE_GATE_TIME_SEC - int(_test_elapsed))
    if _test_remaining <= 0 and st.session_state.get(\"test_phase\") == \"quiz\":
        st.session_state.test_time_spent_sec = int(_test_elapsed)
        st.session_state.test_phase = \"result\"
        st.rerun()

    if st.session_state.get(\"test_phase\") == \"result\":
        _render_result(stage, nickname, month_key)
        return

    qi = st.session_state.test_qi
    total = len(TEST_QUESTIONS)

    # 헤더
    st.markdown(f\"\"\"
    <div style=\"text-align:center;padding:16px 0 12px;\">
        <div style=\"font-size:12px;font-weight:700;color:{color};letter-spacing:4px;margin-bottom:4px;\">
            SnapQ TOEIC · {name}
        </div>
        <div style=\"font-size:24px;font-weight:900;color:#fff;\">
            {qi + 1} / {total}
        </div>
        <div style=\"background:rgba(255,255,255,0.1);border-radius:999px;height:6px;margin:8px 0;\">
            <div style=\"background:{color};height:6px;border-radius:999px;
                        width:{int((qi / total) * 100)}%;transition:width 0.3s;\"></div>
        </div>
    </div>
    \"\"\", unsafe_allow_html=True)

    # ─── ⏱ JS 카운트다운 타이머 (60초 이하 빨간 깜빡임) ───
    import streamlit.components.v1 as _components
    _mm, _ss = divmod(_test_remaining, 60)
    _components.html(f\"\"\"
    <div style=\"text-align:center;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;\">
      <div id=\"snapq-test-timer-box\" style=\"
           font-size:20px;font-weight:900;color:{color};
           padding:8px 22px;border-radius:24px;display:inline-block;
           background:rgba(0,229,255,0.10);
           border:1.5px solid {color}99;
           transition:all 0.3s ease;\">
        ⏱ <span id=\"snapq-test-time\">{_mm}:{_ss:02d}</span>
      </div>
    </div>
    <script>
    (function() {{
        let rem = {_test_remaining};
        const timeEl = document.getElementById('snapq-test-time');
        const boxEl  = document.getElementById('snapq-test-timer-box');
        if (!timeEl || !boxEl) return;
        function fmt(n) {{ return n < 10 ? '0' + n : '' + n; }}
        function render() {{
            const m = Math.floor(rem / 60);
            const s = rem % 60;
            timeEl.textContent = m + ':' + fmt(s);
            if (rem <= 60) {{
                boxEl.style.color = '#EF4444';
                boxEl.style.background = 'rgba(239,68,68,0.15)';
                boxEl.style.borderColor = 'rgba(239,68,68,0.6)';
                boxEl.style.animation = 'snapq-test-pulse 0.9s ease-in-out infinite';
            }}
        }}
        render();
        const iv = setInterval(function() {{
            rem -= 1;
            if (rem < 0) {{
                clearInterval(iv);
                try {{ window.parent.location.reload(); }} catch(e) {{ location.reload(); }}
                return;
            }}
            render();
        }}, 1000);
    }})();
    </script>
    <style>
    @keyframes snapq-test-pulse {{
        0%, 100% {{ opacity: 1; transform: scale(1); }}
        50%      {{ opacity: 0.55; transform: scale(1.04); }}
    }}
    body {{ margin:0; padding:0; background:transparent; }}
    </style>
    \"\"\", height=62)"""

if old_6 in content:
    content = content.replace(old_6, new_6)
    print("✅ 패치 ⑤: _render_test() 15분 타이머 + 자동완료")
    patches += 1
else:
    print("⚠️  패치 ⑤: 원본 못 찾음")

# ═══════════════════════════════════════════════════════════
# 저장 (CRLF/BOM 복원)
# ═══════════════════════════════════════════════════════════
print("")
if content == original:
    print("❌ 변경 내용 없음. 원본 유지.")
    sys.exit(1)

# 줄바꿈 복원
if original_crlf:
    content = content.replace("\n", "\r\n")

out_bytes = content.encode("utf-8")
if had_bom:
    out_bytes = b"\xef\xbb\xbf" + out_bytes

FILE.write_bytes(out_bytes)
print(f"✅ 저장 완료 ({patches}/6 패치 적용)")
print(f"📁 백업: {backup_path}")
print("")
print("🧪 다음 단계:")
print("   1. git add app/core/pretest_gate.py")
print("   2. git commit -m \"refactor: 연구 설계 재조정 Day 2/11/20 + 관문 15분 타이머\"")
print("   3. git push")
print("   4. ~1분 후 모바일 https://snapq-toeic.streamlit.app 에서 재테스트")
