import re

path = r"""C:\Users\최정은\Desktop\snapq_toeic\app\arenas\p7_reading_arena.py"""
src = open(path, "r", encoding="utf-8").read()

if "P7_FORCE_SKIN_V2" in src:
    print("[SKIP] P7_FORCE_SKIN_V2 already present in p7_reading_arena.py")
    raise SystemExit(0)

m = re.search(r"^def\s+inject_css\s*\(\s*\)\s*:\s*\n", src, flags=re.M)
if not m:
    raise SystemExit("inject_css() not found")

# find inject_css function end
m2 = re.search(r"^\s*def\s+\w+\s*\(", src[m.end():], flags=re.M)
func_end = (m.end() + m2.start()) if m2 else len(src)
body = src[m.start():func_end]

# Insert after the FIRST st.markdown(...) call inside inject_css (CRIT always)
pos = body.find("unsafe_allow_html=True")
if pos < 0:
    insert_at = m.end()
else:
    close = body.find("\n    )", pos)
    insert_at = (close + len("\n    )")) if close >= 0 else m.end()

FORCE_BLOCK = '''
    # ---- P7 FORCE SKIN (ALWAYS) ----
    st.markdown(
        """
        <style>
        /* P7_FORCE_SKIN_V2 (ALWAYS, LAST-WINS via !important) */

        .stApp{
          background:
            radial-gradient(900px 650px at 18% 16%, rgba(34,211,238,0.22), transparent 60%),
            radial-gradient(900px 650px at 72% 14%, rgba(167,139,250,0.18), transparent 62%),
            radial-gradient(900px 900px at 50% 78%, rgba(56,189,248,0.12), transparent 70%),
            linear-gradient(180deg, #141C2B 0%, #0E1624 55%, #0B1020 100%) !important;
          color: #E5E7EB !important;
        }

        .p7-zone{
          border-radius: 18px !important;
          padding: 16px 18px !important;
          border: 1px solid rgba(34,211,238,0.26) !important;
          background: rgba(10,16,28,0.78) !important;
          box-shadow: 0 14px 34px rgba(0,0,0,0.25) !important;
          backdrop-filter: blur(8px) !important;
          margin: 10px 0 !important;
          overflow: hidden !important;
        }
        .p7-zone:before{
          content:"" !important;
          position:absolute !important;
          left:0 !important; top:0 !important; bottom:0 !important;
          width: 6px !important;
          border-radius: 18px 0 0 18px !important;
          background: rgba(34,211,238,0.92) !important;
        }
        .p7-zone .p7-zone-body{
          color:#ffffff !important;
          font-weight: 850 !important;
          line-height: 1.65 !important;
          text-shadow: 0 2px 12px rgba(0,0,0,0.55) !important;
          font-size: 18px !important;
        }

        .p7-opt-wrap{
          display:grid !important;
          gap: 14px !important;
          margin-top: 12px !important;
        }
        .p7-opt-wrap div[data-testid="stButton"] > button{
          width: 100% !important;
          min-height: 76px !important;
          padding: 18px 18px !important;
          border-radius: 18px !important;

          font-size: 18px !important;
          font-weight: 900 !important;
          line-height: 1.20 !important;

          background: rgba(255,255,255,0.96) !important;
          color: #0F172A !important;
          border: 1px solid rgba(255,255,255,0.22) !important;
          box-shadow: 0 14px 34px rgba(0,0,0,0.22) !important;

          white-space: normal !important;
          text-align: center !important;

          transition: transform .10s ease, box-shadow .10s ease, filter .10s ease !important;
        }
        .p7-opt-wrap div[data-testid="stButton"] > button:hover{
          transform: translateY(-2px) !important;
          filter: brightness(1.04) saturate(1.06) !important;
          box-shadow: 0 18px 42px rgba(0,0,0,0.28) !important;
          background: linear-gradient(135deg, rgba(34,211,238,0.95), rgba(167,139,250,0.90)) !important;
          color:#ffffff !important;
        }
        .p7-opt-wrap div[data-testid="stButton"] > button:hover *{ color:#ffffff !important; }
        .p7-opt-wrap div[data-testid="stButton"] > button:active{
          transform: translateY(1px) scale(0.995) !important;
          box-shadow: 0 10px 22px rgba(0,0,0,0.18) !important;
        }

        /* 타이머(심장 박동 + 구간별 강화) */
        .p7-time-chip{ font-weight: 1000 !important; }
        .p7-time-chip b{ font-size: 20px !important; font-weight: 1100 !important; }

        @keyframes p7AlivePulse{
          0%{transform:scale(1); filter:brightness(1.00)}
          50%{transform:scale(1.05); filter:brightness(1.16)}
          100%{transform:scale(1); filter:brightness(1.00)}
        }
        @keyframes p7Blink{
          0%{filter:brightness(1.0)}
          50%{filter:brightness(1.55)}
          100%{filter:brightness(1.0)}
        }
        @keyframes p7Jitter{
          0%{transform:translateX(0)}
          20%{transform:translateX(-2px)}
          40%{transform:translateX(2px)}
          60%{transform:translateX(-2px)}
          80%{transform:translateX(2px)}
          100%{transform:translateX(0)}
        }

        .p7-time-alive{ animation: p7AlivePulse 1.05s ease-in-out infinite !important; }
        .p7-time-warn{
          background: rgba(255,204,0,0.18) !important;
          border-color: rgba(255,204,0,0.50) !important;
          box-shadow: 0 0 0 1px rgba(255,204,0,0.18) inset, 0 0 24px rgba(255,204,0,0.12) !important;
          animation: p7AlivePulse .85s ease-in-out infinite !important;
        }
        .p7-time-danger2{
          background: rgba(255,45,45,0.22) !important;
          border-color: rgba(255,45,45,0.60) !important;
          box-shadow: 0 0 0 1px rgba(255,45,45,0.20) inset, 0 0 34px rgba(255,45,45,0.22) !important;
          animation: p7Blink .65s infinite !important;
        }
        .p7-time-final2{
          background: rgba(255,0,0,0.26) !important;
          border-color: rgba(255,0,0,0.75) !important;
          box-shadow: 0 0 0 1px rgba(255,0,0,0.22) inset, 0 0 46px rgba(255,0,0,0.30) !important;
          animation: p7Jitter .22s linear infinite, p7Blink .33s infinite !important;
        }

        @media (max-width: 640px){
          .p7-zone .p7-zone-body{ font-size: 18px !important; }
          .p7-opt-wrap div[data-testid="stButton"] > button{
            min-height: 86px !important;
            font-size: 18px !important;
            padding: 18px 14px !important;
          }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
'''

body2 = body[:insert_at] + FORCE_BLOCK + body[insert_at:]
patched = src[:m.start()] + body2 + src[func_end:]
open(path, "w", encoding="utf-8").write(patched)
print("[OK] P7_FORCE_SKIN_V2 injected into inject_css()")

