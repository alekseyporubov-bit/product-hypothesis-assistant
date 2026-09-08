# 🔌 MCP Server для Product Hypothesis Assistant

## Описание

MCP сервер для подключения к локальному приложению проверки гипотез на localhost:5000

## 📋 Требования

```bash
pip3 install mcp requests
# Flask приложение запущено: python3 app.py
```

## 🚀 Запуск

```bash
python3 mcp_hypothesis_server.py
```

## 📚 Доступные инструменты

| Инструмент | Описание |
|------------|---------|
| **create_hypothesis** | Создать новую гипотезу |
| **add_evidence** | Добавить доказательство |
| **validate_hypothesis** | Валидировать и получить Score |
| **get_hypothesis** | Получить информацию |
| **get_research_sources** | Получить научные исследования |
| **list_hypotheses** | Список всех гипотез |
| **record_outcome** | Записать исход фичи |
| **correlation_analysis** | Анализ корреляции |

## 🔌 Подключение в Cline

Добавьте в `cline_mcp_settings.json`:

```json
{
  "mcpServers": {
    "hypothesis-assistant": {
      "url": "stdio:///Users/a.porubov/python/mcp_hypothesis_server.py",
      "disabled": false
    }
  }
}
```

## 📊 Пример использования

```python
import requests

# Создать гипотезу
resp = requests.post("http://localhost:5000/api/create-hypothesis", json={
    "title": "Тёмный режим",
    "problem_statement": "Боль в глазах ночью"
})

hypothesis_id = resp.json()["hypothesis_id"]

# Добавить доказательство
requests.post("http://localhost:5000/api/add-evidence", json={
    "hypothesis_id": hypothesis_id,
    "evidence_type": "USER_FEEDBACK",
    "title": "Отзывы",
    "confidence": 0.9
})

# Валидировать
score = requests.post(
    f"http://localhost:5000/api/validate-hypothesis/{hypothesis_id}",
    json={}
).json()

print(f"Score: {score['score']}")
```

## 🐛 Проблемы

- **"Не удалось подключиться к localhost:5000"** → Запустите `python3 app.py`
- **"ModuleNotFoundError: mcp"** → Установите `pip3 install mcp`
- **Сервер не отвечает** → Проверьте `ps aux | grep mcp_hypothesis_server`

---

**🚀 Готово! MCP Server активирован для Product Hypothesis Assistant**
