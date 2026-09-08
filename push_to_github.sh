#!/bin/bash

# Скрипт для автоматического пуша на GitHub
# Использование: ./push_to_github.sh https://github.com/YOUR_USERNAME/product-hypothesis-assistant.git

echo "🚀 Product Hypothesis Assistant - Git Push Script"
echo "=================================================="
echo ""

# Проверяем что репозиторий есть
if [ ! -d .git ]; then
    echo "❌ Ошибка: Git репозиторий не найден!"
    echo "Выполните: git init && git add . && git commit -m 'Initial commit'"
    exit 1
fi

# Проверяем что передана ссылка
if [ -z "$1" ]; then
    echo "❌ Ошибка: нужна ссылка на GitHub репозиторий!"
    echo ""
    echo "Использование:"
    echo "  ./push_to_github.sh https://github.com/YOUR_USERNAME/product-hypothesis-assistant.git"
    echo ""
    echo "Или с SSH:"
    echo "  ./push_to_github.sh git@github.com:YOUR_USERNAME/product-hypothesis-assistant.git"
    exit 1
fi

REPO_URL="$1"

echo "📝 Ссылка на репозиторий: $REPO_URL"
echo ""

# Проверяем статус
echo "1️⃣  Проверка статуса Git..."
git status

echo ""
echo "2️⃣  Добавление всех изменений..."
git add .

echo ""
echo "3️⃣  Проверка что есть что коммитить..."
if git diff --cached --quiet; then
    echo "✓ Нет новых изменений"
else
    echo "✓ Есть новые файлы для коммита"
fi

echo ""
echo "4️⃣  Добавление remote..."
if git remote get-url origin > /dev/null 2>&1; then
    echo "⚠️  Remote 'origin' уже существует"
    echo "   Удаляю старый remote..."
    git remote remove origin
fi

git remote add origin "$REPO_URL"
echo "✓ Remote добавлен: $REPO_URL"

echo ""
echo "5️⃣  Переименование ветки на main (если нужно)..."
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
    git branch -M main
    echo "✓ Ветка переименована на: main"
else
    echo "✓ Уже на ветке main"
fi

echo ""
echo "6️⃣  Проверка коннекции..."
if git ls-remote "$REPO_URL" > /dev/null 2>&1; then
    echo "✓ Коннекция успешна!"
else
    echo "⚠️  Не удалось подключиться к репозиторию"
    echo "   Убедитесь что:"
    echo "   1. Ссылка правильная"
    echo "   2. Репозиторий создан на GitHub"
    echo "   3. Вы вошли в GitHub"
fi

echo ""
echo "7️⃣  Пуш кода на GitHub..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ УСПЕШНО!"
    echo ""
    echo "🎉 Ваш код теперь на GitHub!"
    echo ""
    echo "📌 Ссылка для relaxdev.ru:"
    echo "   $REPO_URL"
    echo ""
    echo "🚀 Дальше:"
    echo "   1. Откройте https://relaxdev.ru"
    echo "   2. Нажмите 'Deploy New Project'"
    echo "   3. Выберите 'Deploy from Git'"
    echo "   4. Вставьте эту ссылку"
    echo "   5. Нажмите 'Deploy'"
else
    echo ""
    echo "❌ Ошибка при пуше!"
    echo ""
    echo "Возможные причины:"
    echo "   1. Неверная ссылка на репозиторий"
    echo "   2. Не создан репозиторий на GitHub"
    echo "   3. Проблемы с аутентификацией"
    echo ""
    echo "Решение:"
    echo "   1. Проверьте ссылку"
    echo "   2. Убедитесь что репозиторий есть на GitHub"
    echo "   3. Попробуйте заново"
fi
