#!/usr/bin/env python3
"""Полный тест гипотезы о красной кнопке"""

import requests
import json

BASE = "http://localhost:5000/api"

print("=" * 90)
print("🔴 ГИПОТЕЗА: КРАСНАЯ КНОПКА ОПЛАТЫ УВЕЛИЧИТ КОНВЕРСИЮ")
print("=" * 90)
print()

hyp_data = {
    "title": "Красная кнопка оплаты увеличит конверсию на 15-20%",
    "problem_statement": "Серая кнопка неактивна. Красный = действие и срочность",
    "description": "Изменение цвета кнопки оплаты с серого на красный",
    "target_users": "Все пользователи при оформлении заказа",
    "expected_outcome": "Увеличение конверсии на 15-20%"
}

try:
    # 1. Создать
    print("1️⃣ СОЗДАНИЕ ГИПОТЕЗЫ")
    resp = requests.post(f"{BASE}/create-hypothesis", json=hyp_data, timeout=10)
    hid = resp.json().get("hypothesis_id")
    print(f"✅ ID: {hid}")
    print()
    
    # 2. Добавить доказательства
    print("2️⃣ ДОБАВЛЕНИЕ ДОКАЗАТЕЛЬСТВ")
    
    evidence = [
        ("MARKET_RESEARCH", "Red increases urgency", "Harvard BizReview: красный +34% срочность", 0.95),
        ("COMPETITIVE_ANALYSIS", "Top e-commerce use red", "Amazon, eBay, Taobao используют красное", 0.90),
        ("ANALYTICS", "Our data supports it", "Красные элементы CTR 6.2% vs серые 2.8%", 0.98),
        ("USER_FEEDBACK", "User survey feedback", "23/40 пользователей: красное более заметно", 0.85),
        ("MARKET_RESEARCH", "A/B test meta-analysis", "156 тестов: красное +14.2% конверсия", 0.92),
    ]
    
    for etype, title, desc, conf in evidence:
        data = {
            "hypothesis_id": hid,
            "evidence_type": etype,
            "title": title,
            "description": desc,
            "source": "Various sources",
            "confidence": conf,
            "supports": True
        }
        resp = requests.post(f"{BASE}/add-evidence", json=data, timeout=10)
        if resp.status_code == 200:
            print(f"   ✅ {title}")
    print()
    
    # 3. Валидировать
    print("3️⃣ ВАЛИДИРОВАНИЕ И РАСЧЕТ SCORE")
    resp = requests.post(f"{BASE}/validate-hypothesis/{hid}", json={}, timeout=10)
    val = resp.json()
    
    if "score" in val:
        sc = val["score"]
        print(f"✅ Score: {sc.get('score', '?')}/100")
        print(f"✅ Рекомендация: {sc.get('recommendation', '?').upper()}")
        print(f"✅ Уверенность: {sc.get('confidence', '?')}")
        if "reasoning" in sc and sc["reasoning"]:
            print(f"✅ Причина: {sc['reasoning'][:100]}...")
    print()
    
    # 4. Информация
    print("4️⃣ ИНФОРМАЦИЯ О ГИПОТЕЗЕ")
    resp = requests.get(f"{BASE}/get-hypothesis/{hid}", timeout=10)
    hyp = resp.json().get("hypothesis", {})
    print(f"✅ Статус: {hyp.get('status', '?')}")
    print(f"✅ Доказательств: {len(hyp.get('evidence', []))}")
    print()
    
    # 5. Исследования
    print("5️⃣ НАУЧНЫЕ ИССЛЕДОВАНИЯ")
    resp = requests.get(f"{BASE}/research-sources/{hid}", timeout=10)
    sources = resp.json().get("sources", [])
    print(f"✅ Найдено: {len(sources)} исследований")
    if sources:
        print("   Примеры:")
        for s in sources[:2]:
            print(f"   • {s.get('title', '?')[:60]}")
    print()
    
    # Итого
    print("=" * 90)
    print("✅ ГИПОТЕЗА УСПЕШНО ПРОВЕРЕНА ЧЕРЕЗ MCP HYPOTHESIS SERVER")
    print("=" * 90)
    print()
    print(f"Гипотеза ID: {hid}")
    print(f"Score: {sc.get('score', '?')}/100")
    print(f"Рекомендация: {sc.get('recommendation', '?').upper()}")
    print(f"Доказательств: {len(evidence)}")
    print(f"Исследований найдено: {len(sources)}")
    print()
    print("🎬 Следующие шаги:")
    if sc.get('recommendation', '').lower() == 'proceed':
        print("  ✅ Провести A/B тест с красной кнопкой")
        print("  ✅ Тестировать 2+ недели")
        print("  ✅ Отслеживать: CTR, конверсию, AOV")
    print()

except requests.exceptions.ConnectionError:
    print("❌ Flask не запущен! Запустите: python3 app.py")
except Exception as e:
    print(f"❌ Ошибка: {e}")
