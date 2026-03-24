with open("C:/Users/최정은/Desktop/snapq_toeic_V3/pages/04_P7_Reading.py", "r", encoding="utf-8-sig") as f:
    content = f.read()

old = "⚔️ 📖 읽고 → 이해하고 → 저장! → 오답전장 반복!"
new = "📖 읽고 → 이해하고 → 저장! → 오답전장 반복!"
old2 = "💾 저장 → 오답전장!"
old3 = "⚔️ 무기 획득하기"

print("멘트:", old in content)
print("버튼1:", old2 in content)
print("버튼2:", old3 in content)

idx = content.find("읽고")
if idx != -1:
    print("읽고 위치:", repr(content[idx-30:idx+60]))
idx2 = content.find("획득")
if idx2 != -1:
    print("획득 위치:", repr(content[idx2-30:idx2+60]))