"""
FILE: 02_Firepower.py  (援? 02_P5_Arena.py)
ROLE: ?붾젰????臾몃쾿쨌?댄쐶 5臾몄젣 ?쒕컮?대쾶 ?꾩옣
PHASES: LOBBY ??BATTLE ??BRIEFING ??RESULT
DATA:   storage_data.json ??rt_logs(?쇰ЦD), adp_logs(?쇰ЦA), word_prison(?ㅻ떟 ?먮룞 ?ы쉷)
LINKS:  main_hub.py (?묒쟾?щ졊遺 洹?? | 03_POW_HQ.py (?щ줈?щ졊遺)
PAPERS: ?쇰ЦD(rt_logs 諛섏쓳?띾룄), ?쇰ЦA(adp_logs ?곸쓳???쒖씠??
EXTEND: P5 ?щ줈?섏슜???먮룞????ш뎄???덉젙 (?덉쟾???듭뀡A 諛⑹떇)
EXTEND: Adaptive ?쒖씠??怨좊룄???덉젙
"""
import streamlit as st
import streamlit.components.v1 as components
from streamlit_autorefresh import st_autorefresh
import random, time, json, os, re

st.set_page_config(page_title="?붾젰????, page_icon="??, layout="wide", initial_sidebar_state="collapsed")
# ?끸쁾??iOS Safari ?몄뀡 媛????WebSocket ?딄꺼???몄뀡 ?먮룞 蹂듭썝 ?끸쁾??_qs_nick = st.query_params.get("nick", "")
_qs_ag   = st.query_params.get("ag", "")
if _qs_nick and _qs_ag == "1":
    if not st.session_state.get("access_granted"):
        st.session_state["battle_nickname"] = _qs_nick
        st.session_state["nickname"]        = _qs_nick
        st.session_state["access_granted"]  = True
        st.session_state["_code_verified"]  = True
        st.session_state["_id_verified"]    = True
    st.query_params.clear()


# ??怨듭쑀 諛섏쓳??CSS (iOS Safari ?섏젙 + PC 湲???뺣?)
import sys as _sys
_sys.path.insert(0, os.path.dirname(__file__))
from _responsive_css import inject_css as _inject_css
_inject_css()

# ?먥븧??STORAGE PATH ?먥븧??STORAGE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage_data.json")

def load_storage():
    if os.path.exists(STORAGE_FILE):
        with open(STORAGE_FILE, "r", encoding="utf-8") as f:
            d = json.load(f)
            if isinstance(d, dict):
                return d
            return {"saved_questions": d, "saved_expressions": []}
    return {"saved_questions": [], "saved_expressions": []}

def save_to_storage(items):
    data = load_storage()
    existing = data.get("saved_questions", [])
    ids = {x["id"] for x in existing if isinstance(x, dict) and "id" in x}
    for it in items:
        if it["id"] not in ids:
            existing.append(it)
            ids.add(it["id"])
    data["saved_questions"] = existing
    with open(STORAGE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ?먥븧???꾩뿭 CSS ???붾젰???꾩슜 ?곌쾶???ㅽ????먥븧??st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=Rajdhani:wght@600;700&display=swap');

/* ?? 湲곕컲 ?? */
.stApp{background:#06060e!important;color:#eeeeff!important;}
section[data-testid="stSidebar"]{display:none!important;}
header[data-testid="stHeader"]{background:transparent!important;height:0!important;min-height:0!important;overflow:hidden!important;}
.block-container{padding-top:0!important;padding-bottom:0!important;margin-top:-8px!important;}

/* ?? ??댄? ?ㅻ뜑 ?? */
.ah{text-align:center;padding:0;margin:0 0 2px 0;line-height:1;}
.ah h1{font-family:'Orbitron',monospace!important;font-size:0.85rem;font-weight:900;margin:0;
  background:linear-gradient(90deg,#00d4ff,#ffffff,#FFD600,#00d4ff);background-size:300%;
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
  animation:titleShine 2s linear infinite;letter-spacing:4px;}

/* ?? ?ㅽ봽?덉엫 ?? */
@keyframes titleShine{0%{background-position:200% center}100%{background-position:-200% center}}
@keyframes warningPulse{0%,100%{color:#ff4466;text-shadow:0 0 8px rgba(255,68,102,0.8);}50%{color:#ff8888;text-shadow:0 0 20px rgba(255,68,102,1),0 0 40px rgba(255,0,50,0.6);}}
@keyframes neonPulse{0%,100%{box-shadow:0 0 5px #00d4ff,0 0 15px rgba(0,212,255,0.4);}50%{box-shadow:0 0 15px #00d4ff,0 0 40px rgba(0,212,255,0.7),0 0 60px rgba(0,212,255,0.3);}}
@keyframes answerGlow{0%,100%{opacity:1;}50%{opacity:0.85;}}
@keyframes shake{0%{transform:translate(0,0)}20%{transform:translate(-4px,2px)}40%{transform:translate(4px,-2px)}60%{transform:translate(-3px,3px)}80%{transform:translate(3px,-3px)}100%{transform:translate(0,0)}}

/* ?? HUD 諛고?諛??? */
.bt{display:flex;align-items:center;justify-content:space-between;
  padding:0.15rem 0.8rem;border-radius:8px;margin-bottom:2px;
  background:#0a0c18;border:1px solid rgba(0,212,255,0.4);
  box-shadow:0 0 15px rgba(0,212,255,0.1);}
.bt-g,.bt-v{background:#080c14;border:1px solid rgba(0,212,255,0.5);}
.bq{font-family:'Orbitron',monospace;font-size:1.5rem;font-weight:900;}
.bq-g,.bq-v{color:#00d4ff;text-shadow:0 0 12px rgba(0,212,255,0.9);}
.bs{font-family:'Orbitron',monospace;font-size:1.0rem;font-weight:800;color:#fff;}

/* ?? ?쇱슫???꾪듃 ???꾪닾 ?꾨줈洹몃젅??pill ?? */
.rd-dots{display:flex;justify-content:center;gap:0.3rem;}
.rd-dot{width:38px;height:22px;border-radius:5px;border:1.5px solid #1e2030;
  display:flex;align-items:center;justify-content:center;
  font-size:0.62rem;font-weight:900;letter-spacing:0.5px;}
.rd-cur{border-color:#00d4ff!important;color:#00d4ff!important;
  box-shadow:0 0 10px rgba(0,212,255,0.6)!important;
  background:rgba(0,212,255,0.08)!important;animation:neonPulse 1s infinite;}
.rd-ok{background:#ff6600;border-color:#ff8800;color:#fff;}
.rd-no{background:#ff2244;border-color:#ff2244;color:#fff;}
.rd-wait{background:#0a0c18;border-color:#1e2030;color:#2a2a3a;}

/* ?? 臾몄젣 移대뱶 ?? */
.qb{border-radius:14px;padding:0.55rem 0.75rem;margin:0.05rem 0;background:#080c1a;}
.qb-g{background:#07091a!important;
  border:1.5px solid rgba(0,212,255,0.35)!important;
  border-left:4px solid rgba(0,212,255,0.75)!important;
  border-radius:14px!important;
  box-shadow:0 0 24px rgba(0,212,255,0.07);}
.qb-v{background:#07100a!important;
  border:1.5px solid rgba(0,190,100,0.35)!important;
  border-left:4px solid rgba(0,190,100,0.75)!important;
  border-radius:14px!important;
  box-shadow:0 0 24px rgba(0,190,100,0.07);}
.qc{font-family:'Orbitron',monospace;font-size:0.6rem;font-weight:700;margin-bottom:3px;
  letter-spacing:3px;}
.qc-g{color:#2288bb;}
.qc-v{color:#228855;}
.qt{font-family:'Rajdhani',sans-serif;color:#eeeeff;font-size:0.81rem;font-weight:700;line-height:1.6;word-break:keep-all;}
.qk{color:#00d4ff;font-weight:900;font-size:0.85rem;border-bottom:2px solid #00d4ff;
  text-shadow:0 0 12px rgba(0,212,255,0.9);padding:0 2px;}

/* ?? ??踰꾪듉 ??寃뚯엫 ?ㅽ????? */
div[data-testid="stButton"] button{
  background:#0a0c18!important;
  border:2px solid rgba(0,212,255,0.35)!important;
  border-radius:10px!important;
  font-family:'Rajdhani',sans-serif!important;
  font-size:1.05rem!important;font-weight:700!important;
  padding:0.55rem 0.9rem!important;
  text-align:left!important;
  min-height:52px!important;
  width:100%!important;
  transition:box-shadow 0.15s ease,border-color 0.15s ease!important;
  transform:none!important;
  color:#ddd8c8!important;
}
div[data-testid="stButton"] button p{
  font-size:1.05rem!important;font-weight:700!important;
  color:#ddd8c8!important;text-align:left!important;
}
div[data-testid="stButton"] button:hover{
  background:rgba(0,212,255,0.07)!important;
  border-color:#00d4ff!important;
  box-shadow:0 0 20px rgba(0,212,255,0.35)!important;
}
div[data-testid="stButton"] button:active{
  transform:scale(0.98)!important;
}

/* ?? 釉뚮━??移대뱶 ?? */
.wb{background:#0a0c18;border-radius:16px;padding:1.2rem 1.2rem;margin:0.4rem 0;
  border:1px solid rgba(0,212,255,0.3);}
.wb-qn-ok{color:#00d4ff;}.wb-qn-no{color:#ff2244;}
.wb-s{font-size:1.8rem;font-weight:700;color:#f0f0f0;line-height:2;margin-bottom:0.8rem;word-break:keep-all;}
.wb-h{color:#00d4ff;font-weight:900;font-size:2rem;text-decoration:underline;text-decoration-color:#00d4ff;}
.wb-hn{color:#ff2244;font-weight:900;font-size:2rem;text-decoration:underline;text-decoration-color:#ff2244;}
.wb-k{font-size:1.4rem;font-weight:600;color:#ccc;line-height:1.7;}
.wb-e{font-size:1.3rem;color:#aaa;padding:0.5rem 0.8rem;background:rgba(0,212,255,0.06);
  border-left:4px solid #00d4ff;border-radius:0 10px 10px 0;}
.zl{color:#00d4ff!important;font-family:'Orbitron',monospace!important;letter-spacing:4px!important;}
details{background:rgba(0,212,255,0.03)!important;border-radius:12px!important;}
summary{color:#aaa!important;font-weight:700!important;}

/* ?? ?ㅽ겕濡ㅻ컮 ?? */
::-webkit-scrollbar{width:4px;}
::-webkit-scrollbar-track{background:#0a0a0a;}
::-webkit-scrollbar-thumb{background:rgba(0,212,255,0.4);border-radius:2px;}

/* ?? 紐⑤컮??諛섏쓳???? */
@media(max-width:768px){
  .block-container{padding-top:0.5rem!important;padding-bottom:2rem!important;padding-left:0.6rem!important;padding-right:0.6rem!important;}
  .ah h1{font-size:1.4rem!important;letter-spacing:2px!important;}
  div[data-testid="stButton"] button{font-size:1.5rem!important;padding:0.8rem 1rem!important;min-height:64px!important;}
  div[data-testid="stButton"] button p{font-size:1.5rem!important;}
  .qt{font-size:1.49rem!important;}.qk{font-size:1.6rem!important;}
  .wb-s{font-size:1.6rem!important;}.wb-h,.wb-hn{font-size:1.75rem!important;}
  .wb-k{font-size:1.25rem!important;}.wb-e{font-size:1.15rem!important;}
  .bq{font-size:1.2rem!important;}
}
@media(max-width:480px){
  .block-container{padding-top:0.3rem!important;padding-bottom:1.5rem!important;padding-left:0.3rem!important;padding-right:0.3rem!important;}
  .ah h1{font-size:0.95rem!important;letter-spacing:1px!important;}
  div[data-testid="stButton"] button{font-size:0.98rem!important;padding:0.5rem 0.6rem!important;min-height:52px!important;border-radius:8px!important;}
  div[data-testid="stButton"] button p{font-size:0.98rem!important;}
  .qt{font-size:0.98rem!important;line-height:1.6!important;}.qk{font-size:1.06rem!important;}
  .qb{padding:0.7rem!important;border-radius:10px!important;}
  .bq{font-size:0.95rem!important;}.bs{font-size:0.82rem!important;}
  .rd-dot{width:20px!important;height:20px!important;}
}
@media(max-width:360px){
  .ah h1{font-size:0.9rem!important;}
  div[data-testid="stButton"] button{font-size:1.0rem!important;}
  div[data-testid="stButton"] button p{font-size:1.0rem!important;}
  .qt{font-size:1.02rem!important;}.qk{font-size:1.1rem!important;}
}
</style>
""", unsafe_allow_html=True)

# ?먥븧??臾몄젣 ?먥븧??GQ=[
{"id":"G1","word_count":13,"diff":"easy","text":"All employees _______ to attend the safety training session scheduled for next Monday.","ch":["(A) require","(B) are required","(C) requiring","(D) has required"],"a":1,"ex":"二쇱뼱 'All employees'??蹂듭닔+?섎룞????'are required'媛 ?뺣떟. require(?λ룞)??紐⑹쟻???꾩슂, has required????遺덉씪移?","exk":"?쎄쾶: '吏곸썝?ㅼ씠 ?붽뎄?쒕떎'?덇퉴 ?섎룞?? 蹂듭닔 二쇱뼱?덇퉴 are!","cat":"?섎룞???섏씪移?,"kr":"紐⑤뱺 吏곸썝?ㅼ? ?ㅼ쓬 ?붿슂?쇰줈 ?덉젙???덉쟾 援먯쑁 ?몄뀡??李몄꽍?섎룄濡??붽뎄?쒕떎."},
{"id":"G2","word_count":10,"diff":"easy","text":"The manager suggested that the report _______ submitted by Friday.","ch":["(A) is","(B) be","(C) was","(D) will be"],"a":1,"ex":"suggest ??that????(should)+?숈궗?먰삎. 'be submitted'媛 ?뺣떟.","exk":"?쎄쾶: suggest(?쒖븞) ?ㅼ뿉????긽 ?숈궗?먰삎! should媛 ?⑥뼱?덈떎怨??앷컖!","cat":"媛?뺣쾿/?뱀쐞","kr":"留ㅻ땲???洹?蹂닿퀬?쒓? 湲덉슂?쇨퉴吏 ?쒖텧?섏뼱???쒕떎怨??쒖븞?덈떎."},
{"id":"G3","word_count":11,"diff":"easy","text":"_______ the budget has been approved, the project can begin immediately.","ch":["(A) Now that","(B) In case","(C) So that","(D) Even if"],"a":0,"ex":"'Now that~'='~?대?濡?. ?덉궛 ?뱀씤?믫봽濡쒖젥???쒖옉 ?멸낵愿怨?","exk":"?쎄쾶: '?댁젣 ~?덉쑝?덇퉴'?쇰뒗 ?? ?먯씤?믨껐怨??곌껐!","cat":"?묒냽??,"kr":"?덉궛???뱀씤?섏뿀?쇰?濡? ?꾨줈?앺듃??利됱떆 ?쒖옉?????덈떎."},
{"id":"G4","word_count":13,"diff":"easy","text":"Neither the supervisor nor the team members _______ aware of the policy change.","ch":["(A) is","(B) was","(C) were","(D) has been"],"a":2,"ex":"Neither A nor B ??B?????쇱튂. B=team members(蹂듭닔) ??'were'","exk":"?쎄쾶: neither nor?먯꽌???ㅼそ(B)??留욎텛湲? members=蹂듭닔 ??were!","cat":"?섏씪移?,"kr":"?곸궗????먮뱾???뺤콉 蹂寃쎌쓣 ?뚯? 紐삵뻽??"},
{"id":"G5","word_count":11,"diff":"easy","text":"The equipment, along with all the spare parts, _______ shipped yesterday.","ch":["(A) were","(B) have been","(C) was","(D) are"],"a":2,"ex":"'along with'??二쇱뼱 遺덊룷?? 二쇱뼱=equipment(?⑥닔) ??'was'","exk":"?쎄쾶: along with??臾댁떆! 吏꾩쭨 二쇱뼱留?蹂닿린! equipment=?⑥닔 ??was!","cat":"?섏씪移?,"kr":"洹??λ퉬??紐⑤뱺 ?щ텇 遺?덇낵 ?④퍡 ?댁젣 諛곗넚?섏뿀??"},
{"id":"G6","word_count":13,"diff":"easy","text":"Ms. Kim is responsible for _______ that all invoices are processed on time.","ch":["(A) ensure","(B) ensuring","(C) ensured","(D) to ensure"],"a":1,"ex":"?꾩튂??for ?????숇챸??-ing). 'ensuring'???뺣떟.","exk":"?쎄쾶: for ?ㅼ쓬?먮뒗 ~ing! ?꾩튂???숇챸??怨듭떇!","cat":"?숇챸??以?숈궗","kr":"源 ?⑤뒗 紐⑤뱺 ?≪옣???쒕븣 泥섎━?섎뒗 寃껋쓣 蹂댁옣??梨낆엫???덈떎."},
{"id":"G7","word_count":10,"diff":"easy","text":"Had the shipment arrived on time, we _______ the deadline.","ch":["(A) will meet","(B) would meet","(C) would have met","(D) had met"],"a":2,"ex":"Had+S+p.p.=媛?뺣쾿 怨쇨굅?꾨즺 ?꾩튂 ??二쇱젅 would have+p.p.","exk":"?쎄쾶: Had濡??쒖옉=怨쇨굅 媛?뺣쾿! ??would have p.p.媛 吏앷퓤!","cat":"媛?뺣쾿","kr":"留뚯빟 諛곗넚???쒕븣 ?꾩갑?덈뜑?쇰㈃, ?곕━??留덇컧??留욎텧 ???덉뿀???먮뜲."},
{"id":"G8","word_count":9,"diff":"easy","text":"The number of participants _______ increased significantly this year.","ch":["(A) have","(B) has","(C) are","(D) were"],"a":1,"ex":"'The number of~'=?⑥닔 ??'has'","exk":"?쎄쾶: The number of=洹????섎굹) ???⑥닔! A number of=留롮? ??蹂듭닔! 援щ퀎!","cat":"?섏씪移?,"kr":"李멸??먯쓽 ?섍? ?ы빐 ?ш쾶 利앷??덈떎."},
{"id":"G9","word_count":12,"diff":"easy","text":"_______ reviewed the contract, the lawyer found several clauses that needed revision.","ch":["(A) Having","(B) Have","(C) Had","(D) To have"],"a":0,"ex":"遺꾩궗援щЦ ?욎꽑 ?쒖젣 ??Having+p.p.","exk":"?쎄쾶: 癒쇱? ?????섏쨷 ??????Having??'癒쇱?'瑜??쒖떆!","cat":"遺꾩궗援щЦ","kr":"怨꾩빟?쒕? 寃?좏븳 ?? 蹂?몄궗???섏젙???꾩슂???щ윭 議고빆??諛쒓껄?덈떎."},
{"id":"G10","word_count":11,"diff":"easy","text":"It is essential that every employee _______ the new security protocol.","ch":["(A) follows","(B) follow","(C) following","(D) followed"],"a":1,"ex":"It is essential that+S+(should) ?숈궗?먰삎 ??'follow'","exk":"?쎄쾶: essential(?꾩닔?? ?ㅼ뿉???숈궗?먰삎! suggest??媛숈? 洹쒖튃!","cat":"媛?뺣쾿/?뱀쐞","kr":"紐⑤뱺 吏곸썝????蹂댁븞 ?꾨줈?좎퐳???곕Ⅴ??寃껋씠 ?꾩닔?곸씠??"},
{"id":"G11","word_count":12,"diff":"easy","text":"The CEO, _______ founded the company in 2005, announced her retirement today.","ch":["(A) who","(B) whom","(C) which","(D) whose"],"a":0,"ex":"愿怨꾨?紐낆궗 二쇱뼱 ??븷 ??二쇨꺽 'who'. ?щ엺 ??which 遺덇?.","exk":"?쎄쾶: 鍮덉뭏 ?ㅼ뿉 諛붾줈 ?숈궗(founded) ??二쇨꺽 who! ?щ엺?대땲源?which ????","cat":"愿怨꾨?紐낆궗","kr":"2005?꾩뿉 ?뚯궗瑜??ㅻ┰??CEO媛 ?ㅻ뒛 ??대? 諛쒗몴?덈떎."},
{"id":"G12","word_count":12,"diff":"easy","text":"Not until the final report is submitted _______ begin the evaluation process.","ch":["(A) we can","(B) we will","(C) can we","(D) will"],"a":2,"ex":"Not until~ 臾몃몢 ??二쇱젅 ?꾩튂 ??'can we'","exk":"?쎄쾶: Not until???욎뿉 ?ㅻ㈃ ?ㅼ쭛湲? can+we ?쒖꽌!","cat":"?꾩튂","kr":"理쒖쥌 蹂닿퀬?쒓? ?쒖텧???뚭퉴吏???됯? 怨쇱젙???쒖옉?????녿떎."},
{"id":"G13","word_count":13,"diff":"easy","text":"The policies _______ by the board last week will take effect next month.","ch":["(A) approve","(B) approving","(C) approved","(D) to approve"],"a":2,"ex":"紐낆궗 ?섏떇 ?섎룞 ??怨쇨굅遺꾩궗 approved","exk":"?쎄쾶: ?뺤콉???뱀씤?섎뒗 寃껋씠???섎룞! approved!","cat":"?섎룞???섏씪移?,"kr":"吏?쒖＜ ?댁궗?뚯뿉 ?섑빐 ?뱀씤???뺤콉?ㅼ? ?ㅼ쓬 ?щ????⑤젰??諛쒗쐶??寃껋씠??"},
{"id":"G14","word_count":11,"diff":"easy","text":"A number of employees _______ volunteered to work overtime this week.","ch":["(A) has","(B) have","(C) is","(D) was"],"a":1,"ex":"A number of=留롮? ??蹂듭닔 ??have","exk":"?쎄쾶: A number of=?щ윭 紐끸넂蹂듭닔! The number of=洹??섃넂?⑥닔!","cat":"?섏씪移?,"kr":"留롮? 吏곸썝?ㅼ씠 ?대쾲 二?珥덇낵 洹쇰Т瑜??먯썝?덈떎."},
{"id":"G15","word_count":14,"diff":"easy","text":"If the company _______ more staff last year, the project would have been completed.","ch":["(A) hired","(B) had hired","(C) would hire","(D) has hired"],"a":1,"ex":"媛?뺣쾿 怨쇨굅?꾨즺 ??if??had+p.p.","exk":"?쎄쾶: 怨쇨굅 紐삵븳 ??媛????if?덉뿉 had p.p.!","cat":"媛?뺣쾿","kr":"?뚯궗媛 ?묐뀈??吏곸썝????梨꾩슜?덈뜑?쇰㈃ ?꾨줈?앺듃媛 ?꾨즺?섏뿀??寃껋씠??"},
{"id":"G16","word_count":9,"diff":"easy","text":"Only after the meeting ended _______ the final decision.","ch":["(A) they announced","(B) announced they","(C) did they announce","(D) they did announce"],"a":2,"ex":"Only after~ 臾몃몢 ?꾩튂 ??did+二쇱뼱+?숈궗?먰삎","exk":"?쎄쾶: Only濡??쒖옉?섎㈃ ?ㅼ쭛湲? did+they+announce!","cat":"?꾩튂","kr":"?뚯쓽媛 ?앸궃 ?꾩뿉??洹몃뱾? 理쒖쥌 寃곗젙??諛쒗몴?덈떎."},
{"id":"G17","word_count":12,"diff":"easy","text":"The contractor, _______ proposal was accepted last week, will start work Monday.","ch":["(A) who","(B) whom","(C) whose","(D) which"],"a":2,"ex":"鍮덉뭏 ??紐낆궗(proposal) ???뚯쑀寃?愿怨꾨?紐낆궗 whose","exk":"?쎄쾶: 鍮덉뭏 ?ㅼ뿉 紐낆궗 諛붾줈 ?ㅻ㈃ whose!","cat":"愿怨꾨?紐낆궗","kr":"吏?쒖＜ ?쒖븞?쒓? 梨꾪깮??怨꾩빟?낆껜媛 ?붿슂?쇱뿉 ?묒뾽???쒖옉??寃껋씠??"},
{"id":"G18","word_count":12,"diff":"easy","text":"_______ the construction noise, the staff managed to concentrate on their work.","ch":["(A) Despite","(B) Although","(C) However","(D) Because of"],"a":0,"ex":"鍮덉뭏 ??紐낆궗援????꾩튂??Despite","exk":"?쎄쾶: Despite ??紐낆궗! Although ??二쇱뼱+?숈궗!","cat":"?묒냽??,"kr":"怨듭궗 ?뚯쓬?먮룄 遺덇뎄?섍퀬 吏곸썝?ㅼ? ?낅Т??吏묒쨷?????덉뿀??"},
{"id":"G19","word_count":14,"diff":"easy","text":"The report _______ by the committee before the deadline was praised by the board.","ch":["(A) submit","(B) submitting","(C) submitted","(D) to submit"],"a":2,"ex":"紐낆궗 ?섏떇 ?섎룞 ??怨쇨굅遺꾩궗 submitted","exk":"?쎄쾶: 蹂닿퀬?쒓? ?쒖텧??寃????섎룞! submitted!","cat":"?섎룞???섏씪移?,"kr":"留덇컧 ?꾩뿉 ?꾩썝?뚯뿉 ?섑빐 ?쒖텧??蹂닿퀬?쒕뒗 ?댁궗?뚯쓽 移?갔??諛쏆븯??"},
{"id":"G20","word_count":12,"diff":"easy","text":"Not only _______ the project on time, but they also exceeded expectations.","ch":["(A) they completed","(B) did they complete","(C) they did complete","(D) completed they"],"a":1,"ex":"Not only~ 臾몃몢 ?꾩튂 ??did+二쇱뼱+?숈궗?먰삎","exk":"?쎄쾶: Not only媛 ?욎뿉 ?ㅻ㈃ ?ㅼ쭛湲? did+they+complete!","cat":"?꾩튂","kr":"洹몃뱾? ?꾨줈?앺듃瑜??쒕븣 ?꾨즺?덉쓣 肉먮쭔 ?꾨땲??湲곕?瑜?珥덇낵?덈떎."},
{"id":"G21","word_count":10,"diff":"easy","text":"The employee _______ performance has improved significantly received a bonus.","ch":["(A) who","(B) whom","(C) whose","(D) which"],"a":2,"ex":"鍮덉뭏 ??紐낆궗(performance) ???뚯쑀寃?whose","exk":"?쎄쾶: ?ㅼ뿉 紐낆궗 諛붾줈 ?ㅻ㈃ whose!","cat":"愿怨꾨?紐낆궗","kr":"?깃낵媛 ?ш쾶 ?μ긽??吏곸썝? 蹂대꼫?ㅻ? 諛쏆븯??"},
{"id":"G22","word_count":11,"diff":"easy","text":"_______ she had more experience, she might have gotten the promotion.","ch":["(A) If","(B) Unless","(C) Had","(D) Since"],"a":2,"ex":"Had+S ??媛?뺣쾿 怨쇨굅?꾨즺 ?꾩튂","exk":"?쎄쾶: Had濡??쒖옉=怨쇨굅 媛?뺣쾿 ?꾩튂!","cat":"媛?뺣쾿","kr":"洹몃?媛 ??留롮? 寃쏀뿕???덉뿀?ㅻ㈃ ?뱀쭊?덉쓣 寃껋씠??"},
{"id":"G23","word_count":10,"diff":"easy","text":"The team is proud of _______ the project under budget.","ch":["(A) complete","(B) completed","(C) having completed","(D) to complete"],"a":2,"ex":"?꾩튂??of ??+ ?꾨즺 ??having+p.p.","exk":"?쎄쾶: of ???숇챸?? ?대? ?꾨즺????having completed!","cat":"?숇챸??以?숈궗","kr":"?? ?덉궛 ?댁뿉???꾨줈?앺듃瑜??꾨즺??寃껋쓣 ?먮옉?ㅻ윭?뚰븳??"},
{"id":"G24","word_count":12,"diff":"easy","text":"_______ all the data, the analyst presented her findings to the board.","ch":["(A) Having reviewed","(B) Have reviewed","(C) Reviewed","(D) To reviewing"],"a":0,"ex":"?욎꽑 ?숈옉 遺꾩궗援щЦ ??Having+p.p.","exk":"?쎄쾶: 癒쇱? ?????섏쨷 ??????Having p.p.媛 癒쇱?!","cat":"遺꾩궗援щЦ","kr":"紐⑤뱺 ?곗씠?곕? 寃?좏븳 ??遺꾩꽍媛???댁궗?뚯뿉 寃곌낵瑜?諛쒗몴?덈떎."},
]

# ?먥븧??GRAMMAR BATCH JSON ?먮룞 濡쒕뱶 ?먥븧??import glob as _glob

def _load_grammar_batches():
    """data/ ?대뜑??firepower_grammar_batch*.json ?꾨? ?쎌뼱??GQ ?щ㎎?쇰줈 蹂??""
    DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    batch_files = sorted(_glob.glob(os.path.join(DATA_DIR, "firepower_grammar_batch*.json")))
    loaded = []
    existing_ids = {q["id"] for q in GQ}
    for fpath in batch_files:
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                items = json.load(f)
            for q in items:
                if q.get("id") in existing_ids:
                    continue  # 以묐났 諛⑹?
                # 諛곗튂 ?щ㎎ ??GQ ?щ㎎ 蹂??                converted = {
                    "id":       q.get("id", ""),
                    "word_count": q.get("word_count", 10),
                    "diff":     q.get("diff", "easy"),
                    "text":     q.get("sentence", q.get("text", "")),
                    "ch":       q.get("choices",  q.get("ch", [])),
                    "a":        q.get("answer",   q.get("a", 0)),
                    "ex":       q.get("explanation",    q.get("ex", "")),
                    "exk":      q.get("explanation_kr", q.get("exk", "")),
                    "cat":      q.get("cat", "GRAMMAR"),
                    "kr":       q.get("kr", ""),
                    "tp":       "grammar",
                }
                loaded.append(converted)
                existing_ids.add(converted["id"])
        except Exception:
            pass
    return loaded

GQ.extend(_load_grammar_batches())

# ?먥븧??FORM BATCH JSON ?먮룞 濡쒕뱶 ?먥븧??FQ = []  # Form Questions

def _load_form_batches():
    """data/ ?대뜑??firepower_form_batch*.json ?꾨? ?쎌뼱??FQ ?щ㎎?쇰줈 蹂??""
    DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    batch_files = sorted(_glob.glob(os.path.join(DATA_DIR, "firepower_form_batch*.json")))
    loaded = []
    existing_ids = set()
    for fpath in batch_files:
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                items = json.load(f)
            for q in items:
                if q.get("id") in existing_ids:
                    continue
                converted = {
                    "id":        q.get("id", ""),
                    "word_count": q.get("word_count", 10),
                    "diff":      q.get("diff", "easy"),
                    "text":      q.get("sentence", q.get("text", "")),
                    "ch":        q.get("choices",  q.get("ch", [])),
                    "a":         q.get("answer",   q.get("a", 0)),
                    "ex":        q.get("explanation",    q.get("ex", "")),
                    "exk":       q.get("explanation_kr", q.get("exk", "")),
                    "cat":       q.get("cat", "FORM"),
                    "kr":        q.get("kr", ""),
                    "tp":        "form",
                }
                loaded.append(converted)
                existing_ids.add(converted["id"])
        except Exception:
            pass
    return loaded

FQ.extend(_load_form_batches())
# ?먥븧??LINK BATCH JSON 濡쒕뵫 ?먥븧??LQ = []

def _load_link_batches():
    """data/ ?대뜑??firepower_link_batch*.json ?쎌뼱??LQ 濡?蹂??""
    DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    batch_files = sorted(_glob.glob(os.path.join(DATA_DIR, "firepower_link_batch*.json")))
    loaded = []
    seen = set()
    for fp in batch_files:
        try:
            with open(fp, "r", encoding="utf-8") as f:
                items = json.load(f)
            for q in items:
                if q.get("id") in seen:
                    continue
                converted = {
                    "id":        q.get("id", ""),
                    "word_count": q.get("word_count", 10),
                    "diff":      q.get("diff", "easy"),
                    "text":      q.get("sentence", q.get("text", "")),
                    "ch":        q.get("choices",  q.get("ch", [])),
                    "a":         q.get("answer",   q.get("a", 0)),
                    "ex":        q.get("explanation",    q.get("ex", "")),
                    "exk":       q.get("explanation_kr", q.get("exk", "")),
                    "cat":       q.get("cat", "LINK"),
                    "kr":        q.get("kr", ""),
                    "tp":        "link",
                }
                loaded.append(converted)
                seen.add(converted["id"])
        except Exception:
            pass
    return loaded

LQ.extend(_load_link_batches())


# ?먥븧??VOCAB BATCH JSON 濡쒕뵫 ?먥븧??VQ = []

def _load_vocab_batches():
    """data/ ?대뜑??firepower_vocab_batch*.json ?쎌뼱??VQ 濡?蹂??""
    DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    batch_files = sorted(_glob.glob(os.path.join(DATA_DIR, "firepower_vocab_batch*.json")))
    loaded = []
    seen = set()
    for fp in batch_files:
        try:
            with open(fp, "r", encoding="utf-8") as f:
                items = json.load(f)
            for q in items:
                if q.get("id") in seen:
                    continue
                converted = {
                    "id":        q.get("id", ""),
                    "word_count": q.get("word_count", 10),
                    "diff":      q.get("diff", "easy"),
                    "text":      q.get("sentence", q.get("text", "")),
                    "ch":        q.get("choices",  q.get("ch", [])),
                    "a":         q.get("answer",   q.get("a", 0)),
                    "ex":        q.get("explanation",    q.get("ex", "")),
                    "exk":       q.get("explanation_kr", q.get("exk", "")),
                    "cat":       q.get("cat", "VOCAB"),
                    "kr":        q.get("kr", ""),
                    "tp":        "vocab",
                }
                loaded.append(converted)
                seen.add(converted["id"])
        except Exception:
            pass
    return loaded

VQ.extend(_load_vocab_batches())

# ?먥븧???몄뀡 ?먥븧??D={"started":False,"cq":None,"qi":0,"sc":0,"wrong":0,"ta":0,"sk":0,"msk":0,
    "ans":False,"sel":None,"tsec":30,"qst":None,"round_qs":[],"round_results":[],
    "round_num":1,"phase":"lobby","mode":None,"used":[],
    "adp_level":"normal",
    "adp_history":[],
}
for k,v in D.items():
    if k not in st.session_state: st.session_state[k]=v

if st.session_state.get("_p5_just_left", False):
    st.session_state._p5_just_left = False
    for k in ["cq","qi","sc","wrong","ta","ans","sel","round_qs","round_results","round_num","mode"]:
        if k in D: st.session_state[k] = D[k]
    st.session_state.phase = "lobby"
    st.session_state.sel_mode = None
    st.session_state.tsec = 30
    st.session_state.tsec_chosen = False

def pool(m): return GQ if m=="grammar" else FQ if m=="form" else LQ if m=="link" else VQ if m=="vocab" else LQ+VQ
FORM_CATS=["紐낆궗??,"?뺤슜?ы삎","遺?ы삎","?숈궗??,"遺꾩궗??,"FORM"]
GRP={
    # g1 = GRAMMAR
    "g1":[
        "?섎룞??,"?섏씪移?,"?쒖젣","媛?뺣쾿","?꾩튂",
        "?섎룞???섏씪移?,"媛?뺣쾿/?뱀쐞","遺꾩궗援щЦ",
        "愿怨꾨?紐낆궗","?묒냽??,"?숇챸??以?숈궗","GRAMMAR"
    ],
    # g2 = FORM (?덉궗?꾪솚)
    "g2": FORM_CATS,
    # g3 = LINK (誘몃옒)
    "g3":["?묒냽??,"?숇챸??以?숈궗","遺꾩궗援щЦ","愿怨꾨?紐낆궗"]
}
GRP["g3"] = ["?꾩튂??,"?묒냽??,"?묒냽遺??,"LINK"]

VGRP={"v1":"easy","v2":"hard"}

def _calc_adp_level():
    """
    利됱떆 ?꾪솚 諛⑹떇: 1臾몄젣 寃곌낵濡?諛붾줈 ?쒖씠??蹂寃?    word_count 湲곗? ??easy:??5 / normal:16-19 / hard:20-23
    留욎쑝硫????④퀎 UP, ?由щ㈃ ???④퀎 DOWN
    """
    hist = st.session_state.get("adp_history", [])
    if len(hist) < 1:
        return st.session_state.get("adp_level", "normal")
    last = hist[-1]  # 媛??理쒓렐 1臾몄젣留?諛섏쁺
    cur  = st.session_state.get("adp_level", "normal")
    if last == 1:   # ?뺣떟 ?????④퀎 UP
        if cur == "easy":   return "normal"
        if cur == "normal": return "hard"
        return "hard"
    else:           # ?ㅻ떟 ?????④퀎 DOWN
        if cur == "hard":   return "normal"
        if cur == "normal": return "easy"
        return "easy"

def pick5(m, grp=None):
    # ?? FORM 紐⑤뱶(g2): FQ ? ?ъ슜 ??
    if grp == "g2":
        p = FQ if FQ else pool(m)
        adp = _calc_adp_level()
        st.session_state.adp_level = adp
        diff_p = [q for q in p if q.get("diff","easy") == adp]
        if len(diff_p) >= 5: p = diff_p
        cat_p = [q for q in p if q.get("cat","") in FORM_CATS]
        if len(cat_p) >= 5: p = cat_p
        avail = [q for q in p if q["id"] not in st.session_state.used]
        if len(avail) < 5: st.session_state.used = []; avail = p.copy()
        chosen = random.sample(avail, min(5, len(avail)))
        for q in chosen: st.session_state.used.append(q["id"]); q["tp"] = "form"
        return chosen
    p=pool(m)
    if grp and grp in GRP:
        cats=GRP[grp]
        p=[q for q in p if q.get("cat","") in cats]
        adp = _calc_adp_level()
        st.session_state.adp_level = adp
        # ?? word_count 湲곕컲 diff ?꾪꽣 (臾몄젣 異⑸텇???뚮쭔 ?곸슜) ??
        diff_p = [q for q in p if q.get("diff","easy") == adp]
        if len(diff_p) >= 5:
            p = diff_p
        # ?? 湲곗〈 cat 湲곕컲 ?곸쓳??(fallback) ??
        if adp == "hard" and len(p) >= 5:
            hard_cats = ["媛?뺣쾿","媛?뺣쾿/?뱀쐞","?꾩튂","遺꾩궗援щЦ"]
            hard_p = [q for q in p if q.get("cat","") in hard_cats]
            easy_p = [q for q in p if q.get("cat","") not in hard_cats]
            if len(hard_p) >= 3 and len(easy_p) >= 2:
                avail_h = [q for q in hard_p if q["id"] not in st.session_state.used]
                avail_e = [q for q in easy_p if q["id"] not in st.session_state.used]
                if len(avail_h) < 3: avail_h = hard_p.copy()
                if len(avail_e) < 2: avail_e = easy_p.copy()
                chosen = random.sample(avail_h, min(3,len(avail_h))) + random.sample(avail_e, min(2,len(avail_e)))
                random.shuffle(chosen)
                for q in chosen: st.session_state.used.append(q["id"]); q["tp"]="grammar"
                return chosen
        elif adp == "easy" and len(p) >= 5:
            easy_cats = ["?섏씪移?,"?섎룞???섏씪移?,"?묒냽??,"愿怨꾨?紐낆궗"]
            easy_p = [q for q in p if q.get("cat","") in easy_cats]
            hard_p = [q for q in p if q.get("cat","") not in easy_cats]
            if len(easy_p) >= 4 and len(hard_p) >= 1:
                avail_e = [q for q in easy_p if q["id"] not in st.session_state.used]
                avail_h = [q for q in hard_p if q["id"] not in st.session_state.used]
                if len(avail_e) < 4: avail_e = easy_p.copy()
                if len(avail_h) < 1: avail_h = hard_p.copy()
                chosen = random.sample(avail_e, min(4,len(avail_e))) + random.sample(avail_h, min(1,len(avail_h)))
                random.shuffle(chosen)
                for q in chosen: st.session_state.used.append(q["id"]); q["tp"]="grammar"
                return chosen
    elif grp and grp in VGRP:
        adp = _calc_adp_level()
        st.session_state.adp_level = adp
        if adp == "hard":
            diff_p = [q for q in p if q.get("diff","") == "hard"]
            if len(diff_p) >= 5: p = diff_p
        elif adp == "easy":
            diff_p = [q for q in p if q.get("diff","") == "easy"]
            if len(diff_p) >= 5: p = diff_p
        else:
            diff = VGRP[grp]
            p = [q for q in p if q.get("diff","") == diff]
        if len(p) < 5: p = pool(m)
    avail=[q for q in p if q["id"] not in st.session_state.used]
    if len(avail)<5: st.session_state.used=[]; avail=p.copy()
    chosen=random.sample(avail,min(5,len(avail)))
    for q in chosen: st.session_state.used.append(q["id"]); q["tp"]="grammar" if q["id"].startswith("G") else "vocab"
    return chosen

def fq(t): return t.replace("_______",'<span class="qk">________</span>')
def tcls(r,t):
    x=r/t if t>0 else 0
    return "safe" if x>0.6 else "warn" if x>0.35 else "danger" if x>0.15 else "critical"

# ?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧
# PHASE: BATTLE
# ?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧
if st.session_state.phase=="battle":
    if st.session_state.get("_battle_entry_ans_reset", False):
        st.session_state.ans = False
        st.session_state["_battle_entry_ans_reset"] = False
    q=st.session_state.cq
    if not q: st.session_state.phase="lobby"; st.rerun()
    ig=q.get("tp")=="grammar"; th="g" if ig else "v"; bt="primary" if ig else "secondary"
    ej="?뵶" if ig else "?뵷"; tn="臾몃쾿" if ig else "?댄쐶"

    _en_mode = "GRAMMAR" if ig else "VOCAB"
    _rn_str  = f"WAVE {st.session_state.round_num}" if st.session_state.round_num > 1 else "WAVE 1"
    st.markdown(f'<div class="ah"><h1>??{_en_mode} FIREPOWER 쨌 {_rn_str}</h1></div>', unsafe_allow_html=True)

    # ?? HUD 諛고?諛???
    qi=st.session_state.qi; results=st.session_state.round_results
    dots=""
    for i in range(5):
        if i<len(results):
            cls="rd-ok" if results[i] else "rd-no"
            sym="?? if results[i] else "??
        elif i==qi:
            cls="rd-cur"; sym=str(i+1)
        else:
            cls="rd-wait"; sym=str(i+1)
        dots+=f'<div class="rd-dot {cls}">{sym}</div>'

    st.markdown(f'''<div class="bt bt-{th}">
        <span class="bq bq-{th}">{ej} {qi+1}/5</span>
        <div class="rd-dots">{dots}</div>
        <span class="bs">??st.session_state.sc} ??st.session_state.wrong}</span>
    </div>''', unsafe_allow_html=True)

    # ?? ??대㉧ ??
    if not st.session_state.ans:
        st_autorefresh(interval=1000, limit=st.session_state.tsec+5, key="battle_timer")
        elapsed=time.time()-st.session_state.qst
        total=st.session_state.tsec; rem=max(0,total-int(elapsed))
        tcl=tcls(rem,total); pct=rem/total*100 if total>0 else 0

        components.html(f"""
        <style>
        *{{margin:0;padding:0;box-sizing:border-box;}}
        body{{background:transparent;overflow:hidden;font-family:'Arial Black',monospace;margin:0;padding:0;}}
        #w{{text-align:center;padding:0 4px;margin:0;line-height:1;}}
        #n{{font-size:2.4rem;font-weight:900;animation:pulse 1s ease-in-out infinite;letter-spacing:2px;}}
        #bw{{background:#111;border-radius:10px;height:12px;margin:3px 4px 0;overflow:hidden;border:1px solid #222;}}
        #b{{height:100%;border-radius:10px;transition:width 1s linear;}}
        .safe{{color:#ff8833;text-shadow:0 0 20px #ff8833,0 0 40px #ff6600;}}
        .warn{{color:#FFD600;text-shadow:0 0 25px #FFD600,0 0 50px #ff8800;}}
        .danger{{color:#ff4444;text-shadow:0 0 35px #ff4444,0 0 70px #ff0000;animation:shakeNum 0.3s infinite!important;}}
        .critical{{color:#ff0000;text-shadow:0 0 50px #ff0000,0 0 100px #ff0000;font-size:2.8rem!important;animation:shakeNum 0.15s infinite!important;}}
        .bs{{background:linear-gradient(90deg,#cc4400,#ff8833);box-shadow:0 0 10px #ff6600;}}
        .bw{{background:linear-gradient(90deg,#cc8800,#FFD600);box-shadow:0 0 10px #FFD600;}}
        .bd{{background:linear-gradient(90deg,#cc2200,#ff4444);box-shadow:0 0 15px #ff4444;animation:bpulse 0.5s infinite;}}
        .bc{{background:linear-gradient(90deg,#ff0000,#ff4444);box-shadow:0 0 25px #ff0000;animation:bpulse 0.2s infinite;}}
        @keyframes pulse{{0%,100%{{transform:scale(1);opacity:1}}50%{{transform:scale(1.08);opacity:0.85}}}}
        @keyframes shakeNum{{0%{{transform:translate(0,0)}}25%{{transform:translate(-4px,0)}}75%{{transform:translate(4px,0)}}100%{{transform:translate(0,0)}}}}
        @keyframes bpulse{{0%,100%{{opacity:1}}50%{{opacity:0.5}}}}
        </style>
        <div id="w">
          <div id="n" class="{tcl}">{rem}</div>
          <div id="bw"><div id="b" class="b{'s' if tcl=='safe' else 'w' if tcl=='warn' else 'd' if tcl=='danger' else 'c'}" style="width:{pct}%"></div></div>
        </div>
        <script>
        var l={rem},t={total};
        var e=document.getElementById("n"),b=document.getElementById("b");
        setInterval(function(){{
            l--;if(l<0)l=0;
            e.textContent=l;
            var r=l/t;
            var c=r>0.6?"safe":r>0.35?"warn":r>0.15?"danger":"critical";
            e.className=c;
            b.className="b"+(r>0.6?"s":r>0.35?"w":r>0.15?"d":"c");
            b.style.width=(r*100)+"%";
        }},1000);
        </script>""", height=52)

        if rem<=0:
            st.session_state.phase="lost"; st.rerun()

    # ?? 臾몄젣 移대뱶 ??
    st.markdown(f'<div class="qb qb-{th}"><div class="qc qc-{th}">{ej} {tn} 쨌 {q.get("cat","")}</div><div class="qt">{fq(q["text"])}</div></div>', unsafe_allow_html=True)

    # ?? ??踰꾪듉 4媛???A/B/C/D ?ㅼ삩 ?ㅽ?????
    if not st.session_state.ans:
        _qi = st.session_state.get('qi', 0)
        _rn = st.session_state.get('round_num', 0)

        _labels = ["A", "B", "C", "D"]
        # ??div id ?섑띁濡?踰꾪듉 ?됱긽 ?뺤떎??怨좎젙
        # ??.stMarkdown/.element-container ?щ갚 0?쇰줈 ??踰꾪듉 媛꾧꺽 諛由?諛⑹?
        _ans_cfg = [
            ("fp-ans-a", "#ff6633", "#160800", "rgba(255,102,51,0.55)"),
            ("fp-ans-b", "#00E5FF", "#001518", "rgba(0,229,255,0.55)"),
            ("fp-ans-c", "#FF2D55", "#140008", "rgba(255,45,85,0.55)"),
            ("fp-ans-d", "#44FF88", "#001408", "rgba(68,255,136,0.55)"),
        ]
        _css = """<style>
        /* ?? ?꾩옣 踰꾪듉 ?섑띁 ?щ갚 ?꾩쟾 ?쒓굅 ?? */
        .stMarkdown{margin:0!important;padding:0!important;}
        .element-container{margin:0!important;padding:0!important;}
        div[data-testid="stVerticalBlock"]{gap:3px!important;}
        /* ?? ??踰꾪듉 怨듯넻 ?? */
        div[data-testid="stButton"] button{
            min-height:50px!important;font-size:0.95rem!important;
            font-weight:800!important;border-radius:10px!important;
            text-align:left!important;padding:0.45rem 0.9rem!important;
            margin:0!important;
            -webkit-tap-highlight-color:rgba(0,0,0,0)!important;
            -webkit-touch-callout:none!important;
            outline:none!important;
        }
        div[data-testid="stButton"] button p{font-size:0.95rem!important;font-weight:800!important;}
        div[data-testid="stButton"] button:active,
        div[data-testid="stButton"] button:focus,
        div[data-testid="stButton"] button:focus-visible,
        div[data-testid="stButton"] button:disabled,
        div[data-testid="stButton"] button[disabled]{
            background-color:rgba(255,255,255,0.04)!important;
            border:1px solid rgba(255,255,255,0.2)!important;
            color:rgb(250,250,250)!important;
            -webkit-text-fill-color:rgb(250,250,250)!important;
            opacity:1!important;
            box-shadow:none!important;
            outline:none!important;
            filter:none!important;
            -webkit-filter:none!important;
        }
        """
        for _aid, _col, _bg, _sh in _ans_cfg:
            _css += (
                f'#btn-{_aid} div[data-testid="stButton"] button{{'
                f'border-left:5px solid {_col}!important;background:{_bg}!important;'
                f'border-color:{_col}!important;color:{_col}!important;}}'
                f'#btn-{_aid} div[data-testid="stButton"] button p{{color:{_col}!important;}}'
                f'#btn-{_aid} div[data-testid="stButton"] button:hover{{box-shadow:0 0 22px {_sh}!important;}}'
            )
        _css += "</style>"
        st.markdown(_css, unsafe_allow_html=True)

        _clicked = None
        for _ii, _ch in enumerate(q['ch']):
            _ch_clean = re.sub(r'^\([A-D]\)[:\s]*', '', _ch).strip()
            _display = f"??_labels[_ii]}?? {_ch_clean}"
            _aid = _ans_cfg[_ii][0]
            st.markdown(f'<div id="btn-{_aid}">', unsafe_allow_html=True)
            if st.button(_display, key=f"ans_{_rn}_{_qi}_{_ii}", use_container_width=True):
                _clicked = _ii
            st.markdown('</div>', unsafe_allow_html=True)

        if _clicked is not None:
            if time.time()-st.session_state.qst > st.session_state.tsec:
                st.session_state.phase='lost'; st.rerun()
            i = _clicked
            st.session_state.ans=True; st.session_state.sel=i
            ok=i==q['a']
            st.session_state.round_results.append(ok)
            if ok: st.session_state.sc+=1
            else: st.session_state.wrong+=1
            st.session_state.ta+=1

            # ?? ?곗씠???섏쭛 (rt_logs + zpd_logs + p5_logs) ??
            try:
                _elapsed_now = time.time() - st.session_state.qst
                _tsec_now    = st.session_state.tsec
                _sec_rem     = round(max(0.0, _tsec_now - _elapsed_now), 2)
                _rt_proxy    = round(_tsec_now - _sec_rem, 2)
                _rem_ratio   = _sec_rem / _tsec_now if _tsec_now > 0 else 0
                if ok:
                    _err_type = "correct"
                elif _rem_ratio > 0.8:
                    _err_type = "fast_wrong"
                elif _rem_ratio < 0.2:
                    _err_type = "slow_wrong"
                else:
                    _err_type = "mid_wrong"
                _uid  = st.session_state.get("nickname", "guest")
                _cat  = q.get("cat", "")
                _qid  = q.get("id", "?")
                _today = __import__("datetime").datetime.now().strftime("%Y-%m-%d")
                if "p5_session_no" not in st.session_state:
                    st.session_state.p5_session_no = 0
                _sno = st.session_state.p5_session_no
                if "p5_start_date" not in st.session_state:
                    st.session_state.p5_start_date = _today
                try:
                    _dt = __import__("datetime")
                    _days = (_dt.datetime.strptime(_today, "%Y-%m-%d") -
                             _dt.datetime.strptime(st.session_state.p5_start_date, "%Y-%m-%d")).days
                    _week = _days // 7 + 1
                except:
                    _week = 1
                _st_data = load_storage()
                _rt_log = {
                    "user_id":          _uid,
                    "session_date":     _today,
                    "session_no":       _sno,
                    "timer_setting":    _tsec_now,
                    "question_no":      st.session_state.qi + 1,
                    "question_id":      _qid,
                    "seconds_remaining": _sec_rem,
                    "rt_proxy":         _rt_proxy,
                    "correct":          ok,
                    "grammar_type":     _cat,
                    "error_timing_type": _err_type,
                    "difficulty_level": st.session_state.get("adp_level", "normal"),
                    "week":             _week,
                    "timestamp":        __import__("datetime").datetime.now().isoformat(),
                }
                if "rt_logs" not in _st_data:
                    _st_data["rt_logs"] = []
                _st_data["rt_logs"].append(_rt_log)
                if not ok:
                    _st_data.setdefault("_zpd_pending", {})
                    _st_data["_zpd_pending"][_uid] = {
                        "session_date":   _today,
                        "session_no":     _sno,
                        "arena":          "P5",
                        "timer_setting":  _tsec_now,
                        "game_over_q_no": st.session_state.qi + 1,
                        "max_q_reached":  st.session_state.qi + 1,
                        "week":           _week,
                    }
                with open(STORAGE_FILE, "w", encoding="utf-8") as _f:
                    json.dump(_st_data, _f, ensure_ascii=False, indent=2)
            except Exception as _e:
                pass

            try:
                import sys as _sys, os as _os
                _sys.path.insert(0, _os.path.dirname(_os.path.dirname(__file__)))
                from data_collector import DataCollector as _DC
                _DC(st.session_state.get('nickname','guest')).log_activity('P5', q.get('id','?'), i, ok, round(time.time()-st.session_state.qst,2))
            except: pass

            if st.session_state.wrong>=2:
                st.session_state.phase='lost'; st.rerun()
            if st.session_state.qi>=4:
                st.session_state.phase='victory' if st.session_state.sc>=4 else 'lost'
                st.rerun()
            nqi = st.session_state.qi + 1
            if nqi < len(st.session_state.round_qs):
                st.session_state.qi = nqi
                st.session_state.cq = st.session_state.round_qs[nqi]
                st.session_state.ans=False; st.session_state.sel=None
            else:
                st.session_state.phase='victory' if st.session_state.sc>=4 else 'lost'
            st.rerun()

    else:
        # ?? ?뺣떟/?ㅻ떟 ?쇰뱶諛?(???좏깮 ?? ??
        _sel = st.session_state.sel
        _correct_idx = q['a']
        _ok = (_sel == _correct_idx)
        if _ok:
            components.html("""
            <style>
            *{margin:0;padding:0;box-sizing:border-box;}
            body{background:transparent;display:flex;align-items:center;justify-content:center;height:60px;}
            @keyframes popIn{0%{transform:scale(0.5);opacity:0;}60%{transform:scale(1.15);}100%{transform:scale(1);opacity:1;}}
            .hit{font-family:'Arial Black',sans-serif;font-size:1.6rem;font-weight:900;color:#44FF88;
              text-shadow:0 0 20px #44FF88,0 0 50px #22cc66;letter-spacing:4px;
              animation:popIn 0.4s cubic-bezier(0.34,1.56,0.64,1) forwards;}
            </style>
            <div class="hit">?뮙 寃⑺뙆!</div>""", height=60)
        else:
            _ans_text = q['ch'][_correct_idx]
            components.html(f"""
            <style>
            *{{margin:0;padding:0;box-sizing:border-box;}}
            body{{background:transparent;display:flex;align-items:center;justify-content:center;height:60px;}}
            @keyframes shk{{0%{{transform:translate(0,0)}}20%{{transform:translate(-5px,0)}}40%{{transform:translate(5px,0)}}60%{{transform:translate(-4px,0)}}80%{{transform:translate(4px,0)}}100%{{transform:translate(0,0)}}}}
            .miss{{font-family:'Arial Black',sans-serif;font-size:1.4rem;font-weight:900;color:#FF2D55;
              text-shadow:0 0 20px #FF2D55,0 0 50px #cc0033;letter-spacing:3px;
              animation:shk 0.4s ease-in-out;}}
            </style>
            <div class="miss">?? ?쇨꺽! &nbsp;<span style="font-size:1rem;color:#aaa;">?뺣떟: {_ans_text}</span></div>""", height=60)

        st.markdown(f'<div style="background:#0a0c14;border-left:4px solid {"#44FF88" if _ok else "#FF2D55"};border-radius:0 10px 10px 0;padding:8px 12px;margin:4px 0;">'
                    f'<span style="font-size:0.85rem;color:{"#44FF88" if _ok else "#FF2D55"};font-weight:700;">?뮕 {q.get("exk","")}</span></div>', unsafe_allow_html=True)

        if st.button("???ㅼ쓬 臾몄젣", key="next_q", use_container_width=True):
            if st.session_state.wrong>=2:
                st.session_state.phase='lost'; st.rerun()
            if st.session_state.qi>=4:
                st.session_state.phase='victory' if st.session_state.sc>=4 else 'lost'; st.rerun()
            nqi = st.session_state.qi + 1
            if nqi < len(st.session_state.round_qs):
                st.session_state.qi = nqi
                st.session_state.cq = st.session_state.round_qs[nqi]
                st.session_state.ans=False; st.session_state.sel=None
            else:
                st.session_state.phase='victory' if st.session_state.sc>=4 else 'lost'
            st.rerun()

# ?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧
# PHASE: VICTORY
# ?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧
elif st.session_state.phase=="victory":
    # ?? adaptive difficulty 湲곕줉 ??
    try:
        _sc_adp = st.session_state.get("sc", 0)
        _rate_adp = _sc_adp / 5.0
        _hist = st.session_state.get("adp_history", [])
        _hist.append(_rate_adp)
        st.session_state.adp_history = _hist
        st.session_state.adp_level = _calc_adp_level()
    except: pass
    # ?? zpd_logs + p5_logs ??
    try:
        st.session_state.p5_session_no = st.session_state.get("p5_session_no", 0) + 1
        _st2 = load_storage()
        _uid2 = st.session_state.get("nickname", "guest")
        _today2 = __import__("datetime").datetime.now().strftime("%Y-%m-%d")
        _sno2 = st.session_state.p5_session_no
        if "p5_start_date" not in st.session_state:
            st.session_state.p5_start_date = _today2
        try:
            _dt2 = __import__("datetime")
            _days2 = (_dt2.datetime.strptime(_today2, "%Y-%m-%d") -
                      _dt2.datetime.strptime(st.session_state.p5_start_date, "%Y-%m-%d")).days
            _week2 = _days2 // 7 + 1
        except:
            _week2 = 1
        _zpd_entry = {
            "user_id":        _uid2,"session_date":   _today2,"session_no":     _sno2,
            "arena":          "P5","timer_setting":  st.session_state.tsec,
            "game_over_q_no": None,"result":         "VICTORY","max_q_reached":  5,
            "week":           _week2,"timestamp":      __import__("datetime").datetime.now().isoformat(),
        }
        if "zpd_logs" not in _st2: _st2["zpd_logs"] = []
        _st2["zpd_logs"].append(_zpd_entry)
        _p5_entry = {
            "user_id":       _uid2,"session_date":  _today2,"session_no":    _sno2,
            "timer_selected": st.session_state.tsec,"mode":          st.session_state.mode,
            "result":        "VICTORY","correct_count": st.session_state.sc,
            "wrong_count":   st.session_state.wrong,"week":          _week2,
            "timestamp":     __import__("datetime").datetime.now().isoformat(),
        }
        if "p5_logs" not in _st2: _st2["p5_logs"] = []
        if not any(p.get("session_no") == _sno2 and p.get("user_id") == _uid2 and p.get("result") == "VICTORY"
                   for p in _st2["p5_logs"]):
            _st2["p5_logs"].append(_p5_entry)
        with open(STORAGE_FILE, "w", encoding="utf-8") as _f2:
            json.dump(_st2, _f2, ensure_ascii=False, indent=2)
    except: pass

    _sc_v = st.session_state.sc
    _wr_v = st.session_state.wrong
    _rn_v = st.session_state.round_num

    _PERFECT_list = [
        ("?몣 PERFECT!", "泥쒖옱 ?깆옣!! ?좎씡 990? 洹몃깷 ?곕넃? ?뱀긽?댁옏???몣", "#FFD600"),
        ("?몣 PERFECT!", "5/5?? ?ㅽ솕??? ?섎룄 ?댁젣 ?덊븳??諛곗썙?쇨쿋???솂", "#FFD600"),
        ("?몣 PERFECT!", "?ㅻ떟???놁뼱... ?닿굅 ?뱀떆 而ㅻ떇??嫄??꾨땲吏?? ?삈", "#FFD600"),
        ("?몣 PERFECT!", "?멸컙 臾몃쾿 ?ъ쟾 ?깆옣!! ?좎씡? 洹몃깷 ?곗콉?닿쿋???슯", "#FFD600"),
        ("?몣 PERFECT!", "???ㅻ젰?대㈃ 援먯옱 ?⑤룄 ?섍쿋?붾뜲?? 吏꾩떖?쇰줈 ?룇", "#FFD600"),
        ("?몣 PERFECT!", "?... 吏꾩쭨?? ?꾨꼍??! ?좎씡 留뚯젏??洹몃깷 ?곕넃? 嫄곗?? ?뵦", "#FFD600"),
        ("?몣 PERFECT!", "5媛??꾨? 寃⑺뙆!! ??怨듬??섎윭 ??寃??꾨땲???먮옉?섎윭 ??嫄곗??? ?뮙", "#FFD600"),
        ("?몣 PERFECT!", "臾몃쾿 媛뺤궗 ?대룄 ?섎뒗 嫄??꾨땲??? ???뺣룄硫?吏꾩떖 ?럳", "#FFD600"),
        ("?몣 PERFECT!", "留뚯젏?댁옏??! ?좎씡 ?쒗뿕??媛硫??대쫫留??⑤룄 ?섍쿋?붾뜲? ?쁻", "#FFD600"),
        ("?몣 PERFECT!", "?꾨꼍 洹??먯껜!! ?ㅻ뒛 ???ㅻ젰 洹몃?濡??쒗뿕??媛硫?990???렞", "#FFD600"),
    ]
    _VICTORY_list = [
        ("?뷂툘 VICTORY!", "媛뺥빐!! ??湲곗꽭硫??좎씡 900+ 洹몃깷 媛꾨떎! ?뮞", "#ff8833"),
        ("?뷂툘 VICTORY!", "4/5!! ???섎굹 諛⑹떖??嫄곗?? ?ㅼ쓬??PERFECT 媛곸씠???뵦", "#ff8833"),
        ("?뷂툘 VICTORY!", "?꾧튉???섎굹!! 洹??섎굹留??≪쑝硫??좎씡 怨좊뱷???뺤젙?댁빞 ?렞", "#ff8833"),
        ("?뷂툘 VICTORY!", "90?먯쭨由??ㅻ젰!! 議곌툑留???媛덈㈃ 吏꾩쭨 ?쒕떎 ?뮙", "#ff8833"),
        ("?뷂툘 VICTORY!", "嫄곗쓽 ???붿뼱!! ?꾨꼍源뚯? ????嫄몄쓬?댁빞 ?삤", "#ff8833"),
    ]
    _CLEAR_list = [
        ("??CLEAR!", "?꾩뒳?꾩뒳 ?댁븘?⑥븯??.. 寃⑥슦寃⑥슦吏留?洹몃옒???댁븯?뽰븘 ?쁾", "#ff9944"),
        ("??CLEAR!", "3媛?.. ???앹〈?좎씠?? ?댁씠 醫뗭븯????", "#ff9944"),
        ("??CLEAR!", "?닿릿 ?댁븯?붾뜲, ?닿쾶 ?ㅻ젰?댁빞? ?붿쭅??留먰빐遊??삉", "#ff9944"),
        ("??CLEAR!", "?듦낵???덈뒗??.. ?좎씡? ?대젃寃????섍굅?? ?뚯?? ?삱", "#ff9944"),
        ("??CLEAR!", "3/5... 湲곗큹???먯뼱. 洹쇰뜲 ??湲곗큹留뚯씠???삊", "#ff9944"),
    ]
    if _sc_v == 5:
        _grade, _praise, _pcol = random.choice(_PERFECT_list)
    elif _sc_v == 4:
        _grade, _praise, _pcol = random.choice(_VICTORY_list)
    else:
        _grade, _praise, _pcol = random.choice(_CLEAR_list)

    _stars_html = "".join([
        f'<div style="position:absolute;left:{random.randint(2,98)}%;top:{random.randint(2,98)}%;'
        f'width:{random.randint(3,12)}px;height:{random.randint(3,12)}px;'
        f'border-radius:50%;background:{"#FFD600" if random.random()>0.4 else "#fff8cc"};'
        f'animation:twinkle {0.3+random.random()*0.8:.1f}s ease-in-out infinite {random.random():.2f}s both;"></div>'
        for _ in range(90)])
    _coins_html = "".join([
        f'<div style="position:absolute;top:-10px;left:{random.randint(2,98)}%;font-size:{1.0+random.random()*0.8:.1f}rem;'
        f'animation:coinFall {0.8+random.random()*1.2:.1f}s ease-in infinite {random.random():.2f}s;">{"?뮥" if random.random()>0.5 else "狩? if random.random()>0.5 else "?룇"}</div>'
        for _ in range(22)])
    _lightning_html = "".join([
        f'<div style="position:absolute;left:{random.randint(2,95)}%;top:{random.randint(2,90)}%;'
        f'font-size:{random.randint(18,45)}px;opacity:0.18;'
        f'animation:twinkle {0.2+random.random()*0.4:.1f}s ease-in-out infinite {random.random():.2f}s;">{"?? if random.random()>0.5 else "??}</div>'
        for _ in range(14)])

    components.html(f"""
    <style>
    *{{margin:0;padding:0;box-sizing:border-box;}}
    body{{background:linear-gradient(180deg,#060400 0%,#1a1000 50%,#060400 100%);
      overflow:hidden;height:100vh;font-family:'Arial Black',sans-serif;
      display:flex;align-items:center;justify-content:center;}}
    @keyframes vi{{0%{{transform:scale(0) rotate(-20deg);opacity:0;}}65%{{transform:scale(1.12) rotate(3deg);}}100%{{transform:scale(1) rotate(0deg);opacity:1;}}}}
    @keyframes goldGlow{{0%,100%{{text-shadow:0 0 20px #FFD600,0 0 60px #ff8800,0 0 120px #ff4400;}}50%{{text-shadow:0 0 60px #FFD600,0 0 120px #ff8800,0 0 200px #ff4400;}}}}
    @keyframes twinkle{{0%,100%{{opacity:1;transform:scale(1) rotate(0deg);}}50%{{opacity:0.1;transform:scale(0.2) rotate(180deg);}}}}
    @keyframes coinFall{{0%{{transform:translateY(-20px) rotate(0deg) scale(1);opacity:1;}}100%{{transform:translateY(160px) rotate(540deg) scale(0.4);opacity:0;}}}}
    @keyframes scoreIn{{0%{{transform:translateY(40px);opacity:0;}}100%{{transform:translateY(0);opacity:1;}}}}
    @keyframes barFill{{0%{{width:0%;}}100%{{width:{int(_sc_v/5*100)}%;}}}}
    @keyframes pulse{{0%,100%{{transform:scale(1);}}50%{{transform:scale(1.05);}}}}
    @keyframes borderPulse{{0%,100%{{box-shadow:0 0 20px rgba(255,214,0,0.4),inset 0 0 20px rgba(255,214,0,0.05);}}50%{{box-shadow:0 0 50px rgba(255,214,0,0.8),inset 0 0 40px rgba(255,214,0,0.1);}}}}
    .wrap{{text-align:center;animation:vi 0.8s cubic-bezier(0.34,1.56,0.64,1) forwards;position:relative;z-index:10;width:90%;}}
    .round-tag{{font-size:0.72rem;color:#886600;font-weight:700;letter-spacing:4px;margin-bottom:8px;}}
    .grade{{font-size:3rem;font-weight:900;color:#FFD600;
      animation:goldGlow 1.5s ease-in-out infinite, pulse 1.5s ease-in-out infinite;
      letter-spacing:3px;line-height:1.1;}}
    .scorebox{{background:rgba(255,214,0,0.08);border:2px solid rgba(255,214,0,0.5);
      border-radius:16px;padding:14px 28px;margin:12px auto;display:inline-block;
      animation:scoreIn 0.6s ease 0.3s both, borderPulse 2s ease-in-out infinite;}}
    .sc-num{{font-size:3.5rem;font-weight:900;color:#FFD600;line-height:1;
      text-shadow:0 0 30px rgba(255,214,0,0.8);}}
    .sc-label{{font-size:0.78rem;color:#aa8800;font-weight:700;letter-spacing:2px;margin-top:4px;}}
    .bar-wrap{{background:#1a1100;border-radius:20px;height:12px;margin:12px auto;width:85%;
      overflow:hidden;border:1px solid #443300;}}
    .bar-fill{{height:100%;border-radius:20px;
      background:linear-gradient(90deg,#886600,#FFD600,#fff8aa);
      box-shadow:0 0 12px #FFD600;animation:barFill 1.2s ease 0.6s both;}}
    .praise{{font-size:1.0rem;color:{_pcol};font-weight:900;margin:10px 0 4px;
      animation:scoreIn 0.5s ease 0.8s both;letter-spacing:1px;}}
    </style>
    <div style="position:absolute;width:100%;height:100%;overflow:hidden;top:0;left:0;">
      {_stars_html}{_coins_html}{_lightning_html}
    </div>
    <div class="wrap">
        <div class="round-tag">?뮙 WAVE {_rn_v} COMPLETE ?뮙</div>
        <div class="grade">{_grade}</div>
        <div class="scorebox">
            <div class="sc-num">{_sc_v}<span style="font-size:1.6rem;color:#886600;"> / 5</span></div>
            <div class="sc-label">??{_sc_v}寃⑺뙆 &nbsp;쨌&nbsp; ??{_wr_v}媛??볦묠</div>
        </div>
        <div class="bar-wrap"><div class="bar-fill"></div></div>
        <div class="praise">{_praise}</div>
    </div>
    """, height=320)

    st.markdown("""<style>
    @keyframes zapPulse{
      0%,100%{box-shadow:0 0 18px #00d4ff,0 0 40px rgba(0,212,255,0.5),inset 0 0 18px rgba(0,212,255,0.1);}
      50%{box-shadow:0 0 35px #00d4ff,0 0 80px rgba(0,212,255,0.8),inset 0 0 35px rgba(0,212,255,0.2);}
    }
    /* ??利됱떆 ?ъ텧寃????꾧린 ?뚮? 遺덇퐙, 理쒖긽??媛뺤“ */
    div[data-testid="stButton"]:nth-of-type(1) button{
      background:linear-gradient(135deg,#001a2e,#00121f)!important;
      border:2px solid #00d4ff!important;
      border-left:5px solid #00d4ff!important;
      border-radius:14px!important;
      animation:zapPulse 1.6s ease-in-out infinite!important;
      min-height:62px!important;
    }
    div[data-testid="stButton"]:nth-of-type(1) button p{
      color:#00d4ff!important;font-size:1.25rem!important;font-weight:900!important;
      text-shadow:0 0 12px rgba(0,212,255,0.9)!important;letter-spacing:1px!important;
    }
    div[data-testid="stButton"]:nth-of-type(1) button:hover{
      background:linear-gradient(135deg,#002a40,#001a2e)!important;
      box-shadow:0 0 45px rgba(0,212,255,0.9)!important;
    }
    /* ??釉뚮━??蹂닿린 ??怨⑤뱶 */
    div[data-testid="stButton"]:nth-of-type(2) button{
      background:#0c0c00!important;border:2px solid #FFD600!important;
      border-left:5px solid #FFD600!important;border-radius:12px!important;
    }
    div[data-testid="stButton"]:nth-of-type(2) button p{color:#FFD600!important;font-size:1.05rem!important;font-weight:900!important;}
    div[data-testid="stButton"]:nth-of-type(2) button:hover{box-shadow:0 0 22px rgba(255,214,0,0.6)!important;}
    /* ???????뚯깋 */
    div[data-testid="stButton"]:nth-of-type(3) button{
      background:#0a0a0a!important;border:1.5px solid rgba(255,255,255,0.2)!important;
    }
    div[data-testid="stButton"]:nth-of-type(3) button p{color:#666!important;font-size:0.95rem!important;}
    </style>""", unsafe_allow_html=True)

    # ?? ??利됱떆 ?ъ텧寃?(?꾩껜 ?? 理쒖슦?? ??
    if st.button("??利됱떆 ?ъ텧寃?", use_container_width=True, key="btn_relaunch"):
        _keep_mode = st.session_state.get("mode")
        _keep_grp  = st.session_state.get("battle_grp")
        _keep_adp  = st.session_state.get("adp_level", "normal")
        _keep_hist = st.session_state.get("adp_history", [])
        _reset_keys = ["cq","qi","sc","wrong","ta","ans","sel",
                       "round_qs","round_results","round_num","used",
                       "started","qst","sk","msk","tsec"]
        for k in _reset_keys:
            if k in D: st.session_state[k] = D[k]
        st.session_state.mode         = _keep_mode
        st.session_state.battle_grp   = _keep_grp
        st.session_state.adp_level    = _keep_adp
        st.session_state.adp_history  = _keep_hist
        st.session_state.phase = "lobby"
        st.rerun()

    # ?? ?△몾 釉뚮━??蹂닿린 / ????
    vc=st.columns(2)
    with vc[0]:
        if st.button("?뱥 釉뚮━??蹂닿린", use_container_width=True):
            st.session_state.phase="briefing"; st.rerun()
    with vc[1]:
        if st.button("?룧 ??, use_container_width=True):
            st.session_state._p5_just_left = True
            st.session_state.ans = False
            st.session_state["_battle_entry_ans_reset"] = True
            _nick = st.session_state.get("battle_nickname") or st.session_state.get("nickname", "")
            if _nick:
                st.query_params["nick"] = _nick
                st.query_params["ag"] = "1"
            st.switch_page("main_hub.py")

# ?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧
# PHASE: YOU LOST
# ?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧
elif st.session_state.phase=="lost":
    try:
        _sc_adp = st.session_state.get("sc", 0)
        _rate_adp = _sc_adp / 5.0
        _hist = st.session_state.get("adp_history", [])
        _hist.append(_rate_adp)
        st.session_state.adp_history = _hist
        st.session_state.adp_level = _calc_adp_level()
    except: pass
    try:
        st.session_state.p5_session_no = st.session_state.get("p5_session_no", 0) + 1
        _st3 = load_storage()
        _uid3 = st.session_state.get("nickname", "guest")
        _today3 = __import__("datetime").datetime.now().strftime("%Y-%m-%d")
        _sno3 = st.session_state.p5_session_no
        if "p5_start_date" not in st.session_state:
            st.session_state.p5_start_date = _today3
        try:
            _dt3 = __import__("datetime")
            _days3 = (_dt3.datetime.strptime(_today3, "%Y-%m-%d") -
                      _dt3.datetime.strptime(st.session_state.p5_start_date, "%Y-%m-%d")).days
            _week3 = _days3 // 7 + 1
        except:
            _week3 = 1
        _pending = _st3.get("_zpd_pending", {}).get(_uid3, {})
        _go_q = _pending.get("game_over_q_no", st.session_state.qi + 1)
        _zpd3 = {
            "user_id":        _uid3,"session_date":   _today3,"session_no":     _sno3,
            "arena":          "P5","timer_setting":  st.session_state.tsec,
            "game_over_q_no": _go_q,"result":         "GAME_OVER",
            "max_q_reached":  st.session_state.qi + 1,"week":           _week3,
            "timestamp":      __import__("datetime").datetime.now().isoformat(),
        }
        if "zpd_logs" not in _st3: _st3["zpd_logs"] = []
        if not any(z.get("session_no") == _sno3 and z.get("user_id") == _uid3
                   for z in _st3["zpd_logs"]):
            _st3["zpd_logs"].append(_zpd3)
        _p5e3 = {
            "user_id":        _uid3,"session_date":   _today3,"session_no":     _sno3,
            "timer_selected": st.session_state.tsec,"mode":           st.session_state.mode,
            "result":         "GAME_OVER","correct_count":  st.session_state.sc,
            "wrong_count":    st.session_state.wrong,"week":           _week3,
            "timestamp":      __import__("datetime").datetime.now().isoformat(),
        }
        if "p5_logs" not in _st3: _st3["p5_logs"] = []
        if not any(p.get("session_no") == _sno3 and p.get("user_id") == _uid3 and p.get("result") == "GAME_OVER"
                   for p in _st3["p5_logs"]):
            _st3["p5_logs"].append(_p5e3)
        with open(STORAGE_FILE, "w", encoding="utf-8") as _f3:
            json.dump(_st3, _f3, ensure_ascii=False, indent=2)
    except: pass

    _sc = st.session_state.sc
    _wrong = st.session_state.wrong
    _pct = int(_sc / 5 * 100)
    _is_timeout = (time.time()-st.session_state.qst > st.session_state.tsec)
    _reason = "?쒓컙珥덇낵 ?? if _is_timeout else f"?ㅻ떟 {_wrong}媛???"

    _ZERO_list = [
        ("0媛?? ?닿굔 ?대룄 ???곕씪以щ꽕... 洹몃깷 ?꾨㈇?댁옏????", "臾몃쾿梨???踰덉씠?쇰룄 ?대킄. ????踰덈쭔"),
        ("0?먯씠?? ?꾨㈇. 吏꾩쭨 ?꾨㈇. ??留먯씠 ?녿떎 ?샄", "?섏씪移섎룄 紐⑤Ⅴ硫댁꽌 ?좎씡 ?먯닔 諛붾씪吏 留?),
        ("?섎굹??紐?留욏삍??? 李띿뼱???섎굹??留욎븘???섎뒗???쁻", "?쒕뜡?쇰줈 李띾뒗 ?먯댂?대룄 1媛쒕뒗 留욏엺?ㅺ퀬"),
        ("?닿굔 ?ㅻ젰 臾몄젣媛 ?꾨땲??怨듬?瑜?????嫄곗빞 ?뱴", "援먯옱 ??踰덉씠?쇰룄 ?대뇬?? ?붿쭅??留먰빐遊?),
        ("0媛?寃⑺뙆... 寃⑺뙆?뱁븳 嫄?蹂몄씤?댁옏???뮙", "???뺣룄硫?吏꾩쭨 湲곗큹遺???ㅼ떆 ?쒖옉?댁빞 ??),
    ]
    _TIMEOUT_list = [
        ("?먮젮???덈Т ?먮젮!! ?좎씡? ?ㅽ뵾?쒕룄 ?ㅻ젰?댁빞 ?맊", "?쒓컙 愿由ш? ???섎㈃ ?좎씡 ?덈? 紐??щ젮"),
        ("?쒓컙??遺議깊뻽?ㅺ퀬? 洹멸쾶 ?ㅻ젰?댁빞 ??, "?좎씡? ?먮┛ ?щ엺 湲곕떎?ㅼ＜吏 ?딆븘"),
        ("30珥덈룄 紐⑥옄??? 50珥덈줈 ?대킄... 洹몃옒??鍮좊벏??寃?媛숈?留??쁻", "?앷컖???먮┛ 寃??꾨땲??媛먭컖???녿뒗 嫄곗빞"),
        ("?쒓컙珥덇낵!! ?좎씡 ?쒗뿕?μ뿉?쒕룄 ?대윺 嫄곗빞?? ?삺", "?ㅼ쟾?먯꽑 ?쒓컙??2諛?鍮좊Ⅴ寃??먭뺨吏꾨떎"),
        ("??대㉧ 蹂댁씠吏?? 洹멸쾶 ?곸씠?? 吏湲??곹븳??吏?嫄곗빞 ??, "?띾룄 ?놁씠 ?뺥솗?꾨쭔? ?좎씡???듯븯吏 ?딆븘"),
    ]
    _LOW_list = [
        (f"李띿뼱??{_sc}媛?留욎텣 嫄????뚯븘 ?쁻", "?대룄 ?ㅻ젰?대씪怨? 洹멸굔 ?좎씡???놁뼱"),
        (f"寃⑥슦 {_sc}媛?.. ?대쾿?????뺣룄硫?臾몄옣??紐??쎄쿋???삤", "?묒냽?? ?섏씪移? 湲곗큹遺???ㅼ떆 ??),
        (f"{_sc}媛?? ?대윭怨??좎씡 ?먯닔 ?щ━湲?諛붾씪??嫄곗빞?? ?셾", "湲곕?移섎? ??텛嫄곕굹 怨듬??됱쓣 ?섎젮"),
        (f"吏꾩쭨?? {_sc}媛?? ?ㅻ뒛 而⑤뵒??臾몄젣??嫄?留욎??? ?삱", "而⑤뵒???볦? ????踰덈쭔 ?덉슜?댁쨪寃?),
        (f"臾몃쾿 媛먭컖???녿뒗 寃??꾨땲???놁븷踰꾨┛ 寃?媛숈븘 ??", f"{_sc}媛쒕줈???좎씡 600?먮룄 ?섎뱾??),
    ]
    _CLOSE_list = [
        ("????臾몄젣 李⑥씠?? ?듭슱?섏??? ?삲", "洹???臾몄젣媛 ?좎씡 ?먯닔 50??李⑥씠??),
        ("2媛?紐⑥옄?쇱꽌 ?꾨㈇?대씪??.. 吏꾩쭨 ?꾧튉???삤", "?꾧튉?ㅺ퀬 ?먯닔 ?щ씪媛吏??딆븘. ?ㅼ떆 ??),
        ("???뺣룄 ?ㅻ젰?대㈃ ??議뚯뼱?? 吏묒쨷??臾몄젣???삞", "?ㅻ젰 ?덈뒗??吏硫????듭슱??嫄??뚯??"),
        ("?꾧튉??! 洹쇰뜲 ?좎씡? ?꾧퉴??嫄???遊먯쨾 ?쁻", "?ㅼ쓬????遺꾪븳 留덉쓬 洹몃?濡??쒗뿕??媛"),
        ("嫄곗쓽 ???먮뒗????臾대꼫吏?嫄곗빞!! ?삺", "2媛?李⑥씠硫??ㅻ젰? ?덉뼱. 硫섑깉??臾몄젣??),
    ]
    if _pct == 0:
        _taunt, _sub = random.choice(_ZERO_list)
    elif _is_timeout:
        _taunt, _sub = random.choice(_TIMEOUT_list)
    elif _pct <= 40:
        _taunt, _sub = random.choice(_LOW_list)
    else:
        _taunt, _sub = random.choice(_CLOSE_list)

    _embers = "".join([
        f'<div style="position:absolute;left:{random.randint(2,98)}%;bottom:{random.randint(0,40)}%;'
        f'width:{random.randint(3,14)}px;height:{random.randint(3,14)}px;border-radius:50%;'
        f'background:{"#ff4400" if random.random()>0.4 else "#ff8800" if random.random()>0.5 else "#ff0000"};'
        f'animation:rise {0.6+random.random():.1f}s ease-in infinite {random.random():.1f}s;"></div>'
        for _ in range(80)])
    _skulls = "".join([
        f'<div style="position:absolute;left:{random.randint(2,95)}%;top:{random.randint(2,85)}%;'
        f'font-size:{random.randint(10,32)}px;opacity:{random.random()*0.2:.2f};'
        f'animation:fadeFloat {0.8+random.random()*1.2:.1f}s ease-in-out infinite {random.random():.1f}s;">{"??" if random.random()>0.3 else "?좑툘"}</div>'
        for _ in range(18)])

    components.html(f"""
    <style>
    *{{margin:0;padding:0;box-sizing:border-box;}}
    body{{background:#0a0000;overflow:hidden;display:flex;align-items:center;justify-content:center;
      height:100vh;font-family:'Arial Black',sans-serif;}}
    @keyframes redPulse{{0%,100%{{background:#0a0000;}}50%{{background:#180000;}}}}
    @keyframes crashIn{{0%{{transform:scale(4) rotate(-8deg);opacity:0;}}60%{{transform:scale(0.92) rotate(2deg);}}100%{{transform:scale(1) rotate(0deg);opacity:1;}}}}
    @keyframes shakeX{{0%,100%{{transform:translateX(0);}}20%{{transform:translateX(-10px);}}40%{{transform:translateX(10px);}}60%{{transform:translateX(-7px);}}80%{{transform:translateX(7px);}}}}
    @keyframes rise{{0%{{opacity:1;transform:translateY(0) scale(1);}}100%{{opacity:0;transform:translateY(-350px) scale(0.3);}}}}
    @keyframes flicker{{0%,100%{{opacity:1;}}30%{{opacity:0.6;}}60%{{opacity:0.9;}}}}
    @keyframes fadeFloat{{0%,100%{{opacity:0;transform:translateY(0);}}50%{{opacity:0.15;transform:translateY(-20px);}}}}
    @keyframes scoreIn{{0%{{transform:translateY(30px);opacity:0;}}100%{{transform:translateY(0);opacity:1;}}}}
    body{{animation:redPulse 0.35s ease-in-out infinite;}}
    .wrap{{text-align:center;animation:crashIn 0.6s cubic-bezier(0.34,1.56,0.64,1) forwards;
      z-index:10;position:relative;padding:10px;}}
    .skull{{font-size:2.8rem;animation:shakeX 0.5s ease-in-out infinite;display:inline-block;margin-bottom:6px;}}
    .lost-txt{{font-size:2.2rem;font-weight:900;color:#ff0000;
      text-shadow:0 0 20px #ff0000,0 0 60px #cc0000;
      animation:flicker 0.25s infinite;letter-spacing:4px;}}
    .reason{{font-size:0.9rem;color:#ff6644;font-weight:700;margin:5px 0;letter-spacing:2px;
      background:rgba(255,100,0,0.1);border:1px solid rgba(255,100,0,0.3);
      border-radius:20px;display:inline-block;padding:3px 16px;}}
    .score{{font-size:2.8rem;font-weight:900;color:#ffcc00;
      text-shadow:0 0 30px #ffaa00,0 0 60px #ff8800;margin:8px 0;
      animation:scoreIn 0.5s ease 0.3s both;}}
    .taunt{{font-size:1.05rem;color:#ff8888;font-weight:900;margin:8px 0;
      animation:shakeX 4s ease-in-out infinite;}}
    .sub{{font-size:0.82rem;color:#ff6666;margin-top:4px;font-weight:700;opacity:0.9;}}
    </style>
    <div style="position:absolute;width:100%;height:100%;overflow:hidden;top:0;left:0;">
      {_embers}{_skulls}
    </div>
    <div class="wrap">
        <div class="skull">??</div>
        <div class="lost-txt">GAME OVER</div>
        <div class="reason">[ {_reason} ]</div>
        <div class="score">{_pct}??/div>
        <div class="taunt">{_taunt}</div>
        <div class="sub">{_sub}</div>
    </div>""", height=300)

    st.markdown("""<style>
    div[data-testid="stButton"]:nth-of-type(1) button{
      background:#0a0000!important;border:2px solid #FF2D55!important;
      border-left:5px solid #FF2D55!important;border-radius:12px!important;
    }
    div[data-testid="stButton"]:nth-of-type(1) button p{color:#FF2D55!important;font-size:1.1rem!important;font-weight:900!important;}
    div[data-testid="stButton"]:nth-of-type(1) button:hover{box-shadow:0 0 25px rgba(255,45,85,0.6)!important;}
    div[data-testid="stButton"]:nth-of-type(2) button{
      background:#0a0a0a!important;border:1.5px solid rgba(255,255,255,0.15)!important;
    }
    div[data-testid="stButton"]:nth-of-type(2) button p{color:#666!important;font-size:0.95rem!important;}
    </style>""", unsafe_allow_html=True)
    bc=st.columns(2)
    with bc[0]:
        if st.button("?뵦 ?ㅼ슃?? ?ㅼ떆 ?몄슫??", use_container_width=True):
            for k in ["cq","qi","sc","wrong","ta","ans","sel","round_qs","round_results","round_num"]:
                if k in D: st.session_state[k]=D[k]
            st.session_state.phase="lobby"; st.rerun()
    with bc[1]:
        if st.button("?룧 ??, use_container_width=True):
            st.session_state._p5_just_left = True
            st.session_state.ans = False
            st.session_state["_battle_entry_ans_reset"] = True
            _nick = st.session_state.get("battle_nickname") or st.session_state.get("nickname", "")
            if _nick:
                st.query_params["nick"] = _nick
                st.query_params["ag"] = "1"
            st.switch_page("main_hub.py")

# ?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧
# PHASE: BRIEFING
# ?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧
elif st.session_state.phase=="briefing":
    st.markdown("""<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&display=swap');
    section[data-testid="stSidebar"]{display:none!important;}
    header[data-testid="stHeader"]{height:0!important;visibility:hidden!important;}
    .block-container{padding-top:0.3rem!important;padding-bottom:1rem!important;margin-top:0!important;}
    .stMarkdown{margin:0!important;padding:0!important;}
    div[data-testid="stVerticalBlock"]{gap:5px!important;}
    .element-container{margin:0!important;padding:0!important;}
    div[data-testid="stHorizontalBlock"]{margin:0!important;padding:0!important;flex-wrap:nowrap!important;gap:5px!important;}
    div[data-testid="stHorizontalBlock"] div[data-testid="stColumn"]{min-width:0!important;flex:1!important;padding:0!important;}
    div[data-testid="stButton"] button{width:100%!important;min-height:44px!important;
        font-size:0.88rem!important;padding:6px 4px!important;border-radius:10px!important;}

    /* ?? ?꾪듃 pill ?ㅽ????? */
    .br-dots div[data-testid="stButton"] button{
        font-size:0.68rem!important;min-height:28px!important;max-height:28px!important;
        padding:2px!important;border-radius:5px!important;font-weight:900!important;}
    .br-dots div[data-testid="stButton"] button p{font-size:0.68rem!important;font-weight:900!important;}

    /* ?? ???踰꾪듉 ?? */
    .br-save-btn div[data-testid="stButton"] button{
        background:#0c1800!important;border:2.5px solid #44ee66!important;
        border-radius:12px!important;color:#44ee66!important;
        font-size:1.0rem!important;font-weight:900!important;min-height:52px!important;
        letter-spacing:1px!important;}
    .br-save-btn div[data-testid="stButton"] button p{color:#44ee66!important;font-size:1.0rem!important;font-weight:900!important;}
    .br-saved-btn div[data-testid="stButton"] button{
        background:#050f05!important;border:1.5px solid #226633!important;
        border-radius:12px!important;color:#336644!important;
        font-size:0.88rem!important;min-height:44px!important;}
    .br-saved-btn div[data-testid="stButton"] button p{color:#336644!important;}

    /* ?? POW HQ CTA 踰꾪듉 ?? */
    .br-pow-btn div[data-testid="stButton"] button{
        background:#0e0020!important;border:2px solid #8833ff!important;
        border-radius:12px!important;color:#ff6644!important;
        font-size:0.92rem!important;font-weight:900!important;min-height:48px!important;
        letter-spacing:0.5px!important;}
    .br-pow-btn div[data-testid="stButton"] button p{color:#aa66ff!important;font-size:0.92rem!important;font-weight:900!important;}

    /* ?? ?ъ쟾??踰꾪듉 ?? */
    .br-retry-btn div[data-testid="stButton"] button{
        background:#1a0600!important;border:2px solid #ff6600!important;
        border-radius:12px!important;color:#ff9944!important;
        font-size:0.92rem!important;font-weight:900!important;min-height:48px!important;}
    .br-retry-btn div[data-testid="stButton"] button p{color:#ff9944!important;font-size:0.92rem!important;font-weight:900!important;}

    /* ?? ??踰꾪듉 ?? */
    .br-home-btn div[data-testid="stButton"] button{
        background:#05050e!important;border:1px solid #151525!important;
        border-radius:10px!important;color:#3d5066!important;min-height:40px!important;font-size:0.82rem!important;}
    .br-home-btn div[data-testid="stButton"] button p{color:#3d5066!important;}
    </style>""", unsafe_allow_html=True)

    was_victory = st.session_state.sc >= 3
    if "br_idx" not in st.session_state: st.session_state.br_idx = 0

    # ?? ??寃뚯엫?대㈃ br_saved 珥덇린????
    rqs_temp = st.session_state.get("round_qs", [])
    _br_game_uid = rqs_temp[0].get("id","") if rqs_temp else ""
    if st.session_state.get("_br_game_uid") != _br_game_uid:
        st.session_state.br_saved = set()
        st.session_state.br_idx   = 0
        st.session_state["_br_game_uid"] = _br_game_uid
    elif "br_saved" not in st.session_state:
        st.session_state.br_saved = set()

    bi     = st.session_state.br_idx
    rqs    = st.session_state.round_qs
    rrs    = st.session_state.round_results
    saved  = st.session_state.br_saved
    num_qs = min(len(rqs), len(rrs))
    if bi >= num_qs: bi = num_qs - 1
    if bi < 0: bi = 0
    rn    = st.session_state.round_num
    sc_v  = st.session_state.sc
    wr_v  = st.session_state.wrong

    # ?? ?곷떒 諛곕꼫 (?곷Ц) ??
    if was_victory:
        st.markdown(f'''<div style="background:#150800;border:2px solid #ff6600;border-left:5px solid #ff6600;
            border-radius:10px;padding:10px 12px;margin-bottom:2px;">
            <div style="font-family:Orbitron,monospace;font-size:0.85rem;font-weight:900;
              color:#ff8833;letter-spacing:2px;">?뮙 WAVE {rn} 쨌 FIREPOWER COMPLETE</div>
            <div style="font-size:0.75rem;color:#cc6622;font-weight:700;margin-top:3px;letter-spacing:1px;">
              ??{sc_v} ELIMINATED &nbsp;쨌&nbsp; ??{wr_v} MISSED</div>
        </div>''', unsafe_allow_html=True)
    else:
        st.markdown(f'''<div style="background:#0c0008;border:2px solid #FF2D55;border-left:5px solid #FF2D55;
            border-radius:10px;padding:10px 12px;margin-bottom:2px;">
            <div style="font-family:Orbitron,monospace;font-size:0.85rem;font-weight:900;
              color:#FF2D55;letter-spacing:2px;">?? WAVE {rn} 쨌 MISSION FAILED</div>
            <div style="font-size:0.75rem;color:#ee4455;font-weight:700;margin-top:3px;letter-spacing:1px;">
              ??{sc_v} ELIMINATED &nbsp;쨌&nbsp; ??{wr_v} MISSED</div>
        </div>''', unsafe_allow_html=True)

    # ?? 臾몄젣 踰덊샇 ?꾪듃 ??pill ?ㅽ?????
    st.markdown('<div class="br-dots">', unsafe_allow_html=True)
    _ncols = st.columns(num_qs)
    for _i in range(num_qs):
        with _ncols[_i]:
            _ok_i  = rrs[_i] if _i < len(rrs) else None
            _col   = "#ff6600" if _ok_i else "#ff2244" if _ok_i is not None else "#2a2a3a"
            _bg    = "#1a0800" if _ok_i else "#1a0008" if _ok_i is not None else "#0a0c18"
            _sym   = "?? if _ok_i else "?? if _ok_i is not None else str(_i+1)
            _sel   = f"box-shadow:0 0 0 2px #aaa;outline:2px solid #aaa;" if _i==bi else ""
            st.markdown(f'''<style>
            div[data-testid="stHorizontalBlock"] div[data-testid="stColumn"]:nth-child({_i+1}) button{{
                background:{_bg}!important;border:1.5px solid {_col}!important;
                color:{_col}!important;border-radius:5px!important;{_sel}
            }}</style>''', unsafe_allow_html=True)
            if st.button(_sym, key=f"dot_{_i}", use_container_width=True):
                st.session_state.br_idx = _i; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # ?? 臾몄젣 移대뱶 ??
    q  = rqs[bi]; ok = rrs[bi]
    ans_clean = q["ch"][q["a"]].split(") ",1)[-1] if ") " in q["ch"][q["a"]] else q["ch"][q["a"]]
    if ok:
        sent_html = q["text"].replace("_______", f'<span style="color:#50c878;font-weight:900;border-bottom:2px solid #50c878;">{ans_clean}</span>')
        card_border="#00d4ff"; qnum_color="#50c878"; qnum_sym="??
    else:
        sent_html = q["text"].replace("_______",
            f'<span style="color:#ff4466;font-weight:900;text-decoration:line-through;margin-right:4px;">?</span>'
            f'<span style="color:#50c878;font-weight:900;border-bottom:2px solid #50c878;">{ans_clean}</span>')
        card_border="#FF2D55"; qnum_color="#ff4466"; qnum_sym="??
    kr=q.get("kr",""); exk=q.get("exk",""); cat=q.get("cat","")

    _is_saved = bi in saved
    _prisoner_badge = '' if ok else (
        '<span style="background:#1a0000;border:1px solid #ff4444;border-radius:6px;'
        'padding:2px 8px;font-size:0.65rem;color:#ff6644;font-weight:900;margin-left:8px;">'
        '?? ?щ줈 ?깅줉??/span>' if _is_saved else
        '<span style="background:#001a00;border:1px solid #44ee66;border-radius:6px;'
        'padding:2px 8px;font-size:0.65rem;color:#44ee66;font-weight:900;margin-left:8px;">'
        '????ν븯硫??щ줈 ?깅줉!</span>'
    )

    st.markdown(f'''<div style="background:#080c1a;border:1.5px solid {card_border};
        border-left:4px solid {card_border};border-radius:14px;padding:12px;margin:3px 0;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
            <span style="background:#0a0a20;border:1px solid #222;border-radius:8px;
              padding:3px 10px;font-size:0.82rem;font-weight:800;color:{qnum_color};">
              {qnum_sym} Q{bi+1}/{num_qs}</span>
            <span style="font-size:0.65rem;color:#444;letter-spacing:2px;">{cat}{_prisoner_badge}</span>
        </div>
        <div style="font-size:1.05rem;font-weight:700;color:#eeeeff;line-height:1.7;margin-bottom:8px;">{sent_html}</div>
        <div style="font-size:0.82rem;color:#6a7a8a;margin-bottom:7px;">?뱰 {kr}</div>
        <div style="background:#040d04;border-left:3px solid #50c878;border-radius:0 8px 8px 0;padding:7px 10px;">
            <div style="font-size:0.82rem;color:#50c878;font-weight:700;">?뮕 {exk}</div>
        </div>
    </div>''', unsafe_allow_html=True)

    # ?? ???踰꾪듉 (理쒖슦??CTA) ??
    if not _is_saved:
        st.markdown('<div class="br-save-btn">', unsafe_allow_html=True)
        if st.button("?뮶  ??? ???щ줈?щ졊遺 + ?⑥뼱?섏슜???먮룞 ?깅줉!", key=f"sv_{q['id']}_{bi}", use_container_width=True):
            item = {"id":q["id"],"text":q["text"],"ch":q["ch"],"a":q["a"],"ex":q.get("ex",""),
                    "exk":q.get("exk",""),"cat":q.get("cat",""),"kr":q.get("kr",""),"tp":q.get("tp","grammar")}
            save_to_storage([item])
            # ?? ?⑥뼱 ?⑤?由?DB ?ㅼ틪 ??word_prison ?먮룞 ?깅줉 ??
            try:
                import datetime as _fdt, sys as _sys2, os as _os2
                _sys2.path.insert(0, _os2.path.dirname(__file__))
                from _word_family_db import find_words_in_sentence as _find_words
                _fp_sent = q.get("text","").replace("_______", ans_clean)
                _fp_cat  = q.get("cat","")
                _matched = _find_words(_fp_sent, max_words=3)
                _fp_data = load_storage()
                if "word_prison" not in _fp_data: _fp_data["word_prison"] = []
                _changed = False
                for _m in _matched:
                    _w = _m["word"].strip()
                    if not _w or len(_w) < 3: continue
                    if any(p.get("word","").lower()==_w.lower() for p in _fp_data["word_prison"]): continue
                    _fp_data["word_prison"].append({
                        "word":           _w,
                        "kr":             _m["kr"],
                        "pos":            _m["pos"],
                        "family_root":    _m["family_root"],
                        "source":         "P5",
                        "sentence":       _fp_sent,
                        "captured_date":  _fdt.datetime.now().strftime("%Y-%m-%d"),
                        "correct_streak": 0,
                        "last_reviewed":  None,
                        "cat":            _fp_cat,
                    })
                    _changed = True
                if _changed:
                    import json as _jfp2
                    with open(STORAGE_FILE,"w",encoding="utf-8") as _ffp:
                        _jfp2.dump(_fp_data,_ffp,ensure_ascii=False,indent=2)
            except Exception:
                pass
            st.session_state.br_saved.add(bi)
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        # ??λ맖: ?묒? 諭껋?濡??쒖떆 (踰꾪듉 ?쒓굅)
        st.markdown(
            '<div style="text-align:center;padding:4px 0;font-size:0.78rem;color:#336644;'
            'font-weight:700;letter-spacing:1px;">??????꾨즺 쨌 ?щ줈?щ졊遺 ?湲곗쨷</div>',
            unsafe_allow_html=True)

    st.markdown('<div style="height:1px;background:#111122;margin:4px 0;"></div>', unsafe_allow_html=True)

    # ?? ?섎떒 踰꾪듉 (?щ줈?щ졊遺:??= 3:1) ??
    def _go_home():
        st.session_state._p5_just_left = True
        st.session_state.ans = False
        st.session_state["_battle_entry_ans_reset"] = True
        _nick = st.session_state.get("battle_nickname") or st.session_state.get("nickname", "")
        if _nick:
            st.query_params["nick"] = _nick
            st.query_params["ag"] = "1"
        st.switch_page("main_hub.py")

    if was_victory:
        _bc1, _bc2 = st.columns([3, 1])
        with _bc1:
            st.markdown('<div class="br-pow-btn">', unsafe_allow_html=True)
            if st.button("??  ?щ줈?щ졊遺!", use_container_width=True):
                st.switch_page("pages/03_POW_HQ.py")
            st.markdown('</div>', unsafe_allow_html=True)
        with _bc2:
            st.markdown('<div class="br-home-btn">', unsafe_allow_html=True)
            if st.button("?룧 ??, use_container_width=True):
                _go_home()
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        # 寃뚯엫?ㅻ쾭: ?ㅼ슃???ш쾶 + ?щ줈?щ졊遺쨌???묎쾶
        st.markdown('<div class="br-retry-btn">', unsafe_allow_html=True)
        if st.button("?뵦  ?ㅼ슃??", use_container_width=True):
            for k in ["cq","qi","sc","wrong","ta","ans","sel","round_qs","round_results","br_idx","br_saved"]:
                if k in st.session_state: del st.session_state[k]
            for k,v in D.items():
                if k not in st.session_state: st.session_state[k]=v
            qs = pick5(st.session_state.mode)
            st.session_state.round_qs = qs; st.session_state.cq = qs[0]
            st.session_state.qst = time.time(); st.session_state.phase = "battle"; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        _rc1, _rc2 = st.columns([3, 1])
        with _rc1:
            st.markdown('<div class="br-pow-btn">', unsafe_allow_html=True)
            if st.button("??  ?щ줈?щ졊遺!", use_container_width=True):
                st.switch_page("pages/03_POW_HQ.py")
            st.markdown('</div>', unsafe_allow_html=True)
        with _rc2:
            st.markdown('<div class="br-home-btn">', unsafe_allow_html=True)
            if st.button("?룧 ??, use_container_width=True):
                _go_home()
            st.markdown('</div>', unsafe_allow_html=True)


# PHASE: LOBBY
# ?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧
else:
    _nav = st.query_params.get('nav', '')
    if _nav == 'hub':
        st.query_params.clear()
        st.session_state._p5_just_left = True
        st.session_state.ans = False
        st.session_state["_battle_entry_ans_reset"] = True
        st.switch_page("main_hub.py")
    elif _nav == 'stg':
        st.query_params.clear()
        st.switch_page("pages/03_POW_HQ.py")
    st.session_state.phase="lobby"
    if "sel_mode" not in st.session_state: st.session_state.sel_mode=None

    tsec      = st.session_state.tsec
    sm        = st.session_state.sel_mode
    rn        = st.session_state.round_num
    _tsec_chosen = st.session_state.get('tsec_chosen', False)
    lbl_map  = {"g1":"?뷂툘 GRAMMAR","g2":"?봽 FORM","g3":"?뵕 LINK","vocab":"?뱲 VOCAB"}
    mode_map = {"g1":("grammar","g1"),"g2":("grammar","g2"),"g3":("link","g3"),"vocab":("vocab",None)}
    _cur_sm  = st.session_state.get("sel_mode","") or ""
    _cur_tc  = st.session_state.get("tsec_chosen", False)
    _cur_tsec= st.session_state.get("tsec", 30)
    _ready   = _cur_tc and _cur_sm in ["g1","g2","g3","vocab"]
    _adp     = st.session_state.get("adp_level","normal")
    _adp_lbl = {"easy":"?윟 EASY (??5?⑥뼱)","normal":"?윞 NORMAL (16-19?⑥뼱)","hard":"?뵶 HARD (20-23?⑥뼱)"}.get(_adp,"?윞 NORMAL (16-19?⑥뼱)")
    _hist_len= len(st.session_state.get("adp_history",[]))

    # ?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧
    # 濡쒕퉬 CSS + ?뚮뜑留????뷀샇?대룆 ?섏? 怨좉툒??    # ?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧
    _tlabel_map = {"30":"?뵦 BLITZ 30s","40":"??STANDARD 40s","50":"?썳 SNIPER 50s"}

    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=Rajdhani:wght@600;700&display=swap');

.stApp { background:#04040c !important; }
section[data-testid="stSidebar"] { display:none !important; }
header[data-testid="stHeader"]   { height:0 !important; overflow:hidden !important; }
.block-container { padding:14px 14px 30px !important; margin:0 !important; }
div[data-testid="stVerticalBlock"] { gap:10px !important; }
.element-container { margin:0 !important; padding:0 !important; }
div[data-testid="stHorizontalBlock"] {
  gap:5px !important; margin:0 !important; flex-wrap:nowrap !important;
}
div[data-testid="stHorizontalBlock"] div[data-testid="stColumn"] {
  padding:0 !important; min-width:0 !important; flex:1 !important;
}

@keyframes titleShine {
  0%   { background-position:200% center }
  100% { background-position:-200% center }
}
@keyframes warnBlink {
  0%,100% { opacity:1; color:#ff4466; }
  50%     { opacity:0.65; color:#ff8888; }
}
@keyframes launchGlow {
  0%,100% { box-shadow:0 0 14px rgba(255,70,0,0.7), 0 0 30px rgba(255,50,0,0.3); }
  50%     { box-shadow:0 0 55px rgba(255,210,0,1),  0 0 110px rgba(255,140,0,0.6); }
}
@keyframes selPulse {
  0%,100% { filter:brightness(1); }
  50%     { filter:brightness(1.12); }
}

/* 怨듯넻 踰꾪듉 */
div[data-testid="stButton"] button {
  background:#070b17 !important;
  border:1.5px solid rgba(0,180,255,0.18) !important;
  border-radius:10px !important;
  font-family:'Rajdhani',sans-serif !important;
  font-size:0.88rem !important; font-weight:700 !important;
  padding:8px 6px !important; color:#4a6688 !important;
  min-height:46px !important; width:100% !important;
  white-space:pre-line !important; line-height:1.3 !important;
  transition:border-color 0.12s, box-shadow 0.12s !important;
}
div[data-testid="stButton"] button p {
  font-size:0.88rem !important; font-weight:700 !important;
  color:#4a6688 !important; white-space:pre-line !important; line-height:1.3 !important;
}

/* ?쒓컙: BLITZ 30s ?ㅻ젋吏/遺덇퐙 */
div[data-testid="stButton"] button.fp-t30 {
  background:#0e0700 !important;
  border-color:rgba(200,90,20,0.3) !important; color:#886644 !important;
  min-height:56px !important; font-family:'Orbitron',monospace !important; font-size:0.78rem !important;
}
div[data-testid="stButton"] button.fp-t30 p { color:#886644 !important; }
div[data-testid="stButton"] button.fp-t30.fp-sel {
  background:#220e00 !important;
  border-color:#ff8833 !important; color:#ffaa44 !important;
  box-shadow:0 0 22px rgba(255,130,50,0.55) !important;
  animation:selPulse 1.6s ease-in-out infinite !important;
}
div[data-testid="stButton"] button.fp-t30.fp-sel p { color:#ffaa44 !important; }

/* ?쒓컙: STANDARD 40s ?뚮옉 */
div[data-testid="stButton"] button.fp-t40 {
  background:#03091a !important;
  border-color:rgba(40,110,230,0.3) !important; color:#335577 !important;
  min-height:56px !important; font-family:'Orbitron',monospace !important; font-size:0.78rem !important;
}
div[data-testid="stButton"] button.fp-t40 p { color:#335577 !important; }
div[data-testid="stButton"] button.fp-t40.fp-sel {
  background:#07152e !important;
  border-color:#3388ff !important; color:#55aaff !important;
  box-shadow:0 0 22px rgba(60,140,255,0.55) !important;
  animation:selPulse 1.6s ease-in-out infinite !important;
}
div[data-testid="stButton"] button.fp-t40.fp-sel p { color:#55aaff !important; }

/* ?쒓컙: SNIPER 50s 蹂대씪 */
div[data-testid="stButton"] button.fp-t50 {
  background:#0a051e !important;
  border-color:rgba(130,55,220,0.3) !important; color:#664488 !important;
  min-height:56px !important; font-family:'Orbitron',monospace !important; font-size:0.78rem !important;
}
div[data-testid="stButton"] button.fp-t50 p { color:#664488 !important; }
div[data-testid="stButton"] button.fp-t50.fp-sel {
  background:#180836 !important;
  border-color:#aa44ff !important; color:#cc77ff !important;
  box-shadow:0 0 22px rgba(170,80,255,0.55) !important;
  animation:selPulse 1.6s ease-in-out infinite !important;
}
div[data-testid="stButton"] button.fp-t50.fp-sel p { color:#cc77ff !important; }

/* ?묒쟾 移대뱶 怨듯넻 ??4????以?*/
div[data-testid="stButton"] button.fp-mode {
  min-height:90px !important;
  text-align:center !important; padding:10px 3px !important;
  font-family:'Rajdhani',sans-serif !important; font-size:0.82rem !important;
}

/* 臾몃쾿???뚮옉 */
div[data-testid="stButton"] button.fp-g1 {
  background:#1a0800 !important; border-color:rgba(255,100,0,0.35) !important; color:#cc5500 !important;
}
div[data-testid="stButton"] button.fp-g1 p { color:#cc5500 !important; }
div[data-testid="stButton"] button.fp-g1.fp-sel {
  background:#2a1000 !important; border-color:#ff6600 !important; color:#ff8833 !important;
  box-shadow:0 0 22px rgba(106,173,255,0.5) !important; border-width:2px !important;
  animation:selPulse 1.8s ease-in-out infinite !important;
}
div[data-testid="stButton"] button.fp-g1.fp-sel p { color:#ff8833 !important; }

/* 援ъ“??蹂대씪 */
div[data-testid="stButton"] button.fp-g2 {
  background:#1a0c00 !important; border-color:rgba(220,140,0,0.35) !important; color:#bb8800 !important;
}
div[data-testid="stButton"] button.fp-g2 p { color:#bb8800 !important; }
div[data-testid="stButton"] button.fp-g2.fp-sel {
  background:#200a3e !important; border-color:#cc88ff !important; color:#ddaaff !important;
  box-shadow:0 0 22px rgba(200,136,255,0.5) !important; border-width:2px !important;
  animation:selPulse 1.8s ease-in-out infinite !important;
}
div[data-testid="stButton"] button.fp-g2.fp-sel p { color:#ddaaff !important; }

/* ?곌껐??泥?줉 */
div[data-testid="stButton"] button.fp-g3 {
  background:#181000 !important; border-color:rgba(200,160,0,0.35) !important; color:#aa8800 !important;
}
div[data-testid="stButton"] button.fp-g3 p { color:#aa8800 !important; }
div[data-testid="stButton"] button.fp-g3.fp-sel {
  background:#281800 !important; border-color:#ddaa00 !important; color:#ffdd44 !important;
  box-shadow:0 0 22px rgba(0,220,200,0.5) !important; border-width:2px !important;
  animation:selPulse 1.8s ease-in-out infinite !important;
}
div[data-testid="stButton"] button.fp-g3.fp-sel p { color:#ffdd44 !important; }

/* ?댄쐶??珥덈줉 */
div[data-testid="stButton"] button.fp-vc {
  background:#1a0400 !important; border-color:rgba(220,60,0,0.35) !important; color:#cc3300 !important;
}
div[data-testid="stButton"] button.fp-vc p { color:#cc3300 !important; }
div[data-testid="stButton"] button.fp-vc.fp-sel {
  background:#2a0800 !important; border-color:#ff4400 !important; color:#ff6633 !important;
  box-shadow:0 0 22px rgba(85,238,119,0.5) !important; border-width:2px !important;
  animation:selPulse 1.8s ease-in-out infinite !important;
}
div[data-testid="stButton"] button.fp-vc.fp-sel p { color:#ff6633 !important; }

/* 異쒓꺽 踰꾪듉 */
div[data-testid="stButton"] button.fp-launch {
  background:#280800 !important; border:2.5px solid #ff4400 !important;
  border-radius:14px !important; color:#ffcc55 !important;
  font-family:'Orbitron',monospace !important;
  font-weight:900 !important; font-size:0.88rem !important;
  letter-spacing:2px !important; min-height:56px !important;
  transition:none !important; animation:launchGlow 0.55s ease-in-out infinite !important;
}
div[data-testid="stButton"] button.fp-launch p {
  color:#ffcc55 !important; font-family:'Orbitron',monospace !important;
  font-size:0.88rem !important; font-weight:900 !important; letter-spacing:2px !important;
}
div[data-testid="stButton"] button.fp-launch-off {
  background:#06060f !important; border:1px solid #0e0e1c !important;
  border-radius:12px !important; color:#18182a !important;
  font-family:'Orbitron',monospace !important;
  font-size:0.8rem !important; min-height:50px !important;
}
div[data-testid="stButton"] button.fp-launch-off p { color:#18182a !important; }

/* ?ㅻ퉬 踰꾪듉 */
div[data-testid="stButton"] button.fp-nav {
  background:#05050e !important; border:1px solid #151525 !important;
  border-radius:10px !important; color:#3d5066 !important;
  min-height:40px !important; font-size:0.82rem !important;
}
div[data-testid="stButton"] button.fp-nav p { color:#3d5066 !important; }

@media(max-width:480px) {
  div[data-testid="stButton"] button.fp-t30,
  div[data-testid="stButton"] button.fp-t40,
  div[data-testid="stButton"] button.fp-t50 { min-height:52px !important; }
  div[data-testid="stButton"] button.fp-mode { min-height:82px !important; }
  div[data-testid="stButton"] button.fp-launch { min-height:52px !important; }
}
</style>""", unsafe_allow_html=True)

    # ?? ??댄? ??
    _rb = f'<span style="background:#1a0800;border:1px solid #cc6600;border-radius:20px;padding:1px 10px;font-size:0.68rem;color:#ffaa44;font-weight:900;">?룇 ROUND {rn}</span> ' if rn > 1 else ''
    st.markdown(f"""<div style="text-align:center;padding:10px 0 14px;">
      <div style="font-size:8px;color:#442200;letter-spacing:4px;margin-bottom:4px;font-weight:700;">FIREPOWER BATTLE</div>
      <div style="font-family:Orbitron,monospace;font-size:2rem;font-weight:900;letter-spacing:6px;
        background:linear-gradient(90deg,#00e5ff,#ffffff,#FFD600,#ff3300,#00e5ff);background-size:300%;
        -webkit-background-clip:text;-webkit-text-fill-color:transparent;
        animation:titleShine 2s linear infinite;line-height:1.2;">{_rb}???붾젰??/div>
      <div style="font-size:0.65rem;color:#334455;letter-spacing:2px;margin-top:5px;">
        5臾몄젣 쨌 ?댁븘?⑥븘?? 쨌 臾몃쾿?댄쐶 ?ㅼ쟾 ?ш꺽??/div>
    </div>""", unsafe_allow_html=True)

    import streamlit.components.v1 as _nc
    # NPC_BOARD
    _npc_nick = st.session_state.get('student_nickname', '')
    _npc_html = """<div id='npc-board' style='background:rgba(10,5,20,0.96);border:1.5px solid #cc6633;border-radius:10px;padding:10px 14px;text-align:center;margin-bottom:4px;'><span id='npc-icon' style='font-size:28px;margin-bottom:4px;animation:iconPop 0.9s ease-in-out infinite;display:block;'></span><div id='npc-txt' style='font-size:13px;font-weight:900;color:#fff;min-height:20px;'></div></div><style>@keyframes iconPop{0%,100%{transform:scale(1)}50%{transform:scale(1.18)}}</style><script>(function(){var KEY='snapq_tour_day';var today=new Date().toISOString().slice(0,10);var raw=localStorage.getItem(KEY);var data=raw?JSON.parse(raw):{'first':''};if(!data.first){data.first=today;localStorage.setItem(KEY,JSON.stringify(data));}var diff=(new Date(today)-new Date(data.first))/(1000*60*60*24);var nick='__NICK__';var tour=[["?뵦?뮙", "遺덇컳? P5! ?쒗뿕?μ? 30臾몄젣 9遺?"], ["?렞??, "?쇰떒 50s SNIPER! 5臾몄젣濡??쒖옉!"], ["?뷂툘?뵦", "?쎌젏 移댄뀒怨좊━ 吏묒쨷 ?곗뒿! 痍⑥빟?먯쓣 媛뺤젏?쇰줈!"], ["?뮙?룇", "BLITZ ?뺣났?섎㈃ P5 留뚯젏?대떎!"]];var inbody=[["?뵦??, "__NICK__?? ?ㅻ뒛??遺덉쿂?? P5 ?뺣났?대떎!"], ["?렞?뮙", "__NICK__?? ?쎌젏 移댄뀒怨좊━ 吏묒쨷 怨듬왂!"], ["?깍툘?룇", "__NICK__?? BLITZ ?꾩쟾?????먯뼱!"]];inbody=inbody.map(function(m){return[m[0],m[1].replace(/__NICK__/g,nick)];});var msgs=diff<3?tour:inbody;var ic=document.getElementById('npc-icon');var tx=document.getElementById('npc-txt');var mi=0,ci=0;function run(){var m=msgs[mi%msgs.length];ic.textContent=m[0];if(ci<m[1].length){tx.textContent+=m[1][ci++];setTimeout(run,45);}else{setTimeout(function(){tx.textContent='';ci=0;mi++;run();},3500);}}setTimeout(run,500);})();</script>"""
    _npc_html = _npc_html.replace('__NICK__', _npc_nick)
    import streamlit.components.v1 as _nc
    _nc.html(_npc_html, height=80)
    # ?? COMBAT TIME ?뱀뀡 ??
    st.markdown('<div style="height:4px;"></div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:9px;color:#cc6633;letter-spacing:4px;padding:4px 0 6px;font-weight:700;">?? COMBAT TIME</div>', unsafe_allow_html=True)
    tc1, tc2, tc3 = st.columns(3)
    with tc1:
        if st.button("?뵦 30s\nBLITZ", key="t30", use_container_width=True):
            st.session_state.tsec=30; st.session_state.tsec_chosen=True; st.rerun()
    with tc2:
        if st.button("??40s\nSTANDARD", key="t40", use_container_width=True):
            st.session_state.tsec=40; st.session_state.tsec_chosen=True; st.rerun()
    with tc3:
        if st.button("?썳截?50s\nSNIPER", key="t50", use_container_width=True):
            st.session_state.tsec=50; st.session_state.tsec_chosen=True; st.rerun()

    # ?? MISSION SELECT ?뱀뀡 ??
    st.markdown('<div style="height:6px;"></div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:9px;color:#cc3355;letter-spacing:4px;padding:4px 0 6px;font-weight:700;">?렞  MISSION SELECT</div>', unsafe_allow_html=True)
    b1, b2, b3, b4 = st.columns(4)
    with b1:
        if st.button("?뷂툘\nGRAMMAR\n?쒖젣쨌?쑣룹닔?쇱튂\nGRM", key="sg1", use_container_width=True):
            st.session_state.sel_mode="g1"; st.rerun()
    with b2:
        if st.button("?봽\nFORM\n?덉궗?꾪솚쨌?댄삎\nFORM", key="sg2", use_container_width=True):
            st.session_state.sel_mode="g2"; st.rerun()
    with b3:
        if st.button("?뵕\nLINK\n?곌껐?는룹젒?띿궗\nLINK", key="sg3", use_container_width=True):
            st.session_state.sel_mode="g3"; st.rerun()
    with b4:
        if st.button("?뱲\nVOCAB\n?숈쓽?는룸Ц留μ뼱??nVOCAB", key="svc", use_container_width=True):
            st.session_state.sel_mode="vocab"; st.rerun()

    # ?? ?앹〈 洹쒖튃 ??
    st.markdown(
        '<div style="text-align:center;margin:20px 0 4px;font-size:0.82rem;font-weight:900;'
        'color:#cc3333;letter-spacing:1px;'
        'animation:warnBlink 1.4s ease-in-out infinite;">'
        '?? 3媛??댁긽 寃⑺뙆?댁빞 ?앹〈 쨌 洹??댄븯硫??꾨㈇!</div>',
        unsafe_allow_html=True
    )

    # ?? 異쒓꺽 踰꾪듉 ??
    if _ready:
        _cat = lbl_map.get(_cur_sm,"")
        _tl  = _tlabel_map.get(str(_cur_tsec), str(_cur_tsec)+"s")
        if st.button(f"?뵦 異쒓꺽! ??{_cat}  ??{_tl}", key="go_start", use_container_width=True):
            try:
                _md, _grp = mode_map[_cur_sm]
                _qs = pick5(_md, _grp)
                st.session_state.mode         = _md
                st.session_state.round_qs     = _qs
                st.session_state.cq           = _qs[0]
                st.session_state.qi           = 0
                st.session_state.sc           = 0
                st.session_state.wrong        = 0
                st.session_state.ta           = 0
                st.session_state.ans          = False
                st.session_state.sel          = None
                st.session_state.round_results= []
                st.session_state.qst          = time.time()
                st.session_state["_battle_entry_ans_reset"] = False
                st.session_state.phase        = "battle"
                st.rerun()
            except Exception as _e:
                st.error(f"?ㅻ쪟: {_e}")
    else:
        st.button("??COMBAT TIME + ?렞 MISSION ??異쒓꺽!", key="go_disabled", use_container_width=True, disabled=True)

    # ?? ?ㅻ퉬 ??
    st.markdown('<div style="height:1px;background:#0e0e1e;margin:4px 0 3px;"></div>', unsafe_allow_html=True)
    nc1, nc2 = st.columns(2)
    with nc1:
        if st.button("?? ?щ줈?щ졊遺", key="p5nav1", use_container_width=True):
            st.switch_page("pages/03_POW_HQ.py")
    with nc2:
        if st.button("?룧 ??, key="p5nav2", use_container_width=True):
            st.session_state._p5_just_left = True
            _nick = st.session_state.get("battle_nickname") or st.session_state.get("nickname","")
            if _nick:
                st.query_params["nick"] = _nick
                st.query_params["ag"]   = "1"
            st.switch_page("main_hub.py")

    # ?? JS: ?대옒??遺??(setTimeout 2??+ 異쒓꺽 border-color flicker) ??
    _sel_t  = str(_cur_tsec) if _cur_tc else ""
    _sel_m  = _cur_sm
    _js_ready = "true" if _ready else "false"
    components.html(f"""<script>
(function(){{
  var selT="{_sel_t}", selM="{_sel_m}", isReady={_js_ready};
  var doc=window.parent.document;

  function applyClasses(){{
    doc.querySelectorAll("button").forEach(function(b){{
      var txt=(b.innerText||b.textContent||"").trim();
      if(!txt) return;

      // ?쒓컙 踰꾪듉 (?곷Ц ?쇰꺼)
      if(txt.indexOf("30s")>-1 && txt.indexOf("\ucd9c\uaca9")===-1){{
        b.classList.add("fp-t30");
        if(selT==="30") b.classList.add("fp-sel"); else b.classList.remove("fp-sel");
        b.querySelectorAll("p").forEach(function(p){{p.classList.add("fp-t30");if(selT==="30")p.classList.add("fp-sel");else p.classList.remove("fp-sel");}});
      }}
      if(txt.indexOf("40s")>-1 && txt.indexOf("\ucd9c\uaca9")===-1){{
        b.classList.add("fp-t40");
        if(selT==="40") b.classList.add("fp-sel"); else b.classList.remove("fp-sel");
        b.querySelectorAll("p").forEach(function(p){{p.classList.add("fp-t40");if(selT==="40")p.classList.add("fp-sel");else p.classList.remove("fp-sel");}});
      }}
      if(txt.indexOf("50s")>-1 && txt.indexOf("\ucd9c\uaca9")===-1){{
        b.classList.add("fp-t50");
        if(selT==="50") b.classList.add("fp-sel"); else b.classList.remove("fp-sel");
        b.querySelectorAll("p").forEach(function(p){{p.classList.add("fp-t50");if(selT==="50")p.classList.add("fp-sel");else p.classList.remove("fp-sel");}});
      }}

      // ?묒쟾 移대뱶
      if(txt.indexOf("\uc2dc\uc81c")>-1){{
        b.classList.add("fp-mode","fp-g1");
        if(selM==="g1") b.classList.add("fp-sel"); else b.classList.remove("fp-sel");
        b.querySelectorAll("p").forEach(function(p){{p.classList.add("fp-g1");if(selM==="g1")p.classList.add("fp-sel");else p.classList.remove("fp-sel");}});
      }}
      if(txt.indexOf("\ud488\uc0ac\uc804\ud658")>-1){{
        b.classList.add("fp-mode","fp-g2");
        if(selM==="g2") b.classList.add("fp-sel"); else b.classList.remove("fp-sel");
        b.querySelectorAll("p").forEach(function(p){{p.classList.add("fp-g2");if(selM==="g2")p.classList.add("fp-sel");else p.classList.remove("fp-sel");}});
      }}
      if(txt.indexOf("\uc5f0\uacb0\uc5b4")>-1){{
        b.classList.add("fp-mode","fp-g3");
        if(selM==="g3") b.classList.add("fp-sel"); else b.classList.remove("fp-sel");
        b.querySelectorAll("p").forEach(function(p){{p.classList.add("fp-g3");if(selM==="g3")p.classList.add("fp-sel");else p.classList.remove("fp-sel");}});
      }}
      if(txt.indexOf("\ub3d9\uc758\uc5b4")>-1){{
        b.classList.add("fp-mode","fp-vc");
        if(selM==="vocab") b.classList.add("fp-sel"); else b.classList.remove("fp-sel");
        b.querySelectorAll("p").forEach(function(p){{p.classList.add("fp-vc");if(selM==="vocab")p.classList.add("fp-sel");else p.classList.remove("fp-sel");}});
      }}

      // 異쒓꺽 踰꾪듉
      if(txt.indexOf("\ucd9c\uaca9!")>-1 && txt.indexOf("COMBAT")===-1){{
        if(isReady){{ b.classList.add("fp-launch"); b.classList.remove("fp-launch-off"); }}
        else{{ b.classList.add("fp-launch-off"); b.classList.remove("fp-launch"); }}
      }}
      // ?ㅻ퉬
      if(txt.indexOf("\ud3ec\ub85c\uc0ac\ub839\ubd80")>-1||txt.indexOf("\ud648")>-1){{
        b.classList.add("fp-nav");
      }}
    }});
  }}

  setTimeout(applyClasses, 120);
  setTimeout(applyClasses, 450);

  if(isReady){{
    var _fi=0;
    var _fc=["#ff4400","#ff6600","#ff9900","#FFD600","#ff9900","#ff6600","#ff4400","#ff2200"];
    setInterval(function(){{
      doc.querySelectorAll("button.fp-launch").forEach(function(b){{
        b.style.setProperty("border-color",_fc[_fi%_fc.length],"important");
      }});
      _fi++;
    }}, 130);
  }}
}})();
</script>""", height=0)
