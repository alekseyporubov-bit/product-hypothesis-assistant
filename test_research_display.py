#!/usr/bin/env python3
"""
Тест отображения найденных исследований через API
Проверяет что пользователь может видеть список найденных исследований
"""
import requests
import json
import time

BASE_URL = "http://localhost:5000"
API_URL = f"{BASE_URL}/api"

def test_research_display():
    print("="*70)
    print("ТЕСТ: Отображение найденных исследований в API")
    print("="*70)
    
    # 1. Создаём гипотезу
    print("\n1️⃣ Создаём гипотезу...")
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
    
    # 2. Добавляем доказательства
    print("\n2️⃣ Добавляем доказательства...")
    evidence_items = [
        {
            "hypothesis_id": hyp_id,
            "evidence_type": "USER_FEEDBACK",
            "title": "Отзывы о боли в глазах",
            "description": "Множество жалоб в чате",
            "source": "Internal feedback",
            "confidence": 0.85,
            "supports": True
        },
        {
            "hypothesis_id": hyp_id,
            "evidence_type": "MARKET_RESEARCH",
            "title": "Статистика использования",
            "description": "35% активности ночью",
            "source": "Analytics",
            "confidence": 0.9,
            "supports": True
        }
    ]
    
    for evidence in evidence_items:
        r = requests.post(f"{API_URL}/add-evidence", json=evidence)
        print(f"  ✓ {evidence['title']}")
    
    print(f"✅ Добавлено {len(evidence_items)} доказательств")
    
    # 3. Валидируем гипотезу (при этом система ищет исследования)
    print("\n3️⃣ Валидируем гипотезу (система ищет исследования)...")
    r = requests.post(f"{API_URL}/validate-hypothesis/{hyp_id}")
    result = r.json()
    
    if result.get('success'):
        score = result.get('score', {})
        print(f"✅ Score получен: {score.get('overall_score', 0):.1f}/100")
        
        research_count = len(score.get('research_sources', []))
        print(f"   Найдено исследований: {research_count}")
    else:
        print(f"❌ Ошибка: {result.get('error')}")
        return False
    
    # 4. ГЛАВНОЕ: Получаем список найденных исследований через NEW API endpoint
    print("\n4️⃣ Получаем список найденных исследований...")
    r = requests.get(f"{API_URL}/research-sources/{hyp_id}")
    result = r.json()
    
    if result.get('success'):
        print(f"✅ Ответ получен")
        print(f"   Гипотеза: {result.get('hypothesis_title')}")
        print(f"   Проблема: {result.get('problem_statement')}")
        print(f"   Целевая аудитория: {result.get('target_users')}")
        print(f"   Найдено исследований: {result.get('research_count', 0)}")
        
        # Выводим каждое исследование
        research_sources = result.get('research_sources', [])
        if research_sources:
            print("\n📚 Найденные исследования:")
            for i, research in enumerate(research_sources, 1):
                print(f"\n   {i}. {research.get('title', 'N/A')}")
                print(f"      Авторы: {', '.join(research.get('authors', []))}")
                print(f"      Год: {research.get('year', 'N/A')}")
                print(f"      Источник: {research.get('source', 'N/A')}")
                print(f"      Релевантность: {research.get('relevance_score', 0):.2f}")
                print(f"      Аннотация: {research.get('abstract', 'N/A')[:100]}...")
                print(f"      Ссылка: {research.get('url', 'N/A')}")
            
            print("\n✅ УСПЕХ! Пользователь может видеть все найденные исследования!")
            return True
        else:
            print("\n⚠️ Исследования не найдены")
            return False
    else:
        print(f"❌ Ошибка API: {result.get('error')}")
        return False

if __name__ == "__main__":
    # Ждём пока сервер запустится
    print("Ожидание запуска сервера...")
    time.sleep(3)
    
    success = test_research_display()
    
    print("\n" + "="*70)
    if success:
        print("✅ ТЕСТ ПРОЙДЕН: Пользователь видит найденные исследования!")
        print("\nНовый endpoint: GET /api/research-sources/{hypothesis_id}")
        print("Возвращает:")
        print("  - Список всех найденных исследований")
        print("  - Информацию об авторах, годе, источнике")
        print("  - Оценку релевантности каждого исследования")
        print("  - Аннотацию и ссылку на исследование")
    else:
        print("❌ ТЕСТ НЕ ПРОЙДЕН")
    print("="*70)
    
    exit(0 if success else 1)
