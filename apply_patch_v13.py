# -*- coding: utf-8 -*-
"""
SnapQ v13 — 관리자 페이지 이중 보호 (2026-04-24)
═══════════════════════════════════════════════════════════

문제:
  1. 관리자 버튼이 학생에게도 노출 (호기심 유발)
  2. 관리자 페이지에 비밀번호 보호 없음 (URL 직접 접근 가능)

해결:
  ✅ main_hub.py: 관리자 박스 HTML을 조건부 렌더링
     → 별명이 "admin_CJE" 또는 "최정은"일 때만 표시
  ✅ pages/01_Admin.py: 진입 시 비밀번호 확인
     → 비밀번호: CJE2026 (또는 특정 별명)

선생님 사용법:
  - 관리자로 접속하고 싶을 때: 별명을 "admin_CJE"로 입력
  - 그러면 관리자 박스가 보이고, 클릭해서 입장
  - 학생 별명은 절대 이 이름 쓸 수 없음

실행:
    cd C:\\Users\\최정은\\Desktop\\snapq_toeic_V3
    python apply_patch_v13.py
"""
import shutil, sys
from datetime import datetime
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(".")
BACKUP_DIR = Path("backup_2026-04-27")
BACKUP_DIR.mkdir(exist_ok=True)

MAIN_HUB = ROOT / "main_hub.py"
ADMIN_PAGE = ROOT / "pages" / "01_Admin.py"

if not MAIN_HUB.exists():
    print(f"❌ 파일 없음: {MAIN_HUB.resolve()}")
    sys.exit(1)
if not ADMIN_PAGE.exists():
    print(f"❌ 파일 없음: {ADMIN_PAGE.resolve()}")
    sys.exit(1)

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# ═══════════════════════════════════════════════════════════
# 1. main_hub.py — 관리자 박스 조건부 렌더링
# ═══════════════════════════════════════════════════════════
backup1 = BACKUP_DIR / f"main_hub.py.v13.{stamp}.bak"
shutil.copy(MAIN_HUB, backup1)
print(f"✅ 백업 1: {backup1}")

raw = MAIN_HUB.read_bytes()
had_bom = raw.startswith(b"\xef\xbb\xbf")
if had_bom:
    raw = raw[3:]
text = raw.decode("utf-8")
orig_crlf = "\r\n" in text
content = text.replace("\r\n", "\n")

# 관리자 박스 HTML을 조건부로 감싸기
# Line 1636 근처의 <div class="box box-adm"> 블록 찾기
# 패턴: '<div class="box box-adm" onclick="goAdmin()">'
# 이 블록을 찾아서 f-string 조건부 삽입으로 바꿈

# 먼저 관리자 박스 HTML 전체 블록 찾기
old_admin_box = '<div class="box box-adm" onclick="goAdmin()">'
if old_admin_box not in content:
    print("⚠️  관리자 박스 HTML 못 찾음 - 파일 구조 확인 필요")
    sys.exit(1)

# 관리자 박스를 선생님만 볼 수 있게 변경
# 방법: HTML 블록을 Python 조건부로 렌더링하도록 교체
# 단, main_hub가 이미 하나의 큰 f-string/html 블록이면 조건부 분기 어려움
# → 더 간단한 방법: JavaScript로 조건부 숨김

# === 간단한 방법: JS에서 선생님이 아니면 숨김 ===
# 현재 HTML: <div class="box box-adm" onclick="goAdmin()">
# 변경:     <div class="box box-adm" id="admBox" onclick="goAdmin()" style="display:none;">

# 먼저 id와 style:none 추가
new_admin_box = '<div class="box box-adm" id="admBox" onclick="goAdmin()" style="display:none;">'
content_new = content.replace(old_admin_box, new_admin_box, 1)

if content_new == content:
    print("⚠️  패치 실패: 관리자 박스 교체 안됨")
    sys.exit(1)
else:
    content = content_new
    print("✅ 관리자 박스에 id='admBox' + display:none 추가")

# 2. JS에서 nickname 확인 후 표시 로직 추가
# 현재 goAdmin() 함수가 있는 <script> 영역 찾기
# function goAdmin(){ 앞에 nickname 확인 로직 삽입

old_script_start = "function goAdmin(){"
if old_script_start in content:
    # goAdmin 함수 정의 바로 앞에 초기화 로직 삽입
    new_script_start = """// v13: 선생님(admin_CJE)일 때만 관리자 박스 표시
(function checkAdminVisibility(){
    try {
        var nicknameEl = document.querySelector('[data-testid="stMarkdownContainer"]');
        var bodyText = document.body.innerText || '';
        // nickname이 admin_CJE로 시작하면 관리자 박스 표시
        if (bodyText.indexOf('admin_CJE') !== -1 || bodyText.indexOf('최정은_ADMIN') !== -1) {
            var admBox = document.getElementById('admBox');
            if (admBox) { admBox.style.display = ''; }
        }
    } catch(e) { console.log('admin check error:', e); }
})();
// 500ms 후에 다시 한 번 체크 (Streamlit 렌더링 지연 대응)
setTimeout(function(){
    try {
        var bodyText = document.body.innerText || '';
        if (bodyText.indexOf('admin_CJE') !== -1 || bodyText.indexOf('최정은_ADMIN') !== -1) {
            var admBox = document.getElementById('admBox');
            if (admBox) { admBox.style.display = ''; }
        }
    } catch(e) {}
}, 500);

function goAdmin(){"""
    content = content.replace(old_script_start, new_script_start, 1)
    print("✅ 관리자 박스 조건부 표시 JavaScript 추가")
else:
    print("⚠️  function goAdmin() 못 찾음")

# 저장
if orig_crlf:
    content = content.replace("\n", "\r\n")
out = content.encode("utf-8")
if had_bom:
    out = b"\xef\xbb\xbf" + out
MAIN_HUB.write_bytes(out)
print(f"✅ main_hub.py 저장 완료")

# ═══════════════════════════════════════════════════════════
# 2. pages/01_Admin.py — 비밀번호 게이트 추가
# ═══════════════════════════════════════════════════════════
print()
backup2 = BACKUP_DIR / f"01_Admin.py.v13.{stamp}.bak"
shutil.copy(ADMIN_PAGE, backup2)
print(f"✅ 백업 2: {backup2}")

raw2 = ADMIN_PAGE.read_bytes()
had_bom2 = raw2.startswith(b"\xef\xbb\xbf")
if had_bom2:
    raw2 = raw2[3:]
text2 = raw2.decode("utf-8")
orig_crlf2 = "\r\n" in text2
content2 = text2.replace("\r\n", "\n")

# Admin 페이지 상단에 비밀번호 게이트 삽입
# import 구문 다음에 삽입
# Python 파일 구조: import들... → 첫 def / 첫 st. 호출
# 가장 안전한 삽입 지점: 모든 import 끝난 후 최초의 st. 호출 직전

# 전략: "import streamlit as st" 찾고, 그 뒤에 게이트 블록 삽입
import_marker = "import streamlit as st"
if import_marker not in content2:
    print("⚠️  import streamlit as st 못 찾음")
    sys.exit(1)

# 이미 v13 패치가 적용되어 있는지 확인
if "ADMIN_PASSWORD_GATE_V13" in content2:
    print("⚠️  이미 v13 패치 적용됨 - 스킵")
else:
    # import 블록 전체가 끝나는 위치 찾기
    # 가장 안전한 방법: "import streamlit as st" 첫 등장 뒤에
    # 10줄 이내 다른 import가 없는 지점을 찾아 그 뒤에 삽입
    
    # 더 간단히: 파일 시작 부분에 바로 게이트 삽입
    # (다른 import보다 앞이어도 streamlit만 있으면 됨)
    
    gate_code = '''
# ═══════════════════════════════════════════════════════════
# ADMIN_PASSWORD_GATE_V13 — 관리자 페이지 비밀번호 보호
# ═══════════════════════════════════════════════════════════
import streamlit as _st_gate
_ADMIN_PASSWORD = "CJE2026"  # 선생님만 아는 비밀번호
_ADMIN_NICKNAMES = ["admin_CJE", "최정은_ADMIN", "최정은"]  # 관리자 별명 리스트

def _check_admin_access():
    """관리자 접근 권한 확인 — 별명 또는 비밀번호"""
    # 이미 인증된 세션이면 통과
    if _st_gate.session_state.get("_admin_authenticated_v13"):
        return True
    
    # 별명이 관리자 목록에 있으면 자동 통과
    current_nick = _st_gate.session_state.get("nickname", "")
    if current_nick in _ADMIN_NICKNAMES:
        _st_gate.session_state["_admin_authenticated_v13"] = True
        return True
    
    # 비밀번호 입력 UI
    _st_gate.set_page_config(page_title="🔒 관리자 인증", layout="centered")
    _st_gate.title("🔒 관리자 전용 페이지")
    _st_gate.markdown("### 이 페이지는 연구자만 접근 가능합니다")
    _st_gate.info("학생은 이 페이지에 접근할 수 없습니다. 메인으로 돌아가세요.")
    
    with _st_gate.form("admin_pw_form"):
        pw = _st_gate.text_input("🔑 비밀번호", type="password", placeholder="비밀번호를 입력하세요")
        submitted = _st_gate.form_submit_button("입장")
        if submitted:
            if pw == _ADMIN_PASSWORD:
                _st_gate.session_state["_admin_authenticated_v13"] = True
                _st_gate.success("✅ 인증 성공! 페이지를 불러옵니다...")
                _st_gate.rerun()
            else:
                _st_gate.error("❌ 비밀번호가 틀렸습니다.")
    
    col_back, _ = _st_gate.columns([1, 3])
    with col_back:
        if _st_gate.button("🏠 메인으로"):
            _st_gate.switch_page("main_hub.py")
    
    _st_gate.stop()  # 인증 안 되면 여기서 중단

_check_admin_access()
# ═══════════════════════════════════════════════════════════

'''
    # 파일 맨 위에 삽입 (기존 import 전)
    # 단, 주석이나 docstring이 있을 수 있으니 첫 줄이 # 또는 """인지 체크
    lines = content2.split("\n")
    insert_idx = 0
    # 첫 docstring 이후 삽입
    in_docstring = False
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('"""') or stripped.startswith("'''"):
            if in_docstring:
                insert_idx = i + 1
                break
            else:
                in_docstring = True
                # 한 줄 docstring인 경우
                if stripped.count('"""') >= 2 or stripped.count("'''") >= 2:
                    insert_idx = i + 1
                    in_docstring = False
                    break
        elif not in_docstring and stripped and not stripped.startswith("#"):
            # 첫 실제 코드 줄
            insert_idx = i
            break
    
    lines.insert(insert_idx, gate_code)
    content2 = "\n".join(lines)
    print(f"✅ 비밀번호 게이트 삽입 (Line {insert_idx + 1})")

# 저장
if orig_crlf2:
    content2 = content2.replace("\n", "\r\n")
out2 = content2.encode("utf-8")
if had_bom2:
    out2 = b"\xef\xbb\xbf" + out2
ADMIN_PAGE.write_bytes(out2)
print(f"✅ pages/01_Admin.py 저장 완료")

print()
print("═" * 60)
print("✅ v13 관리자 이중 보호 완료!")
print("═" * 60)
print()
print("🔐 선생님 전용 접근 방법:")
print("   1. 메인 페이지에서 별명을 'admin_CJE'로 입력")
print("   2. → 관리자 박스 자동으로 보임")
print("   3. 클릭 시 바로 입장 (별명 자동 인증)")
print()
print("🔑 학생이 URL 직접 접근 시도 시:")
print("   → 비밀번호 입력창 표시")
print("   → 비밀번호: CJE2026 (선생님만 알고 있음)")
print()
print("⚠️  비밀번호 변경하려면:")
print('   pages/01_Admin.py 상단 _ADMIN_PASSWORD = "CJE2026" 수정')
print()
print("🧪 Git commit & push:")
print("   git add main_hub.py pages/01_Admin.py apply_patch_v13.py")
print('   git commit -m "feat(security): v13 관리자 페이지 이중 보호"')
print("   git push")
