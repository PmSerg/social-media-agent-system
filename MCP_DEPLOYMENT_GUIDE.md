# MCP Server Deployment Guide for Railway & Agencii

## 📋 Prerequisites

1. **Railway account**: https://railway.app
2. **GitHub account** with access to your repository
3. **Backend API** already deployed and running
4. **Environment variables** ready:
   - `BACKEND_API_URL` - Your backend Railway URL
   - `BACKEND_API_KEY` - Your backend API secret key
   - `NOTION_TOKEN` - Notion integration token
   - `NOTION_DATABASE_ID` - Main content database ID
   - `APP_TOKEN` - Secure token for Agencii authentication

## 🚀 Step 1: Deploy MCP Server to Railway

### Option A: Deploy from Main Repository (Recommended)

1. **Login to Railway**: https://railway.app/dashboard

2. **Create New Project**:
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your `social-media-agent-system` repository

3. **Configure Service**:
   - In Railway, click on the service
   - Go to **Settings** → **Root Directory**
   - Set to: `mcp-server`

4. **Add Environment Variables**:
   ```
   BACKEND_API_URL=https://your-backend.up.railway.app
   BACKEND_API_KEY=your-backend-api-secret
   NOTION_TOKEN=secret_xxxxx
   NOTION_DATABASE_ID=24476a959af7810d9ff5c3f835e82ed7
   APP_TOKEN=generate-secure-token-here
   PORT=8080
   MCP_PORT=8000
   MCP_TOOLS_DIR=./social_media_mcp
   MCP_INSTANCE_NAME=social_media
   PYTHONPATH=./social_media_mcp:./tools
   ```

5. **Generate Domain**:
   - Go to **Settings** → **Networking**
   - Click "Generate Domain"
   - Note your URL (e.g., `https://kea-mcp-server.up.railway.app`)

### Option B: Deploy from Separate Repository

1. **Create separate repository** (if needed):
   ```bash
   cd mcp-server
   git init
   git add .
   git commit -m "MCP server for Agencii"
   gh repo create kea-mcp-server --public --push
   ```

2. Follow steps 1-5 from Option A, but select the new repository

## 🔧 Step 2: Verify Deployment

1. **Check health endpoint**:
   ```bash
   curl https://your-mcp-url.up.railway.app/health
   ```
   Expected response:
   ```json
   {"status": "healthy", "service": "kea-mcp-proxy"}
   ```

2. **Check root endpoint**:
   ```bash
   curl https://your-mcp-url.up.railway.app/
   ```
   Expected response:
   ```json
   {
     "name": "Kea MCP Server",
     "version": "1.0.0",
     "endpoints": {
       "sse": "/sse",
       "messages": "/messages",
       "health": "/health"
     }
   }
   ```

3. **Check logs in Railway**:
   - Go to your service in Railway
   - Click "View Logs"
   - Look for:
     - "Starting Python MCP server on port 8000..."
     - "Server started successfully"
     - No error messages

## 🔌 Step 3: Add MCP Server to Agencii

1. **Login to Agencii**: https://app.agencii.ai

2. **Navigate to MCP Integration**:
   - Go to your agency/agent settings
   - Find "MCP Tools" or "External Tools" section

3. **Add New MCP Server**:
   - **Name**: `social-media-mcp`
   - **SSE Endpoint**: `https://your-mcp-url.up.railway.app/social-media/sse`
   - **Authentication Type**: Bearer Token
   - **Token**: Your `APP_TOKEN` value

4. **Configure Tools**:
   The following tools will be available:
   - `CommandProcessor` - Process natural language commands
   - `NotionTaskManager` - Create and manage Notion tasks
   - `ResearchAgentProxy` - Trigger research agent
   - `CopywriterAgentProxy` - Trigger copywriter agent

5. **Test Connection**:
   - Click "Test Connection" or similar button
   - Should show "Connected" status

## 🧪 Step 4: Test Integration

1. **In Agencii, test a simple command**:
   ```
   Use the CommandProcessor tool to parse: "create a twitter post about AI"
   ```

2. **Check Notion database**:
   - Should see a new task created
   - Status should update as agents process

3. **Monitor logs**:
   - Railway logs for MCP server
   - Backend logs for agent processing

## 🚨 Troubleshooting

### MCP Server Not Starting
- Check Python is installed in Railway (it should be automatic)
- Verify all environment variables are set
- Check logs for import errors

### Connection Failed in Agencii
- Verify the SSE endpoint URL is correct
- Check APP_TOKEN matches exactly
- Ensure Railway domain is generated and active

### Tools Not Showing
- Check MCP server logs for tool loading errors
- Verify `social_media_mcp` directory structure
- Ensure all Python dependencies are installed

### Authentication Errors
- APP_TOKEN must match between Railway and Agencii
- Use Bearer token format in Agencii
- Check for extra spaces in token

## 📝 Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `BACKEND_API_URL` | Your backend API URL | `https://backend.up.railway.app` |
| `BACKEND_API_KEY` | Backend authentication key | `secret-key-123` |
| `NOTION_TOKEN` | Notion integration token | `secret_xxxxx` |
| `NOTION_DATABASE_ID` | Main content database | `24476a959af7810d9ff5c3f835e82ed7` |
| `APP_TOKEN` | Agencii authentication | `secure-random-token` |
| `PORT` | Main server port | `8080` |
| `MCP_PORT` | MCP server port | `8000` |
| `MCP_TOOLS_DIR` | Tools directory | `./social_media_mcp` |

## ✅ Success Indicators

1. Railway shows "Active" status
2. Health endpoint returns 200 OK
3. Agencii shows "Connected" for MCP server
4. Tools are listed in Agencii
5. Test commands create tasks in Notion

## 🔗 Next Steps

After successful deployment:
1. Update your Orchestrator agent to use the MCP tools
2. Test the full workflow from Agencii
3. Monitor performance and logs
4. Set up alerts for failures (optional)