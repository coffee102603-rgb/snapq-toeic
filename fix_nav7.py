content = open('pages/02_P5_Arena.py', 'r', encoding='utf-8').read()

# 로비 CSS 블록에 nav 스타일 직접 추가
old = '</style>""", unsafe_allow_html=True)\n    _tsec_chosen = st.session_state.get'

new = '''[data-testid="stHorizontalBlock"]:last-of-type button{font-size:0.8rem!important;padding:4px!important;min-height:0!important;height:36px!important;border:1px solid rgba(255,255,255,0.15)!important;background:transparent!important;box-shadow:none!important;animation:none!important;}
[data-testid="stHorizontalBlock"]:last-of-type button p{font-size:0.8rem!important;color:#555!important;font-weight:400!important;}
</style>""", unsafe_allow_html=True)
    _tsec_chosen = st.session_state.get'''

content = content.replace(old, new, 1)
open('pages/02_P5_Arena.py', 'w', encoding='utf-8').write(content)

# 확인
c = open('pages/02_P5_Arena.py','r',encoding='utf-8').read()
print('css added:', 'last-of-type' in c)