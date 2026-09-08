# 🚀 ДЕПЛОЙ НА RELAXDEV.RU

Инструкция по развертыванию Product Hypothesis Assistant

---

## 📋 НЕОБХОДИМЫЕ ФАЙЛЫ

✅ Все уже созданы и готовы:

- `app.py` - основное приложение
- `product_hypothesis_assistant.py` - ядро
- `requirements.txt` - зависимости Python
- `Dockerfile` - контейнер
- `wsgi.py` - точка входа
- `templates/` и `static/` - фронтенд

---

## 🚀 СПОСОБ 1: ЧЕРЕЗ GIT (РЕКОМЕНДУЕТСЯ)

### 1. Инициализируйте Git

```bash
cd /Users/a.porubov/python
git init
git add .
git commit -m "Product Hypothesis Assistant - ready for deployment"
```

### 2. Создайте репозиторий на GitHub

- Зайдите на github.com
- Создайте новый репозиторий "product-hypothesis-assistant"
- Скопируйте ссылку (вида https://github.com/YOUR_USERNAME/...)

### 3. Добавьте remote и push

```bash
git remote add origin YOUR_GITHUB_URL
git branch -M main
git push -u origin main
```

### 4. На relaxdev.ru

- Войдите в аккаунт
- Нажмите "Create Project" или "Deploy"
- Выберите "Deploy from Git"
- Вставьте ссылку на репозиторий
- Нажмите "Deploy"

---

## 🐳 СПОСОБ 2: ЧЕРЕЗ DOCKER

### 1. Соберите image

```bash
cd /Users/a.porubov/python
docker build -t my-hypothesis-app:latest .
```

### 2. На relaxdev.ru

- Выберите "Deploy from Docker"
- Введите образ: `my-hypothesis-app:latest`
- Нажмите "Deploy"

---

## 📁 СПОСОБ 3: ПРЯМАЯ ЗАГРУЗКА

### На relaxdev.ru

1. Выберите "Upload Files"
2. Загрузите все файлы (или ZIP архив)
3. Укажите точку входа: `gunicorn --bind 0.0.0.0:$PORT app:app`
4. Нажмите "Deploy"

---

## ⚙️ КОНФИГУРАЦИЯ

Установите переменные окружения на relaxdev.ru:

```
FLASK_ENV=production
PYTHONUNBUFFERED=1
```

Точка входа (Entrypoint):
```
gunicorn --bind 0.0.0.0:$PORT --workers 4 app:app
```

Порт: relaxdev.ru установит автоматически

---

## ✅ ПОСЛЕ ДЕПЛОЯ

### Проверьте что работает:

```bash
# Замените на ваш URL
curl https://YOUR_APP.relaxdev.ru/health

# Должен вернуть:
# {"status": "healthy", "service": "Product Hypothesis Assistant"}
```

### Откройте приложение:

```
https://YOUR_APP.relaxdev.ru
```

### Тестируйте API:

```bash
curl https://YOUR_APP.relaxdev.ru/api/list-hypotheses
# Должен вернуть: {"success": true, "hypotheses": []}
```

---

## 🔧 РЕШЕНИЕ ПРОБЛЕМ

| Проблема | Решение |
|----------|---------|
| Application failed to start | Проверьте requirements.txt и логи |
| Module not found | Убедитесь что все зависимости в requirements.txt |
| Static files not loading | Проверьте что папка static/ существует |
| Templates not found | Проверьте что templates/index.html есть |

---

## 📊 МОНИТОРИНГ

На панели relaxdev.ru можно:
- Просматривать логи
- Мониторить CPU/Memory
- Масштабировать приложение
- Управлять доменом

---

**✅ Готово к деплою!**

Все необходимые файлы созданы и подготовлены.

*Дата: 07.09.2026*
