
# ===== P7_FORCE_TEXT_X12_BOLD (DO NOT EDIT) =====
try:
    import streamlit as st
    st.markdown(r'''<style>
/* ===== P7_FORCE_TEXT_X12_BOLD_CSS ===== */
/* Passage / Question (p7-zone body text) */
.p7-pack .p7-zone .p7-zone-body{
  font-size: 22px !important;   /* ~18px * 1.2 = 21.6 -> 22px */
  font-weight: 900 !important;
}

/* Some variants may use mission zone */
.p7-pack .p7-zone.mission .p7-zone-body{
  font-size: 23px !important;
  font-weight: 900 !important;
}

/* Options (radio style) */
.p7-pack div[role="radiogroup"] > label,
.p7-pack div[role="radiogroup"] > label *{
  font-size: 19px !important;   /* ~16px * 1.2 = 19.2 -> 19px */
  font-weight: 900 !important;
}

/* Options (button style fallback, if ever used) */
.p7-pack .p7-opt-wrap div[data-testid="stButton"] > button,
.p7-pack .p7-opt-wrap div[data-testid="stButton"] > button *{
  font-size: 19px !important;
  font-weight: 900 !important;
}

/* HUD는 절대 건드리지 않음(보호막) */
.p7-pack .p7-hud,
.p7-pack .p7-hud *{
  font-size: inherit !important;
  font-weight: inherit !important;
}
/* ===== /P7_FORCE_TEXT_X12_BOLD_CSS ===== */
</style>''', unsafe_allow_html=True)
except Exception:
    pass
# ===== /P7_FORCE_TEXT_X12_BOLD =====

# ===== P7_TEXT_FORCE_X1P2_V3 (CSS ONLY / LAST WINS) =====
try:
    import streamlit as st
    st.markdown(r"""
    <style>
    /* === P7_TEXT_FORCE_X1P2_V3 === */
    /* 1) Passage + Question text only */
    .p7-zone .p7-zone-body,
    .p7-zone .p7-zone-body p,
    .p7-zone .p7-zone-body span,
    .p7-zone .p7-zone-body strong,
    .p7-zone .p7-zone-body em{
      font-size: 22px !important;   /* 18px * 1.2 ~= 21.6px -> 22px */
      font-weight: 900 !important;  /* thicker */
    }

    /* 2) Options (radio) text only - scoped to p7-opt-wrap to avoid other radios */
    .p7-opt-wrap div[role="radiogroup"] > label{
      font-size: 1em !important;    /* reset base to prevent double scaling */
      font-weight: 400 !important;  /* label itself normal */
    }

    .p7-opt-wrap div[role="radiogroup"] > label p,
    .p7-opt-wrap div[role="radiogroup"] > label span,
    .p7-opt-wrap div[role="radiogroup"] > label strong,
    .p7-opt-wrap div[role="radiogroup"] > label em,
    .p7-opt-wrap div[role="radiogroup"] > label [data-testid="stMarkdownContainer"] p,
    .p7-opt-wrap div[role="radiogroup"] > label [data-testid="stMarkdownContainer"] span{
      font-size: 1.2em !important;  /* +20% exactly once */
      font-weight: 900 !important;  /* thicker */
    }

    /* (If options are buttons in some modes) */
    .p7-opt-wrap div[data-testid="stButton"] > button,
    .p7-opt-wrap div[data-testid="stButton"] > button *{
      font-size: 1.2em !important;
      font-weight: 900 !important;
    }
    /* === /P7_TEXT_FORCE_X1P2_V3 === */
    /* ===== P7_TEXT_FORCE_V3_X1P2 (TEXT ONLY) ===== */
/* Passage text */
.p7-zone .p7-zone-body{
  font-size: 22px !important;
  font-weight: 800 !important;
}
.p7-zone .p7-zone-body p,
.p7-zone .p7-zone-body span,
.p7-zone .p7-zone-body strong,
.p7-zone .p7-zone-body em{
  font-size: 22px !important;
  font-weight: 800 !important;
}

/* Question text (title area inside zone) */
.p7-zone .p7-q-title,
.p7-zone .p7-q-title *{
  font-size: 22px !important;
  font-weight: 900 !important;
}

/* Options text (radio) */
.p7-zone div[role="radiogroup"] label,
.p7-zone div[role="radiogroup"] label *{
  font-size: 22px !important;
  font-weight: 900 !important;
}

/* Options text (button type, if any) */
.p7-opt-wrap div[data-testid="stButton"] > button,
.p7-opt-wrap div[data-testid="stButton"] > button *{
  font-size: 22px !important;
  font-weight: 900 !important;
}
/* ===== /P7_TEXT_FORCE_V3_X1P2 ===== */
</style>
    """, unsafe_allow_html=True)
except Exception:
    pass
# ===== /P7_TEXT_FORCE_X1P2_V3 =====


