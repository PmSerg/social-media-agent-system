### 🔄 Project Awareness & Context
- **Always read `PLANNING.md`** at the start of a new conversation to understand the project's architecture, goals, style, and constraints.
- **Check `TASK.md`** before starting a new task. If the task isn’t listed, add it with a brief description and today's date.
- **Use consistent naming conventions, file structure, and architecture patterns** as described in `PLANNING.md`.
- **Use venv_linux** (the virtual environment) whenever executing Python commands, including for unit tests.

### 🧱 Code Structure & Modularity
- **Never create a file longer than 500 lines of code.** If a file approaches this limit, refactor by splitting it into modules or helper files.
- **Organize code into clearly separated modules**, grouped by feature or responsibility.
  For agents this looks like:
    - `agent.py` - Main agent definition and execution logic 
    - `tools.py` - Tool functions used by the agent 
    - `prompts.py` - System prompts
- **Use clear, consistent imports** (prefer relative imports within packages).
- **Use clear, consistent imports** (prefer relative imports within packages).
- **Use python_dotenv and load_env()** for environment variables.

### 🧪 Testing & Reliability
- **Always create Pytest unit tests for new features** (functions, classes, routes, etc).
- **After updating any logic**, check whether existing unit tests need to be updated. If so, do it.
- **Tests should live in a `/tests` folder** mirroring the main app structure.
  - Include at least:
    - 1 test for expected use
    - 1 edge case
    - 1 failure case

### ✅ Task Completion
- **Mark completed tasks in `TASK.md`** immediately after finishing them.
- Add new sub-tasks or TODOs discovered during development to `TASK.md` under a “Discovered During Work” section.

### 📎 Style & Conventions
- **Use Python** as the primary language.
- **Follow PEP8**, use type hints, and format with `black`.
- **Use `pydantic` for data validation**.
- Use `FastAPI` for APIs and `SQLAlchemy` or `SQLModel` for ORM if applicable.
- Write **docstrings for every function** using the Google style:
  ```python
  def example():
      """
      Brief summary.

      Args:
          param1 (type): Description.

      Returns:
          type: Description.
      """
  ```

### 📚 Documentation & Explainability
- **Update `README.md`** when new features are added, dependencies change, or setup steps are modified.
- **Comment non-obvious code** and ensure everything is understandable to a mid-level developer.
- When writing complex logic, **add an inline `# Reason:` comment** explaining the why, not just the what.

### 🧠 AI Behavior Rules
- **Never assume missing context. Ask questions if uncertain.**
- **Never hallucinate libraries or functions** – only use known, verified Python packages.
- **Always confirm file paths and module names** exist before referencing them in code or tests.
- **Never delete or overwrite existing code** unless explicitly instructed to or if part of a task from `TASK.md`.

### 📚 Context7 Integration
- **Always check Context7 first** when working with external libraries or frameworks (not just Python packages)
- **Use pattern**: `resolve-library-id` → `get-library-docs` → implement
- **Priority libraries** to check via Context7:
  - Python: Django, Flask, FastAPI, SQLAlchemy, Pydantic
  - JavaScript/TypeScript: Next.js, React, Vue, Express, NestJS
  - Database: Prisma, Drizzle, MongoDB, PostgreSQL clients
  - Testing: Pytest, Jest, Vitest, Playwright
  - Any npm/pip package with significant usage
- **When to use Context7**:
  - Before implementing any library-specific code
  - When encountering API errors or deprecation warnings
  - When user asks about library features or best practices
  - During refactoring to use latest patterns
- **Selection criteria**:
  - Trust Score ≥ 7 preferred
  - Higher Code Snippets count = better documentation
  - Check version compatibility if user specifies version

### 🚀 Advanced Workflow Patterns
- **Use EPCT command** (`/epct`) for structured development of new features
- **Spawn sub-agents** for complex research tasks requiring parallel processing
- **Context management**: Use `/clear` when switching between unrelated features
- **Interactive modes**:
  - Auto-accept (Shift+Tab): For trusted, well-defined tasks
  - Plan mode (Shift+Tab twice): For architecture decisions
  - Interactive (default): For sensitive operations
- **Visual debugging**: Accept screenshots for UI/UX improvements
- **Selective editing**: In editor mode, select specific lines for targeted changes

### 🛠️ GitHub Integration
- **Pull Requests**: Use `gh pr create` with detailed descriptions
- **Issues**: Link PRs to issues using `gh issue` commands
- **Code Reviews**: Include AI-generated code context in PR descriptions
- **Workflow**: Check CI/CD status with `gh workflow view`

### 👥 Team Collaboration
- **Shared CLAUDE.md**: Version control project-specific instructions
- **Custom commands**: Document team-specific commands in README
- **Branch strategy**:
  - `main`: Production-ready code only
  - `feature/*`: Individual development with dedicated Claude sessions
  - `hotfix/*`: Emergency fixes with focused context
- **Code review process**: Always mention when code is AI-assisted

### 🔒 Security Best Practices
- **Never commit secrets**: Always use environment variables
- **Input validation**: Validate all user inputs and API parameters
- **Authentication**: Implement proper auth checks before sensitive operations
- **Dependencies**: Review security implications of new packages
- **OWASP compliance**: Follow OWASP guidelines for web applications

### 📊 Performance Monitoring
- **Use `/optimize` command** for performance analysis
- **Track metrics**: Response times, memory usage, bundle sizes
- **Database queries**: Optimize N+1 queries and add appropriate indexes
- **Caching strategy**: Implement caching where appropriate
- **Load testing**: Consider performance impact of new features

### 💻 System Information
- **Operating System**: macOS (Darwin)
- **Claude Desktop Configuration**:
  - MCP server config: `/Users/sk/.claude/mcp-config.json`
  - Claude settings: `/Users/sk/.claude/settings.json`
  - CLAUDE.md locations: `/Users/sk/.claude/CLAUDE.md` (global), project root (local)
- **Platform-specific considerations**:
  - Use Homebrew for package management (`brew install`)
  - Virtual environments: `python3 -m venv venv` and `source venv/bin/activate`
  - File paths are case-insensitive by default
  - Use `open` command to open files/URLs from terminal
  - Redis installation: `brew install redis` and `brew services start redis`
  - PostgreSQL: `brew install postgresql` and `brew services start postgresql`
  - Node.js via nvm: `brew install nvm`
- **Development tools**:
  - Xcode Command Line Tools required for many packages
  - Use `caffeinate` to prevent sleep during long operations
  - `pbcopy` and `pbpaste` for clipboard operations