content = open('main_hub.py', 'r', encoding='utf-8').read()
content = content.replace("page_icon='??,", "page_icon='\u26a1',")
open('main_hub.py', 'w', encoding='utf-8').write(content)
print('확인:', repr([l for l in content.split('\n') if 'page_icon' in l]))
