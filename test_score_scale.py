"""
Регресс-тест шкалы Score (DL-001).

Проверяет, что итоговый score лежит в диапазоне 0-100 и что рекомендации
"proceed" / "investigate" достижимы, а не всегда "reject".

Red-доказательство (до исправления): тест test_well_supported_reaches_proceed
падал — даже при максимальном наборе подтверждающих доказательств score был
~9.36/100 и рекомендация "reject" (веса факторов суммируются в 1.0, а оценки
факторов 0-10, поэтому weighted_score получался 0-10 вместо 0-100).

Запуск:
    python3 test_score_scale.py
"""

import sys

from product_hypothesis_assistant import HypothesisManager, Evidence, EvidenceType

results = []


def check(name, cond, detail=""):
    results.append((name, bool(cond)))
    print(("PASS" if cond else "FAIL"), "-", name, ("| " + str(detail)[:160] if detail else ""))


def _manager():
    return HypothesisManager()


def _add_many(manager, hypothesis_id, per_type=5):
    for t in EvidenceType:
        for _ in range(per_type):
            manager.add_evidence(hypothesis_id, Evidence(
                evidence_type=t,
                title="ev",
                description="d",
                source="s",
                confidence=0.9,
                supports=True,
            ))


def test_well_supported_reaches_proceed():
    """Хорошо подтверждённая гипотеза -> score >= 70 и recommendation == 'proceed'."""
    m = _manager()
    h = m.create_hypothesis("T", "d", "p", "u", "e")
    _add_many(m, h.id, per_type=5)
    ok, score = m.validate_hypothesis(h.id)
    assert ok and score
    check(
        "хорошо подтверждённая гипотеза -> proceed (score >= 70)",
        score.overall_score >= 70 and score.recommendation == "proceed",
        "score=%.1f, rec=%s" % (score.overall_score, score.recommendation),
    )


def test_no_evidence_rejects():
    """Гипотеза без доказательств -> score < 50 и recommendation != 'proceed'."""
    m = _manager()
    h = m.create_hypothesis("T", "d", "p", "u", "e")
    ok, score = m.validate_hypothesis(h.id)
    assert ok and score
    check(
        "гипотеза без доказательств не рекомендует proceed",
        score.recommendation != "proceed" and score.overall_score < 50,
        "score=%.1f, rec=%s" % (score.overall_score, score.recommendation),
    )


def test_score_within_0_100():
    """Score всегда в диапазоне 0-100."""
    m = _manager()
    h = m.create_hypothesis("T", "d", "p", "u", "e")
    _add_many(m, h.id, per_type=2)
    ok, score = m.validate_hypothesis(h.id)
    assert ok and score
    check(
        "score в диапазоне 0-100",
        0 <= score.overall_score <= 100,
        "score=%.1f" % score.overall_score,
    )


def main():
    test_well_supported_reaches_proceed()
    test_no_evidence_rejects()
    test_score_within_0_100()
    print("---")
    passed = sum(1 for _, c in results if c)
    print("ИТОГО: %d/%d" % (passed, len(results)))
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
