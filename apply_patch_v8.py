# -*- coding: utf-8 -*-
"""
SnapQ v8 — 함수 통째 교체 (위치 기반) + 60px 과감 확대 (2026-04-24)
═══════════════════════════════════════════════════════════

v7 실패 원인:
  - 파일의 현재 CSS 블록이 내 예상과 달라 old 매칭 실패
  - → 매칭 안 해도 되는 방식 = 함수 전체 교체

v8 전략:
  ✅ `def _inject_gate_css(` 위치로 함수 시작 찾음
  ✅ 다음 `# =====` 경계로 함수 끝 찾음
  ✅ 사이를 완전히 새 CSS로 덮어씀
  ✅ 60px 매우 과감하게 (선생님·학생 모두 확실히 보일 크기)
  ✅ min-height: 100px 로 버튼 높이도 확실히 확보

실행:
    cd C:\\Users\\최정은\\Desktop\\snapq_toeic_V3
    python apply_patch_v8.py
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
backup = BACKUP_DIR / f"pretest_gate.py.v8_total.{stamp}.bak"
shutil.copy(FILE, backup)
print(f"✅ 백업: {backup}")

raw = FILE.read_bytes()
had_bom = raw.startswith(b"\xef\xbb\xbf")
if had_bom:
    raw = raw[3:]
text = raw.decode("utf-8")
orig_crlf = "\r\n" in text
content = text.replace("\r\n", "\n")

# ═══════════════════════════════════════════════════════════
# _inject_gate_css 함수 전체 위치 찾기
# ═══════════════════════════════════════════════════════════
start = content.find("def _inject_gate_css(")
if start < 0:
    print("❌ def _inject_gate_css( 함수 시작 못 찾음")
    sys.exit(1)

# 함수 끝 = 다음 # ===== 섹션 구분
# start 이후 50자 뒤부터 검색 (함수 시그니처 자체에 == 있을 가능성 제외)
end = content.find("\n# ====", start + 50)
if end < 0:
    print("❌ 함수 끝(다음 # ==== 섹션) 못 찾음")
    sys.exit(1)

end += 1  # \n 포함

old_block = content[start:end]
print(f"📍 교체 대상: Line {content[:start].count(chr(10))+1} ~ Line {content[:end].count(chr(10))+1}")
print(f"📏 기존 블록 크기: {len(old_block)} 자")

# ═══════════════════════════════════════════════════════════
# 새 _inject_gate_css 함수 (v8 최종)
# ═══════════════════════════════════════════════════════════
new_block = '''def _inject_gate_css(color: str = "#7C5CFF") -> None:
    """v8 — 모든 버튼 60px 강제 확대 (모바일/PC 공통)"""
    st.markdown(f"""
    <style>
    /* 앱 기본 */
    .stApp {{ background: #0D0F1A !important; }}
    .block-container {{
        max-width: 600px !important;
        margin: 0 auto !important;
        padding: 2.5rem 1rem 2rem 1rem !important;
    }}
    /* iOS/Android 자동 축소 방지 */
    html, body {{
        -webkit-text-size-adjust: none !important;
        text-size-adjust: none !important;
    }}
    /* 모든 버튼 총동원 (어떤 Streamlit 버전이든 매칭) */
    button,
    div.stButton button,
    div.stButton > button,
    .stButton button,
    .stButton > button,
    [data-testid*="Button"] button,
    [data-testid*="button"] button,
    [data-testid*="stBaseButton"] button,
    [class*="stButton"] button {{
        font-size: 60px !important;
        font-weight: 900 !important;
        line-height: 1.4 !important;
        padding: 20px !important;
        border-radius: 14px !important;
        touch-action: manipulation !important;
        min-height: 110px !important;
        -webkit-text-size-adjust: none !important;
    }}
    /* 관문검사 2x2 그리드 (columns 안)는 예외로 작게 */
    div[data-testid="column"] button,
    [data-testid="column"] button,
    div[data-testid="column"] div.stButton button {{
        font-size: 28px !important;
        padding: 16px 8px !important;
        line-height: 1.25 !important;
        min-height: 70px !important;
    }}
    /* 텍스트 입력창도 크게 */
    div.stTextArea textarea,
    div.stTextInput input {{
        font-size: 28px !important;
        line-height: 1.5 !important;
    }}
    /* 라디오 */
    div.stRadio > label {{ color: #ffffff !important; font-size: 20px !important; }}
    div[data-testid="stRadio"] label span {{ color: #ffffff !important; font-size: 20px !important; }}
    /* Streamlit 헤더/메뉴 숨김 */
    #MainMenu {{ display: none !important; }}
    footer {{ display: none !important; }}
    header {{ visibility: hidden !important; }}
    [data-testid="stHeader"] {{ visibility: hidden !important; }}
    [data-testid="stToolbar"] {{ display: none !important; }}
    </style>
    """, unsafe_allow_html=True)


'''

# 교체 실행
new_content = content[:start] + new_block + content[end:]

if new_content == content:
    print("❌ 변경 없음")
    sys.exit(1)

# 저장 (CRLF/BOM 복원)
if orig_crlf:
    new_content = new_content.replace("\n", "\r\n")
out = new_content.encode("utf-8")
if had_bom:
    out = b"\xef\xbb\xbf" + out
FILE.write_bytes(out)

print(f"✅ 함수 교체 성공 (새 블록 크기: {len(new_block)}자)")
print(f"📁 백업: {backup}")
print("")
print("🧪 다음 단계:")
print("   git add app/core/pretest_gate.py apply_patch_v8.py")
print('   git commit -m "fix(mobile): v8 - 함수 통째 교체 60px 과감 확대"')
print("   git push")
print("")
print("📱 반드시 모바일 시크릿 탭 또는 ?v=8 붙여서 접속!")
