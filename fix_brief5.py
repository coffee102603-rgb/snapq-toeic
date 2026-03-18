f='C:/Users/최정은/Desktop/snapq_toeic_V3/pages/02_P5_Arena.py'
c=open(f,'r',encoding='utf-8').read()
c=c.replace('"\\U0001f4be \\uc774 \\ubb38\\uc81c \\uc800\\uc7a5"','"\\U0001f4be \\uc800\\uc7a5"')
c=c.replace('"\U0001f4be \uc774 \ubb38\uc81c \uc800\uc7a5"','"\U0001f4be \uc800\uc7a5"')
c=c.replace('"💾 이 문제 저장"','"💾 저장"')
si_ok='"\\u2705" if oi else "\\u274c"'
c=c.replace('f"{si}{i+1}"',f'f"{{i+1}}"')
open(f,'w',encoding='utf-8').write(c)
print('done!')
