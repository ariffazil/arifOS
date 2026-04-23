#!/usr/bin/env python3
"""
notion_tool.py — arifOS Notion Integration
F2 (Truth): Verified Notion data access
F12 (Injection): Token via environment only
"""

import os
import sys

from notion_client import Client
from notion_client.errors import APIResponseError

# Initialize client (F12: token from env only)
NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
if not NOTION_TOKEN:
    print("❌ F12: NOTION_TOKEN not set", file=sys.stderr)
    sys.exit(1)

notion = Client(auth=NOTION_TOKEN)


def query_database(database_id: str, filter_obj=None):
    """
    Query Notion database with optional filter.
    F2: Returns verified data from Notion API.
    """
    try:
        results = notion.databases.query(
            database_id=database_id,
            filter=filter_obj
        )
        return {
            "ok": True,
            "results": results.get("results", []),
            "next_cursor": results.get("next_cursor"),
            "has_more": results.get("has_more", False)
        }
    except APIResponseError as e:
        return {"ok": False, "error": str(e), "code": e.code}


def create_page(parent_id: str, title: str, content: str, icon=None):
    """
    Create Notion page with content.
    F1: Creates reversible record (page can be deleted).
    """
    try:
        page = notion.pages.create(
            parent={"page_id": parent_id},
            icon=icon or {"emoji": "📄"},
            properties={
                "title": {
                    "title": [{"text": {"content": title}}]
                }
            },
            children=[{
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"text": {"content": content}}]
                }
            }]
        )
        return {
            "ok": True,
            "page_id": page["id"],
            "url": page["url"]
        }
    except APIResponseError as e:
        return {"ok": False, "error": str(e), "code": e.code}


def get_page(page_id: str):
    """Retrieve page by ID"""
    try:
        page = notion.pages.retrieve(page_id=page_id)
        return {"ok": True, "page": page}
    except APIResponseError as e:
        return {"ok": False, "error": str(e), "code": e.code}


def update_page(page_id: str, properties: dict):
    """Update page properties"""
    try:
        page = notion.pages.update(page_id=page_id, properties=properties)
        return {"ok": True, "page": page}
    except APIResponseError as e:
        return {"ok": False, "error": str(e), "code": e.code}


def search_notion(query: str, filter_type=None):
    """
    Search across Notion workspace.
    F2: Grounded search results.
    """
    try:
        results = notion.search(
            query=query,
            filter={"value": filter_type, "property": "object"} if filter_type else None
        )
        return {
            "ok": True,
            "results": results.get("results", []),
            "next_cursor": results.get("next_cursor"),
            "has_more": results.get("has_more", False)
        }
    except APIResponseError as e:
        return {"ok": False, "error": str(e), "code": e.code}


# CLI interface for aCLIp integration
if __name__ == "__main__":
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description="arifOS Notion Tool")
    parser.add_argument("action", choices=[
        "query_database", "create_page", "get_page", "update_page", "search"
    ])
    parser.add_argument("--database-id", help="Notion database ID")
    parser.add_argument("--page-id", help="Notion page ID")
    parser.add_argument("--parent-id", help="Parent page ID")
    parser.add_argument("--title", help="Page title")
    parser.add_argument("--content", help="Page content")
    parser.add_argument("--query", help="Search query")
    parser.add_argument("--json", action="store_true", help="JSON output")
    
    args = parser.parse_args()
    
    result = None
    
    if args.action == "query_database":
        if not args.database_id:
            print("❌ --database-id required", file=sys.stderr)
            sys.exit(1)
        result = query_database(args.database_id)
    
    elif args.action == "create_page":
        if not all([args.parent_id, args.title, args.content]):
            print("❌ --parent-id, --title, --content required", file=sys.stderr)
            sys.exit(1)
        result = create_page(args.parent_id, args.title, args.content)
    
    elif args.action == "get_page":
        if not args.page_id:
            print("❌ --page-id required", file=sys.stderr)
            sys.exit(1)
        result = get_page(args.page_id)
    
    elif args.action == "search":
        if not args.query:
            print("❌ --query required", file=sys.stderr)
            sys.exit(1)
        result = search_notion(args.query)
    
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if result.get("ok"):
            print(f"✅ {args.action}: Success")
            if "url" in result:
                print(f"   URL: {result['url']}")
            if "results" in result:
                print(f"   Results: {len(result['results'])}")
        else:
            print(f"❌ {args.action}: {result.get('error')}", file=sys.stderr)
            sys.exit(1)
