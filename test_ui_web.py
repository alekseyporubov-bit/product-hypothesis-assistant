"""
UI-тесты с проверкой авторизации (Selenium).

Перед запуском должен быть поднят Flask-сервер:
    .venv/bin/python app.py   # на http://localhost:5000

Проверяет: экран входа для неавторизованных, 401 для защищённых /api/*,
регистрацию тестового пользователя, создание гипотезы после входа,
logout и повторный вход. Запуск: .venv/bin/python test_ui_web.py
"""

import time
import unittest

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = "http://localhost:5000"


class ProductHypothesisAuthUITests(unittest.TestCase):
    """UI-тесты авторизации и основных use cases."""

    @classmethod
    def setUpClass(cls):
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        cls.driver = webdriver.Chrome(options=options)
        cls.wait = WebDriverWait(cls.driver, 15)
        # Уникальный тестовый пользователь для каждого прогона.
        cls.username = f"uitest_{int(time.time())}"
        cls.password = "Passw0rd123"

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    # -------------------------------------------------------------- helpers

    def open_home(self):
        self.driver.get(BASE_URL)
        self.wait_for_id("auth-gate")
        time.sleep(1.5)  # даём JS завершить checkAuth()

    def wait_for_id(self, element_id, timeout=15):
        return self.wait.until(EC.presence_of_element_located((By.ID, element_id)))

    def wait_for_visible_id(self, element_id, timeout=15):
        return self.wait.until(EC.visibility_of_element_located((By.ID, element_id)))

    def is_displayed(self, element_id):
        try:
            return self.driver.find_element(By.ID, element_id).is_displayed()
        except Exception:
            return False

    def switch_to(self, mode):
        self.driver.find_element(By.ID, f"auth-tab-{mode}").click()
        form_id = "login-form" if mode == "login" else "register-form"
        self.wait.until(EC.visibility_of_element_located((By.ID, form_id)))

    def register(self, login, password, password2=None):
        self.switch_to("register")
        self.driver.find_element(By.ID, "register-username").send_keys(login)
        self.driver.find_element(By.ID, "register-password").send_keys(password)
        self.driver.find_element(By.ID, "register-password2").send_keys(
            password if password2 is None else password2
        )
        self._submit("register-form")
        time.sleep(2)

    def login(self, login, password):
        self.switch_to("login")
        self.driver.find_element(By.ID, "login-username").send_keys(login)
        self.driver.find_element(By.ID, "login-password").send_keys(password)
        self._submit("login-form")
        time.sleep(2)

    def _submit(self, form_id):
        form = self.driver.find_element(By.ID, form_id)
        form.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()

    def auth_error_text(self):
        el = self.driver.find_element(By.ID, "auth-error")
        return el.text.strip() if el.is_displayed() else ""

    def ensure_logged_out(self):
        self.open_home()
        if not self.is_displayed("auth-gate"):
            self.driver.find_element(By.XPATH, "//button[contains(text(),'Выйти')]").click()
            self.wait_for_visible_id("auth-gate")
            time.sleep(0.5)

    def ensure_logged_in(self):
        self.open_home()
        if not self.is_displayed("auth-gate"):
            return
        self.login(self.username, self.password)
        if not self.is_displayed("auth-gate"):
            return
        self.open_home()
        self.register(self.username, self.password)
        self.wait_for_visible_id("auth-user")

    # -------------------------------------------------------------- tests

    def test_01_unauthenticated_sees_login_gate(self):
        self.ensure_logged_out()
        self.assertTrue(self.is_displayed("auth-gate"), "Экран входа должен быть виден")
        self.assertTrue(self.is_displayed("login-form"), "Форма входа должна быть видна")
        self.assertFalse(self.is_displayed("register-form"), "Форма регистрации скрыта по умолчанию")
        self.assertFalse(self.is_displayed("auth-user"), "Блок пользователя скрыт до входа")

    def test_02_protected_api_requires_auth(self):
        self.ensure_logged_out()
        self.driver.get(BASE_URL + "/api/list-hypotheses")
        body = self.driver.find_element(By.TAG_NAME, "body").text
        self.assertIn("Требуется авторизация", body)

    def test_03_register_weak_password_rejected(self):
        self.ensure_logged_out()
        self.register(self.username, "123")
        self.assertTrue(self.is_displayed("auth-gate"), "После слабого пароля остаёмся на экране входа")
        self.assertTrue(self.auth_error_text(), "Должно показаться сообщение об ошибке")

    def test_04_register_valid_user_enters_app(self):
        self.ensure_logged_out()
        self.register(self.username, self.password)
        self.wait_for_visible_id("auth-user")
        self.assertFalse(self.is_displayed("auth-gate"), "Экран входа скрыт после регистрации")
        self.assertIn(self.username, self.driver.find_element(By.ID, "auth-name").text)

    def test_05_register_duplicate_login_rejected(self):
        self.ensure_logged_out()
        self.register(self.username, "AnotherPass1")
        self.assertTrue(self.is_displayed("auth-gate"), "Дубликат логина не должен пускать в приложение")
        self.assertTrue(self.auth_error_text(), "Должно быть сообщение о занятом логине")

    def test_06_create_hypothesis_use_case(self):
        self.ensure_logged_in()
        title = f"UI гипотеза {self.username}"
        self.driver.find_element(By.XPATH, "//button[contains(text(),'+ Создать новую')]").click()
        self.wait_for_visible_id("title").send_keys(title)
        self.driver.find_element(By.ID, "description").send_keys("Проверка сценария через UI")
        self.driver.find_element(By.ID, "problem_statement").send_keys("Пользователь хочет работать после входа")
        self.driver.find_element(By.ID, "target_users").send_keys("Авторизованные пользователи")
        self.driver.find_element(By.ID, "expected_outcome").send_keys("Гипотеза создана и видна в списке")
        self._submit("create-form")
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#hypotheses-list .hypothesis-item")))
        self.assertIn(title, self.driver.find_element(By.ID, "hypotheses-list").text)
        self.assertTrue(self.is_displayed("hypothesis-detail"), "Детали гипотезы должны открыться")

    def test_07_logout_returns_to_gate(self):
        self.ensure_logged_in()
        self.driver.find_element(By.XPATH, "//button[contains(text(),'Выйти')]").click()
        self.wait_for_visible_id("auth-gate")
        self.assertFalse(self.is_displayed("auth-user"), "После выхода блок пользователя скрыт")

    def test_08_login_wrong_password_rejected(self):
        self.ensure_logged_out()
        self.login(self.username, "WrongPass999")
        self.assertTrue(self.is_displayed("auth-gate"), "Неверный пароль не пускает в приложение")
        self.assertTrue(self.auth_error_text(), "Должно быть сообщение о неверном пароле")

    def test_09_login_correct_password_restores_data(self):
        self.ensure_logged_out()
        self.login(self.username, self.password)
        self.wait_for_visible_id("auth-user")
        self.assertFalse(self.is_displayed("auth-gate"))
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#hypotheses-list .hypothesis-item")))


if __name__ == "__main__":
    unittest.main(verbosity=2)

