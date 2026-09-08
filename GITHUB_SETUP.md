# 🐙 НАСТРОЙКА GITHUB И ПУША РЕПОЗИТОРИЯ

Локальный Git репозиторий уже создан! Теперь нужно создать удаленный репозиторий на GitHub.

---

## 📋 ИНСТРУКЦИЯ (5 МИНУТ)

### Шаг 1: Создайте репозиторий на GitHub

1. Откройте https://github.com/new
2. Если не вошли - нажмите "Sign in" и авторизуйтесь
3. На странице создания репозитория:
   - **Repository name:** `product-hypothesis-assistant`
   - **Description:** `Product Hypothesis Assistant - Cloud-ready Flask application`
   - **Public:** Выберите (не важно)
   - **Initialize this repository with:** НЕ выбирайте ничего!
4. Нажмите "Create repository"

---

### Шаг 2: Скопируйте ссылку на репозиторий

На странице вашего репозитория вверху вы увидите кнопку "Code" (зеленая).

Кликните на неё и скопируйте HTTPS ссылку:
```
https://github.com/YOUR_USERNAME/product-hypothesis-assistant.git
```

Или если предпочитаете SSH:
```
git@github.com:YOUR_USERNAME/product-hypothesis-assistant.git
```

**Замените YOUR_USERNAME на ваше имя пользователя на GitHub!**

---

### Шаг 3: Добавьте remote и сделайте push

В терминале выполните эти команды:

```bash
cd /Users/a.porubov/python

# Добавьте remote (замените ССЫЛКА на вашу ссылку)
git remote add origin https://github.com/YOUR_USERNAME/product-hypothesis-assistant.git

# Переименуйте ветку на main (если нужно)
git branch -M main

# Отправьте код на GitHub
git push -u origin main
```

**Вот и всё!** Ваш код теперь на GitHub! 🎉

---

## ✅ ПРОВЕРКА

После пуша откройте https://github.com/YOUR_USERNAME/product-hypothesis-assistant

Вы должны увидеть все файлы вашего проекта:
- ✅ app.py
- ✅ product_hypothesis_assistant.py
- ✅ requirements.txt
- ✅ Dockerfile
- ✅ templates/
- ✅ static/
- ✅ И другие файлы

---

## 🔗 ССЫЛКА ДЛЯ RELAXDEV.RU

Когда код будет на GitHub, скопируйте эту ссылку:

```
https://github.com/YOUR_USERNAME/product-hypothesis-assistant.git
```

И вставьте её в relaxdev.ru когда создаете новый проект!

---

## 🆘 ЕСЛИ ВОЗНИКЛИ ПРОБЛЕМЫ

### Проблема: "fatal: not a git repository"
**Решение:** Уже создан, просто продолжайте

### Проблема: Permission denied при push
**Решение:** 
1. Используйте HTTPS вместо SSH
2. Или установите SSH ключи в GitHub

### Проблема: "Already exists"
**Решение:**
1. Удалите старый remote: `git remote remove origin`
2. Добавьте новый: `git remote add origin ...`

### Проблема: Что-то пошло не так
1. Проверьте что вы вошли в GitHub
2. Проверьте что репозиторий создан на GitHub
3. Проверьте правильность ссылки
4. Попробуйте еще раз

---

## 💡 ПОЛЕЗНЫЕ КОМАНДЫ

```bash
# Проверить статус
git status

# Посмотреть все коммиты
git log --oneline

# Посмотреть remotes
git remote -v

# Посмотреть текущую ветку
git branch

# После первого пуша можно просто писать
git push
# (без -u origin main)
```

---

## 📖 ДАЛЬШЕ

После пуша на GitHub:

1. Скопируйте ссылку вашего репозитория
2. Откройте https://relaxdev.ru
3. Создайте новый проект
4. Выберите "Deploy from Git"
5. Вставьте ссылку
6. Нажмите "Deploy"

**И готово! Ваше приложение в облаке!** 🚀

---

*Дата: 07.09.2026*
