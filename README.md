# Product Hypothesis Assistant

Cloud-ready Flask application for testing and validating product hypotheses.

---

## 🚀 Быстрый старт

### Локально:
```bash
python3 app.py
# Откройте http://localhost:5000
```

### На облаке (relaxdev.ru):
1. Откройте `GIT_QUICK_GUIDE.md`
2. Создайте репозиторий на GitHub
3. Загрузите код
4. Задеплойте на relaxdev.ru

---

## 📋 Что это?

Product Hypothesis Assistant помогает:
- ✅ Создавать и тестировать гипотезы о продукте
- ✅ Добавлять доказательства из разных источников
- ✅ Вычислять score для гипотезы
- ✅ Анализировать корреляцию predictions vs reality
- ✅ Получать научные исследования

---

## 🛠️ Технологии

- **Backend:** Flask (Python)
- **Frontend:** HTML, CSS, JavaScript
- **Deployment:** Docker, Gunicorn
- **Cloud:** relaxdev.ru

---

## 📚 Документация

| Документ | Описание |
|----------|---------|
| **GIT_QUICK_GUIDE.md** | Как загрузить код на GitHub (5 минут) |
| **GITHUB_DEPLOYMENT_STEPS.md** | GitHub + relaxdev.ru полный гайд |
| **DEPLOYMENT_QUICK_START.md** | Быстрый старт деплоя |
| **DEPLOY_TO_RELAXDEV.md** | Полная инструкция deплоя |
| **GIT_SETUP_COMPLETE.md** | Статус Git репозитория |

---

## 🔗 GitHub и Облако

### Текущий статус:
- ✅ Локальный Git репозиторий готов
- ⏳ Нужно создать репозиторий на GitHub
- ⏳ Нужно задеплоить на relaxdev.ru

### Как это сделать:
1. Прочитайте `GIT_QUICK_GUIDE.md` (5 минут)
2. Создайте репозиторий на GitHub.com
3. Запустите: `./push_to_github.sh YOUR_GITHUB_URL`
4. Задеплойте на relaxdev.ru

---

## 🎯 API Endpoints

- `GET /` - Главная страница
- `POST /api/create-hypothesis` - Создать гипотезу
- `GET /api/get-hypothesis/<id>` - Получить гипотезу
- `POST /api/add-evidence` - Добавить доказательство
- `POST /api/validate-hypothesis/<id>` - Валидировать гипотезу
- `GET /api/list-hypotheses` - Список гипотез
- `GET /api/research-sources/<id>` - Научные исследования
- `POST /api/record-outcome` - Записать результат

---

## 📝 Примеры

### Создать гипотезу:
```bash
curl -X POST http://localhost:5000/api/create-hypothesis \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Red button increases conversion",
    "problem_statement": "Gray button has low CTR",
    "target_users": "All checkout users",
    "expected_outcome": "15-20% increase in conversion"
  }'
```

### Получить список гипотез:
```bash
curl http://localhost:5000/api/list-hypotheses
```

---

## 🚀 Деплой

### GitHub:
```bash
git remote add origin YOUR_GITHUB_URL
git push -u origin main
```

### relaxdev.ru:
1. Откройте https://relaxdev.ru
2. Нажмите "Deploy New Project"
3. Выберите "Deploy from Git"
4. Вставьте ссылку на GitHub репозиторий
5. Нажмите "Deploy"

---

## 📊 Структура проекта

```
product-hypothesis-assistant/
├── app.py                      # Flask приложение
├── product_hypothesis_assistant.py  # Ядро системы
├── requirements.txt            # Python зависимости
├── Dockerfile                  # Docker конфигурация
├── wsgi.py                     # WSGI точка входа
├── templates/
│   └── index.html             # HTML интерфейс
├── static/
│   ├── css/                   # Стили
│   └── js/                    # JavaScript
└── README.md                   # Этот файл
```

---

## 🔧 Установка локально

```bash
# Клонировать репозиторий
git clone https://github.com/YOUR_USERNAME/product-hypothesis-assistant.git
cd product-hypothesis-assistant

# Создать виртуальное окружение
python3 -m venv venv
source venv/bin/activate

# Установить зависимости
pip install -r requirements.txt

# Запустить приложение
python3 app.py

# Откройте http://localhost:5000
```

---

## 🐳 Docker

```bash
# Собрать образ
docker build -t product-hypothesis-assistant:latest .

# Запустить контейнер
docker run -p 5000:5000 product-hypothesis-assistant:latest

# Откройте http://localhost:5000
```

---

## 📞 Поддержка

- GitHub Issues: https://github.com/YOUR_USERNAME/product-hypothesis-assistant/issues
- relaxdev.ru Help: https://docs.relaxdev.ru

---

## 📄 Лицензия

MIT License

---

## 🎉 Готово!

Приложение готово к деплою. Следуйте инструкциям в `GIT_QUICK_GUIDE.md`!

---

*Product Hypothesis Assistant v1.0*  
*Production Ready - 07.09.2026*
