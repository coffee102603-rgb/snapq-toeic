with open("C:/Users/최정은/Desktop/snapq_toeic_V3/pages/04_P7_Reading.py", "r", encoding="utf-8-sig") as f:
    content = f.read()

# 현재 멘트 찾기
idx = content.find("P7예문=P5문제")
print(repr(content[idx-80:idx+100]))