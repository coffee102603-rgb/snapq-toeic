import urllib.request
src='/tmp/02_P5_Arena_fixed.py'
dst='C:/Users/최정은/Desktop/snapq_toeic_V3/pages/02_P5_Arena.py'
c=open(src,'r',encoding='utf-8').read()

# nav 제거
old_nav="""    nc1, nc2, nc3 = st.columns([0.7, 8, 0.7])
    with nc1:
        if st.button("\u25c0", key="br_p", disabled=bi<=0, use_container_width=True):
            st.session_state.br_idx = bi - 1; st.rerun()
    with nc2:
        dots = ""
        for i in range(num_qs):
            dcls = "br-dot-ok" if rrs[i] else "br-dot-no"
            if i == bi: dcls += " br-dot-cur"
            dots += \'<div class="br-dot \'+dcls+\'"></div>\'
        st.markdown(\'<div class="br-nav">\'+dots+\'</div>\', unsafe_allow_html=True)
    with nc3:
        if st.button("\u25b6", key="br_n", disabled=bi>=num_qs-1, use_container_width=True):
            st.session_state.br_idx = bi + 1; st.rerun()"""
c=open(dst,'r',encoding='utf-8').read()
c=c.replace(old_nav,'')

OLD3='button[kind="primary"],button[kind="secondary"]{background:#0d0d0d!important;color:#fff!important;border:1.5px solid rgba(0,212,255,0.5)!important;border-radius:8px!important;font-family:\'Rajdhani\',sans-serif!important;font-size:2.1rem!important;font-weight:700!important;padding:1.2rem 1.4rem!important;text-align:center!important;transition:none!important;animation:p5bounce 1.4s ease-in-out infinite,p5flash 3s ease-in-out infinite!important;}\nbutton[kind="primary"] p,button[kind="primary"] span,button[kind="secondary"] p,button[kind="secondary"] span{font-family:\'Rajdhani\',sans-serif!important;font-size:2.1rem!important;font-weight:700!important;text-align:center!important;}'
NEW3='button[kind="primary"],button[kind="secondary"]{background:#0d0d0d!important;color:#fff!important;border:1.5px solid rgba(0,212,255,0.5)!important;border-radius:8px!important;font-family:\'Rajdhani\',sans-serif!important;font-size:1rem!important;font-weight:700!important;padding:0.4rem 0.3rem!important;text-align:center!important;transition:none!important;animation:p5bounce 1.4s ease-in-out infinite,p5flash 3s ease-in-out infinite!important;}\nbutton[kind="primary"] p,button[kind="primary"] span,button[kind="secondary"] p,button[kind="secondary"] span{font-family:\'Rajdhani\',sans-serif!important;font-size:1rem!important;font-weight:700!important;text-align:center!important;}'
idx=c.find(OLD3); idx2=c.find(OLD3,idx+1); idx3=c.find(OLD3,idx2+1)
if idx3!=-1: c=c[:idx3]+c[idx3:].replace(OLD3,NEW3,1)
open(dst,'w',encoding='utf-8').write(c)
print('done!' if 'br_p' not in c else 'nav still there!')
