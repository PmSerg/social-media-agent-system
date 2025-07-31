# Setting Up Social Media Agent System with Agencii

## Architecture Overview

```
Agencii Platform (UI)
    ↓
Orchestrator Agent (Main Agent in Agencii)
    ↓
MCP Server (Railway) - Contains 4 tools:
    ├── CommandProcessor
    ├── NotionTaskManager  
    ├── ResearchAgentProxy → Backend API (ResearchAgent)
    └── CopywriterAgentProxy → Backend API (CopywriterAgent)
```

## Step 1: Deploy Backend API

1. Deploy the `backend-system` to your preferred hosting:
   ```bash
   cd backend-system
   # Deploy to Railway/Heroku/AWS etc
   ```

2. Note your backend API URL (e.g., `https://your-backend.railway.app`)

## Step 2: Deploy MCP Server

1. **Push MCP server to GitHub:**
   ```bash
   cd mcp-server
   git init
   git add .
   git commit -m "Initial MCP server"
   git remote add origin https://github.com/YOUR_USERNAME/social-media-mcp-server.git
   git push -u origin main
   ```

2. **Deploy to Railway:**
   - Go to [Railway](https://railway.app)
   - Create new project → Deploy from GitHub repo
   - Select your MCP server repository
   - Add environment variables:
     ```
     BACKEND_API_URL=https://your-backend-api.com
     BACKEND_API_KEY=your-api-key
     NOTION_TOKEN=secret_xxx
     NOTION_DATABASE_ID=xxx
     MCP_AUTH_TOKEN=your-secure-token
     ```
   - Generate domain under Settings → Networking

3. **Note your MCP endpoints:**
   - Main SSE endpoint: `https://your-mcp-server.railway.app/sse`

## Step 3: Create Agent in Agencii

1. **Log in to Agencii** at the correct URL (not app.agencii.com)

2. **Create New Agent:**
   - Name: "Social Media Orchestrator"
   - Model: GPT-4 (recommended)
   - Temperature: 0.7

3. **Add Instructions:**
   - Copy content from `agencii-orchestrator/instructions.md`
   - Paste into agent instructions

4. **Add MCP Tools:**
   - Click "Tools" → "New Tool" → "MCP"
   - Title: "Orchestrator Tools"
   - Description: "Command processing, task management, and agent coordination"
   - MCP URL: `https://your-mcp-server.railway.app/sse`
   - Authentication: Bearer token (use your MCP_AUTH_TOKEN)

5. **Save Agent**

## Step 4: Test the System

1. **Test command parsing:**
   ```
   /create-content-post topic:"Test topic" platform:Twitter
   ```

2. **Verify workflow:**
   - Command is parsed ✓
   - Task created in Notion ✓
   - Research conducted ✓
   - Content generated ✓
   - Task updated with results ✓

## Troubleshooting

### MCP Server Issues
- Check Railway logs: `railway logs`
- Verify environment variables are set
- Test endpoint: `curl https://your-mcp-server.railway.app/health`

### Backend API Issues
- Ensure backend is running
- Check API authentication
- Verify rate limits not exceeded

### Notion Issues
- Verify database ID is correct
- Check integration has access
- Ensure all properties exist

## Advanced Configuration

### Multiple Environments
Create separate MCP servers for dev/staging/prod:
```
mcp-server-dev/
mcp-server-staging/
mcp-server-prod/
```

### Custom Tools
Add new tools to `mcp-server/tools/`:
1. Create new tool file
2. Inherit from `BaseTool`
3. Implement `run()` method
4. Deploy to Railway

### Monitoring
- Set up Railway metrics
- Add error tracking (Sentry)
- Monitor API usage

## Next Steps

1. **Enhance Agent Prompts** - Add more detailed instructions
2. **Add More Tools** - Analytics, scheduling, etc.
3. **Create Agent Teams** - Multiple specialized agents
4. **Add Integrations** - Connect to more platforms