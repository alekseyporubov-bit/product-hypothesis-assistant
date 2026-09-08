# Product Hypothesis Assistant

## 🎯 Система поддержки принятия решений продуктового менеджера

Разработана на основе **TDPD (Test-Driven Product Development)** фреймворка и структуры **ГОСТ 34.602-2026**.

**Версия:** 1.0  
**Статус:** Production Ready (Вариант A - LLM-агент с эвристическим скорингом)  
**Дата:** 12.08.2026

---

## 📋 Содержание

1. [Назначение системы](#назначение-системы)
2. [Основные возможности](#основные-возможности)
3. [Архитектура](#архитектура)
4. [Быстрый старт](#быстрый-старт)
5. [Использование](#использование)
6. [Примеры](#примеры)
7. [API документация](#api-документация)
8. [TDPD Workflow](#tdpd-workflow)
9. [Калибровка системы](#калибровка-системы)
10. [Лицензия и атрибуция](#лицензия-и-атрибуция)

---

## Назначение системы

### Проблема (as-is)
Продакт-менеджер вручную собирает фактуру для обоснования фичи (~40 часов в неделю):
- Сбор доказательств из открытых источников
- Составление плана исследования
- Проектирование анкет опросов
- Подготовка презентации для руководства

**Результат:** 20% фичей после релиза не приносят измеримого эффекта — решения принимаются с недостаточной валидацией на входе.

### Решение (to-be)
**Product Hypothesis Assistant** помогает подготовить количественно обоснованное заключение о потенциале продуктовой гипотезы в виде:
- ✅ **Score уверенности** (0-100)
- ✅ **Подтверждения/опровержения** гипотезы
- ✅ **Рекомендация** (proceed/investigate/reject)
- ✅ **Готовая анкета** для опроса пользователей

**Целевой результат:**
- 📈 Сократить время подготовки обоснования с 40 часов до нескольких часов (сокращение в 6-10 раз)
- 📈 Снизить долю неудачных фичей с 20% до 5% (за счёт лучшей валидации)
- 📈 Подтвердить корреляцию между score и реальным успехом фичи

---

## Основные возможности

| ID | Требование | Статус | Реализовано |
|---|---|---|---|
| F-01 | Приём описания проблемы/идеи фичи | Обязательное | ✅ Диалоговый ввод |
| F-02 | Поиск подтверждений/опровержений в открытых источниках | Обязательное | ✅ Ручной ввод доказательств* |
| F-03 | Формирование score уверенности | Обязательное | ✅ Эвристический скоринг |
| F-04 | Рекомендации по дополнительному исследованию | Обязательное | ✅ Анализ полноты данных |
| F-05 | Генерация примеров вопросов для анкетирования | Обязательное | ✅ Шаблоны вопросов |
| F-06 | Ручной ввод фактического исхода фичи | Обязательное | ✅ Post-release запись |
| F-07 | Альтернативные варианты решений | Опциональное | 🔄 Планируется v2 |
| F-08 | Диалоговый (чат-подобный) режим | Обязательное | ✅ Интерактивное меню |

*Примечание: В production версии рекомендуется интегрировать с API поиска (Google Search, Perplexity AI и т.д.)

---

## Архитектура

### Структура проекта

```
product_hypothesis_assistant.py
├── 1. CONTEXT (Определение контекста и ролей)
│   ├── HypothesisStatus (Enum)
│   ├── EvidenceType (Enum)
│   └── ScoringFactor (Enum)
│
├── 2. DATA MODELS (Структуры данных)
│   ├── Evidence (доказательство)
│   ├── ScoreBreakdown (разложение score)
│   ├── HypothesisScore (итоговая оценка)
│   ├── SurveyQuestion (вопрос опроса)
│   ├── RealWorldOutcome (постфактум результат)
│   └── Hypothesis (основная сущность)
│
├── 3. SCORING ENGINE (Логика вычисления score)
│   └── ScoringEngine.calculate_score()
│       ├── Анализ доказательств
│       ├── Оценка факторов (6 факторов)
│       ├── Взвешивание по importance
│       └── Формирование рекомендации
│
├── 4. HYPOTHESIS MANAGER (Управление гипотезами)
│   ├── create_hypothesis()
│   ├── add_evidence()
│   ├── validate_hypothesis()
│   ├── record_outcome()
│   ├── get_correlation_analysis()
│   └── export_hypothesis()
│
└── 5. INTERACTIVE ASSISTANT (Диалоговый интерфейс)
    ├── start_new_hypothesis()
    ├── add_evidence_interactive()
    ├── generate_survey_template()
    ├── validate_and_score()
    ├── record_outcome_interactive()
    └── show_correlation_analysis()
```

### TDPD Workflow

Система реализует полный TDPD цикл:

```
CONTEXT (Определение контекста)
   ↓
PROBLEM (Формулировка проблемы)
   ├─→ create_hypothesis()
   └─→ Определение целевых пользователей и результатов
   ↓
INPUT (Сбор входных данных)
   └─→ add_evidence()
   └─→ Добавление доказательств разного типа
   ↓
RED (Отрицательные тесты)
   └─→ Анализ противоречащих доказательств
   ↓
GREEN (Позитивные тесты)
   ├─→ validate_hypothesis()
   └─→ calculate_score()
   ↓
OUTPUT/UAT (Приёмка пользователем)
   ├─→ record_outcome()
   └─→ Запись реального результата после релиза
   ↓
CORRELATION CHECK (Проверка гипотез)
   └─→ get_correlation_analysis()
   └─→ Проверка предсказаний vs реальность (Цель 3 ТЗ)
```

---

## Быстрый старт

### Установка

```bash
# Требования: Python 3.7+
python --version

# Скопируйте файлы в ваш проект
cp product_hypothesis_assistant.py ./
cp test_product_hypothesis.py ./
```

### Запуск демонстрации

```bash
# Запуск всех тестов
python test_product_hypothesis.py

# Запуск интерактивной сессии
python product_hypothesis_assistant.py
```

---

## Использование

### Интерактивный режим

```bash
$ python product_hypothesis_assistant.py

======================================================================
Product Hypothesis Assistant v1.0
Система поддержки принятия решений по новым фичам
======================================================================

======================================================================
МЕНЮ
======================================================================
1. Создать новую гипотезу
2. Добавить доказательства
3. Сгенерировать шаблон опроса
4. Валидировать и получить score
5. Записать исход фичи (постфактум)
6. Анализ корреляции score ↔ успех
7. Экспортировать гипотезу (JSON)
8. Список всех гипотез
0. Выход
======================================================================

Выберите опцию: 1
```

### Программный интерфейс

```python
from product_hypothesis_assistant import HypothesisManager, Evidence, EvidenceType

# 1. Создаём менеджер
manager = HypothesisManager()

# 2. Создаём гипотезу
hypothesis = manager.create_hypothesis(
    title="Тёмный режим",
    description="Добавить поддержку тёмного режима",
    problem_statement="Пользователи жалуются на усталость глаз",
    target_users="Активные пользователи",
    expected_outcome="Увеличение времени использования на 15%"
)

# 3. Добавляем доказательства
manager.add_evidence(hypothesis.id, Evidence(
    evidence_type=EvidenceType.USER_FEEDBACK,
    title="Запросы в поддержку",
    description="50+ запросов в месяц о тёмном режиме",
    source="Helpdesk",
    confidence=0.9,
    supports=True
))

# 4. Валидируем и получаем score
success, score = manager.validate_hypothesis(hypothesis.id)

# 5. Выводим результаты
print(f"Score: {score.overall_score}/100")
print(f"Рекомендация: {score.recommendation}")
print(f"Уверенность: {score.confidence_level}")
```

---

## Примеры

### Пример 1: Тёмный режим в приложении

```python
# Создание гипотезы
hypothesis = manager.create_hypothesis(
    title="Тёмный режим в приложении",
    description="Добавить поддержку тёмного режима для мобильного приложения",
    problem_statement="Пользователи жалуются на усталость глаз в тёмное время",
    target_users="Активные пользователи приложения (18-45 лет)",
    expected_outcome="Увеличение времени использования вечером на 15%"
)

# Добавляем доказательства
evidence_list = [
    Evidence(
        evidence_type=EvidenceType.USER_FEEDBACK,
        title="Запросы в поддержку",
        description="50+ запросов в месяц о тёмном режиме",
        source="Helpdesk система",
        confidence=0.9,
        supports=True
    ),
    Evidence(
        evidence_type=EvidenceType.MARKET_RESEARCH,
        title="Исследование конкурентов",
        description="Все топ-приложения имеют тёмный режим",
        source="App Store анализ",
        confidence=0.95,
        supports=True
    ),
    Evidence(
        evidence_type=EvidenceType.ANALYTICS,
        title="Статистика использования",
        description="60% использования приложения происходит после 18:00",
        source="Google Analytics",
        confidence=0.85,
        supports=True
    )
]

for ev in evidence_list:
    manager.add_evidence(hypothesis.id, ev)

# Валидация
success, score = manager.validate_hypothesis(hypothesis.id)

# Результат
# Score: 78.5/100
# Рекомендация: PROCEED (идти в разработку)
# Уверенность: HIGH
```

### Пример 2: Анализ корреляции (Цель 3 ТЗ)

```python
# После 6 месяцев эксплуатации записываем реальные результаты

# Фича была успешной
outcome_success = RealWorldOutcome(
    was_successful=True,
    actual_impact="Увеличение времени сессии на 18%",
    lessons_learned="Тёмный режим был очень востребован"
)
manager.record_outcome(hypothesis.id, outcome_success)

# Фича была неудачной
outcome_fail = RealWorldOutcome(
    was_successful=False,
    actual_impact="Минимальный эффект",
    lessons_learned="Ожидания были переоценены"
)
manager.record_outcome(other_hypothesis.id, outcome_fail)

# Анализируем корреляцию
analysis = manager.get_correlation_analysis()
print(f"Точность предсказаний: {analysis['accuracy_percentage']:.1f}%")
```

---

## API документация

### HypothesisManager

#### `create_hypothesis(title, description, problem_statement, target_users, expected_outcome) → Hypothesis`

Создаёт новую гипотезу (Context + Problem этапы TDPD).

**Параметры:**
- `title` (str): Название фичи
- `description` (str): Краткое описание (1-2 предложения)
- `problem_statement` (str): Какую проблему решает
- `target_users` (str): Целевые пользователи
- `expected_outcome` (str): Ожидаемый результат

**Возвращает:** `Hypothesis` объект с уникальным ID

---

#### `add_evidence(hypothesis_id, evidence) → bool`

Добавляет доказательство в поддержку гипотезы (Input этап TDPD).

**Параметры:**
- `hypothesis_id` (str): ID гипотезы
- `evidence` (Evidence): Объект доказательства

**Возвращает:** True/False

---

#### `validate_hypothesis(hypothesis_id) → Tuple[bool, Optional[HypothesisScore]]`

Валидирует гипотезу и вычисляет score (Red/Green этапы TDPD).

**Параметры:**
- `hypothesis_id` (str): ID гипотезы

**Возвращает:** Кортеж (success, score)

**Выходные данные score:**
```python
{
    "overall_score": 78.5,      # 0-100
    "confidence_level": "high",  # low/medium/high
    "recommendation": "proceed", # proceed/investigate/reject
    "breakdown": [
        {
            "factor": "problem_severity",
            "score": 7.5,
            "rationale": "Найдено 3 доказательства...",
            "evidence_count": 3
        },
        # ... другие факторы
    ],
    "supporting_evidence_count": 5,
    "contradicting_evidence_count": 0,
    "data_completeness": 0.6,
    "recommendation": "proceed"
}
```

---

#### `record_outcome(hypothesis_id, outcome) → bool`

Записывает фактический исход фичи после релиза (Output/UAT этап TDPD).

**Параметры:**
- `hypothesis_id` (str): ID гипотезы
- `outcome` (RealWorldOutcome): Объект результата

**Возвращает:** True/False

---

#### `get_correlation_analysis() → Dict`

Анализирует корреляцию между score и реальным исходом (Цель 3 ТЗ).

**Возвращает:**
```python
{
    "total_completed": 10,
    "correct_predictions": 8,
    "accuracy_percentage": 80.0,
    "data": [
        {
            "hypothesis_id": "uuid",
            "title": "Тёмный режим",
            "predicted_recommendation": "proceed",
            "predicted_score": 78.5,
            "actual_outcome": True,
            "correlation_match": True
        },
        # ... другие гипотезы
    ]
}
```

---

### Evidence (Доказательство)

```python
@dataclass
class Evidence:
    id: str                          # Уникальный ID
    evidence_type: EvidenceType      # Тип доказательства
    title: str                       # Название
    description: str                 # Описание
    source: str                      # Источник информации
    confidence: float                # 0-1, уверенность в доказательстве
    supports: bool                   # Поддерживает (True) или опровергает (False)
    created_at: datetime             # Дата создания
```

**Типы доказательств (EvidenceType):**
- `MARKET_RESEARCH` - Исследование рынка
- `USER_FEEDBACK` - Обратная связь пользователей
- `COMPETITOR_ANALYSIS` - Анализ конкурентов
- `ANALYTICS` - Данные аналитики
- `EXPERT_OPINION` - Мнение эксперта
- `CASE_STUDY` - Case study успеха

---

### ScoringFactor (Факторы скоринга)

Система оценивает гипотезу по 6 факторам:

1. **PROBLEM_SEVERITY** (20% веса) - Серьёзность проблемы
2. **MARKET_SIZE** (15% веса) - Размер рынка
3. **USER_DEMAND** (25% веса) - Спрос пользователей
4. **COMPETITIVE_ADVANTAGE** (15% веса) - Конкурентное преимущество
5. **IMPLEMENTATION_EFFORT** (15% веса) - Усилия реализации
6. **ALIGNMENT** (10% веса) - Соответствие стратегии

---

## TDPD Workflow

### Этап 1: CONTEXT (Определение контекста)

**Цель:** Понять контекст и роли в процессе.

```python
# Система определяет контекст через enum'ы
class HypothesisStatus(Enum):
    DRAFT = "draft"                    # Черновик
    IN_RESEARCH = "in_research"        # На исследовании
    VALIDATED = "validated"            # Валидирована
    REJECTED = "rejected"              # Отклонена
    IN_DEVELOPMENT = "in_development"  # На разработке
    RELEASED = "released"              # В production
    COMPLETED = "completed"            # Закончена (с результатом)
```

### Этап 2: PROBLEM (Формулировка проблемы)

**Цель:** Определить проблему, которую решает фича.

```python
hypothesis = manager.create_hypothesis(
    title="Название фичи",
    problem_statement="Какую проблему решает",
    target_users="Кто целевые пользователи",
    expected_outcome="Какой результат ожидается"
)
```

### Этап 3: INPUT (Сбор входных данных)

**Цель:** Собрать доказательства и данные для валидации.

```python
manager.add_evidence(hypothesis.id, evidence)
manager.add_survey_question(hypothesis.id, question)
```

### Этап 4: RED/GREEN (Проверка гипотез)

**Цель:** Провести тесты гипотезы на доказательствах.

```python
success, score = manager.validate_hypothesis(hypothesis.id)
```

Система проверяет:
- ✅ GREEN: Есть ли поддерживающие доказательства
- ❌ RED: Есть ли противоречащие доказательства

### Этап 5: OUTPUT/UAT (Приёмка пользователем)

**Цель:** Получить одобрение от ответственного человека (продакта).

```python
# На основе score система выдаёт рекомендацию
if score.recommendation == "proceed":
    # Идти в разработку
    pass
elif score.recommendation == "investigate":
    # Требуется дополнительное исследование
    pass
else:
    # Отклонить
    pass
```

### Этап 6: CORRELATION CHECK (Проверка корреляций)

**Цель:** Проверить, соответствуют ли предсказания реальности (Цель 3 ТЗ).

```python
# Записываем реальный результат после релиза
manager.record_outcome(hypothesis.id, outcome)

# Анализируем корреляцию
analysis = manager.get_correlation_analysis()
# Показывает, насколько точны предсказания система
```

---

## Калибровка системы

### Веса факторов (FACTOR_WEIGHTS)

Текущие веса (требуют калибровки на реальных данных):

```python
FACTOR_WEIGHTS = {
    ScoringFactor.PROBLEM_SEVERITY: 0.20,           # 20%
    ScoringFactor.MARKET_SIZE: 0.15,                # 15%
    ScoringFactor.USER_DEMAND: 0.25,                # 25% (наиболее важный)
    ScoringFactor.COMPETITIVE_ADVANTAGE: 0.15,      # 15%
    ScoringFactor.IMPLEMENTATION_EFFORT: 0.15,      # 15%
    ScoringFactor.ALIGNMENT: 0.10,                  # 10%
}
```

### Пороги уверенности

```python
if score >= 70:
    confidence_level = "high"
    recommendation = "proceed"          # Идти в разработку

elif score >= 50:
    confidence_level = "medium"
    recommendation = "investigate"      # Требуется доисследование

else:
    confidence_level = "low"
    recommendation = "reject"           # Отклонить
```

### Калибровка на реальных данных

После 6+ месяцев эксплуатации с регулярной записью исходов:

1. Используйте `get_correlation_analysis()` для проверки точности
2. Если accuracy < 75%, отрегулируйте веса факторов
3. Пересчитайте пороги уверенности
4. Обновите формулу скоринга в `ScoringEngine.calculate_score()`

**Пример калибровки:**
```python
# Текущая точность: 65%
# План: Увеличить вес USER_DEMAND с 0.25 до 0.30
# Уменьшить вес IMPLEMENTATION_EFFORT с 0.15 до 0.10

FACTOR_WEIGHTS = {
    ScoringFactor.PROBLEM_SEVERITY: 0.20,
    ScoringFactor.MARKET_SIZE: 0.15,
    ScoringFactor.USER_DEMAND: 0.30,        # ↑ увеличили
    ScoringFactor.COMPETITIVE_ADVANTAGE: 0.15,
    ScoringFactor.IMPLEMENTATION_EFFORT: 0.10,  # ↓ уменьшили
    ScoringFactor.ALIGNMENT: 0.10,
}
```

---

## Расширения и Интеграции

### Планируемые интеграции (v2)

- [ ] **Web Search API** (Google Search, Perplexity AI) для автоматического поиска доказательств
- [ ] **LLM Integration** (GPT-4, Claude) для синтеза информации и генерации вопросов
- [ ] **Database** (PostgreSQL) для хранения гипотез
- [ ] **REST API** для интеграции с другими системами
- [ ] **Webhook** для интеграции с analytics (Segment, Mixpanel и т.д.)
- [ ] **Alternative Solutions Generator** (F-07) для предложения альтернативных решений

### Вариант B (для будущих версий)

Модульный pipeline с явной формулой скоринга:
1. Декомпозиция запроса
2. Поиск и классификация надёжности источников
3. Агрегация доказательств по явным весам
4. Генерация анкет по шаблонам
5. Модуль сбора обратной связи

---

## Лицензия и атрибуция

### Основа

- **TDPD Framework:** [github.com/InnokentyB/tdpd-product-framework](https://github.com/InnokentyB/tdpd-product-framework)
  - Автор: Innokenty Bodrov
  - Лицензия: Требует определения (см. исходный репозиторий)

- **Структура ТЗ:** ГОСТ 34.602-2026 и ГОСТ 19.201-78
  - Источники: [leantech.ai](https://leantech.ai/blog/tehnicheskoe-zadanie-gost-34-razrabotka-po-2026), [habr.com](https://habr.com/ru/articles/769648/)

### Компоненты системы

| Компонент | Автор | Лицензия |
|---|---|---|
| TDPD Workflow | Innokenty Bodrov | TBD |
| Product Hypothesis Assistant | Разработка 2026 | TBD |

---

## Контрибьютинг

Приветствуются:
- 🐛 Отчёты об ошибках через issues
- 📝 Предложения по улучшению
- 📚 Улучшения документации
- 🧪 Дополнительные тесты и примеры

---

## Часто задаваемые вопросы (FAQ)

### Q: Почему score зависит от количества доказательств?
**A:** Система предполагает, что больше качественных доказательств = более точная оценка. Однако веса можно отрегулировать после калибровки на реальных данных.

### Q: Что если нет доказательств, опровергающих гипотезу?
**A:** Это нормально. Система анализирует и поддерживающие и противоречащие доказательства. Отсутствие негативных — это хороший знак.

### Q: Как быстро калибровать систему?
**A:** Минимум 5-10 фичей с записанными исходами (через 6+ месяцев). Рекомендуется собрать 20-30 для точной калибровки.

### Q: Можно ли использовать только автоматизированный поиск доказательств?
**A:** Да, в v2 планируется интеграция с LLM и Web Search API. Текущая версия требует ручного ввода для большей контроля.

### Q: Совместима ли система с нашим BI?
**A:** Да, вы можете экспортировать гипотезы в JSON и интегрировать с вашими системами. В v2 планируется REST API и Webhook'и.

---

## Поддержка

Если у вас есть вопросы или предложения, создайте issue в репозитории или свяжитесь с командой разработки.

**Дата последнего обновления:** 12.08.2026  
**Версия:** 1.0  
**Автор:** TDPD Product Framework adaption
