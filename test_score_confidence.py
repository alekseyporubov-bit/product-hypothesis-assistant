"""
Регресс-тест формулы score с учётом confidence (DL-002).

Проверяет, что итоговый score:
1) учитывает confidence доказательств (надёжные источники дают больший вклад);
2) приближается к 100 при нескольких надёжных подтверждающих источниках
   и многих положительных доказательствах (recommendation = "proceed");
3) остаётся низким (< 50), когда большинство доказательств опровергает проблему.

Формула (DL-002):
    support_weight    = Σ confidence(поддерживающих доказательств)
    contradict_weight = Σ confidence(опровергающих доказательств)
    research_weight   = min(research_count, 5) × average_relevance
    total_support     = support_weight + research_weight
    agreement         = total_support / (total_support + contradict_weight)
    strength          = min(1.0, total_support / 8.0)
    overall_score     = 100 × agreement × strength

Red-доказательство (до исправления):
    - test_confidence_increases_score падал — score не зависел от confidence
      (факторные оценки считались по количеству доказательств);
    - test_reliable_sources_reach_high_score падал — 5 подтверждающих @0.9
      + 3 авто-исследования давали ~55.8/100 (investigate) вместо >=85.

Запуск:
    python3 test_score_confidence.py
"""

import sys

from product_hypothesis_assistant import HypothesisManager, Evidence, EvidenceType

results = []


def check(name, cond, detail=""):
    results.append((name, bool(cond)))
    print(("PASS" if cond else "FAIL"), "-", name,
          ("| " + str(detail)[:160] if detail else ""))


def _manager():
    return HypothesisManager()


def _add_supporting(manager, hypothesis_id, count, confidence):
    types = list(EvidenceType)
    for i in range(count):
        manager.add_evidence(hypothesis_id, Evidence(
            evidence_type=types[i % len(types)],
            title="ev%d" % i,
            description="d",
            source="s",
            confidence=confidence,
            supports=True,
        ))


def test_confidence_increases_score():
    """Одинаковое количество доказательств, но выше confidence -> выше score."""
    m_high = _manager()
    h_high = m_high.create_hypothesis("T", "d", "p", "u", "e")
    _add_supporting(m_high, h_high.id, count=4, confidence=0.9)

    m_low = _manager()
    h_low = m_low.create_hypothesis("T", "d", "p", "u", "e")
    _add_supporting(m_low, h_low.id, count=4, confidence=0.2)

    ok_high, score_high = m_high.validate_hypothesis(h_high.id)
    ok_low, score_low = m_low.validate_hypothesis(h_low.id)
    assert ok_high and score_high and ok_low and score_low

    check(
        "confidence влияет на score (0.9 > 0.2)",
        score_high.overall_score > score_low.overall_score,
        "high=%.1f, low=%.1f" % (score_high.overall_score, score_low.overall_score),
    )


def test_reliable_sources_reach_high_score():
    """Несколько надёжных источников + много положительных доказательств -> близко к 100."""
    m = _manager()
    h = m.create_hypothesis("T", "d", "p", "u", "e")
    _add_supporting(m, h.id, count=5, confidence=0.9)
    ok, score = m.validate_hypothesis(h.id)
    assert ok and score
    check(
        "несколько надёжных источников + много положительных -> score >= 85 и proceed",
        score.overall_score >= 85 and score.recommendation == "proceed",
        "score=%.1f, rec=%s" % (score.overall_score, score.recommendation),
    )


def test_contradicting_majority_gives_low_score():
    """Большинство доказательств опровергают проблему -> низкий score (< 50)."""
    m = _manager()
    h = m.create_hypothesis("T", "d", "p", "u", "e")
    m.add_evidence(h.id, Evidence(
        evidence_type=EvidenceType.USER_FEEDBACK,
        title="support", source="s", confidence=0.8, supports=True,
    ))
    for i in range(6):
        m.add_evidence(h.id, Evidence(
            evidence_type=EvidenceType.USER_FEEDBACK,
            title="contradict%d" % i, source="s",
            confidence=0.8, supports=False,
        ))
    ok, score = m.validate_hypothesis(h.id)
    assert ok and score
    check(
        "большинство опровергающих доказательств -> score < 50 и reject",
        score.overall_score < 50 and score.recommendation == "reject",
        "score=%.1f, rec=%s" % (score.overall_score, score.recommendation),
    )


def main():
    test_confidence_increases_score()
    test_reliable_sources_reach_high_score()
    test_contradicting_majority_gives_low_score()
    print("---")
    passed = sum(1 for _, c in results if c)
    print("ИТОГО: %d/%d" % (passed, len(results)))
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
