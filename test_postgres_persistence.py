#!/usr/bin/env python3
"""
Критические пользовательские сценарии с сохранением в PostgreSQL.

Запуск (требуется реальная БД):
    DATABASE_URL=postgresql://user:pass@host:5432/dbname \
        python3 test_postgres_persistence.py

Проверяет, что данные действительно сохраняются в PostgreSQL и переживают
«редеплой» (новый экземпляр HypothesisManager загружает их из БД).

Без DATABASE_URL тест пропускается и завершается с кодом 0.
"""

import os
import sys

from product_hypothesis_assistant import (
    HypothesisManager,
    Evidence,
    EvidenceType,
    SurveyQuestion,
    RealWorldOutcome,
)

DB_URL = (os.environ.get("DATABASE_URL") or os.environ.get("POSTGRES_URL") or "").strip()


def _cleanup(ids):
    """Удаляет тестовые гипотезы из БД, чтобы не засорять таблицу."""
    if not ids:
        return
    try:
        import psycopg2

        conn = psycopg2.connect(
            HypothesisManager._normalize_postgres_url(DB_URL), sslmode="disable"
        )
        try:
            with conn, conn.cursor() as cur:
                cur.execute("DELETE FROM hypotheses WHERE id::text = ANY(%s)", (list(ids),))
        finally:
            conn.close()
    except Exception as e:
        print(f"⚠️ Не удалось очистить тестовые данные: {e}")


def main() -> int:
    if not DB_URL:
        print("⚠️ DATABASE_URL не задан — пропуск теста PostgreSQL (требуется реальная БД).")
        return 0

    created_ids = []
    passed = 0
    total = 4

    try:
        # ── Сценарий 1: полный жизненный цикл гипотезы ─────────────────────
        print("=" * 70)
        print("СЦЕНАРИЙ 1: Создание → доказательства → опрос → валидация → исход")
        print("=" * 70)
        m1 = HypothesisManager()
        hyp = m1.create_hypothesis(
            title="Тёмный режим (PostgreSQL)",
            description="Добавить тёмный режим в приложение",
            problem_statement="Eye strain at night",
            target_users="mobile users",
            expected_outcome="+15% retention",
        )
        created_ids.append(hyp.id)

        ev = Evidence(
            evidence_type=EvidenceType.USER_FEEDBACK,
            title="Опрос 100 пользователей",
            description="Большинство просили тёмный режим",
            source="in-app survey",
            confidence=0.85,
            supports=True,
        )
        assert m1.add_evidence(hyp.id, ev), "не удалось добавить доказательство"

        q = SurveyQuestion(
            question="Насколько важен тёмный режим? (1-10)",
            question_type="rating",
            reasoning="Оценка спроса",
        )
        assert m1.add_survey_question(hyp.id, q), "не удалось добавить вопрос опроса"

        ok, score = m1.validate_hypothesis(hyp.id)
        assert ok and score is not None, "валидация не выполнена"

        outcome = RealWorldOutcome(
            was_successful=True,
            actual_impact="Retention выросла на 12%",
            lessons_learned="Пользователи ценят ночной режим",
        )
        assert m1.record_outcome(hyp.id, outcome), "не удалось записать исход"
        passed += 1
        print("   ✓ гипотеза создана и сохранена в PostgreSQL")

        # ── Сценарий 2: «редеплой» — новый экземпляр менеджера ────────────
        print("\n" + "=" * 70)
        print("СЦЕНАРИЙ 2: Имитация редеплоя (новый HypothesisManager)")
        print("=" * 70)
        m2 = HypothesisManager()
        restored = m2.get_hypothesis(hyp.id)
        assert restored is not None, "гипотеза не загрузилась из PostgreSQL после редеплоя"
        assert restored.title == hyp.title
        assert len(restored.evidence) == 1
        assert restored.evidence[0].title == ev.title
        assert len(restored.survey_questions) == 1
        assert restored.score is not None
        assert restored.score.overall_score == score.overall_score
        assert restored.outcome is not None
        assert restored.outcome.was_successful is True
        passed += 1
        print("   ✓ данные полностью восстановлены из PostgreSQL")

        # ── Сценарий 3: несколько гипотез + анализ корреляции ─────────────
        print("\n" + "=" * 70)
        print("СЦЕНАРИЙ 3: Несколько гипотез + анализ корреляции")
        print("=" * 70)
        hyp2 = m2.create_hypothesis(
            title="Виджет курсов валют",
            description="Виджет на главной",
            problem_statement="Users need FX rates",
            target_users="traders",
            expected_outcome="+engagement",
        )
        created_ids.append(hyp2.id)
        ev2 = Evidence(
            evidence_type=EvidenceType.MARKET_RESEARCH,
            title="Benchmark конкурентов",
            description="У конкурентов есть виджет",
            source="analysis",
            confidence=0.6,
            supports=True,
        )
        assert m2.add_evidence(hyp2.id, ev2)
        assert m2.validate_hypothesis(hyp2.id)[0]
        assert m2.record_outcome(
            hyp2.id,
            RealWorldOutcome(was_successful=False, actual_impact="no effect"),
        )

        m3 = HypothesisManager()
        all_h = m3.list_hypotheses()
        assert any(h.id == hyp.id for h in all_h), "первая гипотеза пропала"
        assert any(h.id == hyp2.id for h in all_h), "вторая гипотеза пропала"

        analysis = m3.get_correlation_analysis()
        assert analysis.get("total_completed") == 2, f"ожидалось 2, получено {analysis.get('total_completed')}"
        assert len(analysis.get("data", [])) == 2, "корреляция должна вернуть 2 завершённые гипотезы"
        passed += 1
        print("   ✓ обе гипотезы сохранены, анализ корреляции работает")

        # ── Сценарий 4: экспорт гипотезы ───────────────────────────────────
        print("\n" + "=" * 70)
        print("СЦЕНАРИЙ 4: Экспорт гипотезы")
        print("=" * 70)
        exported = m3.export_hypothesis(hyp.id)
        assert exported is not None and exported["id"] == hyp.id
        assert exported["evidence_count"] == 1
        assert exported["outcome"]["was_successful"] is True
        passed += 1
        print("   ✓ экспорт корректен")

    except AssertionError as e:
        print(f"\n❌ Сценарий не пройден: {e}")
        return 1
    except Exception as e:
        import traceback

        traceback.print_exc()
        print(f"\n❌ Ошибка: {e}")
        return 1
    finally:
        _cleanup(created_ids)

    print("\n" + "=" * 70)
    print(f"ИТОГО: {passed}/{total} сценариев пройдено — сохранение в PostgreSQL работает ✅")
    print("=" * 70)
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())

