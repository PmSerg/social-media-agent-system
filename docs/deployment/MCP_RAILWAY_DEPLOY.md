# 🚀 Deploy MCP Server to Railway - Quick Guide

## Environment Variables Template

Copy and fill in with your actual values:

```env
BACKEND_API_URL=https://your-backend.up.railway.app
BACKEND_API_KEY=your-backend-api-key
NOTION_TOKEN=your-notion-token
NOTION_DATABASE_ID=24476a959af7810d9ff5c3f835e82ed7
APP_TOKEN=your-secure-app-token
PORT=8080
MCP_PORT=8000
MCP_TOOLS_DIR=./social_media_mcp
MCP_INSTANCE_NAME=social_media
PYTHONPATH=./social_media_mcp:./tools
```

## Step 1: Deploy to Railway

1. **Go to Railway**: https://railway.app/new

2. **Deploy from GitHub**:
   - Click "Deploy from GitHub repo"
   - Select: `PmSerg/social-media-agent-system`
   - Choose branch: `main`

3. **Set Root Directory**:
   - After deployment starts, go to Settings
   - Set **Root Directory**: `mcp-server`
   - Click "Apply Changes"

4. **Add Environment Variables**:
   - Go to "Variables" tab
   - Add each variable from your .env file
   - Make sure to use your actual values

5. **Generate Domain**:
   - Go to Settings → Networking
   - Click "Generate Domain"
   - Save your URL

## Step 2: Verify Deployment

```bash
# Test health endpoint
curl https://YOUR-RAILWAY-URL.up.railway.app/health
```

## Step 3: Add to Agencii

1. **Login to Agencii**: https://app.agencii.ai
2. **Add MCP Server**:
   - Name: `social-media`
   - URL: `https://YOUR-URL.up.railway.app/social-media/sse`
   - Auth: Bearer Token
   - Token: Your APP_TOKEN value

## Available Tools

- CommandProcessor
- NotionTaskManager
- ResearchAgentProxy
- CopywriterAgentProxy