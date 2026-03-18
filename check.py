import codecs
f = codecs.open('pages/02_P5_Arena.py', 'r', encoding='utf-8-sig')
lines = f.readlines()
f.close()
for i, line in enumerate(lines[43:60], start=44):
    print(f"{i}: {repr(line)}")
