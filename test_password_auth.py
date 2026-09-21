#!/usr/bin/env python3
"""
Сценарии регистрации и входа по логину/паролю (дополнение к Google-входу).

Проверяет (Red -> Green по TDPD):
1) базовые требования к сложности пароля и валидности логина;
2) регистрацию нового пользователя по логину/паролю (пароль хранится хешем);
3) вход по логину/паролю (верный/неверный пароль, регистронезависимость);
4) отказ в регистрации при дубликате логина;
5) сосуществование Google- и парольных пользователей;
6) HTTP-уровень: /api/auth/register, /api/auth/password-login, logout, 401/400.

Запуск (без БД — в памяти):
    python3 test_password_auth.py
"""

import sys

try:
    from auth import (
        UserManager,
        validate_login,
        validate_password_strength,
    )
    _AUTH_AVAILABLE = True
    _AUTH_IMPORT_ERROR = None
except Exception as e:  # pragma: no cover
    _AUTH_AVAILABLE = False
    _AUTH_IMPORT_ERROR = e

results = []


def check(name, cond, detail=""):
    results.append((name, bool(cond)))
    print(("PASS" if cond else "FAIL"), "-", name,
          ("| " + str(detail)[:160] if detail else ""))


def _um():
    return UserManager()


def test_password_validation():
    if not _AUTH_AVAILABLE:
        check("auth.py доступен", False, repr(_AUTH_IMPORT_ERROR))
        return
    check("короткий пароль отклоняется",
          validate_password_strength("Ab1") is not None)
    check("пароль без букв отклоняется",
          validate_password_strength("12345678") is not None)
    check("пароль без цифр отклоняется",
          validate_password_strength("abcdefgh") is not None)
    check("пароль, совпадающий с логином, отклоняется",
          validate_password_strength("alice123", "alice123") is not None)
    check("валидный пароль принимается",
          validate_password_strength("alice123") is None)


def test_login_validation():
    if not _AUTH_AVAILABLE:
        return
    check("короткий логин отклоняется", validate_login("ab") is not None)
    check("логин с недопустимым символом отклоняется",
          validate_login("abc def") is not None)
    check("валидный логин принимается", validate_login("alice_1") is None)


def test_register_and_authenticate():
    if not _AUTH_AVAILABLE:
        return
    um = _um()
    u, created, first = um.register_user("Alice1", "secret123")
    check("регистрация создаёт учётку", created is True and first is True)
    check("логин нормализуется к нижнему регистру", u.login == "alice1", u.login)
    check("имя = логину (для отображения)", u.name == "alice1")
    check("auth_method == password", u.auth_method == "password")
    check("пароль хранится как хеш, не открытым текстом",
          bool(u.password_hash) and u.password_hash != "secret123")
    check("to_dict не отдаёт password_hash", "password_hash" not in u.to_dict())
    check("to_storage_dict содержит password_hash",
          "password_hash" in u.to_storage_dict())

    check("правильный пароль проходит",
          um.authenticate_user("Alice1", "secret123") is not None)
    check("вход регистронезависим по логину",
          um.authenticate_user("ALICE1", "secret123") is not None)
    check("неверный пароль отклоняется",
          um.authenticate_user("alice1", "wrong123") is None)
    check("неизвестный логин отклоняется",
          um.authenticate_user("nobody1", "secret123") is None)


def test_duplicate_login():
    if not _AUTH_AVAILABLE:
        return
    um = _um()
    um.register_user("bob", "password1")
    try:
        um.register_user("BOB", "password2")
        check("повторная регистрация логина отклоняется", False)
    except ValueError as e:
        check("повторная регистрация логина отклоняется", True, str(e))


def test_google_and_password_coexist():
    if not _AUTH_AVAILABLE:
        return
    um = _um()
    g, _, _ = um.ensure_user("sub-1", "g@example.com", "Gina", "")
    p, _, _ = um.register_user("pete", "petepass1")
    check("google-пользователь и парольный сосуществуют",
          um.get_user(g.id) is not None and um.get_user(p.id) is not None)
    check("google-email не работает как парольный логин",
          um.authenticate_user("g@example.com", "anything1") is None)


def test_flask_password_auth():
    try:
        import app as app_module
    except Exception as e:
        check("app импортируется", False, repr(e))
        return

    client = app_module.app.test_client()

    r = client.post("/api/auth/register",
                    json={"login": "http_alice", "password": "alicepass1"})
    data = r.get_json()
    check("POST /api/auth/register -> success",
          r.status_code == 200 and bool(data and data.get("success")), r.status_code)
    check("после регистрации сессия авторизована",
          bool(client.get("/api/auth/status").get_json().get("authenticated")))

    r = client.post("/api/auth/register",
                    json={"login": "http_weak", "password": "short"})
    check("слабый пароль -> 400", r.status_code == 400, r.status_code)

    r = client.post("/api/auth/register",
                    json={"login": "HTTP_ALICE", "password": "otherpass1"})
    check("дубликат логина -> 400", r.status_code == 400, r.status_code)

    client.post("/api/auth/logout")
    check("после logout сессия не авторизована",
          client.get("/api/auth/status").get_json().get("authenticated") is False)

    r = client.post("/api/auth/password-login",
                    json={"login": "http_alice", "password": "wrongpass1"})
    check("неверный пароль -> 401", r.status_code == 401, r.status_code)

    r = client.post("/api/auth/password-login",
                    json={"login": "http_alice", "password": "alicepass1"})
    check("верный пароль -> success",
          r.status_code == 200 and bool(r.get_json().get("success")), r.status_code)
    check("после входа сессия авторизована",
          bool(client.get("/api/auth/status").get_json().get("authenticated")))
    check("статус не отдаёт password_hash",
          "password_hash" not in client.get("/api/auth/status").get_json()["user"])


def main() -> int:
    test_password_validation()
    test_login_validation()
    test_register_and_authenticate()
    test_duplicate_login()
    test_google_and_password_coexist()
    test_flask_password_auth()

    failed = [n for n, ok in results if not ok]
    print("\n" + "=" * 70)
    print("ИТОГ: %d/%d пройдено" % (len(results) - len(failed), len(results)))
    if failed:
        print("ПРОВАЛЕНЫ:")
        for n in failed:
            print("  -", n)
        return 1
    print("✓ ВСЕ ТЕСТЫ ПРОЙДЕНЫ")
    return 0


if __name__ == "__main__":
    sys.exit(main())

