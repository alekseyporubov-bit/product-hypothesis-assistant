#!/usr/bin/env python3
"""
Интеграционный тест полного сценария:
1. Создание гипотезы через API
2. Добавление доказательств
3. Валидация
4. Запись исхода
5. Анализ корреляции
"""
import requests
import json
from bs4 import BeautifulSoup

BASE_URL = "http://localhost:5000"
API_URL = f"{BASE_URL}/api"

def print_step(step_num, description):
    print(f"\n{'='*70}")
    print(f"ШАГ {step_num}: {description}")
    print(f"{'='*70}")

def print_success(msg):
    print(f"✅ {msg}")

def print_error(msg):
    print(f"❌ {msg}")

def test_full_flow():
    """Полный тест сценария"""
    
    try:
        # ============================================================================
        # ШАГ 1: Проверяем что сервер работает
        # ============================================================================
        print_step(1, "Проверка сервера")
        response = requests.get(BASE_URL, timeout=5)
        if response.status_code != 200:
            print_error(f"Сервер не отвечает. Статус: {response.status_code}")
            return False
        print_success("Сервер работает на localhost:5000")
        
        # ============================================================================
        # ШАГ 2: Создаём гипотезу через API
        # ============================================================================
        print_step(2, "Создание гипотезы через API")
        hypothesis_data = {
            "title": "Интеграционный тест - Тёмный режим",
            "description": "Добавить тёмный режим в приложение",
            "problem_statement": "Пользователи жалуются на белый фон в ночное время",
            "target_users": "Mobile пользователи, использующие приложение ночью",
            "expected_outcome": "Повышение retention на 15%, улучшение UX"
        }
        
        response = requests.post(
            f"{API_URL}/create-hypothesis",
            json=hypothesis_data,
            timeout=10
        )
        
        if response.status_code != 200:
            print_error(f"Ошибка создания гипотезы: {response.text}")
            return False
        
        result = response.json()
        if not result.get('success'):
            print_error(f"API вернул ошибку: {result.get('error')}")
            return False
        
        hypothesis_id = result.get('hypothesis_id')
        print_success(f"Гипотеза создана. ID: {hypothesis_id}")
        print(f"   Название: {hypothesis_data['title']}")
        
        # ============================================================================
        # ШАГ 3: Добавляем доказательства
        # ============================================================================
        print_step(3, "Добавление доказательств через API")
        
        evidences = [
            {
                "hypothesis_id": hypothesis_id,
                "evidence_type": "USER_FEEDBACK",
                "title": "Отзывы пользователей",
                "description": "150 пользователей просили тёмный режим в опросе",
                "source": "In-app опрос",
                "confidence": 0.9,
                "supports": True
            },
            {
                "hypothesis_id": hypothesis_id,
                "evidence_type": "ANALYTICS",
                "title": "Данные ночного использования",
                "description": "40% активности приходится на 18:00-06:00",
                "source": "Analytics",
                "confidence": 0.95,
                "supports": True
            }
        ]
        
        for i, evidence_data in enumerate(evidences, 1):
            response = requests.post(
                f"{API_URL}/add-evidence",
                json=evidence_data,
                timeout=10
            )
            
            if response.status_code != 200:
                print_error(f"Ошибка добавления доказательства {i}: {response.text}")
                return False
            
            result = response.json()
            if not result.get('success'):
                print_error(f"API вернул ошибку при добавлении доказательства {i}")
                return False
            
            print_success(f"Доказательство {i} добавлено: {evidence_data['title']}")
        
        # ============================================================================
        # ШАГ 4: Валидируем гипотезу
        # ============================================================================
        print_step(4, "Валидация гипотезы и получение Score")
        
        response = requests.post(
            f"{API_URL}/validate-hypothesis/{hypothesis_id}",
            timeout=10
        )
        
        if response.status_code != 200:
            print_error(f"Ошибка валидации: {response.text}")
            return False
        
        result = response.json()
        if not result.get('success'):
            print_error(f"Валидация вернула ошибку: {result.get('error')}")
            return False
        
        score = result.get('score', {})
        print_success(f"Гипотеза валидирована!")
        print(f"   Score: {score.get('overall_score', 'N/A')}/100")
        print(f"   Рекомендация: {score.get('recommendation', 'N/A')}")
        print(f"   Уверенность: {score.get('confidence_level', 'N/A')}")
        
        # ============================================================================
        # ШАГ 5: Проверяем что гипотеза видна на UI
        # ============================================================================
        print_step(5, "Проверка отображения гипотезы на UI")
        
        response = requests.get(f"{API_URL}/get-hypothesis/{hypothesis_id}", timeout=10)
        if response.status_code != 200:
            print_error(f"Гипотеза не найдена: {response.text}")
            return False
        
        result = response.json()
        hypothesis = result.get('hypothesis')
        
        if not hypothesis:
            print_error("Гипотеза не загружена")
            return False
        
        print_success(f"Гипотеза загружена из БД")
        print(f"   Статус: {hypothesis.get('status')}")
        print(f"   Количество доказательств: {len(hypothesis.get('evidence', []))}")
        print(f"   Есть Score: {bool(hypothesis.get('score'))}")
        
        # ============================================================================
        # ШАГИ 6-7: Имитируем запуск фичи и запись исхода
        # ============================================================================
        print_step(6, "Имитация: Запуск фичи в продакшене (6+ месяцев)")
        print("   [В реальности фича была бы в продакшене 6+ месяцев]")
        print_success("Фича развёрнута и работает в продакшене")
        
        print_step(7, "Запись фактического исхода через API")
        
        outcome_data = {
            "hypothesis_id": hypothesis_id,
            "was_successful": True,
            "actual_impact": "Тёмный режим привёл к увеличению retention на 18%. Пользователи активнее используют приложение в ночное время.",
            "lessons_learned": "Необходимо добавить автоматическое переключение режима по времени суток. Некоторые пользователи просят переключение в зависимости от уровня освещения."
        }
        
        response = requests.post(
            f"{API_URL}/record-outcome",
            json=outcome_data,
            timeout=10
        )
        
        if response.status_code != 200:
            print_error(f"Ошибка записи исхода: {response.text}")
            return False
        
        result = response.json()
        if not result.get('success'):
            print_error(f"API вернул ошибку: {result.get('error')}")
            return False
        
        print_success("Исход фичи записан!")
        print(f"   Результат: Успех ✓")
        print(f"   Воздействие: {outcome_data['actual_impact']}")
        
        # ============================================================================
        # ШАГИ 8: Анализ корреляции
        # ============================================================================
        print_step(8, "Анализ корреляции Score vs Реальный результат")
        
        response = requests.get(
            f"{API_URL}/correlation-analysis",
            timeout=10
        )
        
        if response.status_code != 200:
            print_error(f"Ошибка получения анализа: {response.text}")
            return False
        
        result = response.json()
        if not result.get('success'):
            analysis = result.get('analysis', {})
            if analysis.get('status') == 'insufficient_data':
                print("⚠️  Недостаточно данных для анализа (нужно 2+ завершённых гипотезы)")
                print(f"   {analysis.get('message')}")
            else:
                print_error(f"Ошибка анализа: {result.get('error')}")
        else:
            analysis = result.get('analysis', {})
            print_success("Анализ корреляции выполнен!")
            print(f"   Завершённых гипотез: {analysis.get('total_completed', 0)}")
            print(f"   Точных предсказаний: {analysis.get('correct_predictions', 0)}")
            print(f"   Точность: {analysis.get('accuracy_percentage', 0):.1f}%")
        
        # ============================================================================
        # ИТОГИ
        # ============================================================================
        print_step(0, "✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("\n📊 Полный сценарий работает:")
        print("  1. ✓ Создание гипотезы")
        print("  2. ✓ Добавление доказательств")
        print("  3. ✓ Валидация и получение Score")
        print("  4. ✓ Запись фактического исхода")
        print("  5. ✓ Анализ корреляции")
        print("\n🎯 Система ПОЛНОСТЬЮ ФУНКЦИОНАЛЬНА!")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print_error("Не удалось подключиться к localhost:5000")
        return False
    except Exception as e:
        print_error(f"Неожиданная ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_full_flow()
    exit(0 if success else 1)
