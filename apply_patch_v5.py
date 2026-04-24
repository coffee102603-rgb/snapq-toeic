# -*- coding: utf-8 -*-
"""
SnapQ 버튼 확대 v5 — 리커트 세로 1열 + 전체 32px (2026-04-24)
═══════════════════════════════════════════════════════════

변경:
  ✅ 리커트 설문 UI: 5열 그리드 → 세로 1열 (모바일 최적)
  ✅ 전체 버튼 폰트: 22px → 32px
  ✅ 관문검사 2×2 버튼은 예외로 20px 유지 (긴 영문 선택지 때문)
  ✅ 박스 크기(padding)는 유지

실행:
    cd C:\\Users\\최정은\\Desktop\\snapq_toeic_V3
    python apply_patch_v5.py
"""
import shutil, sys
from datetime import datetime
from pathlib import Path

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
backup = BACKUP_DIR / f"pretest_gate.py.v5_mobile.{stamp}.bak"
shutil.copy(FILE, backup)
print(f"✅ 백업: {backup}")

# 읽기 (BOM, CRLF 보존)
raw = FILE.read_bytes()
had_bom = raw.startswith(b"\xef\xbb\xbf")
if had_bom:
    raw = raw[3:]
text = raw.decode("utf-8")
orig_crlf = "\r\n" in text
content = text.replace("\r\n", "\n")
original = content
patches = 0

# ═══════════════════════════════════════════════════════════
# 패치 ① : CSS 블록 교체 (32px + 관문 2×2 예외)
# ═══════════════════════════════════════════════════════════
old_1 = """    div.stButton > button {{
        border-radius: 14px !important; font-size: 22px !important;
        font-weight: 900 !important; padding: 14px !important;
        touch-action: manipulation !important;
    }}
    div.stRadio > label {{ color: #ffffff !important; font-size: 16px !important; }}"""

new_1 = """    div.stButton > button {{
        border-radius: 14px !important; font-size: 32px !important;
        font-weight: 900 !important; padding: 14px !important;
        touch-action: manipulation !important;
        line-height: 1.35 !important;
        -webkit-text-size-adjust: 100% !important;
        text-size-adjust: 100% !important;
    }}
    /* 2x2 그리드 (관문검사) 는 긴 영문 선택지 때문에 작게 유지 */
    div[data-testid="column"] div.stButton > button {{
        font-size: 20px !important;
        padding: 14px 6px !important;
        line-height: 1.3 !important;
    }}
    div.stRadio > label {{ color: #ffffff !important; font-size: 16px !important; }}"""

if old_1 in content:
    content = content.replace(old_1, new_1)
    print("✅ 패치 ①: CSS 32px + 2x2 그리드 20px 예외")
    patches += 1
else:
    # v4가 이미 36px로 바꿨을 가능성 대비
    old_1_alt = old_1.replace("22px", "36px")
    if old_1_alt in content:
        content = content.replace(old_1_alt, new_1)
        print("✅ 패치 ① (v4 36px 기준 적용)")
        patches += 1
    else:
        print("⚠️  패치 ①: 원본 못 찾음")

# ═══════════════════════════════════════════════════════════
# 패치 ② : 리커트 UI 5열 → 세로 1열
# ═══════════════════════════════════════════════════════════
old_2 = """    else:
        # 5점 리커트
        cols = st.columns(5)
        for li, label in enumerate(LIKERT_OPTIONS):
            score = li + 1  # 1~5
            with cols[li]:
                if st.button(f\"{score}\\n{label}\", key=f\"sv_{qi}_{li}\",
                             use_container_width=True):
                    st.session_state.survey_responses[key] = score
                    st.session_state.survey_qi = qi + 1
                    st.rerun()"""

new_2 = """    else:
        # 5점 리커트 — 세로 1열 (v5 모바일 최적, 2026.04.24)
        for li, label in enumerate(LIKERT_OPTIONS):
            score = li + 1  # 1~5
            if st.button(f\"{score}. {label}\", key=f\"sv_{qi}_{li}\",
                         use_container_width=True):
                st.session_state.survey_responses[key] = score
                st.session_state.survey_qi = qi + 1
                st.rerun()"""

if old_2 in content:
    content = content.replace(old_2, new_2)
    print("✅ 패치 ②: 리커트 5열 → 세로 1열 (전체 32px 적용)")
    patches += 1
else:
    print("⚠️  패치 ②: 원본 못 찾음")

# ═══════════════════════════════════════════════════════════
# 저장
# ═══════════════════════════════════════════════════════════
print("")
if content == original:
    print("❌ 변경 내용 없음")
    sys.exit(1)

if orig_crlf:
    content = content.replace("\n", "\r\n")
out = content.encode("utf-8")
if had_bom:
    out = b"\xef\xbb\xbf" + out
FILE.write_bytes(out)

print(f"✅ 저장 완료 ({patches}/2 패치 적용)")
print(f"📁 백업: {backup}")
print("")
print("🧪 다음 단계:")
print("   git add app/core/pretest_gate.py apply_patch_v5.py")
print('   git commit -m "feat(ui): 리커트 세로 1열 + 버튼 32px (모바일 가독성)"')
print("   git push")
