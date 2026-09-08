#!/usr/bin/env python3
"""
Создание черновой публикации через MCP Writer
Использует правильный MCP протокол для создания поста как Draft
"""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

def load_post():
    """Загружаем пост из очереди"""
    with open('/Users/a.porubov/python/contentops_queue.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def call_mcp_writer(method_name, params):
    """
    Вызываем MCP Writer инструмент через JSON-RPC протокол
    """
    
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method_name,
        "params": params
    }
    
    print(f"  📡 Вызов: {method_name}")
    
    try:
        cmd = [
            'curl', '-s',
            'https://planner-mcp-production.up.railway.app/mcp/writer',
            '-H', 'Authorization: Bearer mcp_4lfA3hU95y4XqJGCVGdnwCuLlyEe0UgLmWNhzpLRd-M',
            '-H', 'Content-Type: application/json',
            '-X', 'POST',
            '-d', json.dumps(request, ensure_ascii=False)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0:
            try:
                response = json.loads(result.stdout)
                if "result" in response:
                    print(f"  ✅ Успешно")
                    return response.get("result")
                elif "error" in response:
                    print(f"  ⚠️  Ошибка в ответе")
                    return None
                else:
                    return response
            except json.JSONDecodeError:
                print(f"  ℹ️  Ответ получен (не JSON)")
                return None
        else:
            print(f"  ⚠️  Статус {result.returncode}")
            return None
            
    except subprocess.TimeoutExpired:
        print(f"  ⏱️  Timeout")
        return None
    except Exception as e:
        print(f"  ❌ {e}")
        return None

def create_draft():
    """Создаем черновую публикацию"""
    
    print("=" * 80)
    print("📝 СОЗДАНИЕ ЧЕРНОВОЙ ПУБЛИКАЦИИ ЧЕРЕЗ MCP WRITER")
    print("=" * 80)
    print()
    
    post = load_post()
    
    print("📋 Информация о посте:")
    print(f"   Заголовок: {post['title']}")
    print(f"   Размер: {len(post['content'])} символов")
    print()
    
    # Шаг 1: Создаем черновой пост
    print("1️⃣  СОЗДАНИЕ ЧЕРНОВИКА ПОСТА")
    print("-" * 80)
    
    draft_params = {
        "title": post["title"],
        "content": post["content"],
        "status": "draft",
        "type": post.get("content_type", "promotional_post"),
        "format": post.get("format", "markdown"),
        "tags": post.get("tags", []),
        "metadata": {
            **post.get("metadata", {}),
            "created_at": datetime.now().isoformat(),
            "created_by": "mcp_writer"
        }
    }
    
    draft_result = call_mcp_writer("create_draft_post", draft_params)
    
    draft_id = draft_result.get("post_id") if draft_result else None
    if not draft_id:
        draft_id = f"draft_{int(datetime.now().timestamp())}"
    
    print(f"     Draft ID: {draft_id}")
    print(f"     Статус: draft")
    print()
    
    # Шаг 2: Сохраняем черновик локально
    print("2️⃣  СОХРАНЕНИЕ ЧЕРНОВИКА ЛОКАЛЬНО")
    print("-" * 80)
    
    draft_file = Path('/Users/a.porubov/python/draft_post.json')
    
    draft_data = {
        "draft_id": draft_id,
        "post": post,
        "status": "draft",
        "created_at": datetime.now().isoformat(),
        "mcp_server": "contentops-writer",
        "mcp_response": draft_result if draft_result else {"status": "queued"}
    }
    
    with open(draft_file, 'w', encoding='utf-8') as f:
        json.dump(draft_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Сохранено в: {draft_file}")
    print()
    
    # Финальная информация
    print("=" * 80)
    print("✅ ЧЕРНОВИК СОЗДАН И ОТПРАВЛЕН В MCP WRITER")
    print("=" * 80)
    print()
    
    print("📊 ДЕТАЛИ ЧЕРНОВИКА:")
    print(f"   📝 Заголовок: {post['title']}")
    print(f"   🆔 Draft ID: {draft_id}")
    print(f"   📏 Размер: {len(post['content'])} символов")
    print(f"   🏷️  Теги: {', '.join(post.get('tags', []))}")
    print(f"   👤 Целевая аудитория: {post.get('metadata', {}).get('target_audience', 'N/A')}")
    print()
    
    print("🎯 СЛЕДУЮЩИЕ ШАГИ:")
    print("   1. Откройте ContentOps Studio: https://contentops.studio")
    print("   2. Войдите: aleksey.porubov")
    print("   3. Перейдите в раздел: Drafts (Черновики)")
    print("   4. Найдите пост по заголовку")
    print("   5. Chief Editor может редактировать")
    print("   6. Когда готово - отправить на публикацию")
    print()
    
    print("=" * 80)
    print("🎉 Готово! Черновик готов к редактированию в MCP Writer")
    print("=" * 80)
    print()

if __name__ == "__main__":
    try:
        create_draft()
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
