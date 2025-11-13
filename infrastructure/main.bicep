// Main Bicep Template for AI Icarus V2 with Agent Framework
// Supports Azure Commercial and Government clouds

@description('Environment name (dev, staging, prod, ci)')
param environment string = 'dev'

@description('Azure region for resources')
param location string = resourceGroup().location

@description('Azure cloud environment (Azure CLI format: AzureUSGovernment or AzurePublicCloud)')
@allowed([
  'AzurePublicCloud'
  'AzureUSGovernment'
])
param cloudEnvironment string = 'AzureUSGovernment'

// Map cloud environment to application setting format
var cloudEnvMapping = {
  AzureUSGovernment: 'AZURE_US_GOVERNMENT'
  AzurePublicCloud: 'AZURE_PUBLIC_CLOUD'
}
var normalizedCloudEnv = cloudEnvMapping[cloudEnvironment]

@description('Azure AD App Registration Client ID')
@secure()
param azureAdClientId string

@description('Azure AD App Registration Client Secret')
@secure()
param azureAdClientSecret string

@description('Azure AD Tenant ID')
param azureAdTenantId string

@description('Azure OpenAI Endpoint')
param azureOpenAiEndpoint string = ''

@description('Azure OpenAI Deployment Name')
param azureOpenAiDeployment string = 'gpt-4o'

@description('Deployment timestamp')
param deploymentTimestamp string = utcNow('yyyy-MM-dd')

// Common tags
var commonTags = {
  Application: 'AI-Icarus-V2'
  Environment: environment
  ManagedBy: 'Bicep'
  Cloud: cloudEnvironment
  Framework: 'Microsoft-Agent-Framework'
  CreatedDate: deploymentTimestamp
}

// Resource naming with environment suffix
var appNamePrefix = 'ai-icarus-${environment}-${uniqueString(resourceGroup().id)}'

// App Service Plan (Linux, Python 3.11)
resource appServicePlan 'Microsoft.Web/serverfarms@2023-01-01' = {
  name: '${appNamePrefix}-plan'
  location: location
  tags: commonTags
  sku: {
    name: environment == 'prod' ? 'P1v3' : 'B1'  // Production vs Dev/CI tier
    tier: environment == 'prod' ? 'PremiumV3' : 'Basic'
  }
  kind: 'linux'
  properties: {
    reserved: true
  }
}

// App Service (Backend - Python FastAPI + Agent Framework)
resource appService 'Microsoft.Web/sites@2023-01-01' = {
  name: '${appNamePrefix}-backend'
  location: location
  tags: commonTags
  properties: {
    serverFarmId: appServicePlan.id
    httpsOnly: true
    siteConfig: {
      linuxFxVersion: 'PYTHON|3.11'
      alwaysOn: environment == 'prod' ? true : false
      ftpsState: 'Disabled'
      minTlsVersion: '1.2'
      http20Enabled: true
      cors: {
        allowedOrigins: [
          '*'  // Will be restricted to frontend URL in production
        ]
        supportCredentials: true
      }
      appSettings: [
        {
          name: 'WEBSITE_RUN_FROM_PACKAGE'
          value: '1'
        }
        {
          name: 'AZURE_CLIENT_ID'
          value: azureAdClientId
        }
        {
          name: 'AZURE_CLIENT_SECRET'
          value: azureAdClientSecret
        }
        {
          name: 'AZURE_TENANT_ID'
          value: azureAdTenantId
        }
        {
          name: 'AZURE_CLOUD_ENVIRONMENT'
          value: normalizedCloudEnv
        }
        {
          name: 'AZURE_OPENAI_ENDPOINT'
          value: azureOpenAiEndpoint
        }
        {
          name: 'AZURE_OPENAI_DEPLOYMENT_NAME'
          value: azureOpenAiDeployment
        }
        {
          name: 'ENABLE_CORS'
          value: 'true'
        }
        {
          name: 'LOG_LEVEL'
          value: environment == 'prod' ? 'INFO' : 'DEBUG'
        }
        {
          name: 'PYTHONUNBUFFERED'
          value: '1'
        }
        {
          name: 'WEBSITES_PORT'
          value: '8000'
        }
      ]
    }
  }
}

// Application Insights
resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: '${appNamePrefix}-insights'
  location: location
  tags: commonTags
  kind: 'web'
  properties: {
    Application_Type: 'web'
    Request_Source: 'rest'
  }
}

// App Service - Application Insights connection
resource appServiceAppInsights 'Microsoft.Web/sites/config@2023-01-01' = {
  parent: appService
  name: 'appsettings'
  properties: {
    APPINSIGHTS_INSTRUMENTATIONKEY: appInsights.properties.InstrumentationKey
    APPLICATIONINSIGHTS_CONNECTION_STRING: appInsights.properties.ConnectionString
    ApplicationInsightsAgent_EXTENSION_VERSION: '~3'
  }
}

// Static Web App (Frontend - React + TypeScript)
// Note: Static Web Apps have limited availability in Azure Government
// Only deploy if in commercial cloud
resource staticWebApp 'Microsoft.Web/staticSites@2023-01-01' = if (cloudEnvironment == 'AzurePublicCloud') {
  name: '${appNamePrefix}-frontend'
  location: location
  tags: commonTags
  sku: {
    name: 'Free'
    tier: 'Free'
  }
  properties: {
    repositoryUrl: ''  // Will be configured via GitHub Actions
    branch: 'main'
    buildProperties: {
      appLocation: '/frontend'
      apiLocation: ''
      outputLocation: 'dist'
    }
  }
}

// For Azure Government, use App Service for frontend instead
resource frontendAppService 'Microsoft.Web/sites@2023-01-01' = if (cloudEnvironment == 'AzureUSGovernment') {
  name: '${appNamePrefix}-frontend'
  location: location
  tags: commonTags
  properties: {
    serverFarmId: appServicePlan.id
    httpsOnly: true
    siteConfig: {
      linuxFxVersion: 'NODE|18-lts'
      alwaysOn: false
      ftpsState: 'Disabled'
      minTlsVersion: '1.2'
    }
  }
}

// Outputs
output backendUrl string = 'https://${appService.properties.defaultHostName}'
output frontendUrl string = cloudEnvironment == 'AzureUSGovernment'
  ? 'https://${frontendAppService.properties.defaultHostName}'
  : 'https://${staticWebApp.properties.defaultHostname}'
output appServiceName string = appService.name
output frontendAppServiceName string = cloudEnvironment == 'AzureUSGovernment' ? frontendAppService.name : ''
output staticWebAppName string = cloudEnvironment == 'AzurePublicCloud' ? staticWebApp.name : ''
output resourceGroupName string = resourceGroup().name
output appInsightsInstrumentationKey string = appInsights.properties.InstrumentationKey
output appInsightsConnectionString string = appInsights.properties.ConnectionString
