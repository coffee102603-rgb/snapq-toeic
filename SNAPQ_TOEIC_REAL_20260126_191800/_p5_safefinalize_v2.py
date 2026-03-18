from pathlib import Path
import re, datetime

root = Path(r"C:\Users\최정은\Desktop\SNAPQ_TOEIC")
page = root / r"pages\02_P5_Timebomb_Arena.py"
arena = root / r"app\arenas\p5_timebomb_arena.py"

stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
bkdir = root / f"_BACKUP_P5_SAFEFINAL_{stamp}"
bkdir.mkdir(exist_ok=True)

def backup(p: Path):
    if p.exists():
        (bkdir / p.name).write_text(p.read_text(encoding="utf-8", errors="ignore"), encoding="utf-8")

backup(page); backup(arena)
print("[BACKUP]", bkdir)

# ------------------------
# pages: 정상 최소 래퍼로 재작성 (깨진 주석/잡음 제거)
# ------------------------
page_text = r'''import streamlit as st
from app.arenas import p5_timebomb_arena

st.markdown(r"""
<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
html, body, *{
  font-family: "Pretendard","Apple SD Gothic Neo","Malgun Gothic",Arial,sans-serif !important;
  letter-spacing:-0.2px;
}

/* 중앙 게임 고정 + 상단 여백 최소 */
section.main > div.block-container{
  padding-top:0.35rem !important;
  padding-bottom:0.8rem !important;
  max-width:1200px !important;
}

/* Streamlit 기본 헤더/툴바 숨김 */
header, [data-testid="stHeader"]{ height:0 !important; min-height:0 !important; visibility:hidden !important; }
[data-testid="stToolbar"]{ visibility:hidden !important; height:0 !important; }
</style>
""", unsafe_allow_html=True)

def run():
    return p5_timebomb_arena.run()

if __name__ == "__main__":
    run()
'''
page.write_text(page_text, encoding="utf-8")
print("[OK] pages rewritten:", page)

# ------------------------
# arena: 하단 3개 '표시만' 제거 (주석 처리)
# ------------------------
a = arena.read_text(encoding="utf-8", errors="ignore")

# 새 런/ TIP/ CORE SAFE 관련 라인 주석 처리
a = re.sub(r'(?m)^(\s*)if\s+st\.button\("🔄\s*새\s*런\(리셋\)".*$', r'\1# [HIDDEN_FOOTER] \g<0>', a)
a = re.sub(r'(?m)^(\s*)st\.caption\("TIP:.*$', r'\1# [HIDDEN_FOOTER] \g<0>', a)
a = re.sub(r'(?m)^(\s*)st\.caption\("P5 CORE SAFE"\)\s*$', r'\1# [HIDDEN_FOOTER] \g<0>', a)

arena.write_text(a, encoding="utf-8")
print("[OK] arena footer hidden:", arena)

print("[DONE]")
