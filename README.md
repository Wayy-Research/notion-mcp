# Notion Direct MCP Server

A simple, reliable MCP server for Notion that uses the Notion API directly.

## Features

- **Direct API Integration**: No middleware, just direct API calls that work
- **Core Operations**: Search, create, read, update pages and databases
- **Block Operations**: Read and append blocks to pages
- **Simple & Reliable**: Minimal dependencies, easy to debug

## Setup

### 1. Install Dependencies

```bash
cd ~/mcp-servers/notion-direct
python3 -m venv .venv
source .venv/bin/python
pip install -r requirements.txt
```

### 2. Get Notion Integration Token

1. Go to https://www.notion.so/profile/integrations
2. Create a new internal integration
3. Copy the token (starts with `ntn_`)
4. Grant the integration access to your pages/databases

### 3. Configure Claude Code

Add to `~/.config/claude-code/config.json`:

```json
{
  "mcpServers": {
    "notion": {
      "command": "/home/rcgalbo/mcp-servers/notion-direct/.venv/bin/python",
      "args": ["/home/rcgalbo/mcp-servers/notion-direct/server.py"],
      "env": {
        "NOTION_TOKEN": "your_token_here"
      }
    }
  }
}
```

### 4. Restart Claude Code and Connect

Run `/mcp` in Claude Code to connect to the server.

## Available Tools

- `search_notion`: Search for pages and databases
- `get_page`: Get page details by ID
- `create_page`: Create a new page
- `update_page`: Update page properties
- `query_database`: Query a database with filters and sorts
- `get_block_children`: Get child blocks of a page
- `append_blocks`: Append blocks to a page

## Usage Examples

### Search for a project
```
Use the search_notion tool to find "WNY Leaf" project
```

### Create a task page
```
Create a new task page under the WNY Leaf project with title "Implement backend API"
```

### Query database
```
Query the tasks database and show all incomplete tasks
```

## Troubleshooting

- **Token issues**: Make sure your token starts with `ntn_` and has access to your pages
- **Connection issues**: Check that the virtual environment path is correct
- **API errors**: All errors are returned in the tool response for easy debugging

## For New Projects

To use this server in other projects:
1. Grant your Notion integration access to the project pages
2. Use the same config in Claude Code
3. No additional setup needed!
