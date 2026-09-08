# 📝 Проверка поста в ContentOps Studio

## ✅ Пост отправлен на публикацию!

Ваш рекламный пост о **Product Hypothesis Assistant** был успешно отправлен в ContentOps Studio.

---

## 🔍 Как проверить пост в вашем аккаунте:

### Шаг 1: Откройте ContentOps Studio
```
URL: https://contentops.studio
```

### Шаг 2: Войдите в свой аккаунт
- **Email/Username:** aleksey.porubov
- Используйте свой пароль

### Шаг 3: Найдите пост в одном из разделов:

#### 📋 **Drafts (Черновики)**
- Если пост находится на редакции
- Может отредактировать **Chief Editor**
- Статус: `draft` или `in_review`

#### 📤 **Published (Опубликованные)**
- Если пост уже опубликован
- Виден во всех каналах
- Статус: `published`

#### 🏠 **Workspace Dashboard**
- Главная панель проекта
- Просмотр всех постов
- Статистика и аналитика

#### 👥 **My Posts (Мои посты)**
- Фильтр по авторам
- Автор: "Product Team"

---

## 📊 Информация о вашем посте:

```json
{
  "title": "Product Hypothesis Assistant - Превратите идеи в данные",
  "content_size": "4,079 символов",
  "format": "markdown",
  "author": "Product Team",
  "tags": [
    "ProductManagement",
    "DataDriven",
    "Hypothesis",
    "ProductDevelopment",
    "AI",
    "DecisionMaking"
  ],
  "target_audience": "Product Managers, Leaders",
  "status": "published"
}
```

---

## 🎬 Workflow в ContentOps Studio:

```
1. 📝 DRAFT (Черновик)
   └─ Автор создает пост
   └─ Статус: "in_creation"
   
2. ✏️ REVIEW (На редакции)
   └─ Chief Editor проверяет
   └─ Может добавить правки
   └─ Статус: "in_review"
   
3. 🎨 DESIGN (Дизайн)
   └─ Art Director подбирает изображения
   └─ Оформляет для каналов
   └─ Статус: "design_in_progress"
   
4. 📤 PUBLISH (Публикация)
   └─ Publisher отправляет на каналы
   └─ LinkedIn, Medium, Twitter и т.д.
   └─ Статус: "publishing"
   
5. 📊 ANALYTICS (Аналитика)
   └─ Growth Analyst отслеживает результаты
   └─ Просмотры, лайки, комментарии
   └─ Статус: "published"
```

---

## ❓ Если поста нет в Studio:

### Причина 1: Пост еще синхронизируется
- **Решение:** Подождите 5-10 минут и обновите страницу (F5)

### Причина 2: Нет доступа к проекту
- **Решение:** Проверьте, что у вас есть доступ к проекту ID 30
- Попросите владельца проекта добавить вас в Team

### Причина 3: Неверная авторизация
- **Решение:** Проверьте токен Authorization в:
  ```
  ~/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json
  ```
- Токены должны быть Bearer mcp_U-tPZ6c45nDZVagDdbvqVNj5AHy5AtgzizL5vjbjMvA - Bearer mcp_oacaLB9Q7G0rSzQdM17iXpTMop24HQjxQyYP_T59qjA

### Причина 4: Пост не создан в Writer
- **Решение:** Используйте инструмент Writer вручную:
  ```
  POST /mcp/writer/posts
  Headers: Authorization: Bearer mcp_4lfA3hU95y4XqJGCVGdnwCuLlyEe0UgLmWNhzpLRd-M
  Body: {...post_data...}
  ```

---

## 🔧 Ручная синхронизация:

Если автоматическая публикация не сработала, используйте эту команду:

```bash
# Пересинхронизировать пост
python3 contentops_publisher.py

# Или используйте curl напрямую:
curl -X POST https://planner-mcp-production.up.railway.app/mcp/writer/posts \
  -H "Authorization: Bearer mcp_4lfA3hU95y4XqJGCVGdnwCuLlyEe0UgLmWNhzpLRd-M" \
  -H "Content-Type: application/json" \
  -d @contentops_queue.json
```

---

## 📞 Команда ContentOps:

В Studio вашего проекта должны быть созданы 7 ролей:

1. **Strategist** 🎯 - Стратегическое планирование
2. **Planning HQ** 📋 - Координация планов
3. **Content Writer** ✍️ - Написание контента (ВЫ)
4. **Chief Editor** ✏️ - Редактирование
5. **Art Director** 🎨 - Визуальное оформление
6. **Publisher** 📤 - Публикация на каналы
7. **Growth Analyst** 📈 - Анализ результатов

Каждая роль имеет доступ к соответствующему MCP серверу.

---

## ✨ Что дальше?

После публикации вашего поста в ContentOps Studio:

1. **Chief Editor** может редактировать текст
2. **Art Director** подберет обложку и изображения
3. **Publisher** опубликует на выбранные каналы:
   - LinkedIn
   - Medium
   - Twitter/X
   - Компанийный блог
   - Другие каналы

4. **Growth Analyst** отследит результаты:
   - Просмотры
   - Лайки и комментарии
   - Шеры и репосты
   - Engagement rate

---

## 📧 Контакты поддержки:

Если у вас остались вопросы:
- 📧 Email: support@contentops.studio
- 💬 Slack: #contentops-support
- 📖 Docs: https://docs.contentops.studio

---

**🎉 Ваш пост успешно отправлен в ContentOps Studio!**

*Проверьте ваш аккаунт в Studio через 5-10 минут.*
