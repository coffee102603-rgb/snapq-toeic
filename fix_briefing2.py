f='C:/Users/최정은/Desktop/snapq_toeic_V3/pages/02_P5_Arena.py'
c=open(f,'r',encoding='utf-8').read()

# 1. 화살표 nav 제거
old_nav="""    nc1, nc2, nc3 = st.columns([0.7, 8, 0.7])
    with nc1:
        if st.button("\u25c0", key="br_p", disabled=bi<=0, use_container_width=True):
            st.session_state.br_idx = bi - 1; st.rerun()
    with nc2:
        dots = ""
        for i in range(num_qs):
            dcls = "br-dot-ok" if rrs[i] else "br-dot-no"
            if i == bi: dcls += " br-dot-cur"
            dots += '<div class="br-dot '+dcls+'"></div>'
        st.markdown('<div class="br-nav">'+dots+'</div>', unsafe_allow_html=True)
    with nc3:
        if st.button("\u25b6", key="br_n", disabled=bi>=num_qs-1, use_container_width=True):
            st.session_state.br_idx = bi + 1; st.rerun()"""
c=c.replace(old_nav,'')

# 2. 브리핑 버튼 CSS 작게 (3번째 등장)
OLD3='font-size:2.1rem!important;font-weight:700!important;padding:1.2rem 1.4rem!important;text-align:center!important;transition:none!important;animation:p5bounce'
NEW3='font-size:1rem!important;font-weight:700!important;padding:0.4rem 0.3rem!important;text-align:center!important;transition:none!important;animation:p5bounce'
idx=c.find(OLD3); idx2=c.find(OLD3,idx+1); idx3=c.find(OLD3,idx2+1)
if idx3!=-1: c=c[:idx3]+c[idx3:].replace(OLD3,NEW3,1)

open(f,'w',encoding='utf-8').write(c)
print('nav removed:', 'br_p' not in c)
print('done!')
