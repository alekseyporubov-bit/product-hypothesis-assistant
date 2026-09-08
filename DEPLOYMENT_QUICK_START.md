# 🚀 БЫСТРЫЙ СТАРТ: ДЕПЛОЙ ЗА 5 МИНУТ

Самый быстрый способ развернуть приложение на relaxdev.ru

---

## ⚡ ВАРИАНТ 1: Git (САМЫЙ ЛЕГКИЙ)

### 1. Подготовка (1 минута)

```bash
cd /Users/a.porubov/python
git init
git add .
git commit -m "Ready for deploy"
```

### 2. GitHub (2 минуты)

1. Откройте https://github.com/new
2. Назовите "product-hypothesis-assistant"
3. Нажмите "Create repository"
4. Скопируйте URL (вида `https://github.com/YOUR_USERNAME/...`)

### 3. Загрузка на GitHub (1 минута)

```bash
git remote add origin YOUR_URL
git branch -M main
git push -u origin main
```

### 4. relaxdev.ru (1 минута)

1. Откройте https://relaxdev.ru (войдите в аккаунт)
2. Нажмите "Deploy New Project" или "Deploy"
3. Выберите "Git Repository"
4. Вставьте URL репозитория
5. Нажмите "Deploy"

**✅ ГОТОВО! Приложение развертывается...**

---

## ⚡ ВАРИАНТ 2: Docker

### 1. Соберите образ (2 минуты)

```bash
cd /Users/a.porubov/python
docker build -t my-app:latest .
```

### 2. На relaxdev.ru (3 минуты)

1. Откройте https://relaxdev.ru
2. Нажмите "Deploy"
3. Выберите "Docker"
4. Введите: `my-app:latest`
5. Нажмите "Deploy"

**✅ ГОТОВО!**

---

## ⚡ ВАРИАНТ 3: Прямая загрузка

### 1. На relaxdev.ru (5 минут)

1. Откройте https://relaxdev.ru
2. Нажмите "Deploy"
3. Выберите "Upload Files"
4. Загрузите всю папку `/Users/a.porubov/python`
   (или создайте ZIP архив)
5. Нажмите "Deploy"

**✅ ГОТОВО!**

---

## 📲 ВСЕ ВАРИАНТЫ: ПОСЛЕ ДЕПЛОЯ

Когда relaxdev.ru скажет что приложение развернуто:

```bash
# Замените YOUR_APP на имя вашего приложения на relaxdev.ru

# Проверьте что работает
curl https://YOUR_APP.relaxdev.ru/health

# Откройте в браузере
open https://YOUR_APP.relaxdev.ru
```

**✅ ГОТОВО! Приложение работает!**

---

## 🔧 ЕСЛИ ЧТО-ТО НЕ РАБОТАЕТ

### Проверьте логи на relaxdev.ru

- Войдите в панель управления
- Откройте ваш проект
- Смотрите "Logs" или "Console"
- Ищите сообщения об ошибке

### Самые частые проблемы:

| Ошибка | Решение |
|--------|---------|
| `ModuleNotFoundError` | Все зависимости в requirements.txt? ✅ Да! |
| `Port already in use` | relaxdev.ru выделит сам, не волнуйтесь |
| `No such file` | Все файлы загружены? Проверьте |
| `Application crashed` | Посмотрите логи, обычно там ошибка |

---

## ✨ ГОТОВО!

Приложение доступно по URL:

```
https://YOUR_APP_NAME.relaxdev.ru
```

Замените `YOUR_APP_NAME` на имя которое вы выбрали на relaxdev.ru

---

## 📚 ДОПОЛНИТЕЛЬНЫЕ РЕСУРСЫ

- **Полный гайд:** [DEPLOY_TO_RELAXDEV.md](./DEPLOY_TO_RELAXDEV.md)
- **Чеклист:** [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md)
- **relaxdev документация:** https://docs.relaxdev.ru

---

**Поздравляем! Приложение развернуто! 🎉**

*Дата: 07.09.2026*
