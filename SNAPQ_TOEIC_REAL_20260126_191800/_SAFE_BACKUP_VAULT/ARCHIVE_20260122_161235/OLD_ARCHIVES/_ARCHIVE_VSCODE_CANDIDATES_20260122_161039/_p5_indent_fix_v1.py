from pathlib import Path
import datetime, re

root = Path(r"C:\Users\최정은\Desktop\SNAPQ_TOEIC")
arena = root / r"app\arenas\p5_timebomb_arena.py"

stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
bk = arena.with_suffix(arena.suffix + f".bak_indentfix_{stamp}")
bk.write_text(arena.read_text(encoding="utf-8", errors="ignore"), encoding="utf-8")
print("[BACKUP]", bk)

lines = arena.read_text(encoding="utf-8", errors="ignore").splitlines(True)

def is_effectively_empty_block(i, indent):
    # 다음 줄부터 같은/더 작은 들여쓰기가 나오기 전까지,
    # '실행문'이 하나도 없으면 empty
    j = i + 1
    has_stmt = False
    while j < len(lines):
        s = lines[j]
        # 빈 줄은 무시
        if s.strip() == "":
            j += 1
            continue
        # 다음 블록/상위로 빠지는지 체크
        cur_indent = len(s) - len(s.lstrip(" "))
        if cur_indent <= indent:
            break
        # 주석만 있으면 실행문 아님
        if s.lstrip().startswith("#"):
            j += 1
            continue
        # 실행문 존재
        has_stmt = True
        break
    return not has_stmt

out = []
i = 0
while i < len(lines):
    line = lines[i]
    m = re.match(r"^(\s*)with\s+cols\[\d+\]\s*:\s*$", line)
    if m:
        indent = len(m.group(1))
        out.append(line)
        if is_effectively_empty_block(i, indent):
            out.append(" " * (indent + 4) + "pass\n")
        i += 1
        continue
    out.append(line)
    i += 1

arena.write_text("".join(out), encoding="utf-8")
print("[OK] indent fixed:", arena)
