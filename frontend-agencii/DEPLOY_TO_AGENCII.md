# Deploying to Agencii Platform

## Overview

This guide explains how to deploy the Kea Social Media Agency to the Agencii platform.

## Prerequisites

1. **Agencii Account**: Create an account at [agencii.com](https://agencii.com)
2. **Backend Deployed**: Ensure the backend API is deployed to Railway
3. **MCP Server Deployed**: Ensure the MCP server is deployed to Railway
4. **Notion Setup**: All databases created and integration connected

## Deployment Steps

### 1. Prepare Environment Variables

You'll need these values ready:
- `BACKEND_URL`: Your Railway backend URL (e.g., `https://kea-backend.railway.app`)
- `NOTION_TOKEN`: Your Notion integration token (starts with `ntn_`)
- `NOTION_DATABASE_ID`: The Content Plan database ID
- `API_SECRET_KEY`: Secret key for backend authentication

### 2. Upload to Agencii

1. Log into your Agencii dashboard
2. Click "Create New Agency" or "Import Agency"
3. Upload this entire `frontend-agencii` directory
4. Agencii will detect the `agency.py` and `agencii_config.json`

### 3. Configure Environment

1. In Agencii dashboard, go to "Environment Variables"
2. Add all required variables from Step 1
3. Save the configuration

### 4. Tool Configuration

Agencii will automatically detect the tools from:
- `SocialMediaAgency/Orchestrator/tools/`
- Each tool inherits from `BaseTool` and is auto-configured

### 5. Test the Deployment

1. In Agencii, start a chat with your Orchestrator agent
2. Try a test command:
   ```
   /create-content-post topic:"Test post" platform:twitter tone:casual
   ```
3. Check your Notion database for the created task
4. Monitor the real-time updates

## Architecture on Agencii

```
Agencii Platform
    │
    ├── Orchestrator Agent (GPT-4)
    │   ├── CommandProcessor Tool
    │   ├── NotionTaskManager Tool
    │   ├── ResearchAgentProxy Tool
    │   └── CopywriterAgentProxy Tool
    │
    └── Communicates with → Backend API → Agents
```

## Tool Schemas

The platform uses Pydantic schemas from `schemas.py` to:
- Generate UI forms for tools
- Validate inputs
- Provide autocomplete
- Show documentation

## Monitoring

1. **Agencii Logs**: Check agent conversation logs
2. **Backend Logs**: Monitor Railway dashboard
3. **Notion Database**: Track task progress
4. **Error Handling**: Errors appear in chat and Notion

## Troubleshooting

### Common Issues:

1. **"Cannot connect to backend"**
   - Check BACKEND_URL is correct
   - Ensure backend is running on Railway
   - Verify CORS settings allow Agencii domain

2. **"Notion authentication failed"**
   - Regenerate Notion integration token
   - Ensure integration has database access
   - Check token starts with 'ntn_'

3. **"Tool not found"**
   - Ensure all tools inherit from BaseTool
   - Check __init__.py imports
   - Verify tool files are uploaded

### Debug Mode

Enable debug logging in Agencii:
1. Go to Agency Settings
2. Enable "Debug Mode"
3. View detailed logs in console

## Best Practices

1. **Version Control**: Tag releases before deploying
2. **Testing**: Test locally with `agency.demo_gradio()`
3. **Documentation**: Keep instructions.md updated
4. **Monitoring**: Set up alerts for backend errors
5. **Rollback**: Keep previous version ready

## Support

- **Agencii Docs**: [docs.agencii.com](https://docs.agencii.com)
- **Agency Swarm**: [github.com/VRSEN/agency-swarm](https://github.com/VRSEN/agency-swarm)
- **Backend Issues**: Check Railway logs
- **Notion Issues**: Check integration permissions