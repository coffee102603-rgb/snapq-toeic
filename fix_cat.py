content = open('pages/02_P5_Arena.py', 'r', encoding='utf-8').read()

# 카테고리 버튼 padding 줄이기
content = content.replace(
    'button[kind="primary"],button[kind="secondary"]{background:#0d0d0d!important;color:#fff!important;border:1.5px solid rgba(0,212,255,0.5)!important;border-radius:8px!important;font-family:\'Rajdhani\',sans-serif!important;font-size:1.45rem!important;font-weight:700!important;padding:0.55rem 0.6rem!important;box-shadow:0 0 12px rgba(0,212,255,0.15)!important;text-align:center!important;transition:all 0.15s!important;}',
    'button[kind="primary"],button[kind="secondary"]{background:#0d0d0d!important;color:#fff!important;border:1.5px solid rgba(0,212,255,0.5)!important;border-radius:8px!important;font-family:\'Rajdhani\',sans-serif!important;font-size:1.2rem!important;font-weight:700!important;padding:0.35rem 0.4rem!important;box-shadow:0 0 12px rgba(0,212,255,0.15)!important;text-align:center!important;transition:all 0.15s!important;}'
)
content = content.replace(
    'button[kind="primary"] p,button[kind="primary"] span,button[kind="secondary"] p,button[kind="secondary"] span{font-family:\'Rajdhani\',sans-serif!important;font-size:1.45rem!important;font-weight:700!important;text-align:center!important;}',
    'button[kind="primary"] p,button[kind="primary"] span,button[kind="secondary"] p,button[kind="secondary"] span{font-family:\'Rajdhani\',sans-serif!important;font-size:1.2rem!important;font-weight:700!important;text-align:center!important;}'
)

open('pages/02_P5_Arena.py', 'w', encoding='utf-8').write(content)
print('done')