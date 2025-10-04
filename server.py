#!/usr/bin/env python3
"""
Custom Notion MCP Server - Direct API Integration
A simple, reliable MCP server that uses the Notion API directly.
"""

import os
import sys
import json
import asyncio
from typing import Any
import httpx
from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp import stdio_server

# Notion API configuration
NOTION_VERSION = "2022-06-28"
NOTION_API_BASE = "https://api.notion.com/v1"

class NotionMCPServer:
    def __init__(self, token: str):
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Notion-Version": NOTION_VERSION,
            "Content-Type": "application/json"
        }
        self.client = httpx.AsyncClient(headers=self.headers, timeout=30.0)

    async def search(self, query: str = "", filter_type: str | None = None) -> dict:
        """Search Notion workspace"""
        payload = {"query": query} if query else {}
        if filter_type:
            payload["filter"] = {"property": "object", "value": filter_type}

        response = await self.client.post(
            f"{NOTION_API_BASE}/search",
            json=payload
        )
        response.raise_for_status()
        return response.json()

    async def get_page(self, page_id: str) -> dict:
        """Get a Notion page by ID"""
        response = await self.client.get(f"{NOTION_API_BASE}/pages/{page_id}")
        response.raise_for_status()
        return response.json()

    async def create_page(self, parent_id: str, title: str, properties: dict | None = None) -> dict:
        """Create a new page"""
        payload = {
            "parent": {"page_id": parent_id},
            "properties": {
                "title": {
                    "title": [{"text": {"content": title}}]
                }
            }
        }

        if properties:
            payload["properties"].update(properties)

        response = await self.client.post(
            f"{NOTION_API_BASE}/pages",
            json=payload
        )
        response.raise_for_status()
        return response.json()

    async def update_page(self, page_id: str, properties: dict) -> dict:
        """Update page properties"""
        payload = {"properties": properties}
        response = await self.client.patch(
            f"{NOTION_API_BASE}/pages/{page_id}",
            json=payload
        )
        response.raise_for_status()
        return response.json()

    async def query_database(self, database_id: str, filter_obj: dict | None = None,
                            sorts: list | None = None) -> dict:
        """Query a database"""
        payload = {}
        if filter_obj:
            payload["filter"] = filter_obj
        if sorts:
            payload["sorts"] = sorts

        response = await self.client.post(
            f"{NOTION_API_BASE}/databases/{database_id}/query",
            json=payload
        )
        response.raise_for_status()
        return response.json()

    async def get_block_children(self, block_id: str) -> dict:
        """Get children of a block"""
        response = await self.client.get(
            f"{NOTION_API_BASE}/blocks/{block_id}/children"
        )
        response.raise_for_status()
        return response.json()

    async def append_block_children(self, block_id: str, children: list) -> dict:
        """Append children to a block"""
        payload = {"children": children}
        response = await self.client.patch(
            f"{NOTION_API_BASE}/blocks/{block_id}/children",
            json=payload
        )
        response.raise_for_status()
        return response.json()

async def main():
    # Get Notion token from environment
    token = os.getenv("NOTION_TOKEN")
    if not token:
        print("Error: NOTION_TOKEN environment variable not set", file=sys.stderr)
        sys.exit(1)

    # Initialize Notion client
    notion = NotionMCPServer(token)

    # Create MCP server
    server = Server("notion-direct")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name="search_notion",
                description="Search Notion workspace for pages and databases",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query"
                        },
                        "filter_type": {
                            "type": "string",
                            "enum": ["page", "database"],
                            "description": "Filter by type (optional)"
                        }
                    }
                }
            ),
            Tool(
                name="get_page",
                description="Get a Notion page by ID",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "page_id": {
                            "type": "string",
                            "description": "The Notion page ID"
                        }
                    },
                    "required": ["page_id"]
                }
            ),
            Tool(
                name="create_page",
                description="Create a new Notion page",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "parent_id": {
                            "type": "string",
                            "description": "Parent page ID"
                        },
                        "title": {
                            "type": "string",
                            "description": "Page title"
                        },
                        "properties": {
                            "type": "object",
                            "description": "Additional page properties (optional)"
                        }
                    },
                    "required": ["parent_id", "title"]
                }
            ),
            Tool(
                name="update_page",
                description="Update a Notion page's properties",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "page_id": {
                            "type": "string",
                            "description": "The page ID to update"
                        },
                        "properties": {
                            "type": "object",
                            "description": "Properties to update"
                        }
                    },
                    "required": ["page_id", "properties"]
                }
            ),
            Tool(
                name="query_database",
                description="Query a Notion database",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "database_id": {
                            "type": "string",
                            "description": "The database ID to query"
                        },
                        "filter": {
                            "type": "object",
                            "description": "Filter object (optional)"
                        },
                        "sorts": {
                            "type": "array",
                            "description": "Sort array (optional)"
                        }
                    },
                    "required": ["database_id"]
                }
            ),
            Tool(
                name="get_block_children",
                description="Get children blocks of a page or block",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "block_id": {
                            "type": "string",
                            "description": "The block or page ID"
                        }
                    },
                    "required": ["block_id"]
                }
            ),
            Tool(
                name="append_blocks",
                description="Append blocks to a page or block",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "block_id": {
                            "type": "string",
                            "description": "The block or page ID to append to"
                        },
                        "blocks": {
                            "type": "array",
                            "description": "Array of block objects to append"
                        }
                    },
                    "required": ["block_id", "blocks"]
                }
            )
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: Any) -> list[TextContent]:
        try:
            if name == "search_notion":
                result = await notion.search(
                    query=arguments.get("query", ""),
                    filter_type=arguments.get("filter_type")
                )
            elif name == "get_page":
                result = await notion.get_page(arguments["page_id"])
            elif name == "create_page":
                result = await notion.create_page(
                    parent_id=arguments["parent_id"],
                    title=arguments["title"],
                    properties=arguments.get("properties")
                )
            elif name == "update_page":
                result = await notion.update_page(
                    page_id=arguments["page_id"],
                    properties=arguments["properties"]
                )
            elif name == "query_database":
                result = await notion.query_database(
                    database_id=arguments["database_id"],
                    filter_obj=arguments.get("filter"),
                    sorts=arguments.get("sorts")
                )
            elif name == "get_block_children":
                result = await notion.get_block_children(arguments["block_id"])
            elif name == "append_blocks":
                result = await notion.append_block_children(
                    block_id=arguments["block_id"],
                    children=arguments["blocks"]
                )
            else:
                raise ValueError(f"Unknown tool: {name}")

            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=json.dumps({"error": str(e), "type": type(e).__name__}, indent=2)
            )]

    # Run the server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
