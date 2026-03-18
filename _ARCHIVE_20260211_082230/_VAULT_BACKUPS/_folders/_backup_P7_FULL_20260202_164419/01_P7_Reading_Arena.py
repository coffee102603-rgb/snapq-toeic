from __future__ import annotations
import time
import streamlit as st

try:
    from streamlit_autorefresh import st_autorefresh
except Exception:
    st_autorefresh = None

st.set_page_config(page_title="SnapQ P7 Reading Arena", layout="wide", initial_sidebar_state="collapsed")

if "p7_t0" not in st.session_state:
    st.session_state.p7_t0 = time.time()
if "p7_limit" not in st.session_state:
    st.session_state.p7_limit = 150
if "p7_step" not in st.session_state:
    st.session_state.p7_step = 1
if "p7_miss" not in st.session_state:
    st.session_state.p7_miss = 0
if "p7_combo" not in st.session_state:
    st.session_state.p7_combo = 0

def remaining():
    lim = int(st.session_state.p7_limit)
    return max(0, lim - int(time.time() - float(st.session_state.p7_t0)))

def mmss(sec:int)->str:
    m,s = divmod(max(0,int(sec)),60)
    return f"{m:02d}:{s:02d}"

rem = remaining()
if st_autorefresh and rem > 0:
    st_autorefresh(interval=1000, key="p7_tick")

pct = max(0.0, min(1.0, rem / max(1,int(st.session_state.p7_limit))))

stage = "p7-timer-ok"
if rem <= 5:
    stage = "p7-timer-5"
elif rem <= 10:
    stage = "p7-timer-10"
elif rem <= 20:
    stage = "p7-timer-20"
elif rem <= 30:
    stage = "p7-timer-30"

st.markdown("""
<style>
header[data-testid="stHeader"],
div[data-testid="stToolbar"],
div[data-testid="stDecoration"],
footer { display:none !important; height:0 !important; margin:0 !important; padding:0 !important; }
* { overflow-anchor: none !important; }

:root{ --hudH:46px; --barH:10px; }

.p7-hud{
  position:fixed; top:0; left:0; right:0;
  height:var(--hudH);
  z-index:999999;
  display:flex; align-items:center; gap:12px;
  padding:6px 12px;
  background:rgba(20,25,40,0.92);
  color:#fff; font-weight:800;
}

.p7-timer-wrap{
  position:fixed; top:var(--hudH); left:0; right:0;
  height:var(--barH);
  z-index:999998;
  background:rgba(255,255,255,0.10);
}

.p7-timer-bar{
  height:100%;
  width:60%;
  background:linear-gradient(90deg,#30cfd0,#8b5cf6);
  transition:width 0.25s linear;
}

/* BODY sits right under hud+bar */
.p7-body{
  margin-top:calc(var(--hudH) + var(--barH) + 2px);
  padding:6px 12px 20px 12px;
}

.p7-card{
  background:rgba(15,20,35,0.95);
  border-radius:18px;
  padding:16px 18px;
  margin:6px 0;
  color:#fff;
  box-shadow:0 0 0 1px rgba(255,255,255,0.05);
  font-weight:800;
}

/* ===== MONSTER MODE (stage on .p7-body) ===== */
.p7-timer-ok .p7-timer-wrap{ height:10px; }
.p7-timer-ok .p7-timer-bar { box-shadow:0 6px 14px rgba(0,0,0,0.25); transform:translateY(2px); }

.p7-timer-30 .p7-timer-wrap{ height:12px; }
.p7-timer-30 .p7-timer-bar { animation:pulse_soft 1.4s infinite; transform:translateY(3px); box-shadow:0 10px 18px rgba(255,152,0,0.25); }

.p7-timer-20 .p7-timer-wrap{ height:14px; }
.p7-timer-20 .p7-timer-bar { background:linear-gradient(90deg,#ff9800,#ff5722); animation:shake_soft 0.9s infinite; transform:translateY(4px); box-shadow:0 12px 22px rgba(255,87,34,0.28); }

.p7-timer-10 .p7-timer-wrap{ height:16px; }
.p7-timer-10 .p7-timer-bar { background:linear-gradient(90deg,#ff1744,#ff5252); animation:shake_hard 0.45s infinite, pulse_hard 0.9s infinite; transform:translateY(5px); box-shadow:0 14px 26px rgba(255,23,68,0.35); }

.p7-timer-5 .p7-timer-wrap{ height:18px; }
.p7-timer-5 .p7-timer-bar { background:linear-gradient(90deg,#ff0000,#ff5252,#ff0000); animation:heartbeat 0.55s infinite; transform:translateY(6px); box-shadow:0 18px 34px rgba(255,0,0,0.45); }

@keyframes pulse_soft{ 0%{filter:brightness(1)} 50%{filter:brightness(1.25)} 100%{filter:brightness(1)} }
@keyframes pulse_hard{ 0%{filter:brightness(1)} 50%{filter:brightness(1.5)} 100%{filter:brightness(1)} }
@keyframes shake_soft{ 0%{transform:translateY(4px) translateX(0)} 50%{transform:translateY(4px) translateX(1px)} 100%{transform:translateY(4px) translateX(0)} }
@keyframes shake_hard{ 0%{transform:translateY(5px) translateX(0)} 25%{transform:translateY(5px) translateX(-2px)} 50%{transform:translateY(5px) translateX(2px)} 100%{transform:translateY(5px) translateX(0)} }
@keyframes heartbeat{ 0%{transform:translateY(6px) scaleY(1)} 25%{transform:translateY(6px) scaleY(1.25)} 40%{transform:translateY(6px) scaleY(0.9)} 60%{transform:translateY(6px) scaleY(1.35)} 100%{transform:translateY(6px) scaleY(1)} }
</style>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="p7-hud">
  <span>STEP {st.session_state.p7_step}/3</span>
  <span>TIME {mmss(rem)}</span>
  <span>MISS {st.session_state.p7_miss}/3</span>
  <span>COMBO {st.session_state.p7_combo}</span>
</div>

<div class="p7-timer-wrap">
  <div class="p7-timer-bar" style="width:{int(pct*100)}%"></div>
</div>

<div class="p7-body {stage}">
  <div class="p7-card">Dear staff, This is to inform you that our customer support team will be relocated next month.</div>
  <div class="p7-card">What is the main purpose of this message?</div>
</div>
""", unsafe_allow_html=True)

