#!/usr/bin/env python3
"""
Тест интеграции Research Finder в scoring engine
Проверяет что problem_severity теперь считается с учётом исследований из открытых источников
"""
import requests
import json
import time

BASE_URL = "http://localhost:5000"
API_URL = f"{BASE_URL}/api"

def test_research_integration():
    print("="*70)
    print("ТЕСТ: Интеграция поиска исследований в scoring engine")
    print("="*70)
    
    # 1. Создаём гипотезу о тёмном режиме
    print("\n1️⃣ Создаём гипотезу о тёмном режиме...")
    hypothesis_data = {
        "title": "Добавить тёмный режим",
        "description": "Внедрить тёмный режим в приложение",
        "problem_statement": "Eye strain from bright displays at night",
        "target_users": "mobile app users who use app in evening/night",
        "expected_outcome": "Increased retention and user satisfaction during night hours"
    }
    
    r = requests.post(f"{API_URL}/create-hypothesis", json=hypothesis_data)
    result = r.json()
    hyp_id = result['hypothesis_id']
    print(f"✅ Гипотеза создана: {hyp_id}")
    
    # 2. Добавляем доказательства от пользователя
    print("\n2️⃣ Добавляем доказательства от пользователя...")
    evidence_items = [
        {
            "hypothesis_id": hyp_id,
            "evidence_type": "USER_FEEDBACK",
            "title": "Пользователи жалуются на усталость глаз",
            "description": "Множество отзывов в Telegram чате о боли в глазах при использовании ночью",
            "source": "Telegram community feedback",
            "confidence": 0.85,
            "supports": True
        },
        {
            "hypothesis_id": hyp_id,
            "evidence_type": "MARKET_RESEARCH",
            "title": "Статистика ночного использования",
            "description": "Из аналитики: 35% активности происходит в 21:00-06:00",
            "source": "Internal analytics",
            "confidence": 0.9,
            "supports": True
        }
    ]
    
    for evidence in evidence_items:
        r = requests.post(f"{API_URL}/add-evidence", json=evidence)
        result = r.json()
        print(f"  ✓ {evidence['title']}")
    
    print(f"✅ Добавлено {len(evidence_items)} доказательств от пользователя")
    
    # 3. Валидируем гипотезу и получаем score
    # НА ЭТОМ ЭТАПЕ система должна:
    # - Взять пользовательские доказательства
    # - ПЛЮС автоматически поискать исследования в открытых источниках
    # - Скомбинировать оценки (40% user + 60% research)
    
    print("\n3️⃣ Валидируем гипотезу (система ищет исследования в открытых источниках)...")
    r = requests.post(f"{API_URL}/validate-hypothesis/{hyp_id}")
    result = r.json()
    
    if result.get('success'):
        score = result.get('score', {})
        print(f"✅ Score получен: {score.get('overall_score', 0):.1f}/100")
        print(f"   Рекомендация: {score.get('recommendation', 'N/A')}")
        print(f"   Уверенность: {score.get('confidence_level', 'N/A')}")
        
        # Выводим детальный разбор по факторам
        print("\n📊 Разбор по факторам:")
        for breakdown in score.get('breakdown', []):
            print(f"\n   {breakdown['factor'].upper()}:")
            print(f"   Score: {breakdown['score']:.1f}/10")
            print(f"   Обоснование: {breakdown['rationale']}")
            print(f"   Доказательства: {breakdown['evidence_count']}")
        
        # Проверяем что в problem_severity учитываются исследования
        problem_severity = next(
            (b for b in score.get('breakdown', []) if b['factor'] == 'problem_severity'),
            None
        )
        
        if problem_severity:
            rationale = problem_severity['rationale']
            has_research = "Исследования из открытых источников" in rationale
            has_user = "Пользовательские доказательства" in rationale
            
            print("\n✅ ПРОВЕРКА ИНТЕГРАЦИИ:")
            print(f"   {'✓' if has_user else '✗'} Учитываются пользовательские доказательства")
            print(f"   {'✓' if has_research else '✗'} Учитываются исследования из открытых источников")
            
            if has_research and has_user:
                print("\n🎉 УСПЕХ! Система правильно интегрирует открытые исследования в scoring!")
                return True
            else:
                print("\n❌ ПРОБЛЕМА: Не все источники доказательств учитываются")
                return False
    else:
        print(f"❌ Ошибка валидации: {result.get('error', 'Unknown error')}")
        return False

if __name__ == "__main__":
    # Ждём пока сервер запустится
    print("Ожидание запуска сервера...")
    time.sleep(2)
    
    success = test_research_integration()
    
    print("\n" + "="*70)
    if success:
        print("✅ ТЕСТ ПРОЙДЕН: Система использует открытые исследования!")
    else:
        print("❌ ТЕСТ НЕ ПРОЙДЕН: Проблема с интеграцией")
    print("="*70)
    
    exit(0 if success else 1)
