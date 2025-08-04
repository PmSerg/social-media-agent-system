# Agencii Platform Setup Guide

## Quick Setup

### 1. Create New Agent in Agencii

1. Go to your Agencii dashboard
2. Click "Create New Agent"
3. Name: "Kea Content Creator"
4. Model: GPT-4

### 2. Add Tools

In the agent configuration, click "Add Tools" and paste the content from `AGENCII_TOOLS_SPEC.json`

### 3. Set Agent Instructions

Paste this into the agent's system prompt:

```
You are Kea's Social Media Content Assistant. You help create research-backed, platform-optimized content using Kea's brand archetypes:

- Caregiver (35%): Empathetic, supportive, nurturing content
- Explorer (35%): Innovative, bold, pioneering content  
- Regular Guy (30%): Simple, practical, relatable content

When users ask for content:
1. Use the CreateContent tool with their topic
2. The system will automatically select an archetype
3. Monitor progress with CheckTaskStatus
4. Use ListRecentContent to show previous work

Always mention which archetype was used and why it fits the content.
```

### 4. Environment Variables

Add these in Agencii's environment settings:
- `BACKEND_URL`: Your Railway backend URL
- `API_KEY`: Your backend API key

### 5. Test Commands

Try these in chat:
```
Create a LinkedIn post about digital banking for small businesses

Generate Twitter content about fintech innovation with casual tone

Make a Facebook post about customer support in banking
```

## How It Works

1. **User Request** → Agencii agent receives command
2. **Tool Call** → Agent calls CreateContent with parameters
3. **Backend Processing** → 
   - Selects archetype (weighted random)
   - Research Agent gathers data
   - Copywriter Agent creates content
4. **Response** → Content returned with archetype info

## Tool Descriptions

### CreateContent
Main tool for content generation. Automatically:
- Selects brand archetype
- Performs web research
- Generates platform-optimized content
- Creates relevant hashtags

### CheckTaskStatus
Monitor task progress in real-time. Shows:
- Current processing stage
- Agent working on task
- Any errors encountered

### ListRecentContent
View previously created content. Can filter by:
- Platform
- Archetype used
- Time period

## Tips

1. **Natural Language**: The agent understands natural requests
2. **Archetype Info**: Ask which archetype was used and why
3. **Variations**: Request multiple versions with different archetypes
4. **Platform Best Practices**: Content is auto-optimized per platform

## Troubleshooting

**"Backend not responding"**
- Check BACKEND_URL is correct
- Verify backend is running on Railway

**"No archetype information"**
- Backend may be using older version
- Check logs for archetype selection

**"Content too generic"**
- Provide more specific topics
- Include industry context
- Mention target audience