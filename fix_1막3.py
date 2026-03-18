content = open('pages/02_P5_Arena.py', 'r', encoding='utf-8').read()

# 기존 잘못된 CSS :has 셀렉터 제거
import re
content = re.sub(
    r'st\.markdown\("""<style>\ndiv\[data-testid="stButton"\].*?</style>""", unsafe_allow_html=True\)\n        ',
    '',
    content,
    flags=re.DOTALL
)

# JS colorTimers 함수 교체 - 더 단순하게
old = """        // 타이머 버튼 색상
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

new = """        function colorTimers(){
            doc.querySelectorAll('button').forEach(function(b){
                var t=(b.innerText||b.textContent||'').replace(/\\s+/g,' ').trim();
                if(t.indexOf('HARD')>=0){
                    b.style.background='linear-gradient(135deg,#1a0000,#3d0000)';
                    b.style.borderColor='#ff2244';
                    b.style.boxShadow='0 0 25px rgba(255,34,68,0.8)';
                    b.style.animation='tPulseR 1.8s ease-in-out infinite';
                } else if(t.indexOf('NORMAL')>=0){
                    b.style.background='linear-gradient(135deg,#00091a,#001a3d)';
                    b.style.borderColor='#00d4ff';
                    b.style.boxShadow='0 0 25px rgba(0,212,255,0.8)';
                    b.style.animation='tPulseB 1.8s ease-in-out infinite';
                } else if(t.indexOf('EASY')>=0){
                    b.style.background='linear-gradient(135deg,#001a08,#003d15)';
                    b.style.borderColor='#00ff88';
                    b.style.boxShadow='0 0 25px rgba(0,255,136,0.8)';
                    b.style.animation='tPulseG 1.8s ease-in-out infinite';
                } else if(t==='역전장'||t==='메인'||t==='🔥 역전장'||t==='🏠 메인'){
                    b.style.background='transparent';
                    b.style.border='1px solid #1e1e1e';
                    b.style.boxShadow='none';
                    b.style.animation='none';
                    b.style.fontSize='0.85rem';
                    b.style.padding='6px';
                    var p=b.querySelector('p');
                    if(p){p.style.fontSize='0.85rem';p.style.color='#444';}
                }
            });
        }
        setTimeout(colorTimers,300);setTimeout(colorTimers,800);setTimeout(colorTimers,2000);
        new MutationObserver(function(){setTimeout(colorTimers,150);}).observe(doc.body,{childList:true,subtree:true});"""

content = content.replace(old, new)
open('pages/02_P5_Arena.py', 'w', encoding='utf-8').write(content)
print('done')