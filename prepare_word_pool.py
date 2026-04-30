"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SCRIPT:   prepare_word_pool.py (v3)
ROLE:     word_family_db 카테고리화 — 880+개 살리기
DATE:     2026.04.30
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
v3 변경:
    Fallback 정규식 추가:
    - "(과거분사 형용사)" / "(현재분사 형용사)" / "(감정 형용사)"
    - "(현재분사)" / "(과거분사)" → adjective로 분류
    - 그 외 변형도 흡수

LOGIC (2단계):
    1차: 정확히 "(명사/동사원형/동사/형용사/부사)" 매치
    2차: 1차 실패 시 → 괄호 안에 "형용사/분사/동사/명사/부사" 키워드 찾기
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import json
import re
from pathlib import Path

BASE = Path(__file__).parent
INPUT_PATH = BASE / "data" / "word_family_db.json"
OUTPUT_PATH = BASE / "data" / "word_pool_categorized.json"

POS_MAP = {
    "명사":     "noun",
    "동사":     "verb",
    "동사원형": "verb",
    "형용사":   "adjective",
    "부사":     "adverb",
}

# 1차: 정확한 표기
POS_PATTERN_PRIMARY = re.compile(r"\((명사|동사원형|동사|형용사|부사)\)")

# 2차: 변형 표기 (분사/감정 형용사 등)
# "(과거분사 형용사)", "(현재분사 형용사)", "(감정 형용사)" → adjective
# "(현재분사)", "(과거분사)" → adjective
# "(타동사)", "(자동사)" → verb
POS_PATTERN_FALLBACK = re.compile(r"\(([^)]*?)(형용사|분사|동사|명사|부사)([^)]*?)\)")


def detect_pos(meaning: str) -> tuple:
    """
    한글 뜻에서 품사 감지.
    
    Returns:
        (pos_eng, matched_text) — 매치된 영문 품사와 매치된 텍스트
        못 찾으면 (None, None)
    """
    # 1차: 정확한 매치
    m = POS_PATTERN_PRIMARY.search(meaning)
    if m:
        pos_kor = m.group(1)
        return POS_MAP[pos_kor], m.group(0)
    
    # 2차: 변형 매치
    m = POS_PATTERN_FALLBACK.search(meaning)
    if m:
        keyword = m.group(2)  # 형용사/분사/동사/명사/부사 중 하나
        # 분사는 형용사로 분류
        if keyword == "분사":
            return "adjective", m.group(0)
        # 다른 키워드는 매핑 사용
        if keyword in POS_MAP:
            return POS_MAP[keyword], m.group(0)
    
    return None, None


def categorize_words(input_data: dict) -> dict:
    words = input_data.get("words", {})

    result = {
        "noun":      [],
        "verb":      [],
        "adjective": [],
        "adverb":    [],
    }

    skipped_no_pos = 0
    skipped_phrase = 0
    fallback_used = 0

    for word, meaning in words.items():
        if " " in word.strip():
            skipped_phrase += 1
            continue

        pos_eng, matched = detect_pos(meaning)
        if not pos_eng:
            skipped_no_pos += 1
            continue

        # fallback 사용 여부 추적
        if not POS_PATTERN_PRIMARY.search(meaning):
            fallback_used += 1

        # 한글 뜻에서 품사 표시 부분 제거
        clean_meaning = meaning.replace(matched, "").strip()
        clean_meaning = re.sub(r"[\s,]+$", "", clean_meaning)

        if not clean_meaning:
            continue

        result[pos_eng].append({
            "word": word.strip(),
            "meaning": clean_meaning,
        })

    for pos_eng in result:
        result[pos_eng].sort(key=lambda x: x["word"].lower())

    result["_summary"] = {
        "total_input":       len(words),
        "noun":              len(result["noun"]),
        "verb":              len(result["verb"]),
        "adjective":         len(result["adjective"]),
        "adverb":            len(result["adverb"]),
        "categorized_total": (len(result["noun"]) + len(result["verb"]) +
                              len(result["adjective"]) + len(result["adverb"])),
        "skipped_no_pos":    skipped_no_pos,
        "skipped_phrase":    skipped_phrase,
        "fallback_used":     fallback_used,
    }

    return result


def main():
    print("=" * 60)
    print("word_family_db 카테고리화 (v3 — 880+개 살리기)")
    print("=" * 60)

    if not INPUT_PATH.exists():
        print(f"❌ 입력 파일 없음: {INPUT_PATH}")
        return False

    print(f"\n[1] 입력: {INPUT_PATH}")
    input_data = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    total_input = len(input_data.get("words", {}))
    print(f"    총 항목: {total_input}개")

    print(f"\n[2] 카테고리화 처리...")
    result = categorize_words(input_data)

    print(f"\n[3] 결과:")
    s = result["_summary"]
    print(f"    📦 명사    (noun):      {s['noun']:4d}개")
    print(f"    🔥 동사    (verb):      {s['verb']:4d}개")
    print(f"    💎 형용사  (adjective): {s['adjective']:4d}개")
    print(f"    ⚡ 부사    (adverb):    {s['adverb']:4d}개")
    print(f"    ─────────────────────────────────")
    print(f"    ✅ 카테고리화 합계:      {s['categorized_total']:4d}개")
    print(f"    🔄 fallback 사용:       {s['fallback_used']:4d}개 (분사 형용사 등)")
    print(f"    ⚠️  여전히 제외:         {s['skipped_no_pos']:4d}개")
    print(f"    ⚠️  구문이라 제외:       {s['skipped_phrase']:4d}개")

    print(f"\n[4] 샘플 (각 카테고리 첫 3개):")
    for pos in ["noun", "verb", "adjective", "adverb"]:
        print(f"\n   {pos}:")
        for item in result[pos][:3]:
            print(f"      {item['word']:20s} → {item['meaning']}")

    print(f"\n[5] 저장...")
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    sz = OUTPUT_PATH.stat().st_size
    print(f"    {OUTPUT_PATH}")
    print(f"    {sz} bytes ({sz/1024:.1f} KB)")

    print("\n" + "=" * 60)
    print("✅ v3 완료!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    main()
