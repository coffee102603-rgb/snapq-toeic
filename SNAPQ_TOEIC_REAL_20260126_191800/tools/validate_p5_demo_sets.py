import json
from pathlib import Path
import sys

P5_PATH = Path("app/data/p5_bank/p5_demo_sets.json")

def error(msg):
    print(f"❌ {msg}")
    sys.exit(1)

def main():
    if not P5_PATH.exists():
        error(f"파일 없음: {P5_PATH}")

    data = json.loads(P5_PATH.read_text(encoding="utf-8-sig"))

    seen_ids = set()

    for q in data:
        qid = q.get("id")
        mode = q.get("mode")
        level = q.get("level")
        options = q.get("options", [])
        ans = q.get("answer_index")

        if not isinstance(qid, int):
            error(f"id가 int가 아님: {qid}")

        if qid in seen_ids:
            error(f"id 중복 발견: {qid}")
        seen_ids.add(qid)

        if mode == "grammar":
            if not (1 <= qid <= 99):
                error(f"grammar id 범위 오류: {qid} (1~99)")
        elif mode == "vocab" and level == "easy":
            if not (100 <= qid <= 199):
                error(f"vocab easy id 범위 오류: {qid} (100~199)")
        elif mode == "vocab" and level == "hard":
            if not (200 <= qid <= 299):
                error(f"vocab hard id 범위 오류: {qid} (200~299)")
        else:
            error(f"알 수 없는 mode/level 조합: id={qid}, mode={mode}, level={level}")

        if not isinstance(options, list) or len(options) != 4:
            error(f"id {qid}: options 4개 아님")

        if not isinstance(ans, int) or not (0 <= ans < 4):
            error(f"id {qid}: answer_index 오류 (0~3)")

    print("✅ p5_demo_sets.json 검증 통과")

if __name__ == "__main__":
    main()
