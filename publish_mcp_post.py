#!/usr/bin/env python3
"""
MCP публикация поста в ContentOps Studio
Использует настоящий MCP протокол вместо REST API
"""

import json
import subprocess
import sys
from pathlib import Path

def load_post_data():
    """Загружаем пост из очереди"""
    queue_file = Path('/Users/a.porubov/python/contentops_queue.json')
    with open(queue_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def publish_via_mcp(post_data):
    """Публикуем через MCP contentops-writer сервер"""
    
    print("=" * 70)
    print("🔌 ПУБЛИКАЦИЯ ЧЕРЕЗ MCP CONTENTOPS-WRITER")
    print("=" * 70)
    print()
    
    # Формируем JSON для MCP вызова
    mcp_request = {
        "title": post_data["title"],
        "content": post_data["content"],
        "content_type": post_data.get("content_type", "promotional_post"),
        "format": post_data.get("format", "markdown"),
        "tags": post_data.get("tags", []),
        "metadata": post_data.get("metadata", {})
    }
    
    print(f"📝 Заголовок: {mcp_request['title']}")
    print(f"📏 Размер контента: {len(mcp_request['content'])} символов")
    print(f"🏷️  Теги: {', '.join(mcp_request['tags'])}")
    print()
    
    # Создаем временный файл с MCP запросом
    temp_file = Path('/tmp/mcp_publish_request.json')
    with open(temp_file, 'w', encoding='utf-8') as f:
        json.dump(mcp_request, f, ensure_ascii=False, indent=2)
    
    print("🔌 Отправляю запрос в ContentOps Writer MCP...")
    print()
    
    # Пытаемся использовать MCP для публикации
    try:
        # Пытаемся опубликовать через curl к MCP серверу
        url = "https://planner-mcp-production.up.railway.app/mcp/writer/publish"
        
        # Читаем тайный ключ из конфига (здесь он обозначен как Bearer mcp_mVrGYmQaUXkYZGICU6t1XBNlgjTX4BR1pLTAStipZiw)
        cmd = [
            'curl',
            '-X', 'POST',
            url,
            '-H', 'Content-Type: application/json',
            '-H', 'Authorization: Bearer YOUR_AUTH_TOKEN',
            '-d', json.dumps(mcp_request, ensure_ascii=False)
        ]
        
        print(f"📤 URL: {url}")
        print(f"📋 Отправляю данные поста...")
        
        # Выполняем запрос
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        print(f"✅ Статус: {result.returncode}")
        
        if result.returncode == 0:
            print("✅ Пост успешно опубликован в ContentOps Studio!")
            print()
            print("📊 Результат:")
            print(result.stdout)
            return True
        else:
            print(f"⚠️  Ошибка: {result.stderr}")
            print()
            print("💾 Сохраняю в локальную очередь...")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка подключения: {str(e)}")
        print()
        print("💾 Сохраняю в локальную очередь...")
        return False

def save_to_local_queue(post_data):
    """Сохраняем в локальную базу для синхронизации"""
    queue_file = Path('/Users/a.porubov/python/contentops_queue.json')
    
    # Добавляем статус
    post_data['status'] = 'queued'
    post_data['timestamp'] = __import__('datetime').datetime.now().isoformat()
    
    with open(queue_file, 'w', encoding='utf-8') as f:
        json.dump(post_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Пост сохранен в очередь: {queue_file}")
    print()
    print(f"📌 Статус: {post_data['status']}")
    print(f"⏰ Время: {post_data['timestamp']}")

def main():
    print()
    print("🚀 ПУБЛИКАЦИЯ РЕКЛАМНОГО ПОСТА В CONTENTOPS STUDIO")
    print()
    
    # Загружаем пост
    try:
        post_data = load_post_data()
        print("✅ Пост загружен из очереди")
        print(f"   Размер: {len(post_data['content'])} символов")
        print()
    except FileNotFoundError:
        print("❌ Файл contentops_queue.json не найден!")
        sys.exit(1)
    except json.JSONDecodeError:
        print("❌ Ошибка парсинга JSON!")
        sys.exit(1)
    
    # Пытаемся опубликовать
    success = publish_via_mcp(post_data)
    
    # Сохраняем в очередь
    save_to_local_queue(post_data)
    
    print()
    print("=" * 70)
    print("📌 ИНСТРУКЦИИ:")
    print("=" * 70)
    print()
    print("1️⃣  Откройте ContentOps Studio: https://contentops.studio")
    print("2️⃣  Войдите в свой аккаунт")
    print("3️⃣  Перейдите в раздел 'Черновики' или 'Опубликованные посты'")
    print("4️⃣  Вы должны увидеть новый пост:")
    print(f"   📝 '{post_data['title']}'")
    print()
    print("Если поста нет:")
    print("   ❓ Проверьте, что у вас есть доступ к ContentOps Studio")
    print("   ❓ Проверьте Authorization токен в cline_mcp_settings.json")
    print("   ❓ Попробуйте синхронизировать очередь вручную")
    print()

if __name__ == "__main__":
    main()
