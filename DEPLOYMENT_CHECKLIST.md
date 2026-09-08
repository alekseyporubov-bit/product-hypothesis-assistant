# ✅ ЧЕКЛИСТ ДЕПЛОЯ НА RELAXDEV.RU

Быстрый контрольный список перед деплоем

---

## 📦 ФАЙЛЫ И КОНФИГУРАЦИЯ

### Основные файлы приложения
- [x] `app.py` - Flask приложение ✅
- [x] `product_hypothesis_assistant.py` - ядро системы ✅
- [x] `templates/index.html` - главная страница ✅
- [x] `static/` - CSS/JS файлы ✅

### Конфигурация деплоя
- [x] `requirements.txt` - Python зависимости ✅
- [x] `Dockerfile` - Docker контейнер ✅
- [x] `.dockerignore` - игнорируемые файлы ✅
- [x] `wsgi.py` - WSGI точка входа ✅
- [x] `.env.example` - переменные окружения ✅

### Git конфигурация
- [ ] `.gitignore` - файлы для игнорирования
- [ ] Git инициализирован (`git init`)
- [ ] Коммит создан (`git commit`)
- [ ] Remote добавлен (`git remote add`)
- [ ] Push выполнен (`git push`)

---

## 🔍 ПРОВЕРКИ ПЕРЕД ДЕПЛОЕМ

### Код
- [ ] Нет синтаксических ошибок в `app.py`
- [ ] Нет хардкода портов (используем `$PORT` переменную)
- [ ] Debug режим отключен (`debug=False`)
- [ ] Все импорты работают

### Зависимости
- [ ] `requirements.txt` актуален
- [ ] Все необходимые пакеты указаны:
  - Flask ✅
  - requests ✅
  - gunicorn ✅
  - python-dotenv ✅

### Конфигурация
- [ ] `.env` файл создан из `.env.example`
- [ ] `FLASK_ENV=production` установлен
- [ ] Нет чувствительных данных в коде

### Frontend
- [ ] `templates/` директория существует
- [ ] `index.html` там находится
- [ ] `static/` директория существует
- [ ] CSS/JS файлы присутствуют

---

## 🚀 ПРОЦЕСС ДЕПЛОЯ

### Шаг 1: Подготовка
- [ ] Все файлы готовы
- [ ] Все проверки пройдены
- [ ] Git коммит сделан

### Шаг 2: На relaxdev.ru
- [ ] Зарегистрированы на relaxdev.ru ✅ (вы это сделали)
- [ ] Вошли в аккаунт
- [ ] Создали новый проект

### Шаг 3: Выбор способа деплоя

**Рекомендуемый путь (Git):**
- [ ] Создали репозиторий на GitHub
- [ ] Добавили remote
- [ ] Сделали push
- [ ] На relaxdev.ru выбрали "Deploy from Git"
- [ ] Вставили ссылку на репозиторий
- [ ] Нажали "Deploy"

**Альтернатива (Docker):**
- [ ] Собрали Docker image: `docker build -t app:latest .`
- [ ] На relaxdev.ru выбрали "Deploy from Docker"
- [ ] Указали образ
- [ ] Нажали "Deploy"

**Альтернатива (Прямая загрузка):**
- [ ] На relaxdev.ru выбрали "Upload Files"
- [ ] Загрузили все файлы
- [ ] Установили точку входа
- [ ] Нажали "Deploy"

### Шаг 4: Конфигурация на relaxdev.ru

Установите переменные окружения:
- [ ] `FLASK_ENV=production`
- [ ] `PYTHONUNBUFFERED=1`

Установите точку входа:
```
gunicorn --bind 0.0.0.0:$PORT --workers 4 app:app
```

---

## ✅ ПОСЛЕ УСПЕШНОГО ДЕПЛОЯ

### Тестирование

```bash
# Проверка здоровья приложения
curl https://YOUR_APP.relaxdev.ru/health

# Получение списка гипотез
curl https://YOUR_APP.relaxdev.ru/api/list-hypotheses

# Создание тестовой гипотезы
curl -X POST https://YOUR_APP.relaxdev.ru/api/create-hypothesis \
  -H "Content-Type: application/json" \
  -d '{"title": "Test", "description": "Test"}'
```

### Проверки
- [ ] Приложение доступно по URL
- [ ] Главная страница загружается
- [ ] API endpoints работают
- [ ] Нет ошибок в логах
- [ ] Static files загружаются
- [ ] Базовые операции работают

---

## 📊 МОНИТОРИНГ

На панели relaxdev.ru проверьте:
- [ ] Status: Running (зеленый)
- [ ] CPU usage: нормальный
- [ ] Memory usage: нормальный
- [ ] No errors в логах
- [ ] Requests/responses счетчики

---

## 🎯 ФИНАЛ

После успешного деплоя приложение:

✅ Доступно по ссылке: `https://YOUR_APP.relaxdev.ru`
✅ Обслуживается Gunicorn
✅ Запущено в production режиме
✅ Готово к использованию!

---

## 📝 ПРИМЕЧАНИЯ

- Если что-то не работает, проверьте логи на relaxdev.ru
- Убедитесь что все файлы загружены
- Проверьте переменные окружения
- Используйте `curl` для тестирования API

---

**Дата: 07.09.2026**
**Статус: ГОТОВ К ДЕПЛОЮ ✅**
