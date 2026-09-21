# TDPD — Рабочая инструкция агента (для этого репозитория)

> Личная выжимка правил фреймворка **TDPD (Test-Driven Product Development)**, автор — Innokenty Bodrov
> (https://github.com/InnokentyB/tdpd-product-framework). Обязательна к применению при **любой** задаче
> на добавление/изменение функциональности в **Product Hypothesis Assistant** (этот репозиторий).
>
> Полный текст фреймворка: `.tdpd/core/*.md` (METHOD, CONTEXT, GATES, WORKFLOW, ROLES, ORCHESTRATION, RECOVERY)
> и `.tdpd/templates/*` (шаблоны артефактов). Прикладной подробный playbook: `TDPD_FRAMEWORK_PLAYBOOK.md`.
> Точка входа агента: `AGENTS.md` (корень репо).

---

## 0. Главное (прочитываю перед каждой задачей)

1. **Планирование (Plan) и аудит (Audit) НЕ дают права писать код.** Реализация — только в режиме Deliver.
2. Без **зелёных исполняемых сценариев** + **явного человеческого UAT** статус — только
   `engineering complete, awaiting UAT`. Никогда не заявлять «готово».
3. Прохождение тестов ≠ доказанная ценность продукта. Финальный вердикт — человек через UAT.
4. Не ослаблять тесты ради «зелёного». Сначала **доказать Red** (тест падает именно из-за отсутствия
   нужного поведения), потом Green.

---

## 1. Режимы работы (выбираю явно в начале задачи)

| Режим | Делаю | Не делаю |
|---|---|---|
| **Shape** | Проверяю проблему и самое рискованное допущение, выбираю минимальный полезный срез | не пишу код |
| **Plan** | Source map → context pack → findings → decision log → спецификация → scenario matrix → ADR | не имплементирую |
| **Deliver** | Red → Green → верификация → handoff на UAT | не пропускаю Red-доказательство |
| **Audit** | Проверяю доказательства по гейтам, предлагаю путь восстановления | не меняю файлы без запроса |

---

## 2. Канонический пайплайн

```
Business problem → Specification → User scenarios → E2E tests → Agent implementation → Acceptance (UAT)
```

Non-negotiable принципы (`.tdpd/core/METHOD.md`):
- Согласовать противоречащие источники **до** разработки; не выдумывать факты.
- Нетестируемый сценарий = «хотелка», пока нет наблюдаемого критерия или явной пометки «ручная проверка».
- Человеческое суждение — на входе (архитектура) и выходе (UAT), а не построчный ревью каждого шага агента.
- Сохранять трассируемость от бизнес-ценности до evidence приёмки.

---

## 3. Гейты поставки (Definition of Done для фичи, `.tdpd/core/GATES.md`)

1. **Context** — source map + атомарный context pack + review findings + decision log + traceability.
   Каждый факт имеет локатор источника или помечен `NO SOURCE`.
2. **Problem** — actor + реальная боль/job + текущий workaround + желаемый результат + наблюдаемый сигнал успеха.
3. **Input** — согласованный evidence, детерминированное поведение, тестируемые критерии приёмки,
   явные non-goals, одобренные архитектурные решения.
4. **Red** — исполняемые сценарии, падающие именно из-за отсутствующего поведения (не из-за окружения/фикстур).
5. **Green** — целевые e2e + соразмерные более широкие проверки проходят; жёсткое вето на проблемы
   авторизации/безопасности/целостности данных/миграций/платежей/деструктивных операций/отката.
6. **Output/UAT** — человек подтверждает результат в реалистичном сценарии, сверяя с исходной проблемой.

---

## 4. Трассируемость (stable ID везде, где нетривиально)

```
S → F/C/G/A/R → DL → PROB → RULE → SCN → E2E/MANUAL → WORK/HANDOFF → UAT
```

- `S` источник → `F/C/G/A/R` факт/противоречие/пробел/неоднозначность/риск → `DL` решение → `PROB` проблема
  → `RULE` правило → `SCN` сценарий → `E2E/MANUAL` тест/ручная проверка → `WORK/HANDOFF` работа/передача → `UAT` приёмка.
- Шаблоны артефактов: `.tdpd/templates/source-map.md`, `system-context-pack.md`, `review-findings.md`,
  `decision-log.md`, `specification.md`, `scenario-matrix.md`, `traceability-matrix.md`, `product-brief.md`,
  `architecture-decision.md`, `delivery-evidence.md`, `work-unit.md`, `handoff.md`, `uat-record.md`.

---

## 5. Карта проекта (что где лежит)

| Область | Файл(ы) | Примечание |
|---|---|---|
| Точка входа API | `app.py` | Flask; эндпоинты `/api/*` |
| Ядро | `product_hypothesis_assistant.py` | `HypothesisManager`, `Evidence`, `ScoringEngine`, `HypothesisScore`, `RealWorldOutcome`, `SurveyQuestion`; persistence в PostgreSQL |
| Поиск источников | `research_finder.py` | `ResearchFinder` (демо-режим, реальные запросы выключены по умолчанию) |
| UI | `templates/index.html`, `templates/help.html`, `static/script.js`, `static/style.css` | ванильный JS/CSS, без фронт-фреймворка |
| Данные | PostgreSQL (таблица `hypotheses`, JSONB) | БД; подключается через `DATABASE_URL` |
| Сценарии пользователя | `USER_STORIES.md` | Story #1–#6 (Gherkin) — основа Problem/Scenario гейтов |
| Описание системы | `README_PRODUCT_HYPOTHESIS_ASSISTANT.md`, `QUICKSTART.md` | таблица требований F-01…F-08 |
| Тесты | `test_*.py` | **не pytest** — самостоятельные скрипты, печатают «✓ ТЕСТ ПРОЙДЕН», запуск `python3 test_xxx.py` |
| Зависимости | `requirements.txt` | Flask 2.3.3, Werkzeug, requests, gunicorn, python-dotenv, mcp |

Основные эндпоинты API: `/api/create-hypothesis`, `/api/get-hypothesis/<id>`, `/api/add-evidence`,
`/api/validate-hypothesis/<id>`, `/api/research-sources/<id>`, `/api/scan-research/<id>`,
`/api/record-outcome`, `/api/correlation-analysis`, `/api/list-hypotheses`, `/api/export-hypothesis/<id>`,
`/api/evidence-types`.

---

## 6. Чек-лист «добавить фичу в этот проект»

1. **Context** — свериться с `USER_STORIES.md` и таблицей F-01…F-08 (не дублировать существующий функционал);
   для новых требований зафиксировать источник (`S00N` = тикет/сообщение пользователя).
2. **Problem** — actor (Product Manager) + боль + желаемый результат + метрика успеха
   (цели ТЗ: сокращение времени обоснования, снижение доли неудачных фич, точность предсказаний > 75%).
3. **Input** — описать правило(а) в стиле `.tdpd/templates/specification.md` (детерминированное поведение
   эндпоинта/UI, включая пустые/ошибочные состояния; например «гипотеза не найдена → 404 + {success:false}»).
4. **Red** — написать/расширить `test_*.py` (или Gherkin в стиле `USER_STORIES.md`), чтобы он **падал**
   до реализации именно из-за отсутствия нужной логики. Зафиксировать Red-доказательство.
5. **Green** — реализовать минимально достаточное изменение (`product_hypothesis_assistant.py` / `app.py` /
   `templates/`), прогнать новые и существующие тесты (например `python3 test_product_hypothesis.py`,
   `python3 test_postgres_persistence.py`).
6. **Output/UAT** — явно сообщить «engineering complete, awaiting UAT» + как проверить вручную (curl-пример/шаги UI).
7. **Документация** — обновить `README.md`, `USER_STORIES.md`, `README_PRODUCT_HYPOTHESIS_ASSISTANT.md`
   (таблица F-xx), если изменилось поведение API/UI.

---

## 7. Жёсткие стопы этого проекта (хард-стопы → стоп, уточнить у человека)

- **Не терять данные гипотез** — единственное хранилище таблица `hypotheses` в PostgreSQL; без бэкапа/миграции не удалять.
- **Не менять формулу `ScoringEngine.calculate_score()` / веса `FACTOR_WEIGHTS`** без фиксации `DL-###`
  (влияет на бизнес-метрику — корреляция score↔реальность, целевая точность > 75%).
- **Любое изменение публичного контракта `/api/*`** фиксировать как `RULE-###`/`ADR`
  (на него завязаны `static/js`, `mcp_hypothesis_server.py`, `contentops_publisher.py`).
- Секреты, авторизация, миграции, биллинг, деструктивные операции, production-данные, проваленные
  relevant-тесты — hard stop (по фреймворку).

---

## 8. Формат итогового отчёта по задаче

1. Что изучено / какие источники учтены.
2. Выбранный режим и почему.
3. Пройденные гейты (Context→Problem→Input→Red→Green) с артефактами/ID.
4. Red-доказательство (что падало и почему).
5. Green-доказательство (какие проверки прошли, какие — нет).
6. Статус: **engineering complete, awaiting UAT** (пока человек не подтвердил) + шаги ручной проверки.
