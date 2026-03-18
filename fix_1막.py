content = open('pages/02_P5_Arena.py', 'r', encoding='utf-8').read()

# JS로 타이머 버튼 3개에 각각 색상 직접 주입
old = "        setTimeout(styleButtons,150);setTimeout(styleButtons,500);setTimeout(styleButtons,1200);setTimeout(styleButtons,3000);"
new = """        setTimeout(styleButtons,150);setTimeout(styleButtons,500);setTimeout(styleButtons,1200);setTimeout(styleButtons,3000);
        // 타이머 버튼 색상
        function colorTimers(){
            var btns=doc.querySelectorAll('button');
            var timerBtns=[];
            btns.forEach(function(b){
                var t=(b.innerText||'').trim();
                if(t.indexOf('HARD')>=0) timerBtns.push([b,'hard']);
                else if(t.indexOf('NORMAL')>=0) timerBtns.push([b,'norm']);
                else if(t.indexOf('EASY')>=0) timerBtns.push([b,'easy']);
            });
            timerBtns.forEach(function(pair){
                var b=pair[0],tp=pair[1];
                if(tp==='hard'){
                    b.style.cssText+='background:linear-gradient(135deg,#1a0000,#3d0000)!important;border:2px solid #ff2244!important;box-shadow:0 0 25px rgba(255,34,68,0.8)!important;animation:tPulseR 1.5s ease-in-out infinite!important;';
                } else if(tp==='norm'){
                    b.style.cssText+='background:linear-gradient(135deg,#00091a,#001a3d)!important;border:2px solid #00d4ff!important;box-shadow:0 0 25px rgba(0,212,255,0.8)!important;animation:tPulseB 1.5s ease-in-out infinite!important;';
                } else {
                    b.style.cssText+='background:linear-gradient(135deg,#001a08,#003d15)!important;border:2px solid #00ff88!important;box-shadow:0 0 25px rgba(0,255,136,0.8)!important;animation:tPulseG 1.5s ease-in-out infinite!important;';
                }
            });
            // 역전장/메인 버튼 작게
            btns.forEach(function(b){
                var t=(b.innerText||'').trim();
                if(t.indexOf('역전장')>=0||t.indexOf('메인')>=0){
                    b.style.cssText+='font-size:0.85rem!important;padding:6px!important;background:transparent!important;border:1px solid #222!important;color:#444!important;box-shadow:none!important;';
                    var p=b.querySelector('p');
                    if(p) p.style.cssText='font-size:0.85rem!important;color:#555!important;';
                }
            });
        }
        setTimeout(colorTimers,200);setTimeout(colorTimers,600);setTimeout(colorTimers,1500);
        new MutationObserver(function(){setTimeout(colorTimers,100);}).observe(doc.body,{childList:true,subtree:true});"""

content = content.replace(old, new)
open('pages/02_P5_Arena.py', 'w', encoding='utf-8').write(content)
print('done')