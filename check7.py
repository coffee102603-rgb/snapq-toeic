with open("C:/Users/최정은/Desktop/snapq_toeic_V3/pages/04_P7_Reading.py", "r", encoding="utf-8-sig") as f:
    content = f.read()

idx = content.find("무기 장착")
while idx != -1:
    print(repr(content[idx-10:idx+40]))
    idx = content.find("무기 장착", idx+1)