# Social Media Agent System - Backend API

FastAPI backend for the Social Media Agent System with Research and Copywriter agents.

## Features

- Research Agent for web search and content analysis
- Copywriter Agent for platform-optimized content generation
- Rate limiting and error handling
- Async/await throughout
- Notion integration for task tracking

## Setup

1. Copy `.env.example` to `.env`
2. Fill in your API keys
3. Install dependencies: `pip install -r requirements.txt`
4. Run: `uvicorn main:app --reload`

## Environment Variables

- `OPENAI_API_KEY` - OpenAI API key
- `NOTION_TOKEN` - Notion integration token
- `NOTION_DATABASE_ID` - Notion database ID
- `SERPAPI_KEY` - SerpAPI key for web search
- `REDIS_URL` - Redis connection URL

## Deployment

This backend is designed to run on Railway, Heroku, or any Docker-compatible platform.

## API Endpoints

- `POST /api/v1/execute` - Execute command
- `POST /api/v1/agents/research` - Call Research Agent
- `POST /api/v1/agents/copywriter` - Call Copywriter Agent
- `GET /health` - Health check