# 🚀 БЫСТРЫЙ ГАЙД: GIT И GITHUB

Ваш локальный Git репозиторий **уже готов!** Осталось загрузить на GitHub в 3 шага.

---

## ✅ ЧТО УЖЕ СДЕЛАНО

✅ Git репозиторий инициализирован  
✅ .gitignore создан  
✅ Первый коммит сделан  
✅ Скрипт для пуша создан  

---

## 🎯 ОСТАЛОСЬ: 3 ШАГА ПО 2 МИНУТЫ КАЖДЫЙ

### Шаг 1: Создать репозиторий на GitHub (2 минуты)

1. Откройте https://github.com/new
2. Если не вошли - кликните "Sign in"
3. На форме создания репозитория:
   - **Repository name:** `product-hypothesis-assistant`
   - **Description:** `Cloud-ready Flask application for Product Hypothesis testing`
   - **Public/Private:** как вам нравится
   - **Инициализация:** НЕ выбирайте ничего (не нужны README, .gitignore, license)
4. Кликните "Create repository"

---

### Шаг 2: Скопировать ссылку репозитория (1 минута)

После создания на странице репозитория:

1. Кликните зелёную кнопку "Code"
2. Выберите "HTTPS" (обычно выбрана по умолчанию)
3. Скопируйте ссылку, она выглядит так:
   ```
   https://github.com/YOUR_USERNAME/product-hypothesis-assistant.git
   ```

**Замените `YOUR_USERNAME` на ваше имя пользователя на GitHub!**

Сохраните эту ссылку - она нужна для relaxdev.ru.

---

### Шаг 3: Загрузить код на GitHub (2 минуты)

#### Вариант A: Автоматический скрипт (РЕКОМЕНДУЕТСЯ)

```bash
cd /Users/a.porubov/python
./push_to_github.sh https://github.com/YOUR_USERNAME/product-hypothesis-assistant.git
```

Замените ссылку на вашу!

#### Вариант B: Ручные команды

```bash
cd /Users/a.porubov/python

# Добавьте remote
git remote add origin https://github.com/YOUR_USERNAME/product-hypothesis-assistant.git

# Убедитесь что на ветке main
git branch -M main

# Загрузите код
git push -u origin main
```

---

## ✅ ГОТОВО!

После успешного пуша вы должны увидеть:
```
✓ To https://github.com/YOUR_USERNAME/product-hypothesis-assistant.git
  [new branch]      main -> main
Branch 'main' set up to track remote branch 'main' from 'origin'.
```

---

## 📌 ВАША ССЫЛКА ДЛЯ RELAXDEV.RU

Используйте эту ссылку в relaxdev.ru:

```
https://github.com/YOUR_USERNAME/product-hypothesis-assistant.git
```

Эта ссылка понадобится вам когда будете создавать проект на relaxdev.ru!

---

## 🔍 ПРОВЕРКА

Откройте https://github.com/YOUR_USERNAME/product-hypothesis-assistant

Вы должны увидеть:
- Все файлы вашего проекта ✅
- app.py ✅
- product_hypothesis_assistant.py ✅
- requirements.txt ✅
- Dockerfile ✅
- templates/ папка ✅
- static/ папка ✅
- И другие файлы ✅

---

## 🚀 ДАЛЬШЕ

После загрузки на GitHub:

1. Скопируйте ссылку вашего репозитория
2. Откройте https://relaxdev.ru
3. Войдите в аккаунт (вы уже регистрировались)
4. Нажмите "Deploy New Project" или "Create Project"
5. Выберите "Deploy from Git"
6. Вставьте ссылку репозитория
7. Нажмите "Deploy"
8. Дождитесь успешного развертывания
9. Откройте ссылку вашего приложения!

**И готово! Ваше приложение в облаке! 🎉**

---

## 🆘 ПОМОЩЬ

### Ошибка: "Repository not found"
- Проверьте что репозиторий создан на GitHub
- Проверьте что ссылка правильная
- Убедитесь что вы вошли в GitHub

### Ошибка: "Permission denied"
- Попробуйте HTTPS вместо SSH
- Или установите SSH ключи в GitHub settings

### Ошибка: "Already exists"
```bash
git remote remove origin
git remote add origin YOUR_NEW_LINK
git push -u origin main
```

### Что-то другое пошло не так?
1. Попробуйте скрипт: `./push_to_github.sh YOUR_LINK`
2. Если не помогает - ручные команды выше
3. Все еще не работает? Проверьте что GitHub доступен

---

## 📚 СПРАВКА

```bash
# Статус репозитория
git status

# История коммитов
git log --oneline

# Посмотреть remotes
git remote -v

# Посмотреть текущую ветку
git branch

# Посмотреть все ветки
git branch -a
```

---

**🎉 Вот и все! Ваш проект в GitHub и готов к деплою!**

*Дата: 07.09.2026*
