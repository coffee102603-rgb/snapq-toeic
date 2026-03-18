import os, glob
import streamlit as st

def _find_latest_disabled_hub():
    cands = sorted(glob.glob("main_hub_DISABLED_*.py"), key=lambda p: os.path.getmtime(p), reverse=True)
    return cands[0] if cands else None

def _inject_after_set_page_config(code: str) -> str:
    lines = code.splitlines()
    idx = None
    for i, ln in enumerate(lines):
        if "set_page_config" in ln and "st." in ln:
            idx = i
            break

    banner = r'''
# ===== [SNAPQ MASTER SAFE BANNER] =====
import os as _os
import streamlit as st

_cwd = _os.getcwd()
_cwd_lower = _cwd.lower()

# 진짜 ARCHIVE만 차단 (경로에 "_archive_" 포함 시)
if "_archive_" in _cwd_lower:
    st.error("📦 이 폴더는 _ARCHIVE_ 입니다. 실행하면 안 됩니다.")
    st.code(_cwd)
    st.stop()

st.markdown(
    f"""
    <div style="
        background: linear-gradient(90deg,#0b1220,#111827);
        padding: 14px 18px;
        border-radius: 10px;
        margin-bottom: 16px;
        color: #f9fafb;
        font-size: 16px;
        font-weight: 800;">
        ✅ 이 파일은 <span style="color:#22c55e;">MASTER SAFE HUB</span>로 실행 중입니다
        <div style="margin-top:6px;font-size:12px;font-weight:400;color:#cbd5e1;">
            실행 폴더: <code style="color:#93c5fd;">{_cwd}</code>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
# ===== [/SNAPQ MASTER SAFE BANNER] =====
'''.strip("\n")

    # set_page_config가 없는 파일이면, 맨 위에 set_page_config부터 강제
    if idx is None:
        head = 'st.set_page_config(page_title="SNAPQ TOEIC · MASTER", layout="wide")\n'
        return head + banner + "\n\n" + code

    # set_page_config가 여러 줄일 수 있으니, 괄호 닫히는 줄까지 찾기
    paren = 0
    end = idx
    started = False
    for j in range(idx, len(lines)):
        ln = lines[j]
        if "set_page_config" in ln and "st." in ln:
            started = True
        if started:
            paren += ln.count("(") - ln.count(")")
            if paren <= 0 and j > idx:
                end = j
                break

    injected = lines[:end+1] + [""] + [banner] + [""] + lines[end+1:]
    return "\n".join(injected)

def main():
    hub = _find_latest_disabled_hub()
    if not hub:
        st.set_page_config(page_title="SNAPQ SAFE HUB", layout="wide")
        st.error("❌ main_hub_DISABLED_*.py 파일을 찾지 못했습니다.")
        st.stop()

    # 원본 허브 코드 로드
    code = open(hub, "r", encoding="utf-8", errors="replace").read()

    # set_page_config 바로 뒤에 배너+진짜 ARCHIVE 가드 삽입
    patched = _inject_after_set_page_config(code)

    # 실행
    glb = {"__name__": "__main__", "__file__": hub}
    exec(compile(patched, hub, "exec"), glb, glb)

if __name__ == "__main__":
    main()
