import os, sys, runpy

ROOT = os.path.dirname(__file__)
os.chdir(ROOT)

# 1) sys.path에서 snapq_toeic(다른 루트) 경로 제거
cleaned = []
for p in sys.path:
    if not p:
        continue
    pl = p.lower()
    if "snapq_toeic" in pl and "snapq_toeic\\" not in (ROOT.lower() + "\\"):
        continue
    cleaned.append(p)

# ROOT를 최우선으로
sys.path = [ROOT] + [p for p in cleaned if p != ROOT]

# 2) 동명 모듈 캐시 제거 (main_hub 충돌 방지)
for k in list(sys.modules.keys()):
    if k == "main_hub" or k.endswith(".main_hub"):
        sys.modules.pop(k, None)

# 3) SNAPQ_TOEIC/main_hub.py를 직접 실행
runpy.run_path(os.path.join(ROOT, "main_hub.py"), run_name="__main__")
