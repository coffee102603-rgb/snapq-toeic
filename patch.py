# -*- coding: utf-8 -*-
import os
f = os.path.join(os.path.expanduser('~'), 'Desktop', 'snapq_toeic_V3', 'pages', '04_P7_Reading.py')
c = open(f, encoding='utf-8').read()
c = c.replace('padding:8px 6px!important;color:#e0e0e0!important;min-height:48px!important;', 'padding:5px 6px!important;color:#e0e0e0!important;min-height:40px!important;')
c = c.replace('.p7stage{animation:p7stageIn 0.5s ease;border-radius:14px;padding:10px 12px;margin:5px 0;}', '.p7stage{animation:p7stageIn 0.5s ease;border-radius:12px;padding:6px 10px;margin:3px 0;}')
c = c.replace('.p7confirmed{text-align:center;padding:4px;margin-bottom:5px;}', '.p7confirmed{text-align:center;padding:2px;margin-bottom:3px;}')
open(f, 'w', encoding='utf-8').write(c)
print('패치 완료!')
