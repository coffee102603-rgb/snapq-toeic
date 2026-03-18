f='C:/Users/최정은/Desktop/snapq_toeic_V3/pages/02_P5_Arena.py'
c=open(f,'r',encoding='utf-8').read()

# 1. 카드 글자 10% 축소
c=c.replace('font-size:1.2rem!important;color:#ccc!important;font-weight:800!important;}','font-size:1.08rem!important;color:#ccc!important;font-weight:800!important;}')
c=c.replace('p::first-line{font-size:1.52rem!important;font-weight:900!important;color:#fff!important;}','p::first-line{font-size:1.37rem!important;font-weight:900!important;color:#fff!important;}')

# 2. 타이머 불꽃 효과
c=c.replace('.safe{color:#44ff88;text-shadow:0 0 20px #44ff88;}','.safe{color:#44ff88;text-shadow:0 0 20px #44ff88;}')
c=c.replace('.warn{color:#ffcc00;text-shadow:0 0 25px #ffcc00;}','.warn{color:#ffcc00;text-shadow:0 0 25px #ffcc00,0 0 50px #ff8800;}')
c=c.replace('.danger{color:#ff4444;text-shadow:0 0 35px #ff4444;}','.danger{color:#ff4444;text-shadow:0 0 35px #ff4444,0 0 70px #ff0000;}')
c=c.replace('.critical{color:#ff0000;text-shadow:0 0 50px #ff0000;font-size:6rem!important;}','.critical{color:#ff0000;text-shadow:0 0 50px #ff0000,0 0 100px #ff4400;font-size:6rem!important;animation:shake 0.15s infinite!important;}')
c=c.replace('@keyframes bp{0%,100%{opacity:1}50%{opacity:0.4}}','@keyframes bp{0%,100%{opacity:1}50%{opacity:0.4}}@keyframes shake{0%{transform:translate(0,0)}20%{transform:translate(-3px,2px)}40%{transform:translate(3px,-2px)}60%{transform:translate(-2px,3px)}80%{transform:translate(2px,-3px)}100%{transform:translate(0,0)}}')

open(f,'w',encoding='utf-8').write(c)
print('done!')
