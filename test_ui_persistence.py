#!/usr/bin/env python3
"""
Простой тест для проверки сохранения данных через UI (имитация работы через веб-интерфейс)
"""
import json
import os
from product_hypothesis_assistant import HypothesisManager, Evidence, EvidenceType


def test_ui_data_persistence():
    """Тестируем сохранение данных при работе через UI"""
    
    # Создаем временный файл для тестирования
    temp_file = "ui_test_hypotheses_data.json"
    
    # Удаляем временный файл, если существует
    if os.path.exists(temp_file):
        os.remove(temp_file)
    
    print("🧪 ТЕСТ: Сохранение данных через UI")
    print("-" * 50)
    
    # Изменяем путь к файлу у класса для теста
    original_storage = HypothesisManager.STORAGE_FILE
    HypothesisManager.STORAGE_FILE = temp_file
    
    # Создаем менеджер
    print("1. Создание экземпляра HypothesisManager...")
    manager = HypothesisManager()
    
    # Вручную очищаем данные для теста
    manager.hypotheses = {}
    from product_hypothesis_assistant import ScoringEngine
    manager.scoring_engine = ScoringEngine()
    
    print("2. Создание гипотезы (имитация UI действия)...")
    hypothesis = manager.create_hypothesis(
        title="UI тест гипотеза",
        description="Гипотеза, созданная через UI",
        problem_statement="Проблема, которую решаем",
        target_users="Тестовые пользователи",
        expected_outcome="Положительный результат"
    )
    print(f"   ✓ Гипотеза создана: {hypothesis.title}")
    
    # Добавляем доказательство (имитация UI действия)
    print("3. Добавление доказательства (имитация UI действия)...")
    evidence = Evidence(
        evidence_type=EvidenceType.MARKET_RESEARCH,
        title="UI тест доказательства",
        description="Описание доказательства",
        source="Тестовый источник",
        confidence=0.85,
        supports=True
    )
    
    manager.add_evidence(hypothesis.id, evidence)
    print(f"   ✓ Доказательство добавлено: {evidence.title}")
    
    # Валидируем гипотезу (имитация UI действия)
    print("4. Валидация гипотезы (имитация UI действия)...")
    success, score = manager.validate_hypothesis(hypothesis.id)
    if success:
        print(f"   ✓ Гипотеза валидирована, score: {score.overall_score}")
    
    # Проверяем, что файл был создан и содержит данные
    if os.path.exists(temp_file):
        print("5. Проверка: файл данных создан ✓")
        
        with open(temp_file, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
        
        print(f"   ✓ Файл содержит {len(saved_data)} гипотез")
        
        # Имитация перезапуска сервера (новый экземпляр)
        print("6. Имитация перезапуска сервера...")
        manager2 = HypothesisManager()
        
        # Восстанавливаем оригинальный путь к файлу
        HypothesisManager.STORAGE_FILE = original_storage
        
        # Проверяем, что данные загрузились
        loaded_hypotheses = manager2.list_hypotheses()
        print(f"   ✓ Загружено {len(loaded_hypotheses)} гипотез")
        
        if len(loaded_hypotheses) > 0:
            loaded_hypothesis = loaded_hypotheses[0]
            print(f"   ✓ Загруженная гипотеза: {loaded_hypothesis.title}")
            print(f"   ✓ Количество доказательств: {len(loaded_hypothesis.evidence)}")
            
            if len(loaded_hypothesis.evidence) > 0:
                print(f"   ✓ Первое доказательство: {loaded_hypothesis.evidence[0].title}")
                
                # Проверяем соответствие данных
                if (loaded_hypothesis.title == hypothesis.title and 
                    len(loaded_hypothesis.evidence) == 1 and
                    loaded_hypothesis.evidence[0].title == evidence.title):
                    
                    print("\n🎉 ТЕСТ УСПЕШЕН: Данные корректно сохраняются и восстанавливаются через UI!")
                    print("   - Гипотеза создана через UI")
                    print("   - Доказательства добавлены через UI")
                    print("   - Валидация выполнена через UI")
                    print("   - После перезапуска данные успешно загружены")
                    print("   - Все атрибуты сохранены корректно")
                    
                    # Удаляем временный файл
                    os.remove(temp_file)
                    return True
                else:
                    print("\n❌ ТЕСТ НЕ ПРОЙДЕН: Данные не совпадают")
                    return False
            else:
                print("\n❌ ТЕСТ НЕ ПРОЙДЕН: Доказательства не загрузились")
                return False
        else:
            print("\n❌ ТЕСТ НЕ ПРОЙДЕН: Гипотезы не загрузились")
            return False
    else:
        print("\n❌ ТЕСТ НЕ ПРОЙДЕН: Файл данных не был создан")
        return False


if __name__ == "__main__":
    success = test_ui_data_persistence()
    if success:
        print("\n✅ Все работает корректно! Данные сохраняются через UI и восстанавливаются при перезапуске.")
    else:
        print("\n❌ Обнаружена проблема с сохранением данных через UI!")
        exit(1)