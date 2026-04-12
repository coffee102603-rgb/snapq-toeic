"""SnapQ TOEIC 플랫폼 전용 어휘 데이터베이스.

Firepower + Decrypt Op JSON에서 추출한 6,600+ 표현을 통합 관리.
포로사령부(03_POW_HQ.py)에서 단어 뜻 조회, 패밀리 조회에 사용.

API:
    lookup(word) -> dict | None       # {"kr": "한국어 뜻"} 반환
    get_family(word) -> dict          # {"V": [...], "N": [...], ...} 반환
    find_words_in_sentence(sent) -> list  # 문장에서 DB 단어 찾기
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Optional

# ═══ DB 로드 ═══
_DB_PATH = Path(__file__).parent / "data" / "word_family_db.json"
_WORDS: dict[str, str] = {}    # word -> meaning
_PHRASES: dict[str, str] = {}  # phrase -> meaning

try:
    with open(_DB_PATH, "r", encoding="utf-8") as _f:
        _raw = json.load(_f)
        _WORDS = _raw.get("words", {})
        _PHRASES = _raw.get("phrases", {})
except Exception:
    pass

# ═══ 인덱스 구축 ═══
WORD_INDEX: set[str] = set(_WORDS.keys())

# 접미사 기반 품사 분류 (간이)
_POS_SUFFIXES = {
    "V":   ["ate", "ize", "ise", "ify", "en"],
    "N":   ["tion", "sion", "ment", "ness", "ity", "ance", "ence", "ure", "ism", "ist", "ant", "ent", "er", "or", "al"],
    "ADJ": ["ive", "ous", "ful", "less", "able", "ible", "ent", "ant", "ic", "al"],
    "ADV": ["ly"],
}

# FAMILY_DB: 접미사 기반 패밀리 그룹 자동 생성
FAMILY_DB: dict[str, dict] = {}

def _guess_pos(word: str) -> str:
    """접미사 기반 품사 추정."""
    w = word.lower()
    if w.endswith("ly") and len(w) > 4:
        return "ADV"
    for pos, suffixes in _POS_SUFFIXES.items():
        for sfx in suffixes:
            if w.endswith(sfx) and len(w) > len(sfx) + 2:
                return pos
    return "N"  # 기본값

def _stem(word: str) -> str:
    """간이 어간 추출 (패밀리 그룹핑용)."""
    w = word.lower()
    for sfx in ["ation", "tion", "sion", "ment", "ness", "ity", "ance", "ence",
                 "ive", "ous", "ful", "less", "able", "ible", "ize", "ise",
                 "ify", "ate", "ing", "ed", "er", "or", "ly", "al", "en"]:
        if w.endswith(sfx) and len(w) > len(sfx) + 3:
            return w[:-len(sfx)]
    return w

# 패밀리 그룹 빌드
_stem_groups: dict[str, list[tuple[str, str, str]]] = {}
for _w, _m in _WORDS.items():
    _s = _stem(_w)
    _p = _guess_pos(_w)
    if _s not in _stem_groups:
        _stem_groups[_s] = []
    _stem_groups[_s].append((_w, _m, _p))

for _s, _members in _stem_groups.items():
    if len(_members) >= 2:
        family: dict[str, list] = {}
        for _w, _m, _p in _members:
            if _p not in family:
                family[_p] = []
            # meaning에서 괄호 안 품사 정보 제거하여 간결하게
            _kr = re.sub(r'\s*\([^)]*\)\s*$', '', _m).strip()
            family[_p].append((_w, _kr))
        for _w, _m, _p in _members:
            FAMILY_DB[_w] = family


# ═══ Public API ═══

def lookup(word: str) -> Optional[dict]:
    """단어의 한국어 뜻 조회.

    Args:
        word: 영어 단어
    Returns:
        {"kr": "한국어 뜻"} 또는 None
    """
    if not word:
        return None
    key = word.strip().lower()
    meaning = _WORDS.get(key)
    if meaning:
        return {"kr": meaning}
    # 대소문자 변형 시도
    for k, v in [(_WORDS.get(key.capitalize()), key.capitalize()),
                 (_WORDS.get(key.upper()), key.upper())]:
        if k:
            return {"kr": k}
    return None


def get_family(word: str) -> dict:
    """단어 패밀리 반환 (품사별 그룹).

    Args:
        word: 영어 단어
    Returns:
        {"V": [("implement", "시행하다"), ...], "N": [...], ...}
    """
    if not word:
        return {}
    key = word.strip().lower()
    return FAMILY_DB.get(key, {})


def find_words_in_sentence(sentence: str) -> list[str]:
    """문장에서 DB에 등록된 단어들을 찾아 반환.

    Args:
        sentence: 영어 문장
    Returns:
        DB에 존재하는 단어 리스트
    """
    if not sentence:
        return []
    tokens = re.findall(r"[a-zA-Z]+", sentence)
    found = []
    for t in tokens:
        if t.lower() in WORD_INDEX and len(t) >= 3:
            found.append(t.lower())
    return list(dict.fromkeys(found))  # 순서 유지 중복 제거
