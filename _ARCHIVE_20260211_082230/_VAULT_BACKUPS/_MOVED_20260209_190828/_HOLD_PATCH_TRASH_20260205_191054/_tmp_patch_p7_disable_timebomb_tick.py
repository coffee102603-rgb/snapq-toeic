import re

path = r"""C:\Users\최정은\Desktop\snapq_toeic\app\arenas\p7_reading_arena.py"""
src = open(path, "r", encoding="utf-8").read()

# 1) 딱 이것만 잡는다: st_autorefresh(... key="p7_timebomb_tick")
#    - 해당 줄을 주석 처리
#    - 바로 위 import 줄도 함께 주석 처리(같은 블록일 가능성 높음)
lines = src.splitlines(True)
out = []
changed = 0

for i, ln in enumerate(lines):
    if 'st_autorefresh(interval=1000' in ln and 'key="p7_timebomb_tick"' in ln and not ln.lstrip().startswith("#"):
        out.append("# [AUTO-DISABLED duplicate P7 tick] " + ln)
        changed += 1
        continue

    # 같은 블록의 import도 같이 주석(선택): 바로 다음줄이 timebomb_tick이면 import도 죽인다
    if 'from streamlit_autorefresh import st_autorefresh' in ln and not ln.lstrip().startswith("#"):
        # 다음 몇 줄 안에 timebomb_tick 호출이 있으면 이 import도 주석 처리
        window = "".join(lines[i:i+6])
        if 'key="p7_timebomb_tick"' in window:
            out.append("# [AUTO-DISABLED duplicate P7 tick] " + ln)
            changed += 1
            continue

    out.append(ln)

open(path, "w", encoding="utf-8").write("".join(out))
print(f"[OK] disabled p7_timebomb_tick occurrences: {changed}")

