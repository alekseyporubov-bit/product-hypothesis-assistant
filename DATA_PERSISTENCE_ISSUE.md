# 📊 ПОЧЕМУ ПРОПАЛИ ДАННЫЕ ГИПОТЕЗ?

**Вопрос:** Почему после редеплоя пропали гипотезы?

**Ответ:** Приложение **НЕ ИСПОЛЬЗУЕТ БАЗУ ДАННЫХ** и хранит данные в памяти (RAM).

---

## 🔍 ПРОБЛЕМА

### Как работает сейчас:

```
app.py запускается
  ↓
HypothesisManager() инициализируется
  ↓
self.hypotheses: Dict = {} (в памяти)
  ↓
Вы создаете гипотезу → hypotheses[id] = Hypothesis()
  ↓
Данные в памяти сервера
  ↓
РЕДЕПЛОЙ на relaxdev.ru
  ↓
Сервер рестартует
  ↓
HypothesisManager() инициализируется ЗАНОВО
  ↓
hypotheses = {} (пусто!)
  ↓
❌ ВСЕ ДАННЫЕ ПОТЕРЯНЫ ❌
```

---

## 🎯 РЕШЕНИЕ

### Вариант 1: JSON файл (быстро)

Сохранять данные в файл:

```python
class HypothesisManager:
    def __init__(self):
        self.hypotheses = {}
        self.load_from_file()  # ← Загрузить при старте
    
    def load_from_file(self):
        # Загрузить из hypotheses.json
        
    def save_to_file(self):
        # Сохранить в hypotheses.json
    
    def create_hypothesis(self, ...):
        # ...создание...
        self.save_to_file()  # ← Сохранить
```

### Вариант 2: SQLite БД (лучше)

Встроенная база данных:

```python
import sqlite3

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('app.db')
        self.init_tables()
    
    def init_tables(self):
        # Создать таблицы
        
    def save_hypothesis(self, h_id, data):
        # Сохранить в БД
        
    def get_hypothesis(self, h_id):
        # Загрузить из БД
```

---

## ✅ ЭТО НЕ СВЯЗАНО С МОИМИ ИЗМЕНЕНИЯМИ

Я добавил:
- Help раздел (HTML)
- CSS стили
- 7 Git коммитов

Я **НЕ изменял** логику хранения данных!

---

## 🚀 ЧТО ДАЛЬШЕ?

Хотите, чтобы я внедрил SQLite сохранение?

1. ✅ Создам `database.py` с SQLite
2. ✅ Обновлю `HypothesisManager`
3. ✅ Обновлю `app.py`
4. ✅ Протестирую
5. ✅ Коммитю в Git

**Результат:** Данные будут сохраняться при редеплое! 🎉

---

**Выбирайте:** JSON файл (быстро) или SQLite (лучше)?
