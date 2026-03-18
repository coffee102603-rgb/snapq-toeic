# check_armory_path.py
import json
from pathlib import Path

print("\n[ SnapQ Secret Armory 경로 진단 ]\n")

candidates = [
    Path("data/secret_armory.json"),
    Path("data/armory/secret_armory.json"),
    Path("app/data/secret_armory.json"),
    Path("app/data/armory/secret_armory.json"),
]

for p in candidates:
    print(f"▶ 검사 중: {p}")
    if not p.exists():
        print("   ❌ 파일 없음\n")
        continue

    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        items = data.get("items", [])
        print(f"   ✅ 파일 존재 / items 개수 = {len(items)}")
        print(f"   🔑 keys = {list(data.keys())}\n")
    except Exception as e:
        print("   ⚠️ 읽기 실패:", e, "\n")
