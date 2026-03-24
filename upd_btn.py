import sys
sys.stdout.reconfigure(encoding="utf-8")
with open(r"C:\Users\최정은\Desktop\snapq_toeic_V3\pages\03_오답전장.py", "r", encoding="utf-8-sig") as f:
    content = f.read()
content = content.replace('f"\U0001f9e0  P7 \uc5b4\ud718 \ud559\uc2b5\ubaa8\ub4dc\\n\ub2e8\uc5b4\ub97c \uc644\uc804\ud788 \ub0b4 \ubab8\uc5d0 \uc0c8\uaca8\ub77c!', 'f"\U0001f4d6  P7 \ubb38\uc7a5 \ud559\uc2b5\ubaa8\ub4dc\\n\uc601\uc5b4\u2194\ud55c\uae00 \uc545\ubcf4+\ud53c\uc544\ub178 \ud559\uc2b5!')
content = content.replace('\U0001f4a6  \ub2e8\uc5b4 \uc800\uc7a5\uace0 \u00b7 \ubb34\uae30 \uad00\ub9ac', '\U0001f4e6  \ubb38\uc7a5 \uc800\uc7a5\uace0 \u00b7 \ud574\uc11d \uc5f0\uc2b5')
with open(r"C:\Users\최정은\Desktop\snapq_toeic_V3\pages\03_오답전장.py", "w", encoding="utf-8") as f:
    f.write(content)
print("완료!")
