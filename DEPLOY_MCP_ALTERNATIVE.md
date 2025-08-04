# Alternative: Deploy MCP as Separate Repository

If the main repository deployment fails, create a separate repository:

## Step 1: Create Separate MCP Repository

```bash
# From project root
cd mcp-server

# Initialize new git repo
git init

# Add all files
git add .

# Commit
git commit -m "Initial MCP server setup for Agencii"

# Create GitHub repo
gh repo create kea-mcp-server --public --push
```

## Step 2: Deploy to Railway

1. Go to Railway.app
2. New Project → Deploy from GitHub
3. Select `kea-mcp-server` repository
4. No need to set root directory
5. Add all environment variables
6. Generate domain

## Environment Variables

```env
BACKEND_API_URL=https://web-production-c4967.up.railway.app
BACKEND_API_KEY=your-key
NOTION_TOKEN=your-token
NOTION_DATABASE_ID=24476a959af7810d9ff5c3f835e82ed7
APP_TOKEN=your-app-token
PORT=8080
MCP_PORT=8000
MCP_TOOLS_DIR=./social_media_mcp
MCP_INSTANCE_NAME=social_media
PYTHONPATH=./social_media_mcp:./tools
```