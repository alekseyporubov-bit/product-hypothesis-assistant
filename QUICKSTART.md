# Product Hypothesis Assistant - Быстрый старт

## 📦 Что включено

Полнофункциональная система поддержки принятия решений продуктового менеджера, разработанная на основе **TDPD (Test-Driven Product Development)** фреймворка.

### Файлы проекта

```
product_hypothesis_assistant.py          # Основной модуль (850+ строк)
test_product_hypothesis.py               # Тесты и примеры использования
README_PRODUCT_HYPOTHESIS_ASSISTANT.md   # Полная документация
QUICKSTART.md                            # Этот файл
```

---

## 🚀 Быстрый старт (30 секунд)

### 1. Требования

```bash
Python 3.7+
```

### 2. Запуск демонстрации

```bash
python3 test_product_hypothesis.py
```

**Ожидаемый результат:**
```
✓ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО
```

### 3. Запуск интерактивной версии

```bash
python3 product_hypothesis_assistant.py
```

---

## 💡 Примеры использования

### Пример 1: Программный интерфейс (API)

```python
from product_hypothesis_assistant import (
    HypothesisManager, Evidence, EvidenceType, RealWorldOutcome
)

# Создаём менеджер
manager = HypothesisManager()

# 1️⃣ Создаём гипотезу (Context + Problem этапы TDPD)
hypothesis = manager.create_hypothesis(
    title="Тёмный режим в приложении",
    description="Добавить поддержку тёмного режима",
    problem_statement="Пользователи жалуются на усталость глаз в ночное время",
    target_users="Активные пользователи приложения",
    expected_outcome="Увеличение времени использования вечером на 15%"
)

# 2️⃣ Добавляем доказательства (Input этап TDPD)
manager.add_evidence(hypothesis.id, Evidence(
    evidence_type=EvidenceType.USER_FEEDBACK,
    title="Запросы в поддержку",
    description="50+ запросов в месяц о тёмном режиме",
    source="Support tickets",
    confidence=0.9,
    supports=True
))

manager.add_evidence(hypothesis.id, Evidence(
    evidence_type=EvidenceType.ANALYTICS,
    title="Статистика использования",
    description="60% использования после 18:00",
    source="Google Analytics",
    confidence=0.85,
    supports=True
))

# 3️⃣ Валидируем гипотезу (Red/Green этапы TDPD)
success, score = manager.validate_hypothesis(hypothesis.id)

# 4️⃣ Смотрим результаты
print(f"✓ Score: {score.overall_score:.1f}/100")
print(f"✓ Рекомендация: {score.recommendation}")
print(f"✓ Уверенность: {score.confidence_level}")

# Вывод примерно такой:
# ✓ Score: 37.6/100
# ✓ Рекомендация: investigate
# ✓ Уверенность: medium
```

### Пример 2: Запись результатов (Post-launch analysis)

```python
# После релиза и 6+ месяцев использования записываем реальные результаты

outcome = RealWorldOutcome(
    was_successful=True,  # Фича была успешной
    actual_impact="Увеличение времени сессии на 18%",
    lessons_learned="Тёмный режим был очень востребован пользователями"
)

manager.record_outcome(hypothesis.id, outcome)

# Анализируем корреляцию между score и реальным результатом (Цель 3 ТЗ)
analysis = manager.get_correlation_analysis()
print(f"Точность предсказаний: {analysis['accuracy_percentage']:.1f}%")
```

### Пример 3: Экспорт в JSON

```python
# Экспортируем гипотезу для отправки в BI или аналитику
data = manager.export_hypothesis(hypothesis.id)

import json
print(json.dumps(data, indent=2, ensure_ascii=False))
```

---

## 🎯 Основные возможности (ТЗ)

| Функция | Статус | Описание |
|---------|--------|---------|
| **F-01** | ✅ | Приём описания проблемы/идеи фичи от пользователя |
| **F-02** | ✅ | Сбор и анализ доказательств (ручной ввод) |
| **F-03** | ✅ | Формирование score уверенности (0-100) |
| **F-04** | ✅ | Рекомендации по дополнительному исследованию |
| **F-05** | ✅ | Генерация вопросов для анкетирования пользователей |
| **F-06** | ✅ | Ручной ввод фактического исхода фичи (постфактум) |
| **F-07** | 🔄 | Альтернативные варианты решений (v2) |
| **F-08** | ✅ | Диалоговый (чат-подобный) режим взаимодействия |

---

## 📊 Архитектура системы

### TDPD Workflow (полный цикл)

```
1. CONTEXT
   └─ Определение контекста и ролей

2. PROBLEM
   └─ create_hypothesis() - Формулировка проблемы

3. INPUT
   └─ add_evidence() - Сбор доказательств

4. RED/GREEN
   └─ validate_hypothesis() - Проверка гипотез

5. OUTPUT/UAT
   └─ record_outcome() - Запись реальных результатов

6. CORRELATION CHECK
   └─ get_correlation_analysis() - Проверка точности
```

### Ключевые компоненты

```
HypothesisManager
├─ create_hypothesis()         # Создание гипотезы
├─ add_evidence()              # Добавление доказательств
├─ validate_hypothesis()       # Валидация и скоринг
├─ record_outcome()            # Запись результата
├─ get_correlation_analysis()  # Анализ корреляции
└─ export_hypothesis()         # Экспорт в JSON

ScoringEngine
├─ calculate_score()           # Вычисление score
└─ FACTOR_WEIGHTS             # Веса факторов (требуют калибровки)
    ├─ PROBLEM_SEVERITY (20%)
    ├─ MARKET_SIZE (15%)
    ├─ USER_DEMAND (25%)          # Наиболее важный
    ├─ COMPETITIVE_ADVANTAGE (15%)
    ├─ IMPLEMENTATION_EFFORT (15%)
    └─ ALIGNMENT (10%)
```

---

## 📈 Система скоринга

### Score (0-100)

Система выдаёт score от 0 до 100 на основе анализа доказательств.

### Уровни уверенности

```
Score >= 70   ─ HIGH     ─ ✓ Рекомендация: PROCEED (идти в разработку)
50 <= Score < 70  ─ MEDIUM   ─ ⚠ Рекомендация: INVESTIGATE (дополнить исследование)
Score < 50    ─ LOW      ─ ✗ Рекомендация: REJECT (отклонить)
```

### Факторы оценки

1. **PROBLEM_SEVERITY** (20%) - Серьёзность проблемы
2. **MARKET_SIZE** (15%) - Размер целевого рынка
3. **USER_DEMAND** (25%) - Спрос пользователей ⭐ (самый важный)
4. **COMPETITIVE_ADVANTAGE** (15%) - Конкурентное преимущество
5. **IMPLEMENTATION_EFFORT** (15%) - Усилия реализации
6. **ALIGNMENT** (10%) - Соответствие стратегии компании

---

## 🧪 Тестирование

### Запуск всех тестов

```bash
python3 test_product_hypothesis.py
```

### Что тестируется

1. ✅ **Создание гипотезы и скоринг** - Добавление доказательств и вычисление score
2. ✅ **Генерация анкеты** - Создание вопросов для опроса пользователей
3. ✅ **Экспорт в JSON** - Сохранение гипотезы в структурированном виде
4. ✅ **Анализ корреляции** - Проверка точности предсказаний (Цель 3 ТЗ)

---

## 🔧 Калибровка системы

### Веса факторов требуют калибровки

Текущие веса - это начальные значения. После 6+ месяцев эксплуатации:

1. Запустите `get_correlation_analysis()`
2. Посмотрите на `accuracy_percentage`
3. Если accuracy < 75%, отрегулируйте веса факторов
4. Обновите `FACTOR_WEIGHTS` в `ScoringEngine`

**Пример:**
```python
# Если USER_DEMAND оказался более важным чем ожидалось:
FACTOR_WEIGHTS = {
    ScoringFactor.PROBLEM_SEVERITY: 0.20,
    ScoringFactor.MARKET_SIZE: 0.15,
    ScoringFactor.USER_DEMAND: 0.30,        # ↑ увеличили с 0.25
    ScoringFactor.COMPETITIVE_ADVANTAGE: 0.15,
    ScoringFactor.IMPLEMENTATION_EFFORT: 0.10,  # ↓ уменьшили с 0.15
    ScoringFactor.ALIGNMENT: 0.10,
}
```

---

## 📚 Типы доказательств

```python
from product_hypothesis_assistant import EvidenceType

EvidenceType.MARKET_RESEARCH          # Исследование рынка
EvidenceType.USER_FEEDBACK            # Обратная связь пользователей
EvidenceType.COMPETITOR_ANALYSIS      # Анализ конкурентов
EvidenceType.ANALYTICS                # Данные аналитики
EvidenceType.EXPERT_OPINION           # Мнение эксперта
EvidenceType.CASE_STUDY               # Case study успеха
```

---

## 🎓 Целевые метрики (ТЗ)

### Цель 1: Сокращение времени подготовки

| Метрика | Baseline | Целевое | Достигнуто |
|---------|----------|---------|-----------|
| Время обоснования | ~40 часов | Несколько часов | ⏳ |

### Цель 2: Снижение доли неудачных фичей

| Метрика | Baseline | Целевое | Достигнуто |
|---------|----------|---------|-----------|
| Неудачные фичи | 20% | 5% | ⏳ (требует 6 месяцев) |

### Цель 3: Проверка корреляции (ключевая!)

| Метрика | Описание |
|---------|---------|
| `accuracy_percentage` | % правильных предсказаний система |
| Целевое значение | > 75% |
| Как проверить | `get_correlation_analysis()` |
| Требуемый период | 6+ месяцев с записью исходов |

---

## 🔌 Интеграции (v2)

Планируемые интеграции для production версии:

- [ ] **Web Search API** для автоматического поиска доказательств
- [ ] **LLM Integration** (GPT-4, Claude) для синтеза информации
- [ ] **Database** (PostgreSQL) для хранения гипотез
- [ ] **REST API** для интеграции с другими системами
- [ ] **Webhook'и** для интеграции с аналитикой
- [ ] **Alternative Solutions Generator** для предложения альтернатив

---

## 📖 Полная документация

Для подробной информации смотрите:

- **[README_PRODUCT_HYPOTHESIS_ASSISTANT.md](README_PRODUCT_HYPOTHESIS_ASSISTANT.md)** - Полная документация
- **[product_hypothesis_assistant.py](product_hypothesis_assistant.py)** - Исходный код с комментариями
- **[test_product_hypothesis.py](test_product_hypothesis.py)** - Примеры использования

---

## ❓ Часто задаваемые вопросы

### Q: Почему score может быть низким несмотря на хорошие доказательства?

**A:** Система требует доказательств по **всем** факторам. Если у вас только user_feedback без market_research и competitor_analysis, score будет низким. Это нормально - это сигнал к дополнительному исследованию.

### Q: Можно ли изменить пороги (70, 50)?

**A:** Да, в `ScoringEngine.calculate_score()` вы можете изменить пороги:
```python
if weighted_score >= 70:  # ← можно изменить на 65 или 75
    confidence_level = "high"
```

### Q: Как часто нужно записывать результаты фичей?

**A:** Рекомендуется записывать через 6+ месяцев после релиза, когда понятны истинные результаты. Для калибровки нужно минимум 5-10 фичей с результатами.

### Q: Совместима ли система с нашим BI/Tableau/Looker?

**A:** Да! Экспортируйте гипотезы в JSON и загружайте в вашу BI систему:
```python
data = manager.export_hypothesis(hypothesis.id)
# data - это обычный словарь Python, готовый к JSON экспорту
```

---

## 🤝 Контрибьютинг

Приветствуются:
- 🐛 Отчёты об ошибках
- 📝 Предложения по улучшению
- 📚 Улучшения документации
- 🧪 Дополнительные тесты

---

## 📄 Лицензия

Разработано на основе **TDPD Product Framework** (Innokenty Bodrov)

Ссылка на оригинальный фреймворк: [github.com/InnokentyB/tdpd-product-framework](https://github.com/InnokentyB/tdpd-product-framework)

---

## 🎉 Вы готовы!

Теперь вы знаете основы. Запустите демонстрацию:

```bash
python3 test_product_hypothesis.py
```

Или интерактивную версию:

```bash
python3 product_hypothesis_assistant.py
```

**Удачи в валидации ваших гипотез! 🚀**
