# -*- coding: utf-8 -*-
"""
SnapQ 버튼 폰트 모바일 강제 확대 v6 (2026-04-24)
═══════════════════════════════════════════════════════════

문제:
  - v5 패치 ①이 원본을 못 찾아 실패 → CSS는 v4 상태(36px)
  - 사용자 체감으로 36px도 모바일에서 작음
  - iOS Safari의 text-size-adjust 자동 축소 가능성

해결:
  ✅ 기본 버튼 폰트: 36px → 40px
  ✅ 모바일 전용 미디어 쿼리(≤768px): 48px 강제
  ✅ 관문검사 2x2: 22px (기존 16px에서 상향)
  ✅ -webkit-text-size-adjust: 100% 추가 (iOS 자동 축소 방지)

실행:
    cd C:\\Users\\최정은\\Desktop\\snapq_toeic_V3
    python apply_patch_v6.py
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
backup = BACKUP_DIR / f"pretest_gate.py.v6_font.{stamp}.bak"
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
# 패치: v4 CSS 블록(36px + columns 16px) 전체 → v6 강화
# ═══════════════════════════════════════════════════════════
old = """    div.stButton > button {{
        border-radius: 14px !important; font-size: 36px !important;
        font-weight: 900 !important; padding: 14px !important;
        touch-action: manipulation !important;
        line-height: 1.3 !important;
    }}
    /* 그리드 안의 버튼 (리커트 5열, 관문검사 2×2)은 작게 유지 */
    div[data-testid="column"] div.stButton > button {{
        font-size: 16px !important;
        padding: 12px 4px !important;
        line-height: 1.2 !important;
    }}
    div.stRadio > label {{ color: #ffffff !important; font-size: 16px !important; }}"""

new = """    /* v6: 모바일 강제 확대 (2026.04.24) */
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

if old in content:
    content = content.replace(old, new)
    print("✅ 패치: CSS v4 → v6 (40px + 모바일 48px 미디어 쿼리)")
else:
    print("⚠️  원본 못 찾음 — 선생님 로컬 파일 상태 확인 필요")
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
print("   git add app/core/pretest_gate.py apply_patch_v6.py")
print('   git commit -m "fix(mobile): 폰트 강제 확대 40px/48px + text-size-adjust"')
print("   git push")
print("")
print("📱 모바일에서는 반드시 **시크릿 탭**으로 재접속하세요! (캐시 회피)")
