import re
path = r"""C:\Users\최정은\Desktop\snapq_toeic\app\arenas\p7_reading_arena.py"""
src = open(path, "r", encoding="utf-8").read()

m = re.search(r"^def\s+render_top_hud\s*\(\s*\)\s*:\s*\n", src, flags=re.M)
if not m:
    raise SystemExit("render_top_hud() not found")
m2 = re.search(r"^\s*def\s+\w+\s*\(", src[m.end():], flags=re.M)
end = (m.end() + m2.start()) if m2 else len(src)
body = src[m.start():end]

# 1) time_stage가 있으면 그 아래에 강제 덮어쓰기 1줄 삽입
if "time_stage" in body:
    body2 = re.sub(
        r"(time_stage\s*=\s*\"p7-time-ok\"[\s\S]*?elif\s+remaining\s*<=\s*60:\s*\n\s*time_stage\s*=\s*\"p7-time-warn\"\s*\n)",
        r"\1    time_stage = \"p7-time-warn\"  # [TEST FORCE WARN]\n",
        body,
        count=1
    )
else:
    # time_stage가 아예 없다면, remaining 다음에 강제 선언(테스트용)
    body2 = re.sub(
        r"(remaining\s*=\s*max\([^\n]+\)\s*\n)",
        r"\1    time_stage = \"p7-time-warn\"  # [TEST FORCE WARN]\n",
        body,
        count=1
    )

patched = src[:m.start()] + body2 + src[end:]
open(path, "w", encoding="utf-8").write(patched)
print("[OK] TEST MODE applied: time_stage forced to WARN")

