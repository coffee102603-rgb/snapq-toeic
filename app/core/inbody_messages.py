"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FILE:     app/core/inbody_messages.py
ROLE:     멘트 풀 + 시그널 → 실제 텍스트 변환
VERSION:  SnapQ TOEIC V3 — 2026.04.30
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
USAGE:
    from app.core.inbody_messages import render_message

    signal = {
        "character": "skull",
        "key": "same_word_3plus",
        "data": {"word": "allocate", "count": 3},
    }
    text = render_message(signal)
    # → "'allocate' 3번째. 영원히 패자가 될래?"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DESIGN:
    회의 결과 266개 멘트를 임계값별로 풀에 정리.
    시그널 데이터(정답률, 횟수 등) 보고 임계값 분기 →
    해당 풀에서 랜덤 1개 선택 → 데이터로 포맷팅.

POOLS:
    SKULL_POOLS  (~110개) — 포로/추세/시간/마일스톤
    TORI_POOLS    (~84개) — P5 카테고리 7개
    HAE_POOLS     (~72개) — P7 지표 + 글 타입
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import random
from typing import Dict, List


# ═══════════════════════════════════════════════════════════════
# 💀 SKULL POOLS (해골 — 포로·종합·추세)
# ═══════════════════════════════════════════════════════════════

# ─── 같은 단어 반복 오답 (철학 핵심) ──────────────────────────
SKULL_REPEAT_WORD = {
    "2": [
        "'{word}' 또 틀렸어. 반복 안 한 증거다.",
        "이 단어 두 번째. 푸는 게 아니라 외워.",
        "'{word}' 2회. 풀어본 거 ≠ 아는 거.",
    ],
    "3plus": [
        "'{word}' {count}번째. 영원히 패자가 될래?",
        "이 단어 {count}회 틀렸어. 자꾸 풀어도 안 늘어.",
        "{count}번째 같은 단어. 피드백을 무시한 결과.",
        "'{word}' 또 틀린다. 반복이 답이야.",
    ],
}

# ─── 포로 누적 ────────────────────────────────────────────────
SKULL_PRISON = {
    "0": [
        "포로수용소 비었다. 잠시 휴식.",
        "단어 포로 0. 처음이지?",
        "수용소 비었어. 곧 또 채워진다.",
    ],
    "1_5": [
        "포로 {count}명. 지금 풀어. 안 풀면 또 틀린다.",
        "단어 {count}명 가뒀다. 반복만이 답이야.",
        "포로 {count}명. 5분이면 끝나. 안 풀면 패자.",
        "포로 {count}명 누적. 푸는 게 아니라 외워야 한다.",
    ],
    "6_15": [
        "포로 {count}명. 안 풀면 영원히 패자.",
        "{count}명 가뒀어. 자꾸 푼다고 느는 거 아냐. 반복해.",
        "포로 {count}명. 피드백 없으면 실력 안 는다.",
        "{count}명 대기. 반복 안 하면 또 틀린다.",
        "포로 {count}명. 단어가 부족하군. 더 굴려.",
    ],
    "16plus": [
        "포로 {count}명. 이건 직무유기야.",
        "수용소 만원. 반복 안 한 결과다.",
        "포로 {count}명. 새 문제 풀지 말고 여기부터.",
        "{count}명 대기. 단어 부족 심각. 포로수용소로.",
        "포로 {count}명. 자꾸 새 거 풀지 마. 반복해.",
    ],
}

# ─── 출석 스트릭 ──────────────────────────────────────────────
SKULL_STREAK = {
    "1": [
        "신입이군. 오늘부터 시작이다.",
        "첫날. 도망갈 생각하지 마.",
        "1일차. 지켜보고 있다.",
    ],
    "2_6": [
        "{days}일 연속. 슬슬 전사 같다.",
        "{days}일째. 멈추지 마.",
        "{days}일 연속, 누적이다.",
    ],
    "7_29": [
        "🔥 {days}일 연속. 이제 우리 편이야.",
        "{days}일째. 포기 안 했네.",
        "🔥 {days}일. 합격각이다.",
    ],
    "30plus": [
        "🔥 {days}일. 한 달 채웠다.",
        "🔥 {days}일. 너 진짜네.",
        "🔥 {days}일. 합격은 시간 문제.",
    ],
}

# ─── 결석 후 복귀 ────────────────────────────────────────────
SKULL_ABSENT = {
    "1": [
        "어제 안 보였어. 왜?",
        "하루 빠졌다. 따라잡자.",
        "어제 비었네. 포로들이 늘었다.",
    ],
    "2_3": [
        "{days}일 만이군. 포로들이 추가됐다.",
        "{days}일 결석. 이제 다시.",
        "{days}일 만에 왔네. 정신 차리자.",
    ],
    "4plus": [
        "{days}일 만이야. 포로들이 잊혀질까 봐 다행.",
        "일주일 가까이. 다 잊었지?",
        "오랜만이네. 처음부터 다시 가자.",
    ],
}

# ─── 학습 시간 (오늘) ────────────────────────────────────────
SKULL_TODAY_TIME = {
    "short": [   # < 10분
        "오늘 {minutes}분. 그게 다야?",
        "{minutes}분 접속. 시험장 한 지문 시간이다.",
        "{minutes}분만 했네. 더 가.",
    ],
    "normal": [  # 10-30분
        "오늘 {minutes}분. 평소 페이스.",
        "{minutes}분 채웠다. 그대로.",
        "오늘 {minutes}분. 무난하다.",
    ],
    "focus": [   # 30-60분
        "오늘 {minutes}분. 집중력 좋네.",
        "{minutes}분 접속. 컨디션 좋아 보여.",
        "오늘 {minutes}분. 시험 준비 모드.",
    ],
    "long": [    # 60+
        "오늘 {minutes}분. 독한 놈.",
        "{minutes}분 접속. 무리하지 마.",
        "오늘 {minutes}분. 휴식도 챙겨.",
    ],
}

# ─── 시간대 ──────────────────────────────────────────────────
SKULL_TIME_OF_DAY = {
    "dawn": [    # 0-6
        "이 시간에? 독한 놈이네.",
        "이 시간에? 미친 거야?",
        "새벽이다. 잠은 자고 와.",
    ],
    "morning": [ # 6-9
        "이른 시작 좋아.",
        "출근 전이군. 빡세다.",
        "오전이다. 컨디션 잡히네.",
    ],
    "day": [     # 9-18
        "낮에 왔네. 시간 잘 쓴다.",
        "이 시간에. 꾸준하다.",
        "오늘도 시작이군.",
    ],
    "evening": [ # 18-22
        "퇴근 후에도 오네.",
        "하루 끝에 와도 오네.",
        "저녁이다. 꾸준하다.",
    ],
    "night": [   # 22-24
        "잠 줄여가며?",
        "자정 직전. 적당히 해.",
        "밤이다. 내일도 와.",
    ],
    "weekend": [
        "주말에도? 합격각이다.",
        "주말. 진심이네.",
        "주말에도 출근. 무섭다.",
    ],
}

# ─── 정답률 추세 ─────────────────────────────────────────────
SKULL_TREND = {
    "drop_10": [
        "어제 {yesterday}% → 오늘 {today}%. 무슨 일?",
        "어제보다 떨어졌다. 컨디션 안 좋네.",
        "급락. 잠 부족이지?",
    ],
    "up": [
        "어제 {yesterday}% → 오늘 {today}%. 그대로.",
        "꾸준히 ↑. 흐름 탔다.",
        "올라갔네. 그 감각 기억해.",
    ],
    "drop_3day": [
        "3일째 하락. 어제 {yesterday}% → 오늘 {today}%.",
        "추세 ↓. 무리한 거 아니야?",
        "정답률 빠졌다. 휴식도 무기야.",
    ],
}

# ─── 마일스톤 ────────────────────────────────────────────────
SKULL_MILESTONE = {
    "100": [
        "누적 100문제. 시작이다.",
        "100문제 돌파. 본격 시작.",
    ],
    "500": [
        "500문제. 슬슬 토익이 보일 거다.",
        "500개 풀었다. 페이스 좋아.",
    ],
    "1000": [
        "1000문제 돌파. 너 진짜네.",
        "🏆 1000개. 합격 코앞이다.",
    ],
}


# ═══════════════════════════════════════════════════════════════
# 🐱 TORI POOLS (P5 카테고리 — group 단위)
# ═══════════════════════════════════════════════════════════════

TORI_POOLS = {
    "passive_agreement": {  # 수동태·수일치
        "le30": [
            "수동태 {acc}%. 봐둬, 시험 단골이다.",
            "수동태 {acc}%. 능동·수동부터 정리.",
            "수동태 {acc}%. 다시 가.",
        ],
        "31_50": [
            "수동태 {acc}%. 절반도 못 맞춰.",
            "수동태 {acc}%. 한 끗이야.",
            "수동태 {acc}%. 'be + p.p.' 다시.",
        ],
        "51_70": [
            "수동태 {acc}%. 감 잡혔는데 더 가.",
            "수동태 {acc}%. 이제 시제만 잡으면 돼.",
            "수동태 {acc}%. 거의 다 왔다.",
        ],
        "ge71": [
            "수동태 {acc}%. 이건 됐다.",
            "수동태 {acc}%. 클린.",
            "수동태 {acc}%. 시험장 OK.",
        ],
    },
    "tense": {
        "le30": [
            "시제 {acc}%. 과거·완료 다시 봐.",
            "시제 {acc}%. for·since부터 정리.",
            "시제 {acc}%. 기본부터 가자.",
        ],
        "31_50": [
            "시제 {acc}%. 헷갈리지?",
            "시제 {acc}%. 완료 시제 약점이야.",
            "시제 {acc}%. 딱 절반.",
        ],
        "51_70": [
            "시제 {acc}%. 한 끗 차이야.",
            "시제 {acc}%. 좋아지고 있어.",
            "시제 {acc}%. 거의.",
        ],
        "ge71": [
            "시제 {acc}%. OK.",
            "시제 {acc}%. 깔끔하다.",
            "시제 {acc}%. 통과.",
        ],
    },
    "relative": {
        "le30": [
            "관계대명사 {acc}%. who·which 정리부터.",
            "관계대명사 {acc}%. 선행사부터 봐.",
            "관계대명사 {acc}%. that vs which 헷갈리지.",
        ],
        "31_50": [
            "관계대명사 {acc}%. 더 봐.",
            "관계대명사 {acc}%. 절반은 잡았어.",
            "관계대명사 {acc}%. 콤마 유무 체크.",
        ],
        "51_70": [
            "관계대명사 {acc}%. 거의 다 왔어.",
            "관계대명사 {acc}%. 감 잡혔다.",
            "관계대명사 {acc}%. 좋아.",
        ],
        "ge71": [
            "관계대명사 {acc}%. 통과.",
            "관계대명사 {acc}%. 끝.",
            "관계대명사 {acc}%. 클린.",
        ],
    },
    "verbal": {  # 동명사·준동사·분사구문
        "le30": [
            "준동사 {acc}%. 동명사·to부정사 헷갈린다.",
            "준동사 {acc}%. 패턴 외워.",
            "준동사 {acc}%. enjoy·avoid 뒤 뭐 오는지부터.",
        ],
        "31_50": [
            "준동사 {acc}%. 패턴 다시 외워.",
            "준동사 {acc}%. 동사별 짝꿍 정리해.",
            "준동사 {acc}%. 거의 절반.",
        ],
        "51_70": [
            "준동사 {acc}%. 감 잡혔다.",
            "준동사 {acc}%. 분사구문은 OK.",
            "준동사 {acc}%. 통과 직전.",
        ],
        "ge71": [
            "준동사 {acc}%. 굿.",
            "준동사 {acc}%. 클린.",
            "준동사 {acc}%. 끝.",
        ],
    },
    "form": {  # 품사형 (form 폴더)
        "le30": [
            "품사형 {acc}%. 명사·형용사 자리부터.",
            "품사형 {acc}%. 어미 안 보는 거지?",
            "품사형 {acc}%. -tion·-ly 구분 약해.",
        ],
        "31_50": [
            "품사형 {acc}%. 어미 보는 연습.",
            "품사형 {acc}%. 빈자리 품사 판단부터.",
            "품사형 {acc}%. 한 끗.",
        ],
        "51_70": [
            "품사형 {acc}%. 좋아지고 있어.",
            "품사형 {acc}%. 부사 자리만 잡으면 돼.",
            "품사형 {acc}%. 거의.",
        ],
        "ge71": [
            "품사형 {acc}%. 시험장 OK.",
            "품사형 {acc}%. 통과.",
            "품사형 {acc}%. 끝.",
        ],
    },
    "vocab": {  # 어휘 (vocab 폴더)
        "le30": [
            "어휘 {acc}%. 빈출 단어부터 정복.",
            "어휘 {acc}%. 단어 포로수용소 가자.",
            "어휘 {acc}%. 외운 게 안 떠오르지?",
        ],
        "31_50": [
            "어휘 {acc}%. 콜로케이션 약하다.",
            "어휘 {acc}%. 혼동어휘에서 미끄러져.",
            "어휘 {acc}%. 단어 더 봐.",
        ],
        "51_70": [
            "어휘 {acc}%. 문맥은 잡는다.",
            "어휘 {acc}%. 빈출은 잡았어.",
            "어휘 {acc}%. 좋아.",
        ],
        "ge71": [
            "어휘 {acc}%. 이대로.",
            "어휘 {acc}%. 클린.",
            "어휘 {acc}%. 끝.",
        ],
    },
    "linker": {  # 연결어 (link 폴더)
        "le30": [
            "연결어 {acc}%. 접속사·전치사 구분 안 돼.",
            "연결어 {acc}%. however·but부터.",
            "연결어 {acc}%. 점·세미콜론 보는 연습.",
        ],
        "31_50": [
            "연결어 {acc}%. 둘 다 헷갈리지.",
            "연결어 {acc}%. 접속부사 약점.",
            "연결어 {acc}%. 한 끗.",
        ],
        "51_70": [
            "연결어 {acc}%. 이제 보인다.",
            "연결어 {acc}%. 좋아지고 있어.",
            "연결어 {acc}%. 거의.",
        ],
        "ge71": [
            "연결어 {acc}%. 통과.",
            "연결어 {acc}%. 클린.",
            "연결어 {acc}%. 끝.",
        ],
    },
}


# ═══════════════════════════════════════════════════════════════
# 🥷 HAE POOLS (P7 — 첫줄/주제/세부/추론/시간/글타입)
# ═══════════════════════════════════════════════════════════════

HAE_FIRST_LINE = {
    "le30": [
        "첫 줄 {acc}%. 거기 답 있었어.",
        "첫 줄 {acc}%. 첫 두 문장 다시 읽어.",
        "첫 줄 {acc}%. 핵심을 놓치고 있어.",
    ],
    "31_50": [
        "첫 줄 {acc}%. 절반은 잡았다.",
        "첫 줄 {acc}%. 한 끗.",
        "첫 줄 {acc}%. 도입부 더 천천히.",
    ],
    "51_70": [
        "첫 줄 {acc}%. 감 잡혔다.",
        "첫 줄 {acc}%. 좋아.",
        "첫 줄 {acc}%. 이제 보인다.",
    ],
    "ge71": [
        "첫 줄 {acc}%. 99% 거기 있다는 거 알았네.",
        "첫 줄 {acc}%. 클린.",
        "첫 줄 {acc}%. OK.",
    ],
}

HAE_MAIN_IDEA = {
    "le30": [
        "주제 {acc}%. 큰 그림을 못 보네.",
        "주제 {acc}%. 첫 줄·마지막 줄부터.",
        "주제 {acc}%. 세부에 매몰돼 있어.",
    ],
    "31_50": [
        "주제 {acc}%. 반은 맞아.",
        "주제 {acc}%. 거의 절반.",
        "주제 {acc}%. 패러프레이즈 약점.",
    ],
    "51_70": [
        "주제 {acc}%. 안목 생기고 있어.",
        "주제 {acc}%. 좋아.",
        "주제 {acc}%. 거의 다 왔다.",
    ],
    "ge71": [
        "주제 {acc}%. 거시적 시야 OK.",
        "주제 {acc}%. 통과.",
        "주제 {acc}%. 이대로.",
    ],
}

HAE_DETAIL = {
    "le30": [
        "세부정보 {acc}%. 본문에 다 있는데.",
        "세부정보 {acc}%. 키워드부터 찾아.",
        "세부정보 {acc}%. 자꾸 미끄러진다.",
    ],
    "31_50": [
        "세부정보 {acc}%. 절반.",
        "세부정보 {acc}%. 위치 추적 연습.",
        "세부정보 {acc}%. NOT 문제 약점.",
    ],
    "51_70": [
        "세부정보 {acc}%. 잡아내고 있어.",
        "세부정보 {acc}%. 좋아.",
        "세부정보 {acc}%. 거의.",
    ],
    "ge71": [
        "세부정보 {acc}%. 정확하다.",
        "세부정보 {acc}%. 클린.",
        "세부정보 {acc}%. OK.",
    ],
}

HAE_INFERENCE = {
    "le30": [
        "추론 {acc}%. 행간 안 읽혀?",
        "추론 {acc}%. 어렵지. 다시.",
        "추론 {acc}%. 단서 모아보는 연습.",
    ],
    "31_50": [
        "추론 {acc}%. 반은 맞아.",
        "추론 {acc}%. 한 끗.",
        "추론 {acc}%. imply·suggest 약점.",
    ],
    "51_70": [
        "추론 {acc}%. 깊이 보고 있어.",
        "추론 {acc}%. 좋아.",
        "추론 {acc}%. 거의.",
    ],
    "ge71": [
        "추론 {acc}%. 행간 잘 잡는다.",
        "추론 {acc}%. 굿.",
        "추론 {acc}%. OK.",
    ],
}


# ═══════════════════════════════════════════════════════════════
# 🎯 RENDER FUNCTIONS — 시그널 → 텍스트
# ═══════════════════════════════════════════════════════════════

def _pick(pool: List[str], data: Dict) -> str:
    """풀에서 랜덤 1개 선택 + data로 포맷팅."""
    if not pool:
        return ""
    template = random.choice(pool)
    try:
        return template.format(**data)
    except KeyError:
        return template


def _accuracy_tier(acc: float) -> str:
    """정답률 → 임계값 키."""
    if acc <= 30:
        return "le30"
    elif acc <= 50:
        return "31_50"
    elif acc <= 70:
        return "51_70"
    else:
        return "ge71"


def _streak_tier(days: int) -> str:
    if days <= 1:
        return "1"
    elif days <= 6:
        return "2_6"
    elif days <= 29:
        return "7_29"
    else:
        return "30plus"


def _absent_tier(days: int) -> str:
    if days == 1:
        return "1"
    elif days <= 3:
        return "2_3"
    else:
        return "4plus"


def _prison_tier(count: int) -> str:
    if count == 0:
        return "0"
    elif count <= 5:
        return "1_5"
    elif count <= 15:
        return "6_15"
    else:
        return "16plus"


def _time_tier(minutes: int) -> str:
    if minutes < 10:
        return "short"
    elif minutes < 30:
        return "normal"
    elif minutes < 60:
        return "focus"
    else:
        return "long"


def _hour_tier(hour: int, is_weekend: bool) -> str:
    if is_weekend:
        return "weekend"
    if hour < 6:
        return "dawn"
    elif hour < 9:
        return "morning"
    elif hour < 18:
        return "day"
    elif hour < 22:
        return "evening"
    else:
        return "night"


# ─────────────────────────────────────────────────────────────
# 메인 함수
# ─────────────────────────────────────────────────────────────

def render_message(signal: Dict) -> str:
    """
    시그널 → 실제 멘트 텍스트 1개 반환.

    PARAMS:
        signal: {
            "character": "skull"/"tori"/"hae",
            "key": "same_word_3plus"/"weak_p5_category"/...,
            "data": {...}
        }

    RETURNS:
        포맷팅된 멘트 텍스트
    """
    key = signal.get("key", "")
    data = signal.get("data", {})
    char = signal.get("character", "")

    # ─── 해골 멘트 ──────────────────────────────────────
    if char == "skull":

        if key == "same_word_3plus":
            count = data.get("count", 3)
            tier = "3plus" if count >= 3 else "2"
            return _pick(SKULL_REPEAT_WORD[tier], data)

        elif key == "prison_overflow":
            tier = _prison_tier(data.get("count", 0))
            return _pick(SKULL_PRISON[tier], data)

        elif key == "absent_4plus_days" or key == "absent_short":
            tier = _absent_tier(data.get("days", 1))
            return _pick(SKULL_ABSENT[tier], data)

        elif key == "trend_drop_10pct":
            return _pick(SKULL_TREND["drop_10"], data)

        elif key == "trend_up":
            return _pick(SKULL_TREND["up"], data)

        elif key == "milestone_unlock":
            ms = str(data.get("milestone", "100"))
            if ms in SKULL_MILESTONE:
                return _pick(SKULL_MILESTONE[ms], data)
            return _pick(SKULL_MILESTONE["100"], data)

        elif key == "streak_milestone":
            tier = _streak_tier(data.get("days", 1))
            return _pick(SKULL_STREAK[tier], data)

        elif key == "today_time":
            tier = _time_tier(data.get("minutes", 0))
            return _pick(SKULL_TODAY_TIME[tier], data)

        elif key == "time_of_day":
            tier = _hour_tier(
                data.get("hour", 12),
                data.get("is_weekend", False)
            )
            return _pick(SKULL_TIME_OF_DAY[tier], data)

    # ─── TORI 멘트 ──────────────────────────────────────
    elif char == "tori":

        if key == "weak_p5_category":
            group = data.get("group", "")
            acc = data.get("accuracy", 50)
            tier = _accuracy_tier(acc)
            if group in TORI_POOLS and tier in TORI_POOLS[group]:
                return _pick(TORI_POOLS[group][tier], {"acc": acc})
            return f"P5 {acc}%. 더 가."

    # ─── HAE 멘트 ───────────────────────────────────────
    elif char == "hae":

        acc = data.get("accuracy", 50)
        tier = _accuracy_tier(acc)

        if key == "p7_first_line":
            return _pick(HAE_FIRST_LINE[tier], {"acc": acc})
        elif key == "p7_main_idea":
            return _pick(HAE_MAIN_IDEA[tier], {"acc": acc})
        elif key == "p7_detail":
            return _pick(HAE_DETAIL[tier], {"acc": acc})
        elif key == "p7_inference":
            return _pick(HAE_INFERENCE[tier], {"acc": acc})

    # ─── 폴백 ───────────────────────────────────────────
    return ""


def get_pool_size() -> Dict[str, int]:
    """전체 멘트 풀 크기 반환 (디버깅용)."""
    sizes = {"skull": 0, "tori": 0, "hae": 0}

    # 해골
    for pool in [SKULL_REPEAT_WORD, SKULL_PRISON, SKULL_STREAK, SKULL_ABSENT,
                 SKULL_TODAY_TIME, SKULL_TIME_OF_DAY, SKULL_TREND, SKULL_MILESTONE]:
        for tier_pool in pool.values():
            sizes["skull"] += len(tier_pool)

    # TORI
    for group_pools in TORI_POOLS.values():
        for tier_pool in group_pools.values():
            sizes["tori"] += len(tier_pool)

    # HAE
    for pool in [HAE_FIRST_LINE, HAE_MAIN_IDEA, HAE_DETAIL, HAE_INFERENCE]:
        for tier_pool in pool.values():
            sizes["hae"] += len(tier_pool)

    sizes["total"] = sizes["skull"] + sizes["tori"] + sizes["hae"]
    return sizes


# ─────────────────────────────────────────────────────────────
# 자가 점검
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("SnapQ inbody_messages 자가 점검")
    print("=" * 60)

    # 1. 풀 크기
    sizes = get_pool_size()
    print(f"\n[1] 멘트 풀 크기:")
    for k, v in sizes.items():
        print(f"    {k}: {v}개")

    # 2. 다양한 시그널 렌더링 테스트
    print(f"\n[2] 시그널 렌더링 테스트:")

    test_signals = [
        {"character": "skull", "key": "same_word_3plus",
         "data": {"word": "allocate", "count": 3}},
        {"character": "skull", "key": "same_word_3plus",
         "data": {"word": "implement", "count": 5}},
        {"character": "skull", "key": "prison_overflow",
         "data": {"count": 23}},
        {"character": "skull", "key": "prison_overflow",
         "data": {"count": 8}},
        {"character": "skull", "key": "absent_short",
         "data": {"days": 2}},
        {"character": "skull", "key": "streak_milestone",
         "data": {"days": 7}},
        {"character": "skull", "key": "today_time",
         "data": {"minutes": 47}},
        {"character": "skull", "key": "time_of_day",
         "data": {"hour": 1, "is_weekend": False}},
        {"character": "skull", "key": "milestone_unlock",
         "data": {"milestone": "100"}},
        {"character": "skull", "key": "trend_drop_10pct",
         "data": {"yesterday": 80, "today": 62}},
        {"character": "tori", "key": "weak_p5_category",
         "data": {"group": "passive_agreement", "category": "수동태", "accuracy": 17.0}},
        {"character": "tori", "key": "weak_p5_category",
         "data": {"group": "tense", "category": "시제", "accuracy": 47.0}},
        {"character": "tori", "key": "weak_p5_category",
         "data": {"group": "vocab", "category": "콜로케이션", "accuracy": 65.0}},
        {"character": "hae", "key": "p7_first_line",
         "data": {"accuracy": 25.0}},
        {"character": "hae", "key": "p7_inference",
         "data": {"accuracy": 80.0}},
    ]

    for sig in test_signals:
        text = render_message(sig)
        char = sig["character"]
        emoji = {"skull": "💀", "tori": "🐱", "hae": "🥷"}.get(char, "•")
        print(f"  {emoji} [{sig['key']:25s}] → {text}")

    # 3. 같은 시그널 5번 호출 → 다양성 검증
    print(f"\n[3] 같은 시그널 5번 (랜덤 다양성):")
    sig = {"character": "skull", "key": "prison_overflow", "data": {"count": 23}}
    seen = set()
    for _ in range(5):
        text = render_message(sig)
        seen.add(text)
        print(f"    → {text}")
    print(f"    유니크 개수: {len(seen)} / 5")

    print("\n" + "=" * 60)
    print("자가 점검 완료! ✅")
    print("=" * 60)
