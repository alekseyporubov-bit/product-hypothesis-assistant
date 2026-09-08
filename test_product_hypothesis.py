"""
Тесты для Product Hypothesis Assistant
Демонстрация основных функций системы
"""

import json
from product_hypothesis_assistant import (
    HypothesisManager, Evidence, EvidenceType, HypothesisScore,
    SurveyQuestion, RealWorldOutcome
)


def test_create_and_score_hypothesis():
    """Тест: создание гипотезы, добавление доказательств, скоринг"""
    print("\n" + "="*70)
    print("ТЕСТ 1: Создание гипотезы и скоринг")
    print("="*70 + "\n")
    
    manager = HypothesisManager()
    
    # 1. Создаём гипотезу
    hypothesis = manager.create_hypothesis(
        title="Тёмный режим в приложении",
        description="Добавить поддержку тёмного режима для мобильного приложения",
        problem_statement="Пользователи жалуются на усталость глаз в тёмное время",
        target_users="Активные пользователи приложения (18-45 лет)",
        expected_outcome="Увеличение времени использования вечером на 15%"
    )
    print(f"✓ Гипотеза создана: {hypothesis.title}")
    print(f"  ID: {hypothesis.id}\n")
    
    # 2. Добавляем доказательства
    print("Добавляем доказательства:\n")
    
    evidence_list = [
        Evidence(
            evidence_type=EvidenceType.USER_FEEDBACK,
            title="Запросы в поддержку",
            description="50+ запросов в месяц о тёмном режиме",
            source="Helpdesk система",
            confidence=0.9,
            supports=True
        ),
        Evidence(
            evidence_type=EvidenceType.MARKET_RESEARCH,
            title="Исследование конкурентов",
            description="Все топ-приложения имеют тёмный режим",
            source="App Store анализ",
            confidence=0.95,
            supports=True
        ),
        Evidence(
            evidence_type=EvidenceType.ANALYTICS,
            title="Статистика использования",
            description="60% использования приложения происходит после 18:00",
            source="Google Analytics",
            confidence=0.85,
            supports=True
        ),
        Evidence(
            evidence_type=EvidenceType.COMPETITOR_ANALYSIS,
            title="Преимущество конкурентов",
            description="Конкуренты получили +20% активных пользователей после добавления тёмного режима",
            source="Appfigures",
            confidence=0.8,
            supports=True
        ),
        Evidence(
            evidence_type=EvidenceType.EXPERT_OPINION,
            title="Мнение дизайнера",
            description="Тёмный режим соответствует нашей стратегии дизайна",
            source="Интервью с lead designer",
            confidence=0.75,
            supports=True
        ),
    ]
    
    for i, ev in enumerate(evidence_list, 1):
        manager.add_evidence(hypothesis.id, ev)
        print(f"  {i}. [{ev.evidence_type.value}] {ev.title}")
    
    print(f"\n✓ Добавлено {len(evidence_list)} доказательств\n")
    
    # 3. Валидируем и получаем score
    print("Вычисляем score...\n")
    success, score = manager.validate_hypothesis(hypothesis.id)
    
    if success and score:
        print("─" * 70)
        print(f"ИТОГОВЫЙ SCORE: {score.overall_score:.1f}/100")
        print(f"Уровень уверенности: {score.confidence_level.upper()}")
        print(f"Рекомендация: {score.recommendation.upper()}")
        print("─" * 70)
        print(f"\nПолнота данных: {score.data_completeness*100:.0f}%")
        print(f"Поддерживающих доказательств: {score.supporting_evidence_count}")
        print(f"Противоречащих доказательств: {score.contradicting_evidence_count}")
        print(f"\nСтатус гипотезы: {hypothesis.status.value}")
    
    return hypothesis.id


def test_correlation_analysis():
    """Тест: анализ корреляции score ↔ реальный результат"""
    print("\n" + "="*70)
    print("ТЕСТ 2: Анализ корреляции (Цель 3 ТЗ)")
    print("="*70 + "\n")
    
    manager = HypothesisManager()
    
    # Сценарий 1: Гипотеза с высоким score и успешным результатом
    h1 = manager.create_hypothesis(
        title="Фича A - Высокий score + Успех",
        description="Фича с высокой уверенностью",
        problem_statement="Проблема A",
        target_users="Пользователи A",
        expected_outcome="Результат A"
    )
    
    for _ in range(5):
        manager.add_evidence(h1.id, Evidence(
            evidence_type=EvidenceType.USER_FEEDBACK,
            title="Отзыв",
            description="Положительный отзыв",
            source="Users",
            confidence=0.9,
            supports=True
        ))
    
    manager.validate_hypothesis(h1.id)
    outcome1 = RealWorldOutcome(
        was_successful=True,
        actual_impact="Увеличение метрики на 15%",
        lessons_learned="Фича была хорошо принята пользователями"
    )
    manager.record_outcome(h1.id, outcome1)
    
    # Сценарий 2: Гипотеза с низким score и неудачным результатом
    h2 = manager.create_hypothesis(
        title="Фича B - Низкий score + Неудача",
        description="Фича с низкой уверенностью",
        problem_statement="Проблема B",
        target_users="Пользователи B",
        expected_outcome="Результат B"
    )
    
    manager.add_evidence(h2.id, Evidence(
        evidence_type=EvidenceType.USER_FEEDBACK,
        title="Отзыв",
        description="Отрицательный отзыв",
        source="Users",
        confidence=0.7,
        supports=False
    ))
    
    manager.validate_hypothesis(h2.id)
    outcome2 = RealWorldOutcome(
        was_successful=False,
        actual_impact="Нет заметного эффекта",
        lessons_learned="Фича не была востребована пользователями"
    )
    manager.record_outcome(h2.id, outcome2)
    
    # Сценарий 3: Гипотеза с высоким score но неудачным результатом
    h3 = manager.create_hypothesis(
        title="Фича C - Высокий score + Неудача",
        description="Ложный позитив",
        problem_statement="Проблема C",
        target_users="Пользователи C",
        expected_outcome="Результат C"
    )
    
    for _ in range(4):
        manager.add_evidence(h3.id, Evidence(
            evidence_type=EvidenceType.MARKET_RESEARCH,
            title="Исследование",
            description="Позитивное исследование",
            source="Research",
            confidence=0.85,
            supports=True
        ))
    
    manager.validate_hypothesis(h3.id)
    outcome3 = RealWorldOutcome(
        was_successful=False,
        actual_impact="Пользователи не интересовались фичей",
        lessons_learned="Исследование не отражало реальные потребности"
    )
    manager.record_outcome(h3.id, outcome3)
    
    # Получаем анализ корреляции
    print("Анализирую корреляцию между score и реальным результатом...\n")
    analysis = manager.get_correlation_analysis()
    
    print(json.dumps(analysis, indent=2, ensure_ascii=False))
    print()


def test_survey_generation():
    """Тест: генерация анкеты для опроса пользователей"""
    print("\n" + "="*70)
    print("ТЕСТ 3: Генерация шаблона анкеты")
    print("="*70 + "\n")
    
    manager = HypothesisManager()
    
    hypothesis = manager.create_hypothesis(
        title="Персональные рекомендации",
        description="Система AI для персональных рекомендаций контента",
        problem_statement="Пользователи не находят интересный контент",
        target_users="Активные потребители контента",
        expected_outcome="Увеличение engagement на 25%"
    )
    
    print(f"Гипотеза: {hypothesis.title}\n")
    
    questions = [
        SurveyQuestion(
            question="Сколько времени вы тратите на поиск интересного контента?",
            question_type="open",
            reasoning="Оценка затрат времени на текущий процесс"
        ),
        SurveyQuestion(
            question="Насколько актуальны предложения, которые вы получаете?",
            question_type="rating",
            reasoning="Прямая оценка качества рекомендаций"
        ),
        SurveyQuestion(
            question="Готовы ли вы использовать AI-рекомендации?",
            question_type="multiple_choice",
            options=["Да, явно", "Скорее да", "Не знаю", "Скорее нет", "Нет"],
            reasoning="Оценка спроса на AI-решение"
        ),
    ]
    
    for q in questions:
        manager.add_survey_question(hypothesis.id, q)
    
    print("Сгенерированные вопросы для опроса:\n")
    
    h = manager.get_hypothesis(hypothesis.id)
    for i, q in enumerate(h.survey_questions, 1):
        print(f"{i}. {q.question}")
        print(f"   Тип: {q.question_type}")
        if q.options:
            print(f"   Варианты ответов:")
            for opt in q.options:
                print(f"     - {opt}")
        print(f"   Почему важно: {q.reasoning}\n")


def test_export_hypothesis():
    """Тест: экспорт гипотезы в JSON"""
    print("\n" + "="*70)
    print("ТЕСТ 4: Экспорт гипотезы в JSON")
    print("="*70 + "\n")
    
    manager = HypothesisManager()
    
    hypothesis = manager.create_hypothesis(
        title="Уведомления в реальном времени",
        description="Система push-уведомлений для важных событий",
        problem_statement="Пользователи пропускают важные события",
        target_users="Все активные пользователи",
        expected_outcome="Увеличение retention на 10%"
    )
    
    # Добавляем доказательства
    for i in range(3):
        manager.add_evidence(hypothesis.id, Evidence(
            evidence_type=EvidenceType.USER_FEEDBACK,
            title=f"Отзыв {i+1}",
            description=f"Пользователь просит уведомления",
            source="Support tickets",
            confidence=0.8,
            supports=True
        ))
    
    manager.validate_hypothesis(hypothesis.id)
    
    # Экспортируем
    print("Экспортирую гипотезу в JSON:\n")
    data = manager.export_hypothesis(hypothesis.id)
    print(json.dumps(data, indent=2, ensure_ascii=False))


def run_all_tests():
    """Запускает все тесты"""
    print("\n" + "="*70)
    print("ДЕМОНСТРАЦИЯ PRODUCT HYPOTHESIS ASSISTANT")
    print("Все функции системы согласно ТЗ")
    print("="*70)
    
    try:
        test_create_and_score_hypothesis()
        test_survey_generation()
        test_export_hypothesis()
        test_correlation_analysis()
        
        print("\n" + "="*70)
        print("✓ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n✗ ОШИБКА: {e}\n")
        raise


if __name__ == "__main__":
    run_all_tests()
