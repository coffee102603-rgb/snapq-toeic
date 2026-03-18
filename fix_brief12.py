f='C:/Users/최정은/Desktop/snapq_toeic_V3/pages/02_P5_Arena.py'
c=open(f,'r',encoding='utf-8').read()
c=c.replace('sv_c1, sv_c2, sv_c3 = st.columns([1, 5, 1])','sv_c1, sv_c2, sv_c3 = st.columns([1, 8, 1])')
old_v="""    if was_victory:
        bc = st.columns(3)
        with bc[0]:
            nrd = st.session_state.round_num + 1
            if st.button(f"\u2694\ufe0f \ub77c\uc6b4\ub4dc {nrd}!", type="primary", use_container_width=True):
                st.session_state.round_num += 1
                for k in ["cq","qi","sc","wrong","ta","ans","sel","round_qs","round_results","br_idx"]:
                    if k in st.session_state: del st.session_state[k]
                for k,v in D.items():
                    if k not in st.session_state: st.session_state[k]=v
                qs = pick5(st.session_state.mode)
                st.session_state.round_qs = qs; st.session_state.cq = qs[0]
                st.session_state.qst = time.time(); st.session_state.phase = "battle"; st.rerun()
        with bc[1]:
            if st.button("\U0001f3e0 \ub85c\ube44", type="secondary", use_container_width=True):
                for k in ["cq","qi","sc","wrong","ta","ans","sel","round_qs","round_results","br_idx"]:
                    if k in st.session_state: del st.session_state[k]
                for k,v in D.items():
                    if k not in st.session_state: st.session_state[k]=v
                st.session_state.phase = "lobby"; st.rerun()
        with bc[2]:
            if st.button("\U0001f30d \uba54\uc778\ud5c8\ube0c", type="secondary", use_container_width=True):
                st.session_state._p5_just_left = True
                st.session_state.ans = False
                st.session_state["_battle_entry_ans_reset"] = True
                st.switch_page("main_hub.py")"""
new_v="""    if was_victory:
        bc = st.columns(2)
        with bc[0]:
            if st.button("로비", type="secondary", use_container_width=True):
                for k in ["cq","qi","sc","wrong","ta","ans","sel","round_qs","round_results","br_idx"]:
                    if k in st.session_state: del st.session_state[k]
                for k,v in D.items():
                    if k not in st.session_state: st.session_state[k]=v
                st.session_state.phase = "lobby"; st.rerun()
        with bc[1]:
            if st.button("메인", type="secondary", use_container_width=True):
                st.session_state._p5_just_left = True
                st.session_state.ans = False
                st.session_state["_battle_entry_ans_reset"] = True
                st.switch_page("main_hub.py")"""
old_l="""    else:
        bc = st.columns(3)
        with bc[0]:
            if st.button("\U0001f504 \uc7ac\ub3c4\uc804", type="primary", use_container_width=True):
                for k in ["cq","qi","sc","wrong","ta","ans","sel","round_qs","round_results","br_idx"]:
                    if k in st.session_state: del st.session_state[k]
                for k,v in D.items():
                    if k not in st.session_state: st.session_state[k]=v
                qs = pick5(st.session_state.mode)
                st.session_state.round_qs = qs; st.session_state.cq = qs[0]
                st.session_state.qst = time.time(); st.session_state.phase = "battle"; st.rerun()
        with bc[1]:
            if st.button("\U0001f3e0 \ub85c\ube44", type="secondary", use_container_width=True):
                for k in ["cq","qi","sc","wrong","ta","ans","sel","round_qs","round_results","br_idx"]:
                    if k in st.session_state: del st.session_state[k]
                for k,v in D.items():
                    if k not in st.session_state: st.session_state[k]=v
                st.session_state.phase = "lobby"; st.rerun()
        with bc[2]:
            if st.button("\U0001f30d \uba54\uc778\ud5c8\ube0c", type="secondary", use_container_width=True):
                st.session_state._p5_just_left = True
                st.session_state.ans = False
                st.session_state["_battle_entry_ans_reset"] = True
                st.switch_page("main_hub.py")"""
new_l="""    else:
        bc = st.columns(2)
        with bc[0]:
            if st.button("로비", type="secondary", use_container_width=True):
                for k in ["cq","qi","sc","wrong","ta","ans","sel","round_qs","round_results","br_idx"]:
                    if k in st.session_state: del st.session_state[k]
                for k,v in D.items():
                    if k not in st.session_state: st.session_state[k]=v
                st.session_state.phase = "lobby"; st.rerun()
        with bc[1]:
            if st.button("메인", type="secondary", use_container_width=True):
                st.session_state._p5_just_left = True
                st.session_state.ans = False
                st.session_state["_battle_entry_ans_reset"] = True
                st.switch_page("main_hub.py")"""
if old_v in c: c=c.replace(old_v,new_v); print('victory ok!')
else: print('victory not found')
if old_l in c: c=c.replace(old_l,new_l); print('lost ok!')
else: print('lost not found')
open(f,'w',encoding='utf-8').write(c)
print('done!')
