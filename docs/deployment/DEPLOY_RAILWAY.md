# Deploy to Railway - Step by Step

## 1. Backend API Deployment

1. **Go to Railway**: https://railway.app
2. **Create New Project** → **Deploy from GitHub Repo**
3. **Select**: `social-media-agent-backend`
4. **Add Environment Variables**:
   ```
   OPENAI_API_KEY=your-openai-key
   NOTION_TOKEN=secret_your-notion-token
   NOTION_DATABASE_ID=your-database-id
   SERPAPI_KEY=your-serpapi-key
   REDIS_URL=will-be-added-after-redis-setup
   BACKEND_WEBHOOK_SECRET=generate-random-secret
   ENVIRONMENT=production
   ```

5. **Add Redis Service**:
   - In Railway project → **New** → **Database** → **Redis**
   - Copy the `REDIS_URL` from Redis service
   - Update the `REDIS_URL` in your backend service variables

6. **Generate Domain**:
   - Go to backend service → **Settings** → **Networking**
   - Click **Generate Domain**
   - Note your backend URL (e.g., `https://social-media-agent-backend.up.railway.app`)

## 2. MCP Server Deployment

1. **Create Another Project** or use same project
2. **Deploy from GitHub Repo**
3. **Select**: Push MCP server folder as separate repo first:
   ```bash
   cd ../mcp-server
   git init
   git add .
   git commit -m "Initial MCP server"
   gh repo create social-media-agent-mcp --public --description "MCP Server for Agencii" --clone=false
   git remote add origin https://github.com/PmSerg/social-media-agent-mcp.git
   git push -u origin main
   ```

4. **In Railway**, select the new MCP repo
5. **Add Environment Variables**:
   ```
   BACKEND_API_URL=https://your-backend.up.railway.app
   BACKEND_API_KEY=your-backend-webhook-secret
   NOTION_TOKEN=secret_your-notion-token
   NOTION_DATABASE_ID=your-database-id
   MCP_AUTH_TOKEN=generate-secure-token
   PORT=8080
   ```

6. **Generate Domain** for MCP server
7. **Note MCP URL** (e.g., `https://social-media-agent-mcp.up.railway.app`)

## 3. Verify Deployments

### Test Backend:
```bash
curl https://your-backend.up.railway.app/health
```

### Test MCP:
```bash
curl https://your-mcp.up.railway.app/health
```

## 4. Configure Agencii

1. Go to Agencii platform
2. Create new agent
3. Add MCP tools with URL: `https://your-mcp.up.railway.app/sse`
4. Use Bearer token authentication with your `MCP_AUTH_TOKEN`

## Troubleshooting

- **Check Logs**: Railway dashboard → Service → View Logs
- **Environment Variables**: Make sure all are set correctly
- **Redis Connection**: Ensure Redis URL is correct
- **Port Configuration**: Railway uses PORT env variable