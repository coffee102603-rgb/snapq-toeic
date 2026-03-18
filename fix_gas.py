# -*- coding: utf-8 -*-
content = open('pages/02_P5_Arena.py', 'r', encoding='utf-8').read()

old = '        setInterval(function(){{l--;if(l<0)l=0;e.textContent=l;var r=l/t;\n        var c=r>0.6?"safe":r>0.35?"warn":r>0.15?"danger":"critical";e.className=c;\n        b.className="b"+(r>0.6?"s":r>0.35?"w":r>0.15?"d":"c");b.style.width=(r*100)+"%";}},1000);'

new = '        setInterval(function(){{l--;if(l<0)l=0;e.textContent=l;var r=l/t;\n        var c=r>0.6?"safe":r>0.35?"warn":r>0.15?"danger":"critical";e.className=c;\n        b.className="b"+(r>0.6?"s":r>0.35?"w":r>0.15?"d":"c");b.style.width=(r*100)+"%";\n        var pd=window.parent.document;var app=pd.querySelector(".stApp");\n        if(app){{if(r>0.6){{app.style.background="linear-gradient(rgba(0,212,255,0.03) 1px,transparent 1px),linear-gradient(90deg,rgba(0,212,255,0.03) 1px,transparent 1px),#0a0a0a";}}\n        else if(r>0.35){{app.style.background="radial-gradient(ellipse at center,rgba(120,80,0,0.2) 0%,transparent 65%),#0a0a0a";}}\n        else if(r>0.15){{app.style.background="radial-gradient(ellipse at center,rgba(180,30,0,0.28) 0%,rgba(80,0,0,0.15) 45%,transparent 70%),#0a0505";}}\n        else{{app.style.background="radial-gradient(ellipse at center,rgba(255,0,0,0.35) 0%,rgba(120,0,0,0.22) 40%,transparent 65%),#0a0000";}}}}}},1000);'

r = content.replace(old, new, 1)
print('gas ok:', r != content)
content = r

open('pages/02_P5_Arena.py', 'w', encoding='utf-8').write(content)
print('done!')
