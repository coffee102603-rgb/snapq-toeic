import json
from pathlib import Path

P5_PATH = Path("app/data/p5_bank/p5_demo_sets.json")

def main():
    data = json.loads(P5_PATH.read_text(encoding="utf-8-sig"))

    # 현재 사용 중인 id
    used = set()
    for x in data:
        qid = x.get("id")
        if isinstance(qid, int):
            used.add(qid)

    def next_free(start, end):
        for i in range(start, end + 1):
            if i not in used:
                return i
        raise RuntimeError(f"No free id in range {start}-{end}")

    # vocab만 대상으로 easy/hard 분리
    vocab = [x for x in data if x.get("mode") == "vocab"]
    easy = [x for x in vocab if x.get("level") == "easy"]
    hard = [x for x in vocab if x.get("level") == "hard"]

    # easy -> 100~199
    for item in easy:
        old = item.get("id")
        if not (isinstance(old, int) and 100 <= old <= 199):
            new_id = next_free(100, 199)
            if isinstance(old, int):
                used.discard(old)
            used.add(new_id)
            item["id"] = new_id

    # hard -> 200~299
    for item in hard:
        old = item.get("id")
        if not (isinstance(old, int) and 200 <= old <= 299):
            new_id = next_free(200, 299)
            if isinstance(old, int):
                used.discard(old)
            used.add(new_id)
            item["id"] = new_id

    P5_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print("✅ vocab id 재배치 완료 (easy=100~199, hard=200~299)")

if __name__ == "__main__":
    main()
