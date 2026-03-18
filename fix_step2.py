f='C:/Users/최정은/Desktop/snapq_toeic_V3/pages/02_P5_Arena.py'
with open(f,'r',encoding='utf-8') as fp:
    lines=fp.readlines()

# 552번부터 끝까지 로비/메인 버튼 찾기
end=-1
for i in range(551,620):
    if i>=len(lines): break
    if 'switch_page("main_hub.py")' in lines[i]:
        end=i+1

print(f'replacing 552~{end}')

new_nav=[
'    st.markdown("---")\n',
'    nav_html = \'<div style="display:flex;gap:8px;margin:6px 0;">\'\n',
'    nav_html += \'<a href="?br_nav=lobby" style="flex:1;display:flex;align-items:center;justify-content:center;height:40px;background:#0d0d0d;border:1px solid rgba(0,212,255,0.5);border-radius:8px;color:#fff;text-decoration:none;font-size:0.75rem;font-weight:300;">\' + "\ub85c\ube44" + \'</a>\'\n',
'    nav_html += \'<a href="?br_nav=main" style="flex:1;display:flex;align-items:center;justify-content:center;height:40px;background:#0d0d0d;border:1px solid rgba(0,212,255,0.5);border-radius:8px;color:#fff;text-decoration:none;font-size:0.75rem;font-weight:300;">\' + "\uba54\uc778" + \'</a>\'\n',
'    nav_html += "</div>"\n',
'    st.markdown(nav_html, unsafe_allow_html=True)\n',
]

lines[551:end]=new_nav

with open(f,'w',encoding='utf-8') as fp:
    fp.writelines(lines)
print('done! total lines:',len(lines))
