content = open('pages/02_P5_Arena.py', 'r', encoding='utf-8').read()

old = """        if st.button("🔥  HARD  ·  30초  고수의 선택", key="t30", type="secondary", use_container_width=True):
            st.session_state.tsec=30; st.session_state.tsec_chosen=True; st.rerun()
        if st.button("⚡  NORMAL  ·  40초  표준 전투", key="t40", type="secondary", use_container_width=True):
            st.session_state.tsec=40; st.session_state.tsec_chosen=True; st.rerun()
        if st.button("✅  EASY  ·  50초  여유로운 전투", key="t50", type="secondary", use_container_width=True):
            st.session_state.tsec=50; st.session_state.tsec_chosen=True; st.rerun()"""

new = """        import streamlit.components.v1 as _hc2
        _hc2.html(\"\"\"
<style>
*{margin:0;padding:0;box-sizing:border-box;}
body{background:transparent;}
@keyframes pR{0%,100%{box-shadow:0 0 20px rgba(255,34,68,0.7);}50%{box-shadow:0 0 50px rgba(255,34,68,1),0 0 80px rgba(255,0,50,0.5);}}
@keyframes pB{0%,100%{box-shadow:0 0 20px rgba(0,212,255,0.7);}50%{box-shadow:0 0 50px rgba(0,212,255,1),0 0 80px rgba(0,150,255,0.5);}}
@keyframes pG{0%,100%{box-shadow:0 0 20px rgba(0,255,136,0.7);}50%{box-shadow:0 0 50px rgba(0,255,136,1),0 0 80px rgba(0,200,100,0.5);}}
.btn{width:100%;padding:16px 12px;border-radius:12px;font-size:1.25rem;font-weight:900;color:#fff;cursor:pointer;margin-bottom:8px;letter-spacing:1px;font-family:sans-serif;border:2px solid;}
.hard{background:linear-gradient(135deg,#1a0000,#3d0000);border-color:#ff2244;animation:pR 1.8s ease-in-out infinite;}
.norm{background:linear-gradient(135deg,#00091a,#001a3d);border-color:#00d4ff;animation:pB 1.8s ease-in-out infinite;}
.easy{background:linear-gradient(135deg,#001a08,#003d15);border-color:#00ff88;animation:pG 1.8s ease-in-out infinite;}
</style>
<button class="btn hard" onclick="trigger('t30')">🔥 HARD · 30초 고수의 선택</button>
<button class="btn norm" onclick="trigger('t40')">⚡ NORMAL · 40초 표준 전투</button>
<button class="btn easy" onclick="trigger('t50')">✅ EASY · 50초 여유로운 전투</button>
<script>
function trigger(key){
    var btns=window.parent.document.querySelectorAll('button');
    btns.forEach(function(b){
        var t=(b.innerText||'').trim();
        if(key==='t30'&&t.indexOf('HARD')>=0) b.click();
        else if(key==='t40'&&t.indexOf('NORMAL')>=0) b.click();
        else if(key==='t50'&&t.indexOf('EASY')>=0) b.click();
    });
}
</script>\"\"\", height=180)
        if st.button("🔥  HARD  ·  30초  고수의 선택", key="t30", type="secondary", use_container_width=True):
            st.session_state.tsec=30; st.session_state.tsec_chosen=True; st.rerun()
        if st.button("⚡  NORMAL  ·  40초  표준 전투", key="t40", type="secondary", use_container_width=True):
            st.session_state.tsec=40; st.session_state.tsec_chosen=True; st.rerun()
        if st.button("✅  EASY  ·  50초  여유로운 전투", key="t50", type="secondary", use_container_width=True):
            st.session_state.tsec=50; st.session_state.tsec_chosen=True; st.rerun()"""

content = content.replace(old, new)
open('pages/02_P5_Arena.py', 'w', encoding='utf-8').write(content)
print('done:', '_hc2' in content)