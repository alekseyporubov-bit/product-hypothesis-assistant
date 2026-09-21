"""
Аутентификация (Google OAuth и логин/пароль) и управление пользователями.

Два способа входа:
1. Google (JIT, just-in-time): фронтенд показывает кнопку «Войти через Google»
   (Google Identity Services) и получает ID token (JWT). Браузер отправляет
   токен на POST /api/auth/login. Бэкенд проверяет токен через Google tokeninfo,
   извлекает sub / email / name / picture. `UserManager.ensure_user` создаёт
   учётку при первом входе или находит существующую.
2. Логин/пароль: регистрация через `UserManager.register_user` (пароль хранится
   как хеш pbkdf2:sha256), вход через `UserManager.authenticate_user`.

В обоих случаях Flask-сессия хранит `user_id`; остальные /api/*-маршруты
доступны только авторизованным и показывают данные только их пользователя.

Безопасность: проверка Google ID token выполняется на стороне Google
(https://oauth2.googleapis.com/tokeninfo), поэтому поддельный или истёкший
токен отклоняется сервером Google. Если задан GOOGLE_CLIENT_ID, дополнительно
сверяется поле `aud` (audience), чтобы токен был выпущен именно для этого
приложения. При установленном пакете google-auth можно заменить проверку на
`google.oauth2.id_token.verify_oauth2_token` (локальная проверка подписи).
"""

import os
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, Optional, Tuple

from werkzeug.security import generate_password_hash, check_password_hash

from product_hypothesis_assistant import HypothesisManager

GOOGLE_TOKENINFO_URL = "https://oauth2.googleapis.com/tokeninfo"

# --- Требования к логину/паролю --------------------------------------------
PASSWORD_MIN_LENGTH = 8
LOGIN_MIN_LENGTH = 3
LOGIN_MAX_LENGTH = 64
_ALLOWED_LOGIN_CHARS = set("abcdefghijklmnopqrstuvwxyz0123456789._-@")

# Постоянный «холостой» хеш для одинаковой по времени проверки пароля,
# когда пользователь с таким логином не найден (защита от перебора логинов).
_DUMMY_PASSWORD_HASH = generate_password_hash("__dummy__", method="pbkdf2:sha256")


def validate_login(login: str) -> Optional[str]:
    """Возвращает сообщение об ошибке или None, если логин валиден."""
    if not login:
        return "Укажите логин"
    if len(login) < LOGIN_MIN_LENGTH:
        return f"Логин должен быть не короче {LOGIN_MIN_LENGTH} символов"
    if len(login) > LOGIN_MAX_LENGTH:
        return f"Логин должен быть не длиннее {LOGIN_MAX_LENGTH} символов"
    if not all(c in _ALLOWED_LOGIN_CHARS for c in login):
        return "Логин может содержать только латинские буквы, цифры и символы . _ - @"
    return None


def validate_password_strength(password: str, login: str = "") -> Optional[str]:
    """Базовые требования к сложности пароля (сообщение об ошибке или None)."""
    if len(password) < PASSWORD_MIN_LENGTH:
        return f"Пароль должен быть не короче {PASSWORD_MIN_LENGTH} символов"
    if not any(c.isalpha() for c in password):
        return "Пароль должен содержать хотя бы одну букву"
    if not any(c.isdigit() for c in password):
        return "Пароль должен содержать хотя бы одну цифру"
    if login and password.lower() == login.lower():
        return "Пароль не должен совпадать с логином"
    return None


class User:
    """Учётная запись пользователя (Google OAuth или логин/пароль)."""

    def __init__(self, user_id: str, google_sub: str = "", email: str = "",
                 name: str = "", avatar_url: str = "",
                 login: str = "", password_hash: str = "",
                 created_at: Optional[datetime] = None):
        self.id = user_id
        self.google_sub = google_sub or ""
        self.email = email or ""
        self.name = name or ""
        self.avatar_url = avatar_url or ""
        self.login = login or ""
        self.password_hash = password_hash or ""
        self.created_at = created_at or datetime.now(timezone.utc)

    @property
    def auth_method(self) -> str:
        return "google" if self.google_sub else "password"

    def to_dict(self) -> Dict:
        """Публичное представление (без password_hash)."""
        return {
            "id": self.id,
            "google_sub": self.google_sub,
            "email": self.email,
            "name": self.name,
            "avatar_url": self.avatar_url,
            "login": self.login,
            "auth_method": self.auth_method,
            "created_at": self.created_at.isoformat(),
        }

    def to_storage_dict(self) -> Dict:
        """Полное представление для персистентности (включая password_hash)."""
        data = self.to_dict()
        data["password_hash"] = self.password_hash
        return data

    @staticmethod
    def from_dict(data: Dict) -> "User":
        created_at = data.get("created_at", "")
        try:
            created_at = datetime.fromisoformat(created_at)
        except (TypeError, ValueError):
            created_at = datetime.now(timezone.utc)
        return User(
            user_id=data.get("id", ""),
            google_sub=data.get("google_sub", ""),
            email=data.get("email", ""),
            name=data.get("name", ""),
            avatar_url=data.get("avatar_url", ""),
            login=data.get("login", ""),
            password_hash=data.get("password_hash", ""),
            created_at=created_at,
        )


class UserManager:
    """Хранит пользователей и создаёт их при первом входе (JIT).

    Зеркалит подход `HypothesisManager`: при заданном `DATABASE_URL` пользователи
    персистентно хранятся в PostgreSQL (таблица `users`), иначе — только в памяти.
    """

    POSTGRES_TABLE = "users"

    def __init__(self):
        self.users: Dict[str, User] = {}
        self._by_google_sub: Dict[str, User] = {}
        self._by_login: Dict[str, User] = {}

        self.db_url = (
            os.environ.get("DATABASE_URL")
            or os.environ.get("POSTGRES_URL")
            or ""
        ).strip()
        self.use_postgres = bool(self.db_url)

        if self.use_postgres:
            self._ensure_db_table()
            self.load()

    # ------------------------------------------------------------------ JIT
    def ensure_user(self, google_sub: str, email: str, name: str,
                    avatar_url: str = "") -> Tuple[User, bool, bool]:
        """Возвращает (user, created, is_first) для заданного Google-субъекта.

        - `created`  — учётка создана сейчас (первый вход этого пользователя);
        - `is_first` — это самый первый пользователь системы (нужно, чтобы
          привязать «сиротские» легаси-гипотезы к первому вошедшему).
        """
        existing = self._by_google_sub.get(google_sub)
        if existing is not None:
            return existing, False, False

        is_first = len(self.users) == 0
        user = User(
            user_id=str(uuid.uuid4()),
            google_sub=google_sub,
            email=email or "",
            name=name or "",
            avatar_url=avatar_url or "",
        )
        self.users[user.id] = user
        self._by_google_sub[google_sub] = user
        self.save()
        return user, True, is_first

    def get_user(self, user_id: str) -> Optional[User]:
        """Возвращает учётную запись по id или None."""
        return self.users.get(user_id)

    def get_by_google_sub(self, google_sub: str) -> Optional[User]:
        return self._by_google_sub.get(google_sub)

    @staticmethod
    def _normalize_login(login: str) -> str:
        return (login or "").strip().lower()

    def get_by_login(self, login: str) -> Optional[User]:
        return self._by_login.get(self._normalize_login(login))

    def register_user(self, login: str, password: str) -> Tuple[User, bool, bool]:
        """Создаёт учётку по логину/паролю.

        Возвращает `(user, created, is_first)`. Поднимает `ValueError` при
        невалидном логине/пароле или если логин уже занят.
        """
        login = self._normalize_login(login)
        err = validate_login(login)
        if err:
            raise ValueError(err)
        err = validate_password_strength(password, login)
        if err:
            raise ValueError(err)
        if self.get_by_login(login) is not None:
            raise ValueError("Пользователь с таким логином уже существует")

        is_first = len(self.users) == 0
        user = User(
            user_id=str(uuid.uuid4()),
            login=login,
            password_hash=generate_password_hash(password, method="pbkdf2:sha256"),
            name=login,
        )
        self.users[user.id] = user
        self._by_login[login] = user
        self.save()
        return user, True, is_first

    def authenticate_user(self, login: str, password: str) -> Optional[User]:
        """Возвращает User при верном логине/пароле, иначе None."""
        login = self._normalize_login(login)
        user = self.get_by_login(login)
        if user is None or not user.password_hash:
            # Одинаковая по времени проверка, чтобы не раскрывать существование логина.
            check_password_hash(_DUMMY_PASSWORD_HASH, password or "")
            return None
        if check_password_hash(user.password_hash, password or ""):
            return user
        return None

    # ----------------------------------------------------------- Persistence
    def _get_postgres_connection(self):
        try:
            import psycopg2
        except ImportError as e:
            raise RuntimeError(
                "Библиотека psycopg2 не установлена. Добавьте 'psycopg2-binary' "
                "в requirements.txt и выполните pip install."
            ) from e
        return psycopg2.connect(
            HypothesisManager._normalize_postgres_url(self.db_url),
            sslmode="disable",
        )

    def _ensure_db_table(self) -> bool:
        try:
            conn = self._get_postgres_connection()
        except Exception as e:
            print(f"⚠️ users: PostgreSQL не доступен ({e})")
            return False
        try:
            with conn, conn.cursor() as cur:
                cur.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS {self.POSTGRES_TABLE} (
                        id UUID PRIMARY KEY,
                        data JSONB NOT NULL,
                        updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
                    )
                    """
                )
            return True
        except Exception as e:
            print(f"⚠️ users: не удалось создать таблицу: {e}")
            return False
        finally:
            conn.close()

    def _save_to_postgres(self) -> bool:
        try:
            import psycopg2.extras
        except ImportError:
            return False
        try:
            conn = self._get_postgres_connection()
        except Exception as e:
            print(f"❌ users: ошибка сохранения: {e}")
            return False
        try:
            with conn, conn.cursor() as cur:
                for user in self.users.values():
                    payload = psycopg2.extras.Json(
                        user.to_storage_dict(),
                        dumps=lambda obj: json.dumps(obj, ensure_ascii=False, default=str),
                    )
                    cur.execute(
                        f"""
                        INSERT INTO {self.POSTGRES_TABLE} (id, data, updated_at)
                        VALUES (%s, %s, now())
                        ON CONFLICT (id)
                        DO UPDATE SET data = EXCLUDED.data, updated_at = now()
                        """,
                        (user.id, payload),
                    )
            return True
        except Exception as e:
            print(f"❌ users: ошибка сохранения: {e}")
            return False
        finally:
            conn.close()

    def _load_from_postgres(self) -> bool:
        try:
            conn = self._get_postgres_connection()
        except Exception as e:
            print(f"❌ users: ошибка загрузки: {e}")
            return False
        try:
            with conn, conn.cursor() as cur:
                cur.execute(
                    f"SELECT id, data FROM {self.POSTGRES_TABLE} ORDER BY updated_at"
                )
                rows = cur.fetchall()
            for user_id, data in rows:
                if isinstance(data, str):
                    data = json.loads(data)
                user = User.from_dict(data)
                self.users[user.id] = user
                if user.google_sub:
                    self._by_google_sub[user.google_sub] = user
                if user.login:
                    self._by_login[user.login] = user
            return True
        except Exception as e:
            print(f"❌ users: ошибка загрузки: {e}")
            return False
        finally:
            conn.close()

    def save(self) -> bool:
        if not self.use_postgres:
            return True
        return self._save_to_postgres()

    def load(self) -> bool:
        if not self.use_postgres:
            return True
        return self._load_from_postgres()


def verify_google_id_token(id_token: str,
                           client_id: Optional[str] = None) -> Dict:
    """Проверяет Google ID token и возвращает профиль пользователя.

    Поднимает ValueError, если токен недействителен/истёк или (при заданном
    client_id) выдан другому приложению.
    """
    import requests

    resp = requests.get(GOOGLE_TOKENINFO_URL, params={"id_token": id_token},
                        timeout=10)
    if resp.status_code != 200:
        raise ValueError("Google не подтвердил ID token")
    payload = resp.json()
    if payload.get("error_description") or not payload.get("sub"):
        raise ValueError(payload.get("error_description") or "Некорректный токен")

    if client_id and payload.get("aud") != client_id:
        raise ValueError("ID token выдан другому приложению (aud не совпадает)")

    return payload
