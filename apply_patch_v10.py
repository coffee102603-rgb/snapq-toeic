# -*- coding: utf-8 -*-
"""
SnapQ v10 — 선택지 절반 + 문제 카드 확대·굵게 (2026-04-24)
═══════════════════════════════════════════════════════════

변경 (선생님 감각 기반):
  ✅ 선택지 버튼: 40px → 20px (1/2로 축소, 선생님 요청)
  ✅ 데일리 문제: 16px → 22px + font-weight:700 (30% 확대 + 굵게)
  ✅ 설문/관문 문제: 20px → 26px (30% 확대, 이미 bold)
  ✅ 결과: 문제와 선택지 크기 비슷하게 조화

실행:
    cd C:\\Users\\최정은\\Desktop\\snapq_toeic_V3
    python apply_patch_v10.py
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
backup = BACKUP_DIR / f"pretest_gate.py.v10_tune.{stamp}.bak"
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
patches = 0

# ═══════════════════════════════════════════════════════════
# 패치 ① : 선택지 버튼 40px → 20px (1/2)
# ═══════════════════════════════════════════════════════════
old_1 = "font-size: 40px !important"
new_1 = "font-size: 20px !important"
count_1 = content.count(old_1)
if count_1 > 0:
    content = content.replace(old_1, new_1)
    print(f"✅ 패치 ①: 선택지 버튼 40px → 20px ({count_1}곳)")
    patches += 1
else:
    print("⚠️  패치 ①: 'font-size: 40px' 못 찾음")

# ═══════════════════════════════════════════════════════════
# 패치 ② : 데일리 문제 카드 16px → 22px + bold
# ═══════════════════════════════════════════════════════════
old_2 = 'font-size:16px;color:#fff;line-height:1.6'
new_2 = 'font-size:22px;color:#fff;line-height:1.6;font-weight:700'
count_2 = content.count(old_2)
if count_2 > 0:
    content = content.replace(old_2, new_2)
    print(f"✅ 패치 ②: 데일리 문제 16px → 22px + bold ({count_2}곳)")
    patches += 1
else:
    print("⚠️  패치 ②: 'font-size:16px' 못 찾음")

# ═══════════════════════════════════════════════════════════
# 패치 ③ : 설문/관문 문제 카드 20px → 26px
# (두 위치 동시 교체 — 같은 문자열)
# ═══════════════════════════════════════════════════════════
old_3 = 'font-size:20px;font-weight:700;color:#fff;line-height:1.6'
new_3 = 'font-size:26px;font-weight:700;color:#fff;line-height:1.6'
count_3 = content.count(old_3)
if count_3 > 0:
    content = content.replace(old_3, new_3)
    print(f"✅ 패치 ③: 설문/관문 문제 20px → 26px ({count_3}곳)")
    patches += 1
else:
    print("⚠️  패치 ③: 'font-size:20px;font-weight:700' 못 찾음")

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

print(f"\n✅ 저장 완료 ({patches}/3 패치 적용)")
print(f"📁 백업: {backup}")
print("")
print("📏 최종 크기:")
print("   - 데일리 문제:   22px (bold)")
print("   - 선택지 버튼:   20px (1/2)")
print("   - 관문/설문 문제: 26px (bold)")
print("   - 관문 2x2 선택지: 22px (유지)")
print("")
print("🧪 다음 단계:")
print("   git add app/core/pretest_gate.py apply_patch_v10.py")
print('   git commit -m "style: v10 미세조정 - 선택지 1/2 + 문제 카드 30% 확대"')
print("   git push")
print("")
print("📱 모바일: https://snapq-toeic.streamlit.app?v=10")
