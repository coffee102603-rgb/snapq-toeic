# -*- coding: utf-8 -*-
"""
SnapQ v9 — 박스 원복 + 자식 요소(p 태그) 폰트 강제 (2026-04-24)
═══════════════════════════════════════════════════════════

v8 실패 원인 (스크린샷 분석):
  - button 태그에 font-size 적용됨 → 하지만 내부 <p> 태그는 자기만의 크기
  - 박스만 커지고 글자는 그대로
  → Streamlit 버튼 DOM: <button><p>텍스트</p></button>
  → `button *` 로 자식 요소까지 타겟팅 필요

v9 해결:
  ✅ 박스 크기 원래대로 복원 (padding 14px, min-height 제거)
  ✅ `button *, button p, button span` 셀렉터로 자식 폰트 강제
  ✅ 40px (60px은 너무 컸음)
  ✅ stMarkdownContainer 내부 p 태그도 직접 타겟

실행:
    cd C:\\Users\\최정은\\Desktop\\snapq_toeic_V3
    python apply_patch_v9.py
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
backup = BACKUP_DIR / f"pretest_gate.py.v9_child.{stamp}.bak"
shutil.copy(FILE, backup)
print(f"✅ 백업: {backup}")

raw = FILE.read_bytes()
had_bom = raw.startswith(b"\xef\xbb\xbf")
if had_bom:
    raw = raw[3:]
text = raw.decode("utf-8")
orig_crlf = "\r\n" in text
content = text.replace("\r\n", "\n")

# _inject_gate_css 함수 위치 찾기
start = content.find("def _inject_gate_css(")
if start < 0:
    print("❌ 함수 시작 못 찾음")
    sys.exit(1)

end = content.find("\n# ====", start + 50)
if end < 0:
    print("❌ 함수 끝 못 찾음")
    sys.exit(1)
end += 1

print(f"📍 교체 대상: Line {content[:start].count(chr(10))+1} ~ Line {content[:end].count(chr(10))+1}")

# ═══════════════════════════════════════════════════════════
# v9 핵심: button 자식 요소(p, span)까지 font-size 강제
# ═══════════════════════════════════════════════════════════
new_block = '''def _inject_gate_css(color: str = "#7C5CFF") -> None:
    """v9 — button 내부 <p> 태그까지 font-size 강제 적용"""
    st.markdown(f"""
    <style>
    /* 앱 기본 */
    .stApp {{ background: #0D0F1A !important; }}
    .block-container {{
        max-width: 600px !important;
        margin: 0 auto !important;
        padding: 2.5rem 1rem 2rem 1rem !important;
    }}
    /* iOS 자동 축소 방지 */
    html, body {{
        -webkit-text-size-adjust: none !important;
        text-size-adjust: none !important;
    }}
    /* 박스 크기 (원래대로 복원) */
    button,
    div.stButton > button,
    .stButton > button,
    [data-testid*="Button"] button {{
        border-radius: 14px !important;
        padding: 14px !important;
        font-weight: 900 !important;
        touch-action: manipulation !important;
    }}
    /* ⭐⭐⭐ 핵심: button 안의 모든 자식 요소(p, span 등)에 font-size 직접 적용 */
    button,
    button *,
    button p,
    button span,
    button div,
    div.stButton > button,
    div.stButton > button *,
    div.stButton button p,
    div.stButton button span,
    .stButton button,
    .stButton button *,
    .stButton button p,
    [data-testid*="Button"] button,
    [data-testid*="Button"] button *,
    [data-testid*="Button"] button p {{
        font-size: 40px !important;
        line-height: 1.3 !important;
        font-weight: 900 !important;
    }}
    /* 관문검사 2x2 그리드만 작게 유지 */
    div[data-testid="column"] button,
    div[data-testid="column"] button *,
    div[data-testid="column"] button p,
    [data-testid="column"] button,
    [data-testid="column"] button * {{
        font-size: 22px !important;
        line-height: 1.25 !important;
    }}
    /* 입력창 */
    div.stTextArea textarea,
    div.stTextInput input {{
        font-size: 24px !important;
        line-height: 1.5 !important;
    }}
    /* 라디오 */
    div.stRadio > label {{ color: #ffffff !important; font-size: 18px !important; }}
    div[data-testid="stRadio"] label span {{ color: #ffffff !important; }}
    /* Streamlit UI 숨김 */
    #MainMenu {{ display: none !important; }}
    footer {{ display: none !important; }}
    header {{ visibility: hidden !important; }}
    [data-testid="stHeader"] {{ visibility: hidden !important; }}
    [data-testid="stToolbar"] {{ display: none !important; }}
    </style>
    """, unsafe_allow_html=True)


'''

new_content = content[:start] + new_block + content[end:]

if new_content == content:
    print("❌ 변경 없음")
    sys.exit(1)

if orig_crlf:
    new_content = new_content.replace("\n", "\r\n")
out = new_content.encode("utf-8")
if had_bom:
    out = b"\xef\xbb\xbf" + out
FILE.write_bytes(out)

print(f"✅ 함수 교체 성공")
print(f"📁 백업: {backup}")
print("")
print("🎯 v9 핵심 차이: button * 로 <p> 태그 자식까지 font-size 강제")
print("")
print("🧪 다음 단계:")
print("   git add app/core/pretest_gate.py apply_patch_v9.py")
print('   git commit -m "fix(mobile): v9 - button 자식 요소 폰트 강제 (p 태그 타겟)"')
print("   git push")
print("")
print("📱 모바일: https://snapq-toeic.streamlit.app?v=9")
