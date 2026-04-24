# -*- coding: utf-8 -*-
"""
SnapQ 버튼 글자 크기 조정 v4 (2026-04-24)
═══════════════════════════════════════════════════════════

변경:
  ✅ 전면 버튼 (데일리 게이트 A/B/C/D, 설문 선택형, 제출): 22px → 36px
  ✅ 그리드 버튼 (리커트 5열, 관문 2×2): 별도 규칙으로 16px 유지
  ✅ 박스 크기(padding)는 그대로 유지

실행:
    cd C:\\Users\\최정은\\Desktop\\snapq_toeic_V3
    python apply_patch_v4.py
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
backup = BACKUP_DIR / f"pretest_gate.py.v4_font.{stamp}.bak"
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

# ═══════════════════════════════════════════════════════════
# 패치: CSS 블록 교체 (버튼 폰트 분기)
# ═══════════════════════════════════════════════════════════
old = """    div.stButton > button {{
        border-radius: 14px !important; font-size: 22px !important;
        font-weight: 900 !important; padding: 14px !important;
        touch-action: manipulation !important;
    }}
    div.stRadio > label {{ color: #ffffff !important; font-size: 16px !important; }}"""

new = """    div.stButton > button {{
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

if old in content:
    content = content.replace(old, new)
    print("✅ 패치: 데일리·선택형 버튼 36px / 그리드 버튼 16px 분기")
else:
    print("⚠️  원본 못 찾음 (현재 폰트가 22px이 아닐 수 있음)")
    # 22px 없으면 18px에서 시도 (혹시 몰라서)
    old_alt = old.replace("22px", "18px")
    if old_alt in content:
        content = content.replace(old_alt, new)
        print("✅ 패치 (18px 원본 기준)")
    else:
        print("❌ 어느 쪽도 매칭 안 됨 — 수동 확인 필요")
        sys.exit(1)

# 저장
if content == original:
    print("❌ 변경 없음")
    sys.exit(1)

if orig_crlf:
    content = content.replace("\n", "\r\n")
out = content.encode("utf-8")
if had_bom:
    out = b"\xef\xbb\xbf" + out
FILE.write_bytes(out)

print("✅ 저장 완료")
print(f"📁 백업: {backup}")
print("")
print("🧪 다음 단계:")
print("   git add app/core/pretest_gate.py apply_patch_v4.py")
print('   git commit -m "style: 버튼 폰트 분기 — 전면 36px / 그리드 16px 유지"')
print("   git push")
