#!/usr/bin/env python3
"""
Одноразовая миграция: перенос гипотез из JSON-файла в PostgreSQL.

Использование:
    DATABASE_URL=postgresql://user:pass@host:5432/dbname \
        python3 migrate_json_to_postgres.py [путь_к_json]

По умолчанию читает hypotheses_data.json (или значение DATA_FILE).
Таблица hypotheses создаётся автоматически, если её ещё нет.
"""

import json
import os
import sys
from pathlib import Path


TABLE = "hypotheses"

# RelaxDev: «TLS не используется… уберите sslmode=require, ssl=true и channel_binding».
_BLOCKED_SSL_PARAMS = frozenset(
    {"sslmode", "ssl", "channel_binding", "sslcert", "sslkey", "sslrootcert"}
)


def _clean_url(db_url: str) -> str:
    """Убирает SSL-параметры из строки подключения (RelaxDev работает без TLS)."""
    import urllib.parse as _urlparse

    parsed = _urlparse.urlsplit(db_url)
    query = [
        (k, v)
        for k, v in _urlparse.parse_qsl(parsed.query, keep_blank_values=True)
        if k.lower() not in _BLOCKED_SSL_PARAMS
    ]
    return _urlparse.urlunsplit(
        (parsed.scheme, parsed.netloc, parsed.path, _urlparse.urlencode(query), parsed.fragment)
    )


def main() -> int:
    db_url = (os.environ.get("DATABASE_URL") or os.environ.get("POSTGRES_URL") or "").strip()
    if not db_url:
        print("❌ Задайте DATABASE_URL перед запуском миграции.")
        return 1

    json_path = (
        sys.argv[1]
        if len(sys.argv) > 1
        else os.environ.get("DATA_FILE", "hypotheses_data.json")
    )

    if not Path(json_path).exists():
        print(f"ℹ️ Файл {json_path} не найден — мигрировать нечего.")
        return 0

    with open(json_path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    if not isinstance(raw, dict):
        print(f"❌ Файл {json_path} имеет неверный формат (ожидался словарь гипотез).")
        return 1

    try:
        import psycopg2
        import psycopg2.extras
    except ImportError:
        print("❌ Библиотека psycopg2 не установлена. Выполните: pip install psycopg2-binary")
        return 1

    conn = psycopg2.connect(_clean_url(db_url), sslmode="disable")
    try:
        with conn, conn.cursor() as cur:
            cur.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {TABLE} (
                    id UUID PRIMARY KEY,
                    data JSONB NOT NULL,
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
                )
                """
            )
            for h_id, h_data in raw.items():
                cur.execute(
                    f"""
                    INSERT INTO {TABLE} (id, data, updated_at)
                    VALUES (%s, %s, now())
                    ON CONFLICT (id)
                    DO UPDATE SET data = EXCLUDED.data, updated_at = now()
                    """,
                    (h_id, psycopg2.extras.Json(h_data)),
                )
    finally:
        conn.close()

    print(f"✅ Миграция завершена: {len(raw)} гипотез перенесено в PostgreSQL.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
