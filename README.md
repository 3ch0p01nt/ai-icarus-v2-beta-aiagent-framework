# AI Icarus V2 Beta - Agent Framework Edition

**Log Analytics Query Application with Microsoft Agent Framework**

Multi-cloud Azure application (Commercial + Government) with automated CI/CD pipeline that deploys, tests, and auto-destroys validation environments.

![CI/CD Status](https://img.shields.io/badge/CI%2FCD-Deploy%20→%20Test%20→%20Destroy-success)
![Azure](https://img.shields.io/badge/Azure-Government%20%26%20Commercial-0078D4)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![TypeScript](https://img.shields.io/badge/TypeScript-React-61DAFB)

---

## 🎯 Overview

AI Icarus V2 Beta leverages **Microsoft Agent Framework** to provide AI-powered assistance for Azure Log Analytics queries with zero-trust security architecture and user-delegated permissions.

### Key Features

✅ **AI-Powered Query Assistance** - Natural language to KQL with Azure OpenAI
✅ **Multi-Cloud Support** - Azure Commercial & Government (IL2/IL4/IL5)
✅ **Agent Framework Integration** - Custom tools for Azure Resource Graph & Log Analytics
✅ **Zero Trust Architecture** - User-delegated permissions, no stored secrets
✅ **Automated CI/CD** - Deploy → Test → Destroy pipeline on every commit
✅ **Section 508 Compliant** - Accessible UI with WCAG 2.1 Level AA

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│         React + TypeScript SPA              │
│         (MSAL Authentication)               │
└────────────────┬────────────────────────────┘
                 │ HTTPS Bearer Token
                 ▼
┌─────────────────────────────────────────────┐
│     FastAPI Backend (Python 3.11)           │
│     + Microsoft Agent Framework             │
│                                             │
│  ┌──────────────────────────────────────┐  │
│  │   KQL Assistant Agent                │  │
│  │   - Natural language to KQL          │  │
│  │   - Workspace discovery              │  │
│  │   - Query execution                  │  │
│  │   - Query optimization               │  │
│  └──────────────────────────────────────┘  │
│                                             │
│  Custom Tools (@ai_function):              │
│  • discover_workspaces()                   │
│  • execute_kql_query()                     │
│  • get_table_schema()                      │
│  • validate_kql_syntax()                   │
└────────────────┬────────────────────────────┘
                 │ User's Delegated Token
                 ▼
┌─────────────────────────────────────────────┐
│           Azure Services                    │
│  • Azure Resource Graph (discovery)         │
│  • Log Analytics (queries)                  │
│  • Azure OpenAI (AI assistance)             │
└─────────────────────────────────────────────┘
```

### Technology Stack

**Backend:**
- Python 3.11 + FastAPI
- Microsoft Agent Framework (agent-framework-core, agent-framework-azure-ai)
- Azure SDK for Python
- MSAL for authentication

**Frontend:**
- React 19 + TypeScript
- Vite build tool
- MSAL React for Azure AD
- Fluent UI components

**Infrastructure:**
- Azure App Service (backend)
- Azure Static Web Apps (frontend)
- Application Insights (monitoring)
- Bicep IaC templates

---

## 🚀 Quick Start

### Prerequisites

- **GitHub Account** with access to `3ch0p01nt` organization
- **Azure Government Subscription** (argon tenant)
- **Azure AD App Registration** configured
- **Service Principal** with Contributor role
- **Azure CLI** and **PowerShell 7+** installed

### Initial Setup

#### 1. Create GitHub Repository

Since GitHub CLI had authentication issues, create the repository manually:

1. Go to https://github.com/3ch0p01nt
2. Click "New Repository"
3. Name: `ai-icarus-v2-beta-aiagent-framework`
4. Description: "Log Analytics Query Application with Microsoft Agent Framework - Multi-cloud support"
5. Public repository
6. Click "Create repository"

#### 2. Configure GitHub Secrets

Go to repository Settings → Secrets and variables → Actions → New repository secret:

**Azure Government Authentication:**
```
AZURE_CREDENTIALS (JSON format):
{
  "clientId": "your-service-principal-client-id",
  "clientSecret": "your-service-principal-secret",
  "subscriptionId": "your-subscription-id",
  "tenantId": "your-tenant-id"
}
```

**Azure AD App Registration (for the application):**
```
AZURE_AD_CLIENT_ID        - App registration client ID
AZURE_AD_CLIENT_SECRET    - App registration client secret
AZURE_AD_TENANT_ID        - Tenant ID (argon.onmicrosoft.us)
```

**Azure OpenAI Configuration:**
```
AZURE_OPENAI_ENDPOINT     - e.g., https://your-openai.cognitiveservices.azure.us/
AZURE_OPENAI_DEPLOYMENT   - e.g., gpt-4o
```

**Test Credentials (for E2E tests):**
```
TEST_USER_TOKEN           - Bearer token for integration tests
TEST_USERNAME             - Test user email
TEST_PASSWORD             - Test user password
```

**Static Web App:**
```
SWA_DEPLOYMENT_TOKEN      - Static Web App deployment token (generated after first deploy)
```

#### 3. Clone and Push to GitHub

```bash
# Navigate to the local repository directory
cd /mnt/c/VSCode_Projects/VSCode_Projects/GITHUB/ai-icarus-v2-beta-aiagent-framework

# Initialize git if not already done
git init
git add .
git commit -m "Initial commit: AI Icarus V2 with Agent Framework"

# Add remote (replace with your actual repo URL)
git remote add origin https://github.com/3ch0p01nt/ai-icarus-v2-beta-aiagent-framework.git

# Push to main branch (this will trigger CI/CD)
git push -u origin main
```

---

## 🔄 CI/CD Pipeline

The automated pipeline runs on **every commit to main**:

### Pipeline Stages

1. **🚀 Deploy** (5-10 min)
   - Creates unique resource group: `ci-icarus-test-YYYYMMDDHHMMSS`
   - Deploys infrastructure via Bicep
   - Deploys backend (FastAPI + Agent Framework)
   - Deploys frontend (React SPA)

2. **🏥 Health Check** (2-3 min)
   - Backend health endpoint
   - Frontend accessibility
   - API configuration

3. **🧪 Integration Tests** (3-5 min)
   - API endpoint tests
   - Workspace discovery tests
   - Query execution tests
   - Agent endpoint tests

4. **🎭 E2E Tests** (5-7 min)
   - Playwright browser tests
   - User workflow simulation
   - UI component tests

5. **🗑️ Destroy** (2-3 min)
   - Deletes entire resource group
   - Verifies cleanup

6. **✅ Notify Success** or **❌ Notify Failure**

### Total Pipeline Time: ~20-30 minutes

### Viewing Pipeline Results

1. Go to **Actions** tab in GitHub repository
2. Click on the latest workflow run
3. View logs for each stage
4. Download test artifacts (integration results, Playwright reports)

### On Success

✅ All resources automatically destroyed
✅ Confirmation that application works end-to-end
✅ Ready for production deployment

### On Failure

❌ Resources **LEFT RUNNING** for debugging
❌ Review logs in GitHub Actions
❌ Access deployed URLs from workflow output
❌ Manual cleanup required:

```bash
az cloud set --name AzureUSGovernment
az login
az group delete --name ci-icarus-test-YYYYMMDDHHMMSS
```

---

## 💻 Local Development

### Backend Development

```bash
cd backend

# Create virtual environment
python3.11 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export AZURE_CLIENT_ID="your-app-id"
export AZURE_CLIENT_SECRET="your-secret"
export AZURE_TENANT_ID="your-tenant-id"
export AZURE_CLOUD_ENVIRONMENT="AzureUSGovernment"
export AZURE_OPENAI_ENDPOINT="https://your-openai.cognitiveservices.azure.us/"
export AZURE_OPENAI_DEPLOYMENT_NAME="gpt-4o"

# Run development server
uvicorn api.main:app --reload --port 8000
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Set environment variables
export VITE_API_URL="http://localhost:8000"
export VITE_AZURE_CLIENT_ID="your-app-id"
export VITE_AZURE_CLOUD="AzureUSGovernment"

# Run development server
npm run dev
```

Access at: http://localhost:5173

### Running Tests Locally

**Integration Tests:**
```bash
cd tests/integration
pytest -v
```

**E2E Tests:**
```bash
cd tests/e2e
npm install
npx playwright install --with-deps
npx playwright test
```

---

## 📦 Project Structure

```
ai-icarus-v2-beta-aiagent-framework/
├── .github/workflows/
│   └── deploy-test-destroy.yml    # Main CI/CD pipeline
├── backend/
│   ├── agents/
│   │   └── kql_assistant_agent.py # Agent Framework implementation
│   ├── api/
│   │   ├── main.py               # FastAPI application
│   │   └── routes/               # API endpoints
│   ├── auth/                      # Token handling
│   ├── config/                    # Multi-cloud configuration
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/           # React components
│   │   ├── services/             # API clients
│   │   └── config/               # MSAL configuration
│   ├── package.json
│   └── vite.config.ts
├── infrastructure/
│   ├── main.bicep                # Main Bicep template
│   └── parameters/               # Environment-specific parameters
├── tests/
│   ├── integration/              # Python integration tests
│   └── e2e/                      # Playwright E2E tests
├── scripts/                       # Helper scripts
└── README.md
```

---

## 🔧 Manual Deployment

To deploy manually (outside CI/CD):

```bash
# Authenticate to Azure Government
az cloud set --name AzureUSGovernment
az login

# Set variables
RESOURCE_GROUP="my-icarus-test"
LOCATION="usgovvirginia"

# Create resource group
az group create --name $RESOURCE_GROUP --location $LOCATION

# Deploy infrastructure
az deployment group create \
  --resource-group $RESOURCE_GROUP \
  --template-file infrastructure/main.bicep \
  --parameters environment=dev \
              cloudEnvironment=AzureUSGovernment \
              azureAdClientId=$AZURE_AD_CLIENT_ID \
              azureAdClientSecret=$AZURE_AD_CLIENT_SECRET \
              azureAdTenantId=$AZURE_AD_TENANT_ID

# Deploy backend (see CI/CD workflow for details)
# Deploy frontend (see CI/CD workflow for details)
```

---

## 🎓 Agent Framework Integration

This application demonstrates key Agent Framework patterns:

### Custom Tools with `@ai_function`

```python
@ai_function(description="Discover Log Analytics workspaces")
async def discover_workspaces(
    subscription_id: Annotated[str | None, Field(description="...")] = None
) -> str:
    # Uses user's delegated token
    # Returns JSON string for LLM
    pass
```

### Chat Agent Configuration

```python
agent = ChatAgent(
    chat_client=AzureOpenAIChatClient(...),
    instructions="You are a KQL expert...",
    tools=[discover_workspaces, execute_kql_query, ...],
    context_providers=[UserPreferencesMemory()]
)
```

### Streaming Responses

```python
async for chunk in agent.run_stream(message, thread=thread_id):
    yield chunk
```

---

## 🔐 Security

- **Zero Trust**: User delegation, no app-level access
- **HTTPS Only**: Enforced in production
- **Security Headers**: CSP, HSTS, X-Frame-Options
- **Token Validation**: JWT verification with Azure AD
- **On-Behalf-Of Flow**: Backend exchanges user token for resource tokens
- **Audit Logging**: All actions logged with user identity

---

## 📊 Monitoring

- **Application Insights**: Automatic instrumentation
- **OpenTelemetry**: Built-in Agent Framework tracing
- **Health Endpoints**: `/health`, `/api/config`
- **Structured Logging**: JSON format for analysis

---

## 🤝 Contributing

1. Create feature branch: `git checkout -b feature/my-feature`
2. Make changes and test locally
3. Commit: `git commit -m "Add my feature"`
4. Push: `git push origin feature/my-feature`
5. Create Pull Request
6. CI/CD will automatically test your changes

---

## 📝 License

Copyright (c) Microsoft Corporation. All rights reserved.

---

## 🆘 Troubleshooting

### Pipeline Fails at Deployment

- Check GitHub secrets are configured correctly
- Verify Service Principal has Contributor role
- Check Azure OpenAI endpoint is accessible
- Review deployment logs in GitHub Actions

### Pipeline Fails at Health Check

- Backend may need more time to start (increase wait time)
- Check App Service logs in Azure Portal
- Verify environment variables are set correctly

### Tests Fail

- Integration tests require TEST_USER_TOKEN
- E2E tests require TEST_USERNAME and TEST_PASSWORD
- Ensure test user has permissions to sample workspace

### Resources Not Destroyed

- Check "destroy" job logs for errors
- Manually delete: `az group delete --name ci-icarus-test-YYYYMMDDHHMMSS`

---

## 🚀 Next Steps

1. **Configure GitHub Secrets** (most important!)
2. **Push code to trigger CI/CD**
3. **Monitor pipeline in Actions tab**
4. **On success, ready for production deployment**
5. **On failure, debug using deployed resources**

---

**Built with ❤️ using Microsoft Agent Framework**
