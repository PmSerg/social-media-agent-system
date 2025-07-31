# Social Media Agent System

A production-ready multi-agent system for automated social media content creation, featuring intelligent research, content generation, and real-time task management.

## 🚀 Overview

This system combines the power of Agency Swarm, OpenAI GPT-4, and Notion to create a seamless content creation workflow. It consists of:

- **Frontend (Agencii Platform)**: Orchestrator agent that handles commands and manages tasks
- **Backend (Self-hosted API)**: Research and Copywriter agents that perform the actual work
- **Real-time Updates**: Webhook-based notifications for instant feedback

## 📋 Features

- **Instant Execution Mode**: Get results in 30-60 seconds
- **Multi-Platform Support**: Twitter, LinkedIn, and Instagram
- **Intelligent Research**: Web search and trend analysis
- **Smart Content Generation**: Platform-optimized with tone control
- **Task Persistence**: All tasks tracked in Notion
- **Production-Ready**: Rate limiting, error handling, and monitoring

## 🏗️ Architecture

```
┌─────────────────────┐     ┌─────────────────────┐
│   Agencii Platform  │     │    Notion Database  │
│  (Orchestrator)     │────▶│   (Task Storage)    │
└──────────┬──────────┘     └─────────────────────┘
           │
           │ API Calls
           ▼
┌─────────────────────┐
│   Backend System    │
│  ┌──────────────┐   │
│  │ Task Monitor │   │
│  └──────┬───────┘   │
│         │           │
│    ┌────┴────┐      │
│    ▼         ▼      │
│ ┌──────┐ ┌────────┐ │
│ │Research││Copywriter│ │
│ │ Agent ││  Agent  │ │
│ └──────┘ └────────┘ │
└─────────────────────┘
```

## 🛠️ Setup Instructions

### Prerequisites

- Python 3.9+
- Redis (for rate limiting)
- Notion workspace with API access
- OpenAI API key
- SerpAPI key (for web search)
- Agencii platform account

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd backend-system
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-test.txt  # For testing
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your credentials:
   ```env
   OPENAI_API_KEY=your_openai_key
   NOTION_TOKEN=your_notion_token
   NOTION_DATABASE_ID=your_database_id
   SERPAPI_KEY=your_serpapi_key
   REDIS_URL=redis://localhost:6379
   BACKEND_WEBHOOK_SECRET=your_webhook_secret
   ```

5. **Set up Notion database**
   
   Create a database with these properties:
   - Name (title)
   - Status (select): Waiting, Processing, Complete, Error
   - Command Used (text)
   - Parameters (text)
   - Task Description (text)
   - Execution Mode (select): Instant, Scheduled
   - Research Data (text)
   - Content (text)
   - Error (text)
   - Webhook URL (url)

6. **Start Redis**
   ```bash
   redis-server
   ```

7. **Run the backend**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup (Agencii)

1. **Deploy to Agencii platform**
   - Upload the `frontend-agencii` folder to Agencii
   - Configure environment variables in Agencii dashboard
   - Set your backend URL (e.g., `https://your-backend.com`)

2. **Configure webhooks**
   - In Agencii settings, set webhook URL to receive updates
   - Use format: `https://app.agencii.com/webhooks/YOUR_WEBHOOK_ID`

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov

# Run specific test file
pytest tests/test_task_monitor.py

# Run only unit tests
pytest -m unit

# Run integration tests
pytest -m integration
```

## 📝 Usage

### Basic Command

```
/create-content-post topic:"AI in Healthcare" platform:Twitter tone:professional
```

### Parameters

- **topic** (required): Subject to create content about
- **platform**: Twitter, LinkedIn, or Instagram (default: Twitter)
- **tone**: professional, casual, humorous, educational (default: professional)
- **include_hashtags**: true/false (default: true)

### Example Workflows

1. **Twitter Post**
   ```
   /create-content-post topic:"Future of Remote Work" platform:Twitter tone:casual
   ```

2. **LinkedIn Article**
   ```
   /create-content-post topic:"AI Ethics in Business" platform:LinkedIn tone:professional
   ```

3. **Instagram Caption**
   ```
   /create-content-post topic:"Sustainable Living Tips" platform:Instagram tone:casual include_hashtags:true
   ```

## 🔧 Configuration

### Rate Limits

Configure in `config/settings.py`:
- Default: 10 requests per minute per IP
- OpenAI: 50 requests per minute
- Notion: 3 requests per second
- SerpAPI: Based on your plan

### Webhook Events

The system sends these webhook events:
- `workflow_started`: Task execution begins
- `research_started`: Research phase starts
- `research_completed`: Research data ready
- `content_generation_started`: Content creation begins
- `content_generated`: Content ready
- `workflow_completed`: Task finished
- `workflow_error`: Error occurred

## 📊 Monitoring

### Health Check
```
GET /health
```

### Metrics
```
GET /metrics
```

### Logs
- Application logs: `logs/app.log`
- Access logs: `logs/access.log`
- Error logs: `logs/error.log`

## 🚨 Troubleshooting

### Common Issues

1. **Rate Limit Errors**
   - Check Redis connection
   - Verify API limits not exceeded
   - Review `RATE_LIMIT_*` settings

2. **Notion API Errors**
   - Verify database ID is correct
   - Check property names match exactly
   - Ensure bot has access to database

3. **OpenAI Timeout**
   - Increase timeout in settings
   - Check API key validity
   - Monitor token usage

### Debug Mode

Enable debug logging:
```env
LOG_LEVEL=DEBUG
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- Agency Swarm for the multi-agent framework
- OpenAI for GPT-4 capabilities
- Notion for task management
- FastAPI for the backend framework