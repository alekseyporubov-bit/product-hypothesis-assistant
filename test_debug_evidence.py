#!/usr/bin/env python3
"""
Отладочный тест для понимания что происходит с доказательствами
"""
import requests
import json

BASE_URL = "http://localhost:5000"
API_URL = f"{BASE_URL}/api"

def test_debug():
    print("="*70)
    print("ОТЛАДКА: Поиск проблемы с доказательствами")
    print("="*70)
    
    # Создаём гипотезу
    print("\n1️⃣ Создаём гипотезу...")
    hypothesis_data = {
        "title": "Отладочный тест",
        "description": "Тест",
        "problem_statement": "Тест",
        "target_users": "Тест",
        "expected_outcome": "Тест"
    }
    
    r = requests.post(f"{API_URL}/create-hypothesis", json=hypothesis_data)
    result = r.json()
    hyp_id = result['hypothesis_id']
    print(f"✅ Гипотеза создана: {hyp_id}")
    
    # Получаем гипотезу ПЕРЕД добавлением доказательств
    print("\n2️⃣ Получаем гипотезу ПЕРЕД добавлением доказательств...")
    r = requests.get(f"{API_URL}/get-hypothesis/{hyp_id}")
    result = r.json()
    hyp_before = result['hypothesis']
    print(f"✅ Доказательства ДО добавления: {len(hyp_before.get('evidence', []))}")
    
    # Добавляем доказательство
    print("\n3️⃣ Добавляем доказательство...")
    evidence_data = {
        "hypothesis_id": hyp_id,
        "evidence_type": "USER_FEEDBACK",
        "title": "Тестовое доказательство",
        "description": "Это тестовое доказательство",
        "source": "Тест",
        "confidence": 0.8,
        "supports": True
    }
    
    r = requests.post(f"{API_URL}/add-evidence", json=evidence_data)
    result = r.json()
    print(f"✅ Ответ сервера: {result}")
    
    # Получаем гипотезу ПОСЛЕ добавления доказательств
    print("\n4️⃣ Получаем гипотезу ПОСЛЕ добавления доказательств...")
    r = requests.get(f"{API_URL}/get-hypothesis/{hyp_id}")
    result = r.json()
    hyp_after = result['hypothesis']
    print(f"✅ Доказательства ПОСЛЕ добавления: {len(hyp_after.get('evidence', []))}")
    
    if hyp_after.get('evidence'):
        print("\n📋 Доказательства в гипотезе:")
        for ev in hyp_after['evidence']:
            print(f"   - {ev.get('title')}")
    else:
        print("❌ ПРОБЛЕМА: Доказательства не сохранились!")
        print(f"\nПолная гипотеза ПОСЛЕ:")
        print(json.dumps(hyp_after, indent=2))
    
    return len(hyp_after.get('evidence', [])) > 0

if __name__ == "__main__":
    success = test_debug()
    print(f"\n{'='*70}")
    if success:
        print("✅ Доказательства сохраняются правильно")
    else:
        print("❌ БАГ: Доказательства НЕ сохраняются!")
    print(f"{'='*70}")
    exit(0 if success else 1)
