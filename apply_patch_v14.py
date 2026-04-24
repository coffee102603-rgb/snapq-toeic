# -*- coding: utf-8 -*-
"""
SnapQ v14 — 관리자 페이지 astype(float) ValueError 수정 (2026-04-24)
═══════════════════════════════════════════════════════════

문제:
  File "pages/01_Admin.py", line 255
  avg_rt = round(udf["rt_proxy"].astype(float).mean(), 1)
  → ValueError: could not convert string to float (빈 값 또는 None 섞임)

해결:
  astype(float) → pd.to_numeric(..., errors='coerce')
  빈 값/None을 NaN으로 처리 후 평균 계산 (숫자만 사용)

실행:
    cd C:\\Users\\최정은\\Desktop\\snapq_toeic_V3
    python apply_patch_v14.py
"""
import shutil, sys, re
from datetime import datetime
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

FILE = Path("pages/01_Admin.py")
BACKUP_DIR = Path("backup_2026-04-27")
BACKUP_DIR.mkdir(exist_ok=True)

if not FILE.exists():
    print(f"❌ 파일 없음: {FILE.resolve()}")
    sys.exit(1)

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUP_DIR / f"01_Admin.py.v14.{stamp}.bak"
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
# 모든 .astype(float) → pd.to_numeric(errors='coerce')
# ═══════════════════════════════════════════════════════════
# 패턴: udf["컬럼명"].astype(float)  또는  df["컬럼명"].astype(float)
# 변경: pd.to_numeric(udf["컬럼명"], errors='coerce')

# 정규식으로 모든 .astype(float) 매칭
# 예: udf["rt_proxy"].astype(float).mean()
#  → pd.to_numeric(udf["rt_proxy"], errors='coerce').mean()

pattern = re.compile(
    r'(\w+(?:\[["\'][^"\']+["\']\])?)\.astype\(float\)'
)

matches = pattern.findall(content)
print(f"🔍 발견된 .astype(float) 패턴: {len(matches)}개")
for m in matches[:10]:
    print(f"   - {m}.astype(float)")

# 교체
def replace_astype(m):
    target = m.group(1)
    return f"pd.to_numeric({target}, errors='coerce')"

new_content = pattern.sub(replace_astype, content)
count = len(matches)

# pd import 확인
if "import pandas as pd" not in new_content and count > 0:
    # import 추가 필요
    if "import streamlit as st" in new_content:
        new_content = new_content.replace(
            "import streamlit as st",
            "import streamlit as st\nimport pandas as pd",
            1
        )
        print("✅ import pandas as pd 추가")

if new_content == content:
    print("⚠️  변경 없음 - 이미 수정되었거나 패턴 불일치")
    sys.exit(0)

content = new_content
print(f"✅ {count}개 .astype(float) 변환")

# ═══════════════════════════════════════════════════════════
# 추가 안전장치 — astype(int), astype(str) 중 숫자 기대하는 것도 처리
# (필요시에만 - 지금은 에러난 것만 수정)
# ═══════════════════════════════════════════════════════════

# 저장
if orig_crlf:
    content = content.replace("\n", "\r\n")
out = content.encode("utf-8")
if had_bom:
    out = b"\xef\xbb\xbf" + out
FILE.write_bytes(out)

print(f"\n✅ pages/01_Admin.py 저장 완료")
print(f"📁 백업: {backup}")
print()
print("🧪 다음 단계:")
print("   git add pages/01_Admin.py apply_patch_v14.py")
print('   git commit -m "fix(admin): v14 astype(float) ValueError 수정"')
print("   git push")
print()
print("📱 푸시 후 관리자 페이지 재접속:")
print("   1. 별명 'admin_CJE'로 로그인")
print("   2. 관리자 박스 클릭")
print("   3. 에러 없이 대시보드 표시 확인")
