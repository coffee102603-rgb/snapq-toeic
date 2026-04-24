# -*- coding: utf-8 -*-
"""
SnapQ CSS 총폭격 v7 — 강력 셀렉터 + 모바일 강제 확대 (2026-04-24)
═══════════════════════════════════════════════════════════

v6로 안 되는 이유 가능성:
  ① Streamlit 최신 버전이 DOM 구조 변경 (셀렉터 안 맞음)
  ② 모바일 브라우저 캐시

v7 해결:
  ✅ button 태그 직접 + 모든 가능한 셀렉터로 총폭격
  ✅ text-size-adjust: none (100% 대신 완전 차단)
  ✅ @media (max-device-width)도 추가 (구 안드로이드 대응)
  ✅ 여러 번 !important 중첩

실행:
    cd C:\\Users\\최정은\\Desktop\\snapq_toeic_V3
    python apply_patch_v7.py
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
backup = BACKUP_DIR / f"pretest_gate.py.v7_css_total.{stamp}.bak"
shutil.copy(FILE, backup)
print(f"✅ 백업: {backup}")

raw = FILE.read_bytes()
had_bom = raw.startswith(b"\xef\xbb\xbf")
if had_bom:
    raw = raw[3:]
text = raw.decode("utf-8")
orig_crlf = "\r\n" in text
content = text.replace("\r\n", "\n")
original = content

# ═══════════════════════════════════════════════════════════
# v6 CSS 블록 전체 → v7 총폭격
# ═══════════════════════════════════════════════════════════
old = """    /* v6: 모바일 강제 확대 (2026.04.24) */
    html, body {{
        -webkit-text-size-adjust: 100% !important;
        text-size-adjust: 100% !important;
    }}
    div.stButton > button {{
        border-radius: 14px !important;
        font-size: 40px !important;
        font-weight: 900 !important;
        padding: 16px !important;
        touch-action: manipulation !important;
        line-height: 1.35 !important;
        -webkit-text-size-adjust: 100% !important;
    }}
    /* 관문검사 2x2 그리드만 작게 유지 (긴 영문 선택지) */
    div[data-testid="column"] div.stButton > button {{
        font-size: 22px !important;
        padding: 14px 6px !important;
        line-height: 1.25 !important;
    }}
    /* 모바일 (≤768px) 강제 확대 — iOS Safari 자동 축소 방지용 */
    @media (max-width: 768px) {{
        div.stButton > button {{
            font-size: 48px !important;
            line-height: 1.4 !important;
        }}
        div[data-testid="column"] div.stButton > button {{
            font-size: 26px !important;
        }}
    }}
    div.stRadio > label {{ color: #ffffff !important; font-size: 18px !important; }}"""

new = """    /* v7: CSS 총폭격 — 모든 Streamlit 버전 대응 (2026.04.24) */
    html, body, #root, [data-testid="stAppViewContainer"] {{
        -webkit-text-size-adjust: none !important;
        text-size-adjust: none !important;
    }}
    /* 모든 버튼 겨냥 (Streamlit 구/신 버전 총망라) */
    button,
    button[kind],
    button[kind="secondary"],
    button[kind="primary"],
    div.stButton > button,
    div.stButton button,
    .stButton > button,
    .stButton button,
    [data-testid*="stButton"] button,
    [data-testid*="stBaseButton"] button,
    [data-testid*="baseButton"] button,
    [class*="stButton"] button,
    [class*="st-emotion"] button {{
        font-size: 44px !important;
        font-weight: 900 !important;
        line-height: 1.35 !important;
        padding: 16px !important;
        border-radius: 14px !important;
        touch-action: manipulation !important;
        -webkit-text-size-adjust: none !important;
    }}
    /* 관문검사 2x2 그리드만 작게 유지 (긴 영문 선택지) */
    div[data-testid="column"] button,
    div[data-testid="column"] div.stButton > button,
    [data-testid="column"] button {{
        font-size: 22px !important;
        padding: 14px 6px !important;
        line-height: 1.25 !important;
    }}
    /* 모바일 강제 확대 — 모든 모바일 기기 대응 */
    @media (max-width: 768px), (max-device-width: 768px), (pointer: coarse) {{
        button,
        div.stButton > button,
        div.stButton button,
        .stButton button,
        [data-testid*="Button"] button {{
            font-size: 52px !important;
            line-height: 1.4 !important;
            padding: 18px !important;
        }}
        div[data-testid="column"] button,
        [data-testid="column"] button {{
            font-size: 26px !important;
            padding: 14px 6px !important;
        }}
    }}
    div.stRadio > label {{ color: #ffffff !important; font-size: 18px !important; }}
    /* 텍스트 입력창도 크게 */
    div.stTextArea textarea,
    div.stTextInput input {{
        font-size: 22px !important;
        line-height: 1.5 !important;
    }}
    @media (max-width: 768px) {{
        div.stTextArea textarea,
        div.stTextInput input {{
            font-size: 28px !important;
        }}
    }}"""

if old in content:
    content = content.replace(old, new)
    print("✅ 패치: CSS v6 → v7 총폭격 (모든 셀렉터 44px / 모바일 52px)")
else:
    print("⚠️  v6 원본 못 찾음 — 파일 상태 확인 필요")
    sys.exit(1)

if content == original:
    print("❌ 변경 없음")
    sys.exit(1)

if orig_crlf:
    content = content.replace("\n", "\r\n")
out = content.encode("utf-8")
if had_bom:
    out = b"\xef\xbb\xbf" + out
FILE.write_bytes(out)

print(f"✅ 저장 완료")
print(f"📁 백업: {backup}")
print("")
print("🧪 다음 단계:")
print("   git add app/core/pretest_gate.py apply_patch_v7.py")
print('   git commit -m "fix(mobile): CSS 총폭격 v7 - 모든 셀렉터 44/52px"')
print("   git push")
print("")
print("📱 ⭐⭐⭐ 반드시 아래 중 하나로 테스트 ⭐⭐⭐")
print("   1. 모바일 시크릿/프라이빗 탭")
print("   2. 또는 URL에 쿼리 추가: ?v=7")
print("   3. 또는 PC Chrome에서 F12 → 모바일 에뮬레이션")
