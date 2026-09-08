#!/usr/bin/env python3
"""Тестирование гипотезы о красной кнопке оплаты"""

import requests
import json

BASE_URL = "http://localhost:5000/api"

print("=" * 80)
print("🔌 MCP HYPOTHESIS SERVER - ТЕСТ")
print("=" * 80)
print()

hypothesis_data = {
    "title": "Красная кнопка оплаты увеличит конверсию",
    "problem_statement": "Текущая серая кнопка оплаты имеет низкую кликаемость. Красный цвет привлекает внимание.",
    "description": "Тестирование влияния цвета кнопки оплаты на конверсию",
    "target_users": "Все пользователи при оформлении покупки",
    "expected_outcome": "Увеличение конверсии на 15-20%"
}

try:
    print("1️⃣ Создание гипотезы...")
    resp = requests.post(f"{BASE_URL}/create-hypothesis", json=hypothesis_data, timeout=10)
    result = resp.json()
    hypothesis_id = result.get("hypothesis_id")
    print(f"✅ Гипотеза создана: {hypothesis_id}")
    print(f"   Сообщение: {result.get('message')}")
    print()
    
    print("2️⃣ Добавление доказательств...")
    
    evidence_list = [
        {
            "evidence_type": "MARKET_RESEARCH",
            "title": "Исследование Nielsen Norman",
            "description": "Красный цвет увеличивает внимание в 2.3 раза",
            "source": "Nielsen Norman Group",
            "confidence": 0.92,
            "supports": True
        },
        {
            "evidence_type": "COMPETITIVE_ANALYSIS",
            "title": "Анализ конкурентов",
            "description": "Amazon, Alibaba используют красные кнопки оплаты",
            "source": "Competitive analysis",
            "confidence": 0.88,
            "supports": True
        },
        {
            "evidence_type": "ANALYTICS",
            "title": "Текущая аналитика",
            "description": "CTR красных элементов 5.8% vs серых 3.2%",
            "source": "Google Analytics",
            "confidence": 0.95,
            "supports": True
        }
    ]
    
    for evidence in evidence_list:
        evidence_data = {"hypothesis_id": hypothesis_id, **evidence}
        resp = requests.post(f"{BASE_URL}/add-evidence", json=evidence_data, timeout=10)
        if resp.status_code == 200:
            print(f"   ✅ {evidence['title']}")
        else:
            print(f"   ⚠️ Ошибка при добавлении")
    print()
    
    print("3️⃣ Валидирование гипотезы...")
    resp = requests.post(f"{BASE_URL}/validate-hypothesis/{hypothesis_id}", json={}, timeout=10)
    score_data = resp.json()
    
    if "score" in score_data:
        score = score_data["score"]
        print(f"✅ Score вычислен!")
        print(f"   📊 Score: {score.get('score', 'N/A')}/100")
        print(f"   🎯 Рекомендация: {score.get('recommendation', 'N/A').upper()}")
        print(f"   💪 Уверенность: {score.get('confidence', 'N/A')}")
        if "reasoning" in score:
            print(f"   📝 Обоснование: {score.get('reasoning')[:150]}...")
    else:
        print(f"✅ Ответ получен:")
        print(json.dumps(score_data, ensure_ascii=False, indent=2)[:500])
    print()
    
    print("4️⃣ Получение научных исследований...")
    resp = requests.get(f"{BASE_URL}/research-sources/{hypothesis_id}", timeout=10)
    research = resp.json()
    sources = research.get("sources", [])
    print(f"✅ Найдено исследований: {len(sources)}")
    
    if sources:
        print("   📚 Примеры:")
        for source in sources[:2]:
            print(f"      • {source.get('title', 'N/A')[:60]}")
            print(f"        {source.get('authors', 'N/A')[:50]}")
    print()
    
    print("=" * 80)
    print("✅ ГИПОТЕЗА УСПЕШНО ОБРАБОТАНА")
    print("=" * 80)
    print()
    print(f"📌 Hypothesis ID: {hypothesis_id}")
    print(f"📌 Score: {score.get('score')}/100 (Рекомендация: {score.get('recommendation')})")
    print(f"📌 Доказательств добавлено: {len(evidence_list)}")
    print(f"📌 Исследований найдено: {len(sources)}")
    print()

except requests.exceptions.ConnectionError:
    print("❌ Ошибка: Flask приложение не запущено!")
    print()
    print("Решение:")
    print("  python3 app.py")
except Exception as e:
    print(f"❌ Ошибка: {str(e)}")
