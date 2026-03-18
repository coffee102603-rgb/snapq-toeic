import re

path = r"""C:\Users\최정은\Desktop\snapq_toeic\app\arenas\p7_reading_arena.py"""
src = open(path, "r", encoding="utf-8").read()
lines = src.splitlines(True)

# ---------- A) inject_css(): append CSS safely inside function ----------
MARK = "P7_SAFE_VISUAL_V3"
if MARK not in src:
    # find inject_css block range (line indices)
    idx_def = next((i for i,l in enumerate(lines) if l.startswith("def inject_css()")), None)
    if idx_def is None:
        raise SystemExit("inject_css() not found")

    # find next top-level def after inject_css
    idx_next = next((i for i in range(idx_def+1, len(lines)) if lines[i].startswith("def ") and not lines[i].startswith("def inject_css()")), len(lines))

    # insert near end of inject_css (before idx_next)
    # detect indent inside inject_css (usually 4 spaces)
    indent = "    "
    css_block = [
        "\n",
        f"{indent}# ---- {MARK} ----\n",
        f"{indent}st.markdown(\n",
        f"{indent}    r\"\"\"\n",
        f"{indent}    <style>\n",
        f"{indent}    /* {MARK} */\n",
        "\n",
        f"{indent}    /* 선택지: 흰 버튼이면 글자는 검정 + 1.2배 */\n",
        f"{indent}    .p7-opt-wrap div[data-testid=\"stButton\"] > button,\n",
        f"{indent}    .p7-opt-wrap div[data-testid=\"stButton\"] > button *{{\n",
        f"{indent}      color:#0B1020 !important;\n",
        f"{indent}      text-shadow:none !important;\n",
        f"{indent}    }}\n",
        f"{indent}    .p7-opt-wrap div[data-testid=\"stButton\"] > button{{\n",
        f"{indent}      font-size:22px !important;\n",
        f"{indent}      font-weight:950 !important;\n",
        f"{indent}    }}\n",
        f"{indent}    .p7-opt-wrap div[data-testid=\"stButton\"] > button:hover,\n",
        f"{indent}    .p7-opt-wrap div[data-testid=\"stButton\"] > button:hover *{{\n",
        f"{indent}      color:#ffffff !important;\n",
        f"{indent}    }}\n",
        "\n",
        f"{indent}    /* 지문/문제 글자 1.2배 */\n",
        f"{indent}    .p7-zone .p7-zone-body{{ font-size:22px !important; }}\n",
        f"{indent}    .p7-zone.mission .p7-zone-body{{ font-size:23px !important; }}\n",
        "\n",
        f"{indent}    /* 게이지: 30초 단계색 + last60 wiggle + last30 red shake + final */\n",
        f"{indent}    @keyframes p7_gauge_wiggle{{0%{{transform:translateX(0)}}25%{{transform:translateX(-2px)}}50%{{transform:translateX(0)}}75%{{transform:translateX(2px)}}100%{{transform:translateX(0)}}}}\n",
        f"{indent}    @keyframes p7_gauge_shake{{0%{{transform:translateX(0)}}20%{{transform:translateX(-4px)}}40%{{transform:translateX(4px)}}60%{{transform:translateX(-3px)}}80%{{transform:translateX(3px)}}100%{{transform:translateX(0)}}}}\n",
        f"{indent}    @keyframes p7_gauge_flash{{0%{{filter:brightness(1.0)}}50%{{filter:brightness(1.55)}}100%{{filter:brightness(1.0)}}}}\n",
        f"{indent}    .p7-hud-gauge.stage5 .fill{{ background:linear-gradient(90deg, rgba(34,211,238,.95), rgba(124,58,237,.95)) !important; }}\n",
        f"{indent}    .p7-hud-gauge.stage4 .fill{{ background:linear-gradient(90deg, rgba(56,189,248,.95), rgba(167,139,250,.95)) !important; }}\n",
        f"{indent}    .p7-hud-gauge.stage3 .fill{{ background:linear-gradient(90deg, rgba(45,212,191,.95), rgba(34,211,238,.95)) !important; }}\n",
        f"{indent}    .p7-hud-gauge.stage2 .fill{{ background:linear-gradient(90deg, rgba(250,204,21,.95), rgba(34,211,238,.95)) !important; }}\n",
        f"{indent}    .p7-hud-gauge.stage1 .fill{{ background:linear-gradient(90deg, rgba(251,146,60,.95), rgba(250,204,21,.95)) !important; }}\n",
        f"{indent}    .p7-hud-gauge.stage0 .fill{{ background:linear-gradient(90deg, rgba(239,68,68,.98), rgba(220,38,38,.98)) !important; }}\n",
        f"{indent}    .p7-hud-gauge.last60{{ animation:p7_gauge_wiggle .9s linear infinite; }}\n",
        f"{indent}    .p7-hud-gauge.last30{{ animation:p7_gauge_shake .35s linear infinite, p7_gauge_flash .55s ease-in-out infinite; border-color:rgba(239,68,68,.55) !important; box-shadow:0 0 26px rgba(239,68,68,.18) !important; }}\n",
        f"{indent}    .p7-hud-gauge.final{{ animation:p7_gauge_shake .24s linear infinite, p7_gauge_flash .35s ease-in-out infinite; box-shadow:0 0 40px rgba(239,68,68,.25) !important; }}\n",
        "\n",
        f"{indent}    </style>\n",
        f"{indent}    \"\"\",\n",
        f"{indent}    unsafe_allow_html=True,\n",
        f"{indent})\n",
    ]

    lines[idx_next:idx_next] = css_block

# ---------- B) render_top_hud(): add gauge_cls calculation safely ----------
src2 = "".join(lines)
if "GAUGE_DRAMA_V3" not in src2:
    lines = src2.splitlines(True)
    idx_def = next((i for i,l in enumerate(lines) if l.startswith("def render_top_hud()")), None)
    if idx_def is None:
        open(path, "w", encoding="utf-8").write("".join(lines))
        raise SystemExit("render_top_hud() not found")

    idx_next = next((i for i in range(idx_def+1, len(lines)) if lines[i].startswith("def ")), len(lines))

    # find line index of gauge markdown call by searching for 'p7-hud-gauge' inside the function block
    func_lines = lines[idx_def:idx_next]
    # locate first line containing class="p7-hud-gauge"
    hit = None
    for j, ln in enumerate(func_lines):
        if 'class="p7-hud-gauge"' in ln:
            hit = j
            break
    if hit is not None:
        # find the nearest previous line that contains 'st.markdown' (start of that block)
        md_line = None
        for k in range(hit, -1, -1):
            if "st.markdown" in func_lines[k]:
                md_line = k
                break

        if md_line is not None:
            indent = re.match(r"^\s*", func_lines[md_line]).group(0)

            # inject gauge_cls calc right before md_line
            gauge_code = [
                indent + "# ---- GAUGE_DRAMA_V3 ----\n",
                indent + "stage = int(remaining // 30)\n",
                indent + "gauge_cls = f\"p7-hud-gauge stage{stage}\"\n",
                indent + "if remaining <= 60:\n",
                indent + "    gauge_cls += \" last60\"\n",
                indent + "if remaining <= 30:\n",
                indent + "    gauge_cls += \" last30\"\n",
                indent + "if remaining <= 10:\n",
                indent + "    gauge_cls += \" final\"\n",
            ]
            func_lines[md_line:md_line] = gauge_code

            # replace class="p7-hud-gauge" -> class="{gauge_cls}" only on that line (single-line edit)
            func_lines[hit] = func_lines[hit].replace('class="p7-hud-gauge"', 'class="{gauge_cls}"')

            # ensure the markdown is an f-string (line containing st.markdown)
            func_lines[md_line + len(gauge_code)] = func_lines[md_line + len(gauge_code)].replace("st.markdown(", "st.markdown(f", 1)

            lines[idx_def:idx_next] = func_lines

open(path, "w", encoding="utf-8").write("".join(lines))
print("[OK] SAFE patches applied (no triple-quote rewrite)")

