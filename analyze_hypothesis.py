#!/usr/bin/env python3
"""Анализ результатов гипотезы о красной кнопке"""

import requests
import json

BASE = "http://localhost:5000/api"

# ID последней гипотезы
hypothesis_id = "a32f5063-e18e-49a9-93fa-eaeff965cfba"

print("=" * 90)
print("📊 ПОДРОБНЫЙ АНАЛИЗ ГИПОТЕЗЫ")
print("=" * 90)
print()

try:
    # Получить полную информацию
    resp = requests.get(f"{BASE}/get-hypothesis/{hypothesis_id}", timeout=10)
    hypothesis = resp.json().get("hypothesis", {})
    
    print("📋 ИНФОРМАЦИЯ О ГИПОТЕЗЕ:")
    print("-" * 90)
    print(f"ID: {hypothesis.get('id', 'N/A')}")
    print(f"Заголовок: {hypothesis.get('title', 'N/A')}")
    print(f"Статус: {hypothesis.get('status', 'N/A')}")
    print(f"Проблема: {hypothesis.get('problem_statement', 'N/A')}")
    print()
    
    # Доказательства
    evidence_list = hypothesis.get('evidence', [])
    print(f"📚 ДОКАЗАТЕЛЬСТВА ({len(evidence_list)}):")
    print("-" * 90)
    
    for i, ev in enumerate(evidence_list, 1):
        print(f"{i}. {ev.get('title', 'N/A')}")
        print(f"   Тип: {ev.get('evidence_type', 'N/A')}")
        print(f"   Описание: {ev.get('description', 'N/A')}")
        print(f"   Уверенность: {ev.get('confidence', 'N/A')}")
        print()
    
    # Список гипотез
    print("🔍 ВСЕ ГИПОТЕЗЫ В СИСТЕМЕ:")
    print("-" * 90)
    resp = requests.get(f"{BASE}/list-hypotheses", timeout=10)
    hypotheses = resp.json().get("hypotheses", [])
    
    for i, hyp in enumerate(hypotheses, 1):
        print(f"{i}. {hyp.get('title', 'N/A')[:60]}")
        print(f"   ID: {hyp.get('id', 'N/A')[:20]}...")
        print(f"   Статус: {hyp.get('status', 'N/A')}")
        print()
    
    # Анализ корреляции
    print("📈 АНАЛИЗ КОРРЕЛЯЦИИ:")
    print("-" * 90)
    resp = requests.get(f"{BASE}/correlation-analysis", timeout=10)
    correlation = resp.json()
    
    print(json.dumps(correlation, ensure_ascii=False, indent=2)[:500])
    print()
    
    # Исследования
    print("🔬 НАУЧНЫЕ ИССЛЕДОВАНИЯ:")
    print("-" * 90)
    resp = requests.get(f"{BASE}/research-sources/{hypothesis_id}", timeout=10)
    sources = resp.json().get("sources", [])
    
    print(f"Найдено исследований: {len(sources)}")
    for source in sources[:3]:
        print(f"  • {source.get('title', 'N/A')}")
    print()

except Exception as e:
    print(f"Ошибка: {e}")
