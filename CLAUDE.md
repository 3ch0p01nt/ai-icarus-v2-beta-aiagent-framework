# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**AI Icarus V2 Beta with Agent Framework** - A complete rewrite of AI Icarus using Microsoft Agent Framework for building AI-powered Log Analytics query applications. This project includes automated CI/CD that deploys to Azure Government (argon tenant), runs comprehensive tests, and auto-destroys resources.

**Key Difference from AI-Icarus-Universal:** This version properly integrates Microsoft Agent Framework from the ground up, eliminating technical debt and using modern patterns like custom tools with `@ai_function` decorators, context providers for memory, and AG-UI for chat interfaces.

## Current Project State

### ✅ Completed (2025-01-13)
- Project structure initialized
- CI/CD pipeline created (`.github/workflows/deploy-test-destroy.yml`)
- Bicep infrastructure templates (`infrastructure/main.bicep`)
- Integration tests (`tests/integration/test_api.py`)
- E2E Playwright tests (`tests/e2e/`)
- Backend Agent Framework sample (`backend/agents/kql_assistant_agent.py`)
- Requirements file (`backend/requirements.txt`)
- Comprehensive README.md
- Git repository initialized with initial commit

### 🚧 Next Steps (In Order)
1. **User must create GitHub repository manually** at https://github.com/3ch0p01nt/ai-icarus-v2-beta-aiagent-framework
   - GitHub CLI failed due to Enterprise Managed User restrictions
   - Repository must be public
   - Do NOT initialize with README (already exists locally)

2. **Configure GitHub Secrets** (CRITICAL - pipeline won't work without these):
   - `AZURE_CREDENTIALS` (JSON with clientId, clientSecret, subscriptionId, tenantId)
   - `AZURE_AD_CLIENT_ID`, `AZURE_AD_CLIENT_SECRET`, `AZURE_AD_TENANT_ID`
   - `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_DEPLOYMENT`
   - `TEST_USER_TOKEN`, `TEST_USERNAME`, `TEST_PASSWORD`
   - `SWA_DEPLOYMENT_TOKEN` (will be generated after first Static Web App deploy)

3. **Push to GitHub:**
   ```bash
   cd /mnt/c/VSCode_Projects/VSCode_Projects/GITHUB/ai-icarus-v2-beta-aiagent-framework
   git remote add origin https://github.com/3ch0p01nt/ai-icarus-v2-beta-aiagent-framework.git
   git push -u origin main
   ```

4. **Monitor CI/CD pipeline** in GitHub Actions tab
   - Pipeline runs on every push to main
   - Takes ~20-30 minutes total
   - Auto-destroys resources on success
   - Leaves resources for debugging on failure

### 📋 Still To Do (Future Development)
- Complete backend FastAPI implementation (`backend/api/main.py`)
- Implement full Agent Framework integration (tools, context providers)
- Create frontend React application (`frontend/src/`)
- Add real Azure Resource Graph integration
- Add real Log Analytics query execution
- Implement On-Behalf-Of token flow
- Add multi-cloud configuration logic
- Create frontend MSAL authentication
- Add AG-UI client for chat interface

## Key Commands

### Local Development

**Backend:**
```bash
cd backend
python3.11 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Set environment variables
export AZURE_CLIENT_ID="..."
export AZURE_CLIENT_SECRET="..."
export AZURE_TENANT_ID="..."
export AZURE_CLOUD_ENVIRONMENT="AzureUSGovernment"
export AZURE_OPENAI_ENDPOINT="https://...cognitiveservices.azure.us/"
export AZURE_OPENAI_DEPLOYMENT_NAME="gpt-4o"

# Run development server
uvicorn api.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install

# Set environment variables
export VITE_API_URL="http://localhost:8000"
export VITE_AZURE_CLIENT_ID="..."
export VITE_AZURE_CLOUD="AzureUSGovernment"

# Run development server
npm run dev  # Access at http://localhost:5173
```

### Testing

**Integration Tests:**
```bash
cd tests/integration
pytest -v
```

**E2E Tests:**
```bash
cd tests/e2e
npm install
npx playwright install --with-deps chromium
npx playwright test
```

### Deployment

**Manual Deployment:**
```bash
az cloud set --name AzureUSGovernment
az login
az group create --name test-rg --location usgovvirginia
az deployment group create \
  --resource-group test-rg \
  --template-file infrastructure/main.bicep \
  --parameters environment=dev cloudEnvironment=AzureUSGovernment
```

**Cleanup Failed CI/CD Resources:**
```bash
az cloud set --name AzureUSGovernment
az login
az group list --query "[?starts_with(name, 'ci-icarus-test')].name" -o table
az group delete --name ci-icarus-test-YYYYMMDDHHMMSS --yes
```

## Architecture & Key Components

### CI/CD Pipeline Architecture
```
Push to main → Deploy (Bicep) → Health Check → Integration Tests → E2E Tests → Destroy → Notify
```

**On Success:** All resources destroyed, confirmation tests passed
**On Failure:** Resources left running with URLs for debugging

### Backend Architecture (Agent Framework)
```
FastAPI
├── /api/agent (AG-UI endpoint for streaming chat)
├── /api/workspaces/discover (workspace discovery)
├── /api/query/execute (KQL execution)
├── /api/config (runtime configuration)
└── /health (health check)

Agent Framework Components:
├── KQLAssistantAgent (ChatAgent with custom tools)
├── Custom Tools (@ai_function):
│   ├── discover_workspaces() - Azure Resource Graph
│   ├── execute_kql_query() - Log Analytics
│   ├── get_table_schema() - Schema discovery
│   └── validate_kql_syntax() - Query validation
└── Context Providers:
    └── UserPreferencesMemory - Session state
```

### Infrastructure Components (Bicep)
- App Service Plan (Linux, Python 3.11)
- App Service (Backend - FastAPI)
- Static Web App (Frontend - React)
- Application Insights (Monitoring)

## Critical Implementation Details

### Authentication Flow
**User → MSAL (Frontend) → Bearer Token → Backend (FastAPI) → On-Behalf-Of → Azure Resources**

The backend NEVER uses its own service principal to access user data. Always uses On-Behalf-Of flow to exchange user token for resource-specific tokens.

### Multi-Cloud Token Scopes
**Commercial:**
- Management: `https://management.azure.com/.default`
- Log Analytics: `https://api.loganalytics.io/.default`
- Cognitive Services: `https://cognitiveservices.azure.com/.default`

**Government:**
- Management: `https://management.usgovcloudapi.net/.default`
- Log Analytics: `https://api.loganalytics.us/.default`
- Cognitive Services: `https://cognitiveservices.azure.us/.default`

### Agent Framework Integration Patterns

**Creating Custom Tools:**
```python
from typing import Annotated
from pydantic import Field
from agent_framework import ai_function

@ai_function(description="Tool description for LLM")
async def my_tool(
    param: Annotated[str, Field(description="Parameter description")]
) -> str:
    """Detailed docstring for additional context"""
    # Implementation using user's delegated token
    return json.dumps(result)
```

**Creating Agent:**
```python
from agent_framework import ChatAgent
from agent_framework.azure import AzureOpenAIChatClient

agent = ChatAgent(
    chat_client=AzureOpenAIChatClient(...),
    name="KQLAssistant",
    instructions="You are a KQL expert...",
    tools=[discover_workspaces, execute_kql_query, ...],
    context_providers=[UserPreferencesMemory()]
)
```

**Streaming Responses:**
```python
async for chunk in agent.run_stream(message, thread=thread_id):
    yield chunk  # SSE to frontend
```

## File Locations Quick Reference

### CI/CD
- Pipeline: `.github/workflows/deploy-test-destroy.yml`
- Bicep: `infrastructure/main.bicep`

### Backend (Python)
- Agent: `backend/agents/kql_assistant_agent.py`
- API: `backend/api/main.py` (to be created)
- Auth: `backend/auth/` (to be created)
- Config: `backend/config/` (to be created)
- Requirements: `backend/requirements.txt`

### Frontend (React)
- Entry: `frontend/src/main.tsx` (to be created)
- Components: `frontend/src/components/` (to be created)
- MSAL Config: `frontend/src/config/msalConfig.ts` (to be created)

### Tests
- Integration: `tests/integration/test_api.py`
- E2E: `tests/e2e/tests/workflow.spec.ts`

### Documentation
- Main: `README.md`
- This file: `CLAUDE.md`

## Common Issues & Solutions

### Issue: GitHub Repository Creation Failed
**Error:** `GraphQL: Unauthorized: As an Enterprise Managed User`
**Solution:** Create repository manually via GitHub web UI

### Issue: CI/CD Pipeline Not Running
**Cause:** GitHub secrets not configured
**Solution:** Add all required secrets in repository Settings → Secrets

### Issue: Pipeline Fails at Health Check
**Cause:** Services need more startup time
**Solution:** Increase wait time in health-check job, or check App Service logs

### Issue: Integration Tests Fail
**Cause:** TEST_USER_TOKEN not configured or expired
**Solution:** Generate new token and update GitHub secret

### Issue: Resources Not Destroyed
**Cause:** Previous pipeline stages failed
**Solution:** Manually delete: `az group delete --name ci-icarus-test-YYYYMMDDHHMMSS`

## Environment Variables

### Backend Runtime (.env or App Service Settings)
```
AZURE_CLIENT_ID=...
AZURE_CLIENT_SECRET=...
AZURE_TENANT_ID=...
AZURE_CLOUD_ENVIRONMENT=AzureUSGovernment
AZURE_OPENAI_ENDPOINT=https://...cognitiveservices.azure.us/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
LOG_LEVEL=INFO
ENABLE_CORS=true
```

### Frontend Build Time (.env)
```
VITE_API_URL=https://backend-url
VITE_AZURE_CLIENT_ID=...
VITE_AZURE_CLOUD=AzureUSGovernment
```

## Testing Strategy

### Integration Tests (Python + pytest)
- Test API endpoints without UI
- Test authentication requirements
- Test workspace discovery
- Test query execution
- Test agent endpoint

### E2E Tests (Playwright + TypeScript)
- Test complete user workflows
- Test UI components
- Test accessibility
- Test responsive design
- Test error handling

## Important Design Principles

1. **User Delegation Only** - Never use app-level service principal for user data access
2. **Multi-Cloud from Day One** - Support Commercial and Government clouds
3. **Agent Framework First** - Use proper AF patterns, not workarounds
4. **Zero Trust** - All operations use user's delegated permissions
5. **Automated Testing** - Deploy-test-destroy on every commit
6. **Infrastructure as Code** - Everything in Bicep templates
7. **Comprehensive Logging** - Structured logs, Application Insights integration

## Version Control & Branching

**Main Branch:** Protected, requires CI/CD to pass
**Feature Branches:** `feature/description`
**Bugfix Branches:** `bugfix/description`

**Workflow:**
1. Create feature branch
2. Make changes and test locally
3. Push to GitHub (triggers CI/CD)
4. Create Pull Request
5. Merge after CI/CD passes

## Monitoring & Observability

- **Application Insights:** Automatic instrumentation
- **OpenTelemetry:** Built-in Agent Framework tracing
- **Health Endpoints:** `/health`, `/api/config`
- **Structured Logs:** JSON format for queries
- **Metrics:** CPU, memory, request count, error rate

## Security Considerations

- HTTPS only (enforced in production)
- JWT token validation
- CORS configured per environment
- Security headers (CSP, HSTS, etc.)
- No secrets in code (all in Key Vault or GitHub Secrets)
- Audit logging of all user actions
- Regular dependency updates

## Related Projects

- **AI-Icarus-Universal** (`/mnt/c/VSCode_Projects/VSCode_Projects/GITHUB/AI-Icarus-Universal/`)
  - Original implementation with technical debt
  - Node.js backend, React frontend
  - Reference for features to rebuild

- **Agent Framework** (`/mnt/c/VSCode_Projects/VSCode_Projects/AI_Framework_Lab/agent-framework/`)
  - Microsoft Agent Framework repository
  - Reference for patterns and examples

## Contact & Support

- Repository: https://github.com/3ch0p01nt/ai-icarus-v2-beta-aiagent-framework
- Documentation: README.md in root
- Issues: GitHub Issues tab
- Wiki: (to be created)

## Session Notes

**Last Updated:** 2025-01-13

**Current Status:** Repository created locally, ready to push to GitHub

**Blocking Issues:**
- GitHub repository must be created manually (Enterprise Managed User limitation)
- GitHub secrets must be configured before CI/CD will work

**Next Session Should:**
1. Confirm GitHub repository created
2. Verify GitHub secrets configured
3. Push code and monitor first CI/CD run
4. Begin implementing full backend FastAPI application
5. Begin implementing frontend React application
