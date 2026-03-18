import urllib.request, shutil
src='C:/Users/최정은/Desktop/snapq_toeic_V3/pages/02_P5_Arena.py'
with open(src,'r',encoding='utf-8') as f:
    c=f.read()

old_dots='    dot_cols = st.columns(num_qs)\r\n    for i in range(num_qs):\r\n        with dot_cols[i]:\r\n            oi = rrs[i]\r\n            si = "\u2705" if oi else "\u274c"\r\n            bt = "primary" if i == bi else "secondary"\r\n            if st.button(f"{i+1}", key=f"brd_{i}", type=bt, use_container_width=True):\r\n                st.session_state.br_idx = i; st.rerun()'
new_dots="    dot_html = '<div style=\"display:flex;gap:6px;margin:6px 0;\">'\r\n    for _di in range(num_qs):\r\n        _border = '2px solid #00d4ff' if _di == bi else '1px solid #444'\r\n        dot_html += f'<a href=\"?br_q={_di}\" style=\"flex:1;display:flex;align-items:center;justify-content:center;height:36px;background:#0d0d0d;border:{_border};border-radius:8px;color:#fff;text-decoration:none;font-size:0.75rem;font-weight:300;\">{_di+1}</a>'\r\n    dot_html += '</div>'\r\n    st.markdown(dot_html, unsafe_allow_html=True)"
print('dots found:',old_dots in c)
c=c.replace(old_dots,new_dots)

import re
old_nav=re.search(r'    st\.markdown\("---"\)\r\n    if was_victory:.*?st\.switch_page\("main_hub\.py"\)\r?\n',c,re.DOTALL)
if old_nav:
    new_nav='    st.markdown("---")\r\n    nav_html = \'<div style="display:flex;gap:8px;margin:6px 0;"><a href="?br_nav=lobby" style="flex:1;display:flex;align-items:center;justify-content:center;height:40px;background:#0d0d0d;border:1px solid rgba(0,212,255,0.5);border-radius:8px;color:#fff;text-decoration:none;font-size:0.75rem;font-weight:300;">\ub85c\ube44</a><a href="?br_nav=main" style="flex:1;display:flex;align-items:center;justify-content:center;height:40px;background:#0d0d0d;border:1px solid rgba(0,212,255,0.5);border-radius:8px;color:#fff;text-decoration:none;font-size:0.75rem;font-weight:300;">\uba54\uc778</a></div>\'\r\n    st.markdown(nav_html, unsafe_allow_html=True)\r\n'
    c=c[:old_nav.start()]+new_nav+c[old_nav.end():]
    print('nav replaced!')
else:
    print('nav not found')

with open(src,'w',encoding='utf-8') as f:
    f.write(c)
print('done!')
