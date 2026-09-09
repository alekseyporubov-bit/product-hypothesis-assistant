#!/usr/bin/env python3
"""
Простой тест для проверки сохранения и восстановления данных гипотез при перезапуске
"""
import json
import os
from datetime import datetime
from product_hypothesis_assistant import HypothesisManager, Evidence, EvidenceType


def test_data_persistence():
    """Тестируем сохранение и восстановление данных"""
    
    # Создаем временный файл для тестирования
    temp_file = "temp_test_hypotheses_data.json"
    
    # Удаляем временный файл, если существует
    if os.path.exists(temp_file):
        os.remove(temp_file)
    
    print("🧪 ТЕСТ: Сохранение и восстановление данных")
    print("-" * 50)
    
    # Создаем первый экземпляр HypothesisManager с временным файлом
    print("1. Создание первого экземпляра HypothesisManager...")
    manager1 = HypothesisManager.__new__(HypothesisManager)
    manager1.hypotheses = {}
    from product_hypothesis_assistant import ScoringEngine
    manager1.scoring_engine = ScoringEngine()
    manager1.STORAGE_FILE = temp_file
    
    print("2. Создание гипотезы...")
    hypothesis = manager1.create_hypothesis(
        title="Тестовая гипотеза",
        description="Описание тестовой гипотезы",
        problem_statement="Проблема для теста",
        target_users="Тестовые пользователи",
        expected_outcome="Тестовый результат"
    )
    print(f"   ✓ Создана гипотеза: {hypothesis.title}")
    print(f"   ✓ ID: {hypothesis.id}")
    
    # Добавляем доказательство
    evidence = Evidence(
        evidence_type=EvidenceType.MARKET_RESEARCH,
        title="Тестовое доказательство",
        description="Описание тестового доказательства",
        source="Тестовый источник",
        confidence=0.8,
        supports=True
    )
    
    success = manager1.add_evidence(hypothesis.id, evidence)
    print(f"   ✓ Добавлено доказательство: {evidence.title}, успех: {success}")
    
    # Проверяем, что файл был создан и содержит данные
    if os.path.exists(temp_file):
        print("3. Проверка: файл данных создан ✓")
        
        with open(temp_file, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
        
        print(f"   ✓ Файл содержит {len(saved_data)} гипотез")
        
        # Создаем второй экземпляр (симуляция перезапуска)
        print("\n4. Создание второго экземпляра HypothesisManager (симуляция перезапуска)...")
        manager2 = HypothesisManager.__new__(HypothesisManager)
        manager2.hypotheses = {}
        manager2.scoring_engine = ScoringEngine()
        manager2.STORAGE_FILE = temp_file
        
        # Загружаем данные из файла
        load_success = manager2.load_from_file()
        print(f"   ✓ Загрузка успешна: {load_success}")
        
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
                    
                    print("\n🎉 ТЕСТ УСПЕШЕН: Данные корректно сохраняются и восстанавливаются!")
                    print("   - Гипотеза сохранена в файл")
                    print("   - После перезапуска данные успешно загружены")
                    print("   - Все атрибуты сохранены корректно")
                    
                    # Удаляем временный файл
                    os.remove(temp_file)
                    return True
                else:
                    print("\n❌ ТЕСТ НЕ ПРОЙДЕН: Данные не совпадают")
                    print(f"   - Ожидалось: {hypothesis.title}, получено: {loaded_hypothesis.title}")
                    print(f"   - Ожидалось доказательств: 1, получено: {len(loaded_hypothesis.evidence)}")
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
    success = test_data_persistence()
    if success:
        print("\n✅ Все работает корректно! Данные сохраняются и восстанавливаются при перезапуске.")
    else:
        print("\n❌ Обнаружена проблема с сохранением данных!")
        exit(1)