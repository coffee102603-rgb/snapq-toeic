# ===== SNAPQ ARMORY TRACE BANNER (AUTO) =====
try:
    import streamlit as st
    st.error("🔥 SECRET ARMORY FILE LOADED: __FILE__ = " + __file__)
except Exception:
    pass
# ===========================================
# check_armory_path.py
import json
from pathlib import Path

print("\n[ SnapQ Secret Armory 寃쎈줈 吏꾨떒 ]\n")

candidates = [
    Path("data/secret_armory.json"),
    Path("data/armory/secret_armory.json"),
    Path("app/data/secret_armory.json"),
    Path("app/data/armory/secret_armory.json"),
]

for p in candidates:
    print(f"??寃??以? {p}")
    if not p.exists():
        print("   ???뚯씪 ?놁쓬\n")
        continue

    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        items = data.get("items", [])
        print(f"   ???뚯씪 議댁옱 / items 媛쒖닔 = {len(items)}")
        print(f"   ?뵎 keys = {list(data.keys())}\n")
    except Exception as e:
        print("   ?좑툘 ?쎄린 ?ㅽ뙣:", e, "\n")

