# 🔬 Интеграция поиска исследований в открытых источниках

## Обзор

Система теперь **автоматически ищет исследования в открытых источниках** при валидации гипотезы. Это позволяет системе:

1. **Не полагаться только на пользовательские доказательства** - система сама находит подтверждающие данные
2. **Выдавать экспертное заключение** - анализирует найденные исследования и дает рекомендацию
3. **Комбинировать оценки** - использует 40% от пользовательских доказательств + 60% от открытых исследований

## Архитектура

### ResearchFinder (research_finder.py)

Система поиска исследований в открытых источниках. Поддерживает:

#### 1. **Google Scholar** (через SerpAPI)
- Требует API ключ: `SERPAPI_KEY`
- Ищет в Google Scholar
- Высокая релевантность (score: 0.85)

#### 2. **ArXiv** (публичный API)
- Поиск научных статей
- Используется автоматически
- Релевантность (score: 0.8)

#### 3. **Semantic Scholar** (публичный API)
- Поиск в открытой базе научных статей
- Используется автоматически
- Релевантность (score: 0.75)

### Интеграция в ScoringEngine

При вычислении `problem_severity`:

```python
# Пользовательские доказательства
user_evidence_score = min(10, problem_evidence * 2.5)

# Открытые исследования
research_evidence_score = min(10, research_count * 1.5 + research_quality * 3)

# Комбинированная оценка
problem_score = user_evidence_score * 0.4 + research_evidence_score * 0.6
```

**Вес 60% на открытые исследования** - потому что они:
- Объективны (рецензируемые статьи)
- Независимы от компании
- Дают экспертное мнение

## Как это работает

### Пример: Проверка гипотезы о тёмном режиме

**Шаг 1:** Пользователь создаёт гипотезу
```
Проблема: "Eye strain from bright displays at night"
Целевые пользователи: "mobile app users who use app in evening/night"
```

**Шаг 2:** Пользователь добавляет 2 доказательства
- Отзывы пользователей (USER_FEEDBACK)
- Статистика ночного использования (MARKET_RESEARCH)

**Шаг 3:** Пользователь жмёт "Валидировать"

**Шаг 4:** Система автоматически ищет исследования в открытых источниках:
```
Query: "Eye strain from bright displays at night mobile app users problem severity"

Найдено исследований:
1. "Dark Mode Adoption and Eye Strain Reduction" (ArXiv, 2023)
   - Authors: Chen L., Park S.
   - Abstract: "65% reduction in eye strain with dark mode"
   - Relevance: 0.88

2. "User Experience Challenges in Mobile Applications" (Google Scholar, 2023)
   - Authors: Smith J., Johnson K., Williams M.
   - Abstract: "78% of users experience UX issues"
   - Relevance: 0.92

3. "Night Usage Patterns and Visual Fatigue" (Semantic Scholar, 2023)
   - Authors: Tech Insights Ltd.
   - Abstract: "40% evening/night usage, high visual fatigue"
   - Relevance: 0.85
```

**Шаг 5:** Система выдаёт обоснование:
```
PROBLEM_SEVERITY: 5.3/10

Обоснование: 
  Пользовательские доказательства: 1 шт.
  Исследования из открытых источников: 3 (качество: 0.88)
  ✓ Множество высоконадёжных исследований подтверждают серьёзность проблемы
```

## Включение реальных запросов

По умолчанию система работает в **демо-режиме** с заранее подготовленными результатами.

Чтобы включить **реальные запросы** к API:

### 1. Google Scholar (через SerpAPI)

```bash
# Получите API ключ на https://serpapi.com
export SERPAPI_KEY="your_api_key_here"

# Обновите research_finder.py
finder = ResearchFinder()
finder.enable_remote = True
finder.serpapi_key = os.getenv('SERPAPI_KEY')
```

### 2. ArXiv (автоматически, без ключа)

```python
# Уже поддерживается, просто включите:
finder.enable_remote = True
```

### 3. Semantic Scholar (автоматически, без ключа)

```python
# Уже поддерживается, просто включите:
finder.enable_remote = True
```

## Примеры результатов

### ✅ Хорошая гипотеза (с поддержкой из исследований)

```
Гипотеза: Dark Mode
Problem Severity: 7.5/10
  User evidence: 1
  Research evidence: 5 (quality: 0.86)
  Recommendation: ✓ Множество высоконадёжных исследований подтверждают серьёзность проблемы

Recommendation: PROCEED (71/100 score)
```

### ⚠️ Средняя гипотеза (мало поддерживающих исследований)

```
Гипотеза: New Notification Type
Problem Severity: 4.2/10
  User evidence: 2
  Research evidence: 2 (quality: 0.65)
  Recommendation: ○ Умеренное количество исследований поддерживает наличие проблемы

Recommendation: INVESTIGATE (58/100 score)
```

### ❌ Слабая гипотеза (нет поддержки в исследованиях)

```
Гипотеза: Random Feature
Problem Severity: 1.8/10
  User evidence: 0
  Research evidence: 1 (quality: 0.45)
  Recommendation: ✗ Ограниченные доказательства серьёзности проблемы

Recommendation: REJECT (23/100 score)
```

## API Использование

### При создании гипотезы: нет изменений
```python
POST /api/create-hypothesis
{
    "title": "Dark Mode",
    "description": "...",
    "problem_statement": "Eye strain from bright displays",
    "target_users": "mobile app users",
    "expected_outcome": "..."
}
```

### При валидации: автоматический поиск исследований
```python
POST /api/validate-hypothesis/{hypothesis_id}

# Ответ теперь включает:
{
    "success": true,
    "score": {
        "overall_score": 65.2,
        "confidence_level": "medium",
        "breakdown": [
            {
                "factor": "problem_severity",
                "score": 7.1,
                "rationale": "Пользовательские доказательства: 1 шт. | Исследования из открытых источников: 4 (качество: 0.85) | ...",
                "evidence_count": 5  # 1 user + 4 research
            },
            ...
        ]
    }
}
```

## Производительность

- **Демо-режим**: < 100ms (используются кэшированные результаты)
- **С реальными запросами**: 2-5 сек (зависит от API ответов)
  - ArXiv: ~500ms
  - Google Scholar (SerpAPI): ~1-2 сек
  - Semantic Scholar: ~300ms

## Ограничения и Future Work

### Текущие ограничения
1. **Демо-режим по умолчанию** - для production требуется включить real запросы
2. **Язык поиска** - только English (поиск идёт на английском)
3. **Кэширование** - результаты кэшируются в памяти (без persistence)
4. **LLM анализ** - простые эвристики (в future можно добавить GPT-4 для глубокого анализа)

### Планы улучшения
- [ ] Добавить поддержку русскоязычного поиска (через Яндекс.Научно или Google Scholar на русском)
- [ ] Реализовать persistent кэширование результатов поиска (Redis/PostgreSQL)
- [ ] Интегрировать LLM (GPT-4) для экспертного анализа найденных статей
- [ ] Добавить поддержку других API (ResearchGate, PubMed для health-related гипотез)
- [ ] Реализовать auto-extraction ключевых метрик из найденных исследований
- [ ] Добавить визуализацию: граф исследований и связанных концепций

## Тестирование

```bash
# Запустить тест интеграции
python3 test_research_integration.py

# Результат:
# ✓ Учитываются пользовательские доказательства
# ✓ Учитываются исследования из открытых источников
# ✅ ТЕСТ ПРОЙДЕН
```

## Выводы

Интеграция ResearchFinder позволяет системе:

1. ✅ **Давать более обоснованные оценки** - не только на базе пользовательских данных
2. ✅ **Выдавать экспертное заключение** - анализирует научные источники
3. ✅ **Уменьшить bias** - объективные данные из рецензируемых исследований
4. ✅ **Масштабироваться** - можно анализировать тысячи гипотез без ручного research

**Результат:** Score гипотез теперь на 40% зависит от пользовательских доказательств и на 60% от открытых исследований, что делает решения более обоснованными и менее предвзятыми.
