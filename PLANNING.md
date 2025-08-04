# Project Planning - Social Media Agent System

## 🎯 Project Overview

**Project Name**: Kea-Pro-Agentic-System (Social Media Agent System)  
**Purpose**: Automated social media content creation using AI agents  
**Target Users**: Marketing teams, content creators, social media managers  
**Core Technology**: Agency Swarm, OpenAI GPT-4, FastAPI, Notion API

## 🏗️ Architecture Design

### Hybrid Architecture Overview

The Kea-Pro-Agentic-System uses a **hybrid architecture** combining:
- **Agency Swarm Framework** on Agencii platform (no-code agent orchestration)
- **FastAPI Backend** (self-hosted agent processing)
- **MCP Server** (bridge between Agencii and backend)

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Agencii Platform                          │
│                 (No-Code Environment)                        │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Orchestrator Agent                      │   │
│  │            (Agency Swarm Framework)                  │   │
│  │  - Natural language understanding                    │   │
│  │  - Command parsing via tools                        │   │
│  │  - Task delegation through API calls                │   │
│  │  - User interaction management                      │   │
│  └─────────────────────┬───────────────────────────────┘   │
└────────────────────────┼───────────────────────────────────┘
                         │ API Calls
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    MCP Server (Bridge)                       │
│                      (mcp-server/)                           │
│  - Exposes backend tools to Agencii                         │
│  - Handles authentication                                    │
│  - Server-Sent Events (SSE) for real-time updates          │
│  - Deployed on Railway                                      │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                  Backend API System                          │
│                   (backend-system/)                          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                  FastAPI Server                      │   │
│  │  - RESTful API endpoints                            │   │
│  │  - Request validation                               │   │
│  │  - Rate limiting with Redis                         │   │
│  │  - Error handling                                   │   │
│  └────────────────────┬────────────────────────────────┘   │
│                       │                                      │
│  ┌────────────────────┴────────────────────┐               │
│  ▼                                         ▼               │
│  ┌─────────────────────┐      ┌─────────────────────┐     │
│  │   Research Agent    │      │  Copywriter Agent   │     │
│  │  - Web search       │      │ - Content creation  │     │
│  │  - Trend analysis   │      │ - Brand voice       │     │
│  │  - Data extraction  │      │ - Platform optimize │     │
│  │  - Archetype aware  │      │ - Archetype based   │     │
│  └─────────────────────┘      └─────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    External Services                         │
│  - Notion API (task storage & workflow management)          │
│  - OpenAI API (GPT-4 for content generation)               │
│  - SerpAPI (web search capabilities)                        │
│  - Redis (distributed rate limiting)                        │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

#### 1. **Command Reception & Processing**
   - User interacts with Orchestrator agent on Agencii platform
   - Orchestrator uses `CommandProcessor` tool to parse natural language or slash commands
   - Validates parameters (topic, platform, tone, etc.)

#### 2. **Task Creation**
   - Orchestrator uses `NotionTaskManager` tool to create task in Notion
   - Task includes metadata: topic, platform, tone, execution mode
   - Notion task ID returned for tracking

#### 3. **Research Phase**
   - Orchestrator calls `ResearchAgentProxy` tool
   - MCP server forwards request to backend API
   - Backend Research Agent:
     - Searches web using SerpAPI
     - Analyzes trends and data
     - Considers brand archetypes (Caregiver 35%, Explorer 35%, Regular Guy 30%)
     - Updates Notion with research findings

#### 4. **Content Generation**
   - Orchestrator calls `CopywriterAgentProxy` tool
   - Backend Copywriter Agent:
     - Reads research data from Notion
     - Applies brand voice based on archetype
     - Optimizes for target platform
     - Generates content with proper tone
     - Updates Notion with final content

#### 5. **Real-time Updates**
   - Backend sends webhooks to Agencii platform
   - User receives progress updates through Orchestrator
   - Final content delivered with task completion status

### Key Architecture Principles

1. **Separation of Concerns**
   - Agencii: User interaction and orchestration
   - Backend: Business logic and agent processing
   - MCP: Communication bridge

2. **Tool-Based Communication**
   - Orchestrator doesn't directly call APIs
   - Uses Agency Swarm tools for all operations
   - Tools handle API communication details

3. **Stateless Processing**
   - Each request is independent
   - State stored in Notion database
   - Enables horizontal scaling

4. **Brand Archetype Integration**
   - Kea's brand personality embedded in agents
   - Content reflects archetype distribution
   - Consistent brand voice across platforms

## 📁 File Structure & Conventions

### Directory Structure
```
Kea-Pro-Agentic-System/
├── backend-system/          # FastAPI backend
│   ├── agents/             # Agent implementations
│   ├── api/                # API endpoints
│   ├── config/             # Configuration
│   ├── shared/             # Shared utilities
│   ├── commands/           # Command documentation
│   └── tests/              # Test suite
├── frontend-agencii/       # Agencii platform code
│   └── SocialMediaAgency/  # Agency implementation
│       └── Orchestrator/   # Main orchestrator
├── mcp-server/            # MCP server for tools
│   └── tools/             # Tool implementations
├── PRPs/                  # Project documentation
└── docker-compose.yml     # Docker orchestration
```

### Naming Conventions

- **Files**: `snake_case.py` for Python files
- **Classes**: `PascalCase` (e.g., `ResearchAgent`, `TaskMonitor`)
- **Functions**: `snake_case` (e.g., `execute_research`, `create_task`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_RETRIES`, `API_TIMEOUT`)
- **Modules**: Descriptive names reflecting functionality

### Code Organization

1. **Agent Pattern**:
   ```python
   # agent.py - Main agent class and logic
   # tools.py - Tool functions for the agent
   # prompts.py - System and user prompts
   ```

2. **API Pattern**:
   ```python
   # models.py - Pydantic models
   # endpoints.py - FastAPI routes
   # dependencies.py - Dependency injection
   ```

3. **Shared Utilities**:
   ```python
   # client modules - External service clients
   # error_handler.py - Global error handling
   # rate_limiter.py - Rate limiting logic
   ```

## 🛠️ Technology Stack

### Frontend (Agencii Platform)
- **Platform**: Agencii (no-code agent deployment)
- **Framework**: Agency Swarm (agent orchestration)
- **Agent Model**: GPT-4 Turbo
- **Tools**: Python-based custom tools
- **Communication**: HTTP API calls to backend

### Backend System
- **Framework**: FastAPI (async Python web framework)
- **Language**: Python 3.9+
- **Agent Classes**: Custom Python implementations
- **Database**: Notion (via API)
- **Cache**: Redis (rate limiting)
- **Testing**: Pytest + pytest-asyncio

### MCP Server (Bridge)
- **Protocol**: Model Context Protocol (MCP)
- **Communication**: Server-Sent Events (SSE)
- **Authentication**: Bearer token
- **Deployment**: Railway

### External Services
- **LLM**: OpenAI GPT-4
- **Search**: SerpAPI
- **Task Storage**: Notion API
- **Rate Limiting**: Redis

### Infrastructure
- **Backend Deployment**: Railway (PaaS)
- **MCP Deployment**: Railway
- **Frontend Deployment**: Agencii Platform
- **Containerization**: Docker
- **Environment Management**: python-dotenv

## 📊 Notion Database Structure

### Overview
The system uses 4 interconnected Notion databases to manage content creation workflow:

### 1. **Categories and Topics** (`24476a959af7814fb3cbeea2c593ab30`)
Stores content categories and topics for AI agents to work with.

**Properties:**
- **Topic Name** (title): Main identifier for the topic
- **Category** (select): Market news, Case studies, Events, Office life/Team, Products
- **Subcategory** (select): Market Analysis, Team Building, Crypto Exchange, SWIFT, SEPA, DEDICATED IBANS
- **Benefits & Key Points** (rich_text): Key benefits and important points about the topic
- **Description** (relation → Content Plan): Links to related content tasks
- **Industry** (select): *Ready for CMO to add* - Finance, Technology, E-commerce, etc.
- **Target Archetype** (select): *Ready for CMO to add* - Caregiver, Explorer, Regular Guy
- **Archetype Mix** (number): *Ready for CMO to add* - Percentage mix for this topic

### 2. **Content Plan - AI Workflow** (`24476a959af7810d9ff5c3f835e82ed7`)
Main database for tracking content creation tasks and workflow states.

**Properties:**
- **Task name** (title): Task title/name (in English)
- **Status** (select): Idea, In Progress, In Review, Published, Rejected
- **Agent Status** (select): Waiting, Research Agent, Copywriter Agent, Image Prompt Agent, Image Generation Agent, Complete
- **Execution Mode** (select): Instant, Scheduled
- **Category** (relation → Categories and Topics): Links to content category
- **Channel** (select): Facebook, Instagram, Twitter, LinkedIn
- **Command Used** (select): The command that triggered the task
- **Research Data** (rich_text): Research findings from Research Agent
- **Final Text** (rich_text): Generated content from Copywriter Agent
- **Image Prompts** (rich_text): Generated prompts for image creation
- **Image URLs** (url): Links to generated images
- **Error Log** (rich_text): Error messages if any
- **Publication Date** (date): Scheduled publication date
- **Month** (select): December, November, October, September, August
- **Week** (select): Week 1, Week 2, Week 3, Week 4
- **Position in Week** (select): Post 1, Post 2, Post 3
- **Applied Archetype** (select): Caregiver, Explorer, Regular Guy, Mixed - Automatically filled by system
- **Brand Voice Score** (number): *Future enhancement* - How well content matches brand voice (1-10)

### 3. **Rules / Examples** (`24476a959af781aabc96c0b3627fbd55`)
Contains brand guidelines, content rules, and examples for each platform.

**Properties:**
- **Name** (title): Rule/example identifier
- **Channel** (select): Threads, Telegram, Instagram, Facebook, LinkedIn
- **Tone of Voice** (select): Authentic, Aspirational, Informative, Conversational, Professional
- **Brand Guidelines** (rich_text): Brand-specific guidelines
- **Post Format** (rich_text): Format requirements for the platform
- **Content Examples** (rich_text): Example posts for reference
- **Hashtags** (rich_text): Recommended hashtags
- **CTA Examples** (rich_text): Call-to-action examples
- **Content** (rich_text): Additional content guidelines
- **Archetype Guidelines** (rich_text): *Ready for CMO to add* - How to apply each archetype
- **Brand Description** (rich_text): *Ready for CMO to add* - Kea's brand story and values
- **Example Posts** (rich_text): *Ready for CMO to add* - Real successful posts by archetype

### 4. **Image Styles** (`24476a959af781809184e7676e54acf9`)
Defines visual styles and prompts for image generation.

**Properties:**
- **Style Name** (title): Name of the image style
- **Base Prompt** (rich_text): Base prompt template for image generation
- **Image Size** (select): 1792x1024, 1024x1792, 1024x1024
- **Mood** (multi_select): Visual mood tags
- **Categories and Topics** (relation → Categories and Topics): Linked content categories

### Database Relationships
```
Categories and Topics ←→ Content Plan (via Category relation)
Categories and Topics ←→ Image Styles (via Categories and Topics relation)
Rules / Examples (standalone, referenced by Channel)
```

## 🔧 Development Guidelines

### Code Style
- Follow PEP 8
- Use type hints for all functions
- Write docstrings (Google style)
- Max line length: 88 (Black formatter)

### Testing Requirements
- Minimum 80% code coverage
- Test categories: unit, integration, e2e
- Mock external services
- Test both success and failure paths

### Git Workflow
- Branch naming: `feature/description`, `fix/description`
- Commit messages: Conventional commits format
- PR required for main branch
- Code review before merge

### Error Handling
- Use custom exceptions
- Log all errors with context
- Return meaningful error messages
- Implement retry logic for external services

## 🚀 Deployment Strategy

### Environments
1. **Development**: Local with Docker Compose
2. **Staging**: Railway preview environments
3. **Production**: Railway main deployment

### Configuration Management
- Environment variables for secrets
- `.env` files for local development
- Railway environment variables for production
- Pydantic Settings for validation

### Scaling Considerations
- Stateless backend design
- Redis for distributed rate limiting
- Async processing for long tasks
- Webhook-based communication

## 📊 Performance Targets

- **Response Time**: < 2s for command acknowledgment
- **Processing Time**: < 60s for complete workflow
- **Availability**: 99.9% uptime
- **Rate Limits**: 10 req/min per user
- **Concurrent Users**: Support 100+ simultaneous

## 🔒 Security Measures

- API key authentication
- Environment variable encryption
- Input validation on all endpoints
- Rate limiting per IP and user
- No sensitive data in logs
- HTTPS only in production

## 📈 Future Enhancements

### Phase 1 (Current - Completed)
- [x] Basic command execution
- [x] Research and content generation
- [x] Notion integration
- [x] MCP server implementation
- [x] Agency Swarm integration on Agencii
- [x] Brand archetype implementation
- [x] Archetype-based content generation
- [x] Helper functions for archetype management
- [x] Research Agent with archetype awareness
- [x] Copywriter Agent with brand voice application

### Phase 2 (Next)
- [ ] Scheduled post creation
- [ ] Bulk content generation
- [ ] Analytics dashboard
- [ ] Multi-language support
- [ ] Industry-specific content templates
- [ ] CEO bio and press release integration
- [ ] Product catalog integration

### Phase 3 (Future)
- [ ] Image generation integration
- [ ] Video content support
- [ ] A/B testing capabilities
- [ ] Advanced analytics
- [ ] Audience persona matching
- [ ] Content performance tracking by archetype

## 🤝 Team Conventions

### Communication
- Use PR descriptions for context
- Document breaking changes
- Update README for new features
- Comment complex logic

### Code Review Checklist
- [ ] Tests pass
- [ ] Type hints present
- [ ] Docstrings updated
- [ ] No hardcoded values
- [ ] Error handling implemented
- [ ] Performance considered

### Documentation
- Keep README current
- Update API documentation
- Document environment variables
- Maintain command examples