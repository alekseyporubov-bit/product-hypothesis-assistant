#!/usr/bin/env python3
"""MCP Server для Product Hypothesis Assistant"""

import json
import requests
from mcp.server import Server, stdio
from mcp.types import Tool, TextContent, ToolResult

BASE_URL = "http://localhost:5000"
API_URL = f"{BASE_URL}/api"

server = Server("hypothesis-assistant-mcp")

TOOLS_CONFIG = [
    {
        "name": "create_hypothesis",
        "description": "Создать новую гипотезу",
        "props": {
            "title": {"type": "string", "description": "Название гипотезы"},
            "description": {"type": "string", "description": "Описание"},
            "problem_statement": {"type": "string", "description": "Проблема"},
            "target_users": {"type": "string", "description": "Целевые пользователи"},
            "expected_outcome": {"type": "string", "description": "Ожидаемый результат"}
        },
        "required": ["title", "problem_statement"]
    },
    {
        "name": "add_evidence",
        "description": "Добавить доказательство",
        "props": {
            "hypothesis_id": {"type": "string", "description": "ID гипотезы"},
            "evidence_type": {"type": "string", "enum": ["USER_FEEDBACK", "ANALYTICS", "MARKET_RESEARCH", "COMPETITIVE_ANALYSIS", "INTERNAL_DATA", "SURVEY"]},
            "title": {"type": "string", "description": "Заголовок"},
            "description": {"type": "string", "description": "Описание"},
            "source": {"type": "string", "description": "Источник"},
            "confidence": {"type": "number", "minimum": 0, "maximum": 1},
            "supports": {"type": "boolean", "default": True}
        },
        "required": ["hypothesis_id", "evidence_type", "title"]
    },
    {
        "name": "validate_hypothesis",
        "description": "Валидировать гипотезу и получить Score",
        "props": {"hypothesis_id": {"type": "string", "description": "ID гипотезы"}},
        "required": ["hypothesis_id"]
    },
    {
        "name": "get_hypothesis",
        "description": "Получить информацию о гипотезе",
        "props": {"hypothesis_id": {"type": "string", "description": "ID гипотезы"}},
        "required": ["hypothesis_id"]
    },
    {
        "name": "get_research_sources",
        "description": "Получить научные исследования",
        "props": {"hypothesis_id": {"type": "string", "description": "ID гипотезы"}},
        "required": ["hypothesis_id"]
    },
    {
        "name": "list_hypotheses",
        "description": "Получить список гипотез",
        "props": {},
        "required": []
    },
    {
        "name": "record_outcome",
        "description": "Записать исход фичи",
        "props": {
            "hypothesis_id": {"type": "string"},
            "success": {"type": "boolean"},
            "actual_impact": {"type": "string"},
            "lessons_learned": {"type": "string"}
        },
        "required": ["hypothesis_id", "success"]
    },
    {
        "name": "correlation_analysis",
        "description": "Анализ корреляции",
        "props": {},
        "required": []
    }
]

@server.list_tools()
async def list_tools() -> list[Tool]:
    tools = []
    for cfg in TOOLS_CONFIG:
        tools.append(Tool(
            name=cfg["name"],
            description=cfg["description"],
            inputSchema={
                "type": "object",
                "properties": cfg["props"],
                "required": cfg["required"]
            }
        ))
    return tools

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> ToolResult:
    try:
        if name == "create_hypothesis":
            resp = requests.post(f"{API_URL}/create-hypothesis", json=arguments, timeout=10)
        elif name == "add_evidence":
            resp = requests.post(f"{API_URL}/add-evidence", json=arguments, timeout=10)
        elif name == "validate_hypothesis":
            hid = arguments.get("hypothesis_id")
            resp = requests.post(f"{API_URL}/validate-hypothesis/{hid}", json={}, timeout=10)
        elif name == "get_hypothesis":
            hid = arguments.get("hypothesis_id")
            resp = requests.get(f"{API_URL}/get-hypothesis/{hid}", timeout=10)
        elif name == "get_research_sources":
            hid = arguments.get("hypothesis_id")
            resp = requests.get(f"{API_URL}/research-sources/{hid}", timeout=10)
        elif name == "list_hypotheses":
            resp = requests.get(f"{API_URL}/list-hypotheses", timeout=10)
        elif name == "record_outcome":
            hid = arguments.pop("hypothesis_id")
            resp = requests.post(f"{API_URL}/record-outcome", json={"hypothesis_id": hid, **arguments}, timeout=10)
        elif name == "correlation_analysis":
            resp = requests.get(f"{API_URL}/correlation-analysis", timeout=10)
        else:
            return ToolResult(content=[TextContent(type="text", text=f"Неизвестный инструмент: {name}")])
        
        result = resp.json()
        return ToolResult(content=[TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))])
    
    except requests.exceptions.ConnectionError:
        msg = f"❌ Не удалось подключиться к {BASE_URL}\nЗапустите: python3 app.py"
        return ToolResult(content=[TextContent(type="text", text=msg)])
    except Exception as e:
        return ToolResult(content=[TextContent(type="text", text=f"❌ Ошибка: {str(e)}")])

async def main():
    async with stdio.stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
