# Agencii-Specific Project Rules for Kea Pro Agentic System

## 🎯 Project Context
This is a hybrid social media agent system that integrates:
- **Agencii Platform**: No-code agent orchestration using Agency Swarm
- **MCP Server**: Bridge between Agencii and backend services
- **Backend API**: FastAPI-based agent processing system

## 📁 Required Directory Structure

### MCP Server Structure (Following Agencii Standards)
```
mcp-server/
├── tools/                    # Shared tools directory
│   ├── SharedTool1.py
│   └── SharedTool2.py
├── social_media_mcp/        # Instance-specific directory with _mcp suffix
│   ├── ResearchAgentProxy.py
│   ├── CopywriterAgentProxy.py
│   ├── NotionTaskManager.py
│   └── CommandProcessor.py
├── mcp.json                 # Stdio server configuration
├── railway.json             # Railway deployment config
├── .env.example             # Environment template
└── requirements.txt         # Python dependencies
```

### Frontend Agencii Structure (Current - Correct)
```
frontend-agencii/
├── agency.py               # Main entry point
├── requirements.txt        # Dependencies
├── SocialMediaAgency/      # Agency implementation
│   ├── agency_manifesto.md # Shared instructions
│   └── Orchestrator/       # Main agent
│       ├── Orchestrator.py
│       ├── instructions.md
│       └── tools/          # Agent-specific tools
```

## 🔧 Development Rules

### 1. Tool Development
- **Shared Tools**: Place in `/mcp-server/tools/`
- **Instance Tools**: Place in `/mcp-server/social_media_mcp/`
- **Naming**: Use descriptive names, avoid generic terms
- **Format**: Follow Agencii tool template structure

### 2. MCP Configuration
- **Server Type**: Use "Stdio" servers in mcp.json
- **SSE Endpoints**: Format as `https://<domain>/<server-name>/sse`
- **Environment Variables**: 
  - `MCP_TOOLS_DIR`: Path to tools directory
  - `MCP_INSTANCE_NAME`: Instance identifier (e.g., "social_media")

### 3. Deployment Process
- **Platform**: Railway.com
- **Build**: Use nixpacks or Dockerfile
- **Environment**: Set all required variables in Railway dashboard
- **URL Format**: Generate and use Railway deployment URL

### 4. Integration Points
- **Agencii → MCP**: Via SSE endpoints
- **MCP → Backend**: Via HTTP API calls
- **Authentication**: Bearer token in headers
- **Real-time Updates**: Server-Sent Events (SSE)

## 🚫 What NOT to Do
- Don't mix proxy tools with implementation tools
- Don't use generic tool names like "TestTool"
- Don't hardcode URLs or credentials
- Don't deploy without proper environment configuration

## ✅ Checklist Before Deployment
- [ ] Tools organized in correct directories
- [ ] mcp.json properly configured for Stdio servers
- [ ] All environment variables documented in .env.example
- [ ] Railway.json has correct build settings
- [ ] SSE endpoints tested and working
- [ ] Authentication properly implemented
- [ ] No hardcoded values in code

## 🔄 Migration Steps from Current Structure
1. Create `social_media_mcp/` directory
2. Move instance-specific tools to new directory
3. Update import paths in tools
4. Configure mcp.json for Stdio servers
5. Test SSE endpoints
6. Deploy to Railway
7. Connect to Agencii platform

## 📚 References
- [Agencii MCP Template](https://github.com/agency-ai-solutions/agencii-mcp-tools-deployment-template)
- [Agency GitHub Template](https://github.com/agency-ai-solutions/agency-github-template)
- [MCP Protocol Docs](https://docs.agencii.ai/mcp)