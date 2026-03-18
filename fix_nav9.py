content = open('pages/02_P5_Arena.py', 'r', encoding='utf-8').read()

old = '        <a href="?nav=stg" target="_self" style="flex:1;display:block;text-align:center;padding:6px 4px;font-size:0.82rem;color:#666;border:1px solid rgba(255,255,255,0.15);border-radius:8px;text-decoration:none;background:transparent;">🔥 역전장</a>\n        <a href="?nav=hub" target="_self" style="flex:1;display:block;text-align:center;padding:6px 4px;font-size:0.82rem;color:#666;border:1px solid rgba(255,255,255,0.15);border-radius:8px;text-decoration:none;background:transparent;">🏠 메인</a>'

new = '        <a href="?nav=stg" target="_self" style="flex:0.8;display:block;text-align:center;padding:8px 4px;font-size:0.9rem;color:#666;border:1px solid rgba(255,255,255,0.15);border-radius:8px;text-decoration:none;background:transparent;">🔥 역전장</a>\n        <a href="?nav=hub" target="_self" style="flex:0.8;display:block;text-align:center;padding:8px 4px;font-size:0.9rem;color:#666;border:1px solid rgba(255,255,255,0.15);border-radius:8px;text-decoration:none;background:transparent;">🏠 메인</a>'

content = content.replace(old, new)
open('pages/02_P5_Arena.py', 'w', encoding='utf-8').write(content)
print('done:', '0.9rem' in content)