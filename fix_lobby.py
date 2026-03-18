content = open('pages/02_P5_Arena.py', 'r', encoding='utf-8').read()

content = content.replace('.ms-title{text-align:center;padding:14px 8px 6px 8px;animation:stageIn 0.5s ease;}', '.ms-title{text-align:center;padding:3px 8px 2px 8px;animation:stageIn 0.5s ease;}')
content = content.replace('.ms-title h1{font-size:2.2rem;font-weight:900;color:#00d4ff;letter-spacing:3px;animation:titleGlow 3s ease infinite;margin:0;}', '.ms-title h1{font-size:1.4rem;font-weight:900;color:#00d4ff;letter-spacing:2px;animation:titleGlow 3s ease infinite;margin:0;}')
content = content.replace('.ms-title p{font-size:0.9rem;color:#666;letter-spacing:2px;margin:3px 0 0 0;}', '.ms-title p{font-size:0.7rem;color:#555;letter-spacing:1px;margin:1px 0 0 0;}')
content = content.replace('.stage{animation:stageIn 0.4s ease;border-radius:16px;padding:14px 12px;margin:3px 0;}', '.stage{animation:stageIn 0.4s ease;border-radius:12px;padding:6px 10px;margin:2px 0;}')
content = content.replace('.act-label{font-size:0.75rem;font-weight:900;letter-spacing:4px;color:#00d4ff;margin-bottom:8px;text-align:center;}', '.act-label{font-size:0.65rem;font-weight:900;letter-spacing:2px;color:#00d4ff;margin-bottom:2px;text-align:center;}')
content = content.replace('.act-msg{font-size:1.2rem;font-weight:900;color:#fff;text-align:center;margin-bottom:10px;line-height:1.3;}', '.act-msg{font-size:1.0rem;font-weight:900;color:#fff;text-align:center;margin-bottom:3px;line-height:1.2;}')
content = content.replace('.confirmed{text-align:center;padding:6px;margin-bottom:8px;}', '.confirmed{text-align:center;padding:1px;margin-bottom:2px;}')
content = content.replace('.confirmed span{font-size:0.9rem;color:#ffd700;font-weight:900;background:rgba(255,215,0,0.1);padding:4px 12px;border-radius:20px;border:1px solid rgba(255,215,0,0.4);}', '.confirmed span{font-size:0.8rem;color:#ffd700;font-weight:900;background:rgba(255,215,0,0.1);padding:2px 10px;border-radius:20px;border:1px solid rgba(255,215,0,0.4);}')
content = content.replace('st.markdown(\'<div style="font-size:0.7rem;color:#333;text-align:center;letter-spacing:3px;margin-top:4px;padding-top:5px;border-top:1px solid #111;">N A V I G A T E</div>\', unsafe_allow_html=True)', 'st.markdown(\'<div style="height:2px;"></div>\', unsafe_allow_html=True)')

open('pages/02_P5_Arena.py', 'w', encoding='utf-8').write(content)
print('done')