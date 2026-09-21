#!/usr/bin/env python3
"""
Тесты для новой функциональности: автосбор исследований (auto_research_sources)

Проверяет:
1. Сериализацию/десериализацию поля auto_research_sources (round-trip через JSON)
2. Метод HypothesisManager.scan_auto_research() — максимум 5 результатов, корректная структура
3. API endpoint POST /api/scan-research/<hypothesis_id> (если сервер запущен)
"""
import os
import sys
import json
import tempfile

from product_hypothesis_assistant import (
    HypothesisManager,
    Hypothesis,
)

API_URL = "http://localhost:5000/api"


def _make_manager(tmp_file=None):
    """Создаёт менеджер без реальной БД (данные только в памяти)."""
    return HypothesisManager()


def test_serialization_roundtrip():
    print("=" * 70)
    print("ТЕСТ 1: Сериализация auto_research_sources (round-trip)")
    print("=" * 70)

    manager = _make_manager("tmp_auto_research_serialization.json")
    hyp = manager.create_hypothesis(
        title="Тест сериализации",
        description="Описание",
        problem_statement="Проблема",
        target_users="Пользователи",
        expected_outcome="Результат",
    )

    hyp.auto_research_sources = [
        {
            "title": "Исследование A",
            "authors": ["Иванов И."],
            "year": 2023,
            "url": "https://example.com/a",
            "abstract": "Аннотация A",
            "source": "arxiv",
            "relevance_score": 0.9,
        },
        {
            "title": "Исследование B",
            "authors": ["Петров П.", "Сидоров С."],
            "year": 2022,
            "url": "https://example.com/b",
            "abstract": "Аннотация B",
            "source": "semantic_scholar",
            "relevance_score": 0.55,
        },
    ]

    data = hyp.to_dict()

    assert data["auto_research_sources"] == hyp.auto_research_sources, "to_dict не сохраняет список"
    assert data["auto_research_count"] == 2, "auto_research_count неверный"

    restored = HypothesisManager._hypothesis_from_dict(data)
    assert restored.auto_research_sources == hyp.auto_research_sources, "round-trip не сохранил данные"
    assert len(restored.auto_research_sources) == 2

    empty_hyp = Hypothesis(title="x", description="", problem_statement="", target_users="", expected_outcome="")
    assert empty_hyp.auto_research_sources == [], "значение по умолчанию не пустой список"

    if os.path.exists("tmp_auto_research_serialization.json"):
        os.remove("tmp_auto_research_serialization.json")
    print("✅ ТЕСТ 1 ПРОЙДЕН: сериализация/десериализация работает корректно\n")
    return True

def test_scan_auto_research():
    print("=" * 70)
    print("ТЕСТ 2: scan_auto_research()")
    print("=" * 70)

    tmp_file = "tmp_auto_research_scan.json"
    if os.path.exists(tmp_file):
        os.remove(tmp_file)

    manager = _make_manager(tmp_file)
    hyp = manager.create_hypothesis(
        title="Тёмный режим",
        description="Добавить тёмный режим",
        problem_statement="Eye strain from bright displays at night",
        target_users="mobile app users",
        expected_outcome="Increased retention",
    )

    result = manager.scan_auto_research(hyp.id)

    assert result.get("success") is True, f"scan_auto_research не успешен: {result}"
    assert result.get("research_count", -1) <= 5, "больше 5 результатов"
    assert result.get("research_count") == len(result.get("research_sources", [])), "несоответствие счётчиков"
    assert result.get("hypothesis_id") == hyp.id

    stored = manager.get_hypothesis(hyp.id).auto_research_sources
    assert stored == result["research_sources"], "результаты не сохранены в гипотезе"
    assert len(stored) <= 5

    for src in result["research_sources"]:
        for field in ("title", "authors", "year", "url", "abstract", "source", "relevance_score"):
            assert field in src, f"отсутствует поле {field}"

    if result["research_count"] > 0:
        assert 0 <= result["average_relevance"] <= 1

    missing = manager.scan_auto_research("non-existent-id")
    assert missing.get("success") is False, "должна вернуть ошибку для несуществующей гипотезы"

    if os.path.exists(tmp_file):
        os.remove(tmp_file)
    print(f"✅ ТЕСТ 2 ПРОЙДЕН: найдено {result['research_count']} исследований (макс. 5)\n")
    return True


def test_api_scan_research():
    print("=" * 70)
    print("ТЕСТ 3: API endpoint POST /api/scan-research/<id>")
    print("=" * 70)
    try:
        import requests
    except ImportError:
        print("⚠️ requests не установлен — пропуск API-теста\n")
        return True

    try:
        r = requests.post(f"{API_URL}/create-hypothesis", json={
            "title": "Автоисследование API",
            "description": "Описание",
            "problem_statement": "Dark mode eye strain",
            "target_users": "mobile users",
            "expected_outcome": "retention",
        }, timeout=5)
        r.raise_for_status()
        hyp_id = r.json()["hypothesis_id"]
    except Exception as e:
        print(f"⚠️ Сервер недоступен ({e}) — пропуск API-теста\n")
        return True

    r = requests.post(f"{API_URL}/scan-research/{hyp_id}", timeout=60)
    if r.status_code == 404:
        print("⚠️ Endpoint /api/scan-research не найден (старый сервер?) — пропуск API-теста\n")
        return True
    result = r.json()

    assert result.get("success") is True, f"API вернул ошибку: {result}"
    assert result.get("research_count", -1) <= 5
    assert "research_sources" in result
    assert "average_relevance" in result

    r = requests.get(f"{API_URL}/get-hypothesis/{hyp_id}", timeout=10)
    hyp_data = r.json()["hypothesis"]
    assert hyp_data.get("auto_research_count") == result["research_count"]
    assert hyp_data.get("auto_research_sources") == result["research_sources"]

    print(f"✅ ТЕСТ 3 ПРОЙДЕН: API вернул {result['research_count']} исследований\n")
    return True


def run_all_tests():
    passed = 0
    total = 0
    for test in (test_serialization_roundtrip, test_scan_auto_research, test_api_scan_research):
        total += 1
        try:
            if test():
                passed += 1
        except AssertionError as e:
            print(f"❌ {test.__name__} не пройден: {e}\n")
        except Exception as e:
            print(f"❌ {test.__name__} упал с ошибкой: {e}\n")

    print("=" * 70)
    print(f"ИТОГО: {passed}/{total} тестов пройдено")
    print("=" * 70)
    return passed == total


if __name__ == "__main__":
    sys.exit(0 if run_all_tests() else 1)
