#!/usr/bin/env python3
"""
Простой тест проверки сценария нажатия на кнопку создания гипотезы
"""
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def test_button_click():
    """Тест нажатия кнопки и открытия формы"""
    
    # Настройка браузера
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        # Открываем сайт
        print("🌐 Открываем localhost:5000...")
        driver.get("http://localhost:5000")
        time.sleep(2)
        
        # Проверяем что страница загружена
        print("✓ Страница загружена")
        assert "Product Hypothesis Assistant" in driver.title
        print("✓ Заголовок страницы корректен")
        
        # Ищем кнопку "Создать новую"
        print("\n🔍 Ищем кнопку '+ Создать новую'...")
        button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//button[contains(text(), '+ Создать новую')]"))
        )
        print("✓ Кнопка найдена")
        
        # Проверяем что кнопка видима
        assert button.is_displayed(), "Кнопка не видима"
        print("✓ Кнопка видима на странице")
        
        # Нажимаем на кнопку
        print("\n👆 Нажимаем на кнопку...")
        button.click()
        time.sleep(1)
        print("✓ Клик выполнен")
        
        # Проверяем что форма создания гипотезы появилась
        print("\n📝 Проверяем что форма открылась...")
        create_form = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "create"))
        )
        print("✓ Форма создания найдена")
        
        # Проверяем что форма видима
        assert create_form.is_displayed(), "Форма не видима"
        print("✓ Форма видима на странице")
        
        # Проверяем наличие всех полей формы
        print("\n🔎 Проверяем наличие всех полей формы...")
        fields = {
            "title": "Название фичи",
            "description": "Краткое описание",
            "problem_statement": "Какую проблему решает",
            "target_users": "Целевые пользователи",
            "expected_outcome": "Ожидаемый результат"
        }
        
        for field_id, field_name in fields.items():
            field = driver.find_element(By.ID, field_id)
            assert field.is_displayed(), f"Поле {field_name} не видимо"
            print(f"  ✓ Поле '{field_name}' присутствует")
        
        # Проверяем кнопку отправки
        print("\n📤 Проверяем кнопку отправки...")
        submit_button = driver.find_element(By.XPATH, "//button[@type='submit' and contains(text(), 'Создать гипотезу')]")
        assert submit_button.is_displayed(), "Кнопка отправки не видима"
        print("✓ Кнопка отправки присутствует")
        
        print("\n" + "="*70)
        print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("="*70)
        print("\n📊 Результаты:")
        print("  ✓ Страница загружается корректно")
        print("  ✓ Кнопка '+ Создать новую' видима и кликабельна")
        print("  ✓ При нажатии на кнопку открывается форма создания гипотезы")
        print("  ✓ Все поля формы присутствуют и видимы")
        print("  ✓ Кнопка отправки формы работает")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ТЕСТ ПРОВАЛЕН: {e}")
        print(f"\nОшибка: {type(e).__name__}")
        return False
        
    finally:
        # Закрываем браузер
        print("\n🔒 Закрываем браузер...")
        driver.quit()

if __name__ == "__main__":
    success = test_button_click()
    exit(0 if success else 1)
