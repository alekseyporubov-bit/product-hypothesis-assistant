# 🗄️ Сохранение гипотез в PostgreSQL (RelaxDev)

## Что изменилось

Раньше гипотезы сохранялись в JSON-файл (`hypotheses_data.json`). На RelaxDev
файловая система контейнера **эфемерная**: при каждом редеплое файл стирался,
поэтому данные терялись.

Теперь, если задана переменная окружения `DATABASE_URL`, все гипотезы
сохраняются в **PostgreSQL** и переживают редеплой. Если `DATABASE_URL` не
задана — приложение работает как раньше (JSON-файл), поэтому локальная
разработка и старые тесты не ломаются.

| Условие | Куда сохраняются данные |
|---|---|
| `DATABASE_URL` задан | PostgreSQL |
| `DATABASE_URL` не задан | JSON-файл (старое поведение) |

## Структура хранения

Таблица `hypotheses` создаётся **автоматически** при первом старте приложения
(идемпотентный `CREATE TABLE IF NOT EXISTS`), SQL руками выполнять не нужно:

```sql
CREATE TABLE IF NOT EXISTS hypotheses (
    id UUID PRIMARY KEY,
    data JSONB NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

Одна гипотеза = одна строка. Полный документ гипотезы (evidence, score,
survey_questions, auto_research_sources, outcome) лежит в колонке `data` (JSONB).

---

## 📋 Пошаговая инструкция для RelaxDev

### Шаг 1. Добавьте базу (вы уже сделали)
На RelaxDev база добавляется в разделе **«Базы данных»** проекта.

### Шаг 2. Скопируйте строку подключения
В разделе **«Базы данных»** проекта найдите строку подключения PostgreSQL.
Она выглядит так:

```
postgresql://u_xxxxx:ПАРОЛЬ@db-xxx:5432/db_product_hypothesis_assistant
```

> ⚠️ **Важно про TLS (RelaxDev):** база доступна только из внутренней сети, и
> **TLS не используется**. Не добавляйте в строку `sslmode=require`, `ssl=true`
> или `channel_binding` — с ними подключение упадёт с ошибкой
> `server does not support SSL connections`. Код уже сам принудительно
> отключает SSL (`sslmode=disable`) и вырезает эти параметры, поэтому просто
> вставьте строку как есть.

### Шаг 3. Задайте переменную окружения
Откройте проект → **Настройки → Переменные окружения (env)** и добавьте
переменную:

```
Ключ:   DATABASE_URL
Знач.:  postgresql://u_xxxxx:ПАРОЛЬ@db-xxx:5432/db_product_hypothesis_assistant
```

Подставьте **свой** пароль вместо `••••••` из панели RelaxDev. Если RelaxDev уже
сам добавил переменную с базой (например, `DATABASE_URL` или `POSTGRES_URL`) —
проверьте, что она присутствует: код читает обе.

### Шаг 4. Передеплойте
Нажмите **«Запустить редеплой»** (или сделайте `git push`, если включён
автодеплой). При старте приложение само создаст таблицу и начнёт писать в БД.

### Шаг 5. Проверьте
```bash
# 1) Здоровье приложения
curl https://YOUR_APP.relaxdev.ru/health

# 2) Создайте гипотезу
curl -X POST https://YOUR_APP.relaxdev.ru/api/create-hypothesis \
  -H "Content-Type: application/json" \
  -d '{"title": "Проверка БД", "description": "Тест"}'

# 3) Сделайте редеплой в панели RelaxDev

# 4) Убедитесь, что гипотеза не пропала
curl https://YOUR_APP.relaxdev.ru/api/list-hypotheses
```

Если после редеплоя гипотеза осталась в списке — сохранение в БД работает. ✅

---

## 💾 Перенос старых данных из JSON (необязательно)

На RelaxDev эфемерная файловая система, поэтому старых JSON-файлов на сервере
нет — мигрировать нечего. Но если у вас есть локальный `hypotheses_data.json`,
перенесите его в БД одним скриптом:

```bash
pip install psycopg2-binary

DATABASE_URL=postgresql://user:password@host:5432/dbname \
  python3 migrate_json_to_postgres.py
```

---

## 🧪 Тесты

```bash
# Критический сценарий: сохранение в PostgreSQL + «редеплой»
DATABASE_URL=postgresql://user:password@host:5432/dbname \
  python3 test_postgres_persistence.py

# Старые тесты (JSON-режим, без БД) — должны остаться зелёными
python3 test_persistence.py
python3 test_persistence_simple.py
python3 test_ui_persistence.py
```

---

## 🔧 Возможные проблемы

| Симптом | Причина / решение |
|---|---|
| `psycopg2 not found` в логах | Зависимость `psycopg2-binary` не установилась. Убедитесь, что она есть в `requirements.txt` (уже добавлена), и передеплойте. |
| `connection refused` / `could not connect` | Неверный `DATABASE_URL` или база не привязана к проекту. Проверьте хост/порт/пароль в «Базы данных». |
| `server does not support SSL connections` | В строке подключения остались `sslmode=require` / `ssl=true`. Уберите их (на RelaxDev TLS выключен) — код сам отключает SSL. |
| Таблица не создаётся | У пользователя БД нет прав `CREATE`. Выдайте права или создайте таблицу вручную SQL-ом выше. |
| Приложение падает при старте | В логах RelaxDev будет точная ошибка подключения к БД — проверьте `DATABASE_URL`. |
