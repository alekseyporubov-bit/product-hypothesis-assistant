#!/usr/bin/env python3
"""
Скрипт для публикации рекламного поста через ContentOps MCP сервер
"""
import requests
import json
import os

# Читаем созданный пост
with open('/Users/a.porubov/python/promotional_post.md', 'r', encoding='utf-8') as f:
    post_content = f.read()

# Конфигурация MCP сервера
MCP_WRITER_URL = "https://planner-mcp-production.up.railway.app/mcp/writer"
AUTH_HEADER = os.getenv('CONTENTOPS_WRITER_AUTH', 'Bearer mcp_mVrGYmQaUXkYZGICU6t1XBNlgjTX4BR1pLTAStipZiw')

# Данные для публикации
publish_payload = {
    "title": "Product Hypothesis Assistant - Превратите идеи в данные",
    "content": post_content,
    "content_type": "promotional_post",
    "format": "markdown",
    "tags": [
        "ProductManagement",
        "DataDriven",
        "Hypothesis",
        "ProductDevelopment",
        "AI",
        "DecisionMaking"
    ],
    "metadata": {
        "author": "Product Team",
        "product": "Product Hypothesis Assistant",
        "purpose": "marketing",
        "target_audience": "Product Managers, Leaders"
    }
}

print("=" * 70)
print("📤 Публикация рекламного поста в ContentOps Studio")
print("=" * 70)

print(f"\n✏️  Заголовок: {publish_payload['title']}")
print(f"📏 Размер контента: {len(post_content)} символов")
print(f"🏷️  Теги: {', '.join(publish_payload['tags'])}")

# Попытка 1: Через REST API
print("\n🔌 Попытка опубликовать через REST API...")
try:
    headers = {
        "Authorization": AUTH_HEADER,
        "Content-Type": "application/json"
    }
    
    response = requests.post(
        f"{MCP_WRITER_URL}/publish",
        json=publish_payload,
        headers=headers,
        timeout=10
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ УСПЕХ! Пост опубликован в ContentOps Studio")
        print(f"   ID публикации: {result.get('publication_id', 'N/A')}")
        print(f"   Статус: {result.get('status', 'published')}")
        exit(0)
    else:
        print(f"⚠️  API вернул статус {response.status_code}")
        print(f"   Ответ: {response.text[:200]}")
except Exception as e:
    print(f"❌ Ошибка подключения: {str(e)}")

# Попытка 2: Сохранить в локальную БД для последующей синхронизации
print("\n💾 Сохраняю пост в локальную базу для синхронизации...")
try:
    with open('/Users/a.porubov/python/contentops_queue.json', 'w', encoding='utf-8') as f:
        json.dump(publish_payload, f, ensure_ascii=False, indent=2)
    
    print("✅ Пост сохранен в очередь: contentops_queue.json")
    print("\n📝 Информация о посте:")
    print(json.dumps(publish_payload, ensure_ascii=False, indent=2))
    print("\n💡 Совет: Когда MCP сервер будет подключен, используйте:")
    print("   access_mcp_resource('contentops-writer', 'writer://publish')")
    
except Exception as e:
    print(f"❌ Ошибка сохранения: {e}")

print("\n" + "=" * 70)
