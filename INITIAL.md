# INITIAL.md - MVP Social Media Agent System - Phase 1

## FEATURE (MVP):

- **Simplified multi-agent system** using Agency Swarm with frontend-backend separation
- **Instant execution mode**: Real-time command processing for one core workflow
- **Frontend**: Single Orchestrator Agent on Agencii Platform for client interaction
- **Backend**: Self-hosted minimal agents (Research + Copywriter) using OpenAI GPT-4
- **Notion integration** as primary database for task management and content storage
- **Single workflow focus**: create-content-post command
- **Basic monitoring**: Simple logs and execution tracking
- **MVP deployment** on Agencii AI Developer Plan ($79/month) + minimal backend

## ARCHITECTURE:

### **Frontend Layer (Agencii Platform)**:
- **Orchestrator Agent** - Single client-facing agent with Slack integration
  - Command processor for .md-defined workflows with instant execution
  - Natural language interpreter for free-form conversation
  - Agent proxy tools for direct backend communication
  - Real-time progress monitoring with live client updates
  - Notion task creation and result presentation

### **Backend Layer (Self-hosted - MVP)**:
- **TaskMonitor Service**: Instant mode only for MVP
- **Research Agent** - Web search + GPT-4 analysis + Notion integration
- **Copywriter Agent** - Content generation with platform optimization
- **FastAPI Gateway** - Basic HTTP endpoints with rate limiting

### **Command System (MVP)**:
- Single workflow definition: `/commands/create-content-post.md`
- Basic parameter validation
- Simplified execution flow
- Foundation for future command expansion

## EXECUTION MODE (MVP):

### **🚀 Instant Mode Only**:
```
Flow: Client command → Orchestrator → Backend instant execution → Live updates → Result
Timeline: Real-time processing with progress notifications
Use case: "/create-content-post topic='AI trends' platform='linkedin'"
```

*Note: Scheduled mode will be added in Phase 2 after MVP validation*

## MVP COMMAND:

### **Single Command for MVP**:

#### **/create-content-post**
```markdown
# /create-content-post

## Description
Creates social media content with research (MVP: text only, no images)

## Parameters
- topic: Content topic (required)
- platform: Target platform (required) - linkedin|twitter (MVP: 2 platforms only)
- tone: Content tone (optional) - professional|casual

## Workflow Steps
1. Research Agent → Topic analysis and data gathering (2-3 min)
2. Copywriter Agent → Platform-optimized content creation (1-2 min)

## Conditions
- If platform = "linkedin": use professional tone, longer content
- If platform = "twitter": enforce 280 char limit

## Expected Output
- Platform-optimized text content
- Basic hashtags (3-5)
- Saved to Notion with timestamp
```

*Additional commands will be added in Phase 2 after MVP validation:*
- `/research-only` - Deep topic research
- `/visual-content` - Image generation workflow  
- `/rewrite-content` - Content adaptation
- `/hashtag-optimization` - Hashtag strategy

## EXECUTION LOGIC:

### **TaskMonitor Dual-Mode Processing**:

```python
class TaskMonitor:
    async def process_task(self, task):
        """Main task processing logic"""
        execution_mode = task["properties"]["Execution Mode"]["select"]["name"]
        command_used = task["properties"]["Command Used"]["rich_text"][0]["plain_text"]
        
        if execution_mode == "Instant":
            await self.instant_execution(task, command_used)
        else:  # Scheduled
            await self.scheduled_execution(task, command_used)
    
    async def instant_execution(self, task, command):
        """Real-time execution with live updates"""
        if command.startswith("/"):
            # Parse .md command file
            workflow = self.parse_command_file(f"commands/{command[1:]}.md")
        else:
            # Default workflow for manual tasks
            workflow = self.get_default_workflow(task)
        
        # Execute with live client notifications
        for step in workflow["steps"]:
            await self.notify_client(f"🔄 Starting {step}...")
            result = await self.execute_agent_step(task, step)
            await self.notify_client(f"✅ {step} completed")
        
        await self.notify_client("🎉 Task completed successfully!")
    
    async def scheduled_execution(self, task, command):
        """Background execution without live updates"""
        if command.startswith("/"):
            workflow = self.parse_command_file(f"commands/{command[1:]}.md")
        else:
            workflow = self.get_default_workflow(task)
        
        # Execute silently in background
        for step in workflow["steps"]:
            await self.execute_agent_step(task, step)
        
        # Single completion notification
        await self.notify_completion(task)
```

### **Orchestrator Command Processing**:

```python
class CommandProcessor(BaseTool):
    """Processes structured commands from client"""
    
    def execute_command(self, command: str, params: dict):
        """Direct command execution via Orchestrator"""
        
        # Create Notion task with instant execution mode
        task_id = self.create_notion_task({
            **params,
            "Command Used": command,
            "Execution Mode": "Instant",
            "Agent Status": "Waiting"
        })
        
        # Trigger immediate backend processing
        response = requests.post(f"{BACKEND_URL}/execute-command", {
            "task_id": task_id,
            "command": command,
            "params": params,
            "mode": "instant"
        })
        
        return f"⚡ Executing {command} with real-time updates..."
    
    def create_scheduled_task(self, description: str, params: dict):
        """Creates background task for scheduled processing"""
        
        task_id = self.create_notion_task({
            **params,
            "Task Description": description,
            "Command Used": "manual",
            "Execution Mode": "Scheduled",
            "Agent Status": "Waiting"
        })
        
        return f"📋 Task scheduled for background processing: {task_id}"
```

### **Backend API Endpoints**:

```python
# FastAPI endpoints for dual-mode execution

@app.post("/execute-command")
async def execute_command_instant(request: CommandRequest):
    """Instant command execution with live updates"""
    task = await get_notion_task(request.task_id)
    await task_monitor.instant_execution(task, request.command)
    return {"status": "processing", "mode": "instant"}

@app.post("/process-scheduled")
async def process_scheduled_tasks():
    """Background processing of scheduled tasks"""
    tasks = await get_scheduled_tasks_from_notion()
    for task in tasks:
        await task_monitor.scheduled_execution(task, task["command_used"])
    return {"processed": len(tasks)}
```

### **Client Interaction Flow**:

#### **Instant Commands (Live Updates)**:
```
👤 "/create-content-post topic='AI trends' platform='linkedin'"
🤖 "⚡ Executing /create-content-post with real-time updates..."
🤖 "🔄 Starting Research Agent..."
🤖 "✅ Research completed - found 5 key AI trends"
🤖 "🔄 Starting Copywriter Agent..."
🤖 "✅ Content created - 847 characters, LinkedIn optimized"
🤖 "🔄 Starting Image Generation..."
🤖 "🎉 Task completed successfully! Results saved to Notion"
```

#### **Scheduled Tasks (Background)**:
```
👤 "Create a marketing post about our new feature for tomorrow"
🤖 "📋 Task scheduled for background processing: #12345"
[... hours later ...]
🤖 "✅ Your marketing post is ready! Check Notion for details"
```

### **Instant Command Execution**:
```
👤 "/create-content-post topic='AI trends 2025' platform='linkedin'"

🤖 "Запускаю создание поста про AI тренды для LinkedIn..."

🤖 "🔍 Research Agent ищет актуальные данные..."

🤖 "✅ Найдено 5 ключевых трендов. Передаю Copywriter Agent..."

🤖 "✍️ Создаю профессиональный контент для LinkedIn..."

🤖 "✅ Контент готов! 847 символов, оптимизирован под платформу"

🤖 "🎨 Создаю описание для изображения..."

🤖 "🖼️ Генерирую изображение через Flux модель..."

🤖 "✅ Готово! Пост создан за 8 минут. Результат сохранен в Notion"
```

### **Natural Language Processing**:
```
👤 "Создай технический пост про машинное обучение для LinkedIn"

🤖 "Понял! Создаю технический контент про ML для LinkedIn..."
[Автоматическое определение workflow и выполнение]
```

### **Direct Agent Control**:
```
👤 "Скажи Research Agent искать только академические источники за последние 3 месяца"

🤖 "Research Agent: Фокусируюсь на академических источниках за последние 3 месяца..."
[Прямой вызов с кастомными параметрами]
```

## DOCUMENTATION & API REFERENCES:

### **Primary Framework**:
- **Agency Swarm GitHub**: https://github.com/VRSEN/agency-swarm (main framework and examples)
- **Agency Swarm Official Docs**: https://agency-swarm.ai/ (comprehensive documentation)
- **Agency Swarm API Reference**: https://agency-swarm.ai/core-framework/ (detailed API docs)

### **Production Platform**:
- **Agencii Platform**: https://agencii.ai/ (managed deployment with clear pricing)
- **Agencii GitHub App**: Automated deployment integration for CI/CD
- **AI Developer Plan**: $79/month unlimited agents and integrations

### **MVP APIs & Tools**:
- **Notion API**: https://developers.notion.com/ (database integration)
- **OpenAI API**: https://platform.openai.com/docs (GPT-4 for all agents)
- **SerpAPI**: https://serpapi.com/search-api (web search for research)
- **FastAPI**: https://fastapi.tiangolo.com/ (backend framework)
- **Pydantic**: https://docs.pydantic.dev/ (data validation)
- **Slowapi**: https://github.com/laurentS/slowapi (rate limiting)
- **Pytest**: https://docs.pytest.org/ (testing framework)

### **Future Phase APIs** (not needed for MVP):
- **Replicate API**: https://replicate.com/docs (image generation - Phase 2)
- **Anthropic API**: https://docs.anthropic.com/ (multi-model support - Phase 3)
- **Brave Search API**: https://brave.com/search/api/ (alternative search - Phase 3)

### **Development Templates**:
- **Agency GitHub Template**: https://github.com/agency-ai-solutions/agency-github-template
- **MCP Tools Template**: https://github.com/agency-ai-solutions/agencii-mcp-tools-deployment-template (for advanced scaling)

### **Platform SDKs**:
- **notion-client**: Python SDK for Notion API integration
- **replicate**: Python SDK for image generation
- **openai**: Official OpenAI Python SDK
- **anthropic**: Official Anthropic Python SDK
- **requests**: HTTP client for custom API integrations

### **Core Templates & Resources**:
- **Agency GitHub Template**: https://github.com/agency-ai-solutions/agency-github-template
- **Agency Swarm Framework**: https://github.com/VRSEN/agency-swarm
- **MCP Tools Template**: https://github.com/agency-ai-solutions/agencii-mcp-tools-deployment-template (for future scaling)

### **Development Environment Setup**:
- **Windsurf IDE Integration**: AI-assisted development with intelligent code completion and agent generation
- **Agency Swarm CLI Tools**: `agency-swarm genesis`, `agency-swarm create-agent-template`
- **Docker Configuration**: Consistent deployment environments
- **GitHub App Integration**: Automated CI/CD deployment to Agencii

### **API Integration Patterns**:
- **Direct SDK Integration**: `notion-client`, `replicate`, `openai`, `anthropic` Python SDKs
- **Type-Safe Tools**: Pydantic validation with automatic error correction
- **Modular Prompt Management**: Leveraging existing Rules/Examples database
- **State Persistence**: Agent communication patterns with OpenAI Assistants API

## TECHNICAL IMPLEMENTATION:

### **Agency Swarm Integration**:
```python
# agency.py - Main entry point following template structure
from agency_swarm import Agency
from SocialMediaAgency.Orchestrator.Orchestrator import Orchestrator

# Initialize with proper communication flows
agency = Agency([
    orchestrator,  # Main client-facing agent
    # Communication flows for agent interaction
], shared_instructions="./SocialMediaAgency/agency_manifesto.md")

# Agency Swarm CLI usage for development
# agency-swarm genesis --openai_key "YOUR_API_KEY"
# agency-swarm create-agent-template --name "Orchestrator"
```

### **Tool Development Pattern**:
```python
# Following Agency Swarm BaseTool pattern
from agency_swarm.tools import BaseTool
from pydantic import Field
import requests

class BackendAgentProxy(BaseTool):
    """
    Proxy tool for communicating with backend agents.
    Follows Agency Swarm tool development patterns.
    """
    agent_name: str = Field(..., description="Name of the backend agent to call")
    task_data: dict = Field(..., description="Data to send to the backend agent")
    
    def run(self):
        """
        Implementation following Agency Swarm tool patterns.
        Includes automatic type validation and error correction.
        """
        response = requests.post(f"{BACKEND_URL}/agents/{self.agent_name}", 
                               json=self.task_data)
        return response.json()
```
```yaml
# MVP Configuration - Single LLM Provider
agent_models:
  research: "gpt-4"          # Single model for MVP
  copywriter: "gpt-4"        # Same model for consistency
  orchestrator: "gpt-4"      # Unified experience

error_handling:
  retry_attempts: 3
  retry_delay: [1, 2, 4]     # Exponential backoff
  timeout: 30                # 30 seconds per agent call

rate_limiting:
  requests_per_minute: 20    # Conservative limit
  burst_size: 5             # Allow small bursts
```

### **Dual TaskMonitor Architecture**:
```python
class TaskMonitor:
    async def instant_execution(self, command_data):
        """Real-time command processing with live updates"""
        workflow = self.parse_command_file(command_data["command"])
        await self.execute_with_notifications(workflow, command_data)
    
    async def scheduled_processing(self):
        """Background Notion scanning every 5 minutes"""
        while True:
            tasks = self.scan_notion_for_waiting_tasks()
            for task in tasks:
                await self.execute_background_workflow(task)
            await asyncio.sleep(300)
```

### **Command Definition Structure**:
```markdown
# /create-content-post
## Description
Creates complete social media content with research and visuals

## Parameters
- topic: Content topic (required)
- platform: Target platform (required) - linkedin|instagram|twitter|facebook
- tone: Content tone (optional) - professional|casual|playful

## Workflow
1. Research Agent → Topic analysis and data gathering (2-3 min)
2. Copywriter Agent → Platform-optimized content creation (1-2 min)  
3. Image Prompt Agent → Visual description generation (30 sec)
4. Image Generation Agent → Image creation via Flux model (1-2 min)

## Expected Output
- Platform-optimized text content
- Generated image with proper dimensions
- Relevant hashtags and engagement elements
- All results saved to Notion for client access
```

## MVP PROJECT STRUCTURE:

```
social-media-mvp/
├── 📱 frontend-agencii/              # Agencii Platform Deployment
│   ├── agency.py                     # Main entry point
│   ├── requirements.txt              # Minimal dependencies
│   ├── .env.example                  # Environment template
│   └── SocialMediaAgency/
│       ├── agency_manifesto.md       # MVP agent instructions
│       └── Orchestrator/
│           ├── Orchestrator.py       # Client-facing agent
│           ├── instructions.md       # Simplified behavior
│           └── tools/
│               ├── CommandProcessor.py        # Single command processor
│               ├── NotionTaskManager.py       # Basic task management
│               ├── ResearchAgentProxy.py      # Research proxy
│               └── CopywriterAgentProxy.py    # Content proxy
│
├── 🔧 backend-system/                # Minimal Backend
│   ├── main.py                       # FastAPI with rate limiting
│   ├── requirements.txt              # Core dependencies only
│   ├── .env.example                  # Environment template
│   ├── tests/                        # Unit tests from start
│   │   ├── test_agents.py
│   │   └── test_api.py
│   │
│   ├── agents/                       # Two MVP agents
│   │   ├── task_monitor.py           # Instant mode only
│   │   ├── research_agent.py         # Web search + GPT-4
│   │   └── copywriter_agent.py       # Content generation
│   │
│   ├── api/                          # Basic endpoints
│   │   ├── command_endpoint.py       # Single command handler
│   │   └── health_endpoint.py        # Health check
│   │
│   └── shared/                       # Essential utilities
│       ├── openai_client.py          # Single LLM provider
│       ├── notion_client.py          # Database operations
│       ├── rate_limiter.py           # Request throttling
│       └── error_handler.py          # Basic retry logic
│
└── 📚 commands/                      # Single workflow
    └── create-content-post.md        # MVP command definition
```

## NOTION DATABASE STRUCTURE:

### **Existing Databases (Enhanced)**:
- **Categories and Topics**: Topic catalog with trend analysis integration
- **Content Plan - AI Workflow**: Enhanced with dual-mode execution tracking
  - **NEW**: Execution Mode (Select): "Instant" | "Scheduled"
  - **NEW**: Command Used (Text): Reference to .md command file
  - Research Data, Content, Image Prompts, Image URLs (existing)
  - Agent Status: "Waiting" → "Processing" → "Complete" | "Error"
- **Rules / Examples**: Platform-specific guidelines with A/B testing results
- **Image Styles**: Visual configuration with performance analytics
- **Brand Archetypes + Brand**: Enhanced with sentiment analysis integration

## API INTEGRATION ARCHITECTURE:

### **FastAPI Endpoints**:
```python
# Instant execution for commands
@app.post("/execute-command")
async def execute_command_instant(command_data: CommandRequest):
    """Real-time command execution with live updates"""

# Manual agent calls
@app.post("/agents/{agent_name}/manual")
async def call_agent_manual(agent_name: str, request_data: dict):
    """Direct agent invocation for expert control"""

# Progress webhooks
@app.post("/notify-progress")
async def notify_client_progress(progress_data: ProgressUpdate):
    """Send real-time updates to Orchestrator"""

# Background task creation
@app.post("/schedule-task")
async def create_scheduled_task(task_data: TaskRequest):
    """Create background processing task"""
```

## MVP DEVELOPMENT WORKFLOW:

### **Week 1-2: Foundation**:
- Clone agency-github-template
- Configure MVP environment:
  ```
  # MVP Environment Variables
  NOTION_TOKEN=secret_xxx          # Database access
  OPENAI_API_KEY=sk-xxx           # Single LLM provider
  SERP_API_KEY=xxx                # Web search
  ```
- Initialize Agency Swarm structure
- Set up basic unit tests
- Implement rate limiting from start

### **Week 3-4: Core Development**:
- **Orchestrator Agent** (Agencii):
  - Single command processor
  - Notion integration
  - Basic error handling
- **Backend Agents**:
  - Research Agent (search + GPT-4)
  - Copywriter Agent (content generation)
- **FastAPI with rate limiting**
- **Basic monitoring (logs)**

### **Week 5: Integration & Testing**:
- Deploy to Agencii platform
- Deploy backend (single server)
- End-to-end testing
- Basic security setup

### **Week 6: MVP Launch**:
- Soft launch with 1-2 test clients
- Monitor performance and costs
- Gather feedback
- Document learnings

### **Post-MVP Phases**:
- **Phase 2** (Month 2): Add scheduled mode, image generation
- **Phase 3** (Month 3): Multi-model support, advanced commands
- **Phase 4** (Month 4+): Full feature set from original plan

## MVP ERROR HANDLING:

### **Simple Robust Approach**:
```python
# MVP Error Handler with logging
class MVPErrorHandler:
    def __init__(self):
        self.max_retries = 3
        self.base_delay = 1
    
    async def execute_with_retry(self, func, context):
        """Simple retry with exponential backoff"""
        for attempt in range(self.max_retries):
            try:
                return await func()
            except Exception as e:
                delay = self.base_delay * (2 ** attempt)
                logger.error(f"Attempt {attempt + 1} failed: {e}")
                
                if attempt == self.max_retries - 1:
                    # Log to Notion and notify user
                    await self.log_error_to_notion(context, e)
                    raise
                
                await asyncio.sleep(delay)

# Rate Limiting (from start)
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/execute-command")
@limiter.limit("10/minute")  # Conservative limit
async def execute_command(request: Request, command: CommandRequest):
    # Implementation
```

## BRAND ARCHETYPE IMPLEMENTATION:

### **Content Variation Strategy**:
- **Caregiver Archetype**: 35% - Nurturing, helpful, supportive content
- **Explorer Archetype**: 35% - Innovative, adventurous, discovery-focused content  
- **Regular Guy/Gal**: 30% - Relatable, down-to-earth, authentic content

### **Platform-Specific Rules** (from Rules/Examples database):
- **Instagram**: max 2200 chars, hashtag-focused, ratios 1:1, 4:5, 9:16
- **LinkedIn**: professional tone, corporate focus, detailed content allowed
- **Facebook**: max 63206 chars, community engagement focus
- **X/Twitter**: max 280 chars, brevity and impact priority
- **Threads**: max 500 chars, conversational authentic tone
- **Telegram**: max 4096 chars, rich formatting support

## AGENCII PLATFORM INTEGRATION:

### **Deployment Configuration**:
- **AI Developer Plan**: $79/month for unlimited agents and integrations
- **GitHub App Integration**: Automated deployment on push to main branch
- **Secure API Key Management**: Through Agencii dashboard
- **Performance Monitoring**: Built-in agent performance tracking
- **Scaling Management**: Automatic resource allocation and management

### **CI/CD Pipeline**:
```yaml
# GitHub Actions workflow for Agencii deployment
name: Deploy to Agencii
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Agencii
        uses: agencii/deploy-action@v1
        with:
          api-key: ${{ secrets.AGENCII_API_KEY }}
          project-path: ./frontend-agencii
```

### **MVP Environment & Costs**:
- **Agencii Platform**: $79/month
- **Backend Infrastructure**: 
  - Single VPS: $20/month (2GB RAM, 1 vCPU)
  - No Redis/CDN in MVP
- **OpenAI API**: ~$30-50/month (estimated)
- **Total MVP Cost**: ~$130-150/month

### **MVP Performance Targets**:
- **Command Execution**: 3-5 minutes
- **Concurrent Tasks**: 2-3 maximum
- **Uptime Target**: 95% (MVP acceptable)
- **Response Time**: <3 seconds

### **Monitoring (Basic)**:
```python
# Simple metrics collection
import time
import logging

class MetricsCollector:
    def __init__(self):
        self.metrics = []
    
    async def track_execution(self, command, func):
        start = time.time()
        try:
            result = await func()
            duration = time.time() - start
            self.log_metric(command, "success", duration)
            return result
        except Exception as e:
            duration = time.time() - start
            self.log_metric(command, "failure", duration)
            raise
    
    def log_metric(self, command, status, duration):
        metric = {
            "command": command,
            "status": status,
            "duration": duration,
            "timestamp": time.time()
        }
        self.metrics.append(metric)
        logger.info(f"Metric: {metric}")
```

## MVP MONITORING:

### **Essential Metrics Only**:
- Command success/failure rate
- Average execution time
- Daily API costs
- Error logs with context

### **Simple Implementation**:
```python
# Log to file, analyze daily
{"timestamp": "2024-01-20T10:30:00", 
 "command": "create-content-post",
 "duration": 245,
 "status": "success",
 "api_cost": 0.12}
```

## ROADMAP FROM MVP:

### **MVP** (Month 1):
- Single command working end-to-end
- 2 agents (Research + Copywriter)
- Basic monitoring
- 1-2 test clients

### **Phase 2** (Month 2-3):
- Add scheduled mode
- Add image generation
- 3-5 commands
- 5-10 clients

### **Phase 3** (Month 4-6):
- Multi-model support
- Advanced commands
- Better analytics
- 20+ clients

### **Phase 4** (Month 7+):
- Full original feature set
- Enterprise features
- Scale as validated

## MVP TESTING STRATEGY:

### **Unit Tests (Required)**:
```python
# tests/test_agents.py
import pytest
from agents.research_agent import ResearchAgent

class TestResearchAgent:
    async def test_search_success(self):
        agent = ResearchAgent()
        result = await agent.search("AI trends")
        assert result is not None
        assert len(result) > 0
    
    async def test_search_timeout(self):
        agent = ResearchAgent(timeout=0.1)
        with pytest.raises(TimeoutError):
            await agent.search("complex query")
```

### **Integration Tests**:
```python
# tests/test_workflow.py
async def test_create_content_workflow():
    # Test full command execution
    command = CreateContentCommand(
        topic="AI trends",
        platform="linkedin"
    )
    result = await execute_command(command)
    assert result.status == "success"
    assert len(result.content) > 100
```

## MVP SUCCESS CRITERIA:

1. **Technical**: 
   - Single command executes in <5 minutes
   - 90%+ success rate
   - Costs <$0.50 per execution

2. **Business**:
   - 2 satisfied test clients
   - Positive feedback on core functionality
   - Clear path to Phase 2

---

**This MVP approach focuses on validating the core concept with minimal complexity. Once proven, we can incrementally add features while maintaining stability and cost control.**