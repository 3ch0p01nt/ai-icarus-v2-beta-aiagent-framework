<#
.SYNOPSIS
    Deploy AI Icarus V2 Backend to Azure App Service using ZipDeploy API

.DESCRIPTION
    This script packages the backend Python application and deploys it to Azure App Service
    using the ZipDeploy API, which triggers Azure Oryx to build and install dependencies.

.PARAMETER ResourceGroupName
    The name of the Azure resource group containing the App Service

.PARAMETER AppServiceName
    The name of the Azure App Service (backend)

.PARAMETER CloudEnvironment
    Azure cloud environment (AzureCloud, AzureUSGovernment). Default: AzureUSGovernment

.EXAMPLE
    .\deploy-backend.ps1 -ResourceGroupName "my-rg" -AppServiceName "my-app-backend"

.EXAMPLE
    .\deploy-backend.ps1 -ResourceGroupName "my-rg" -AppServiceName "my-app-backend" -CloudEnvironment "AzureCloud"
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$ResourceGroupName,

    [Parameter(Mandatory=$true)]
    [string]$AppServiceName,

    [Parameter(Mandatory=$false)]
    [ValidateSet("AzureCloud", "AzureUSGovernment")]
    [string]$CloudEnvironment = "AzureUSGovernment"
)

$ErrorActionPreference = "Stop"

# Get script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir
$backendDir = Join-Path $projectRoot "backend"
$deployZip = Join-Path $backendDir "deploy.zip"

Write-Host "🚀 AI Icarus V2 Backend Deployment Script" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Resource Group : $ResourceGroupName" -ForegroundColor Yellow
Write-Host "App Service    : $AppServiceName" -ForegroundColor Yellow
Write-Host "Cloud          : $CloudEnvironment" -ForegroundColor Yellow
Write-Host ""

# Ensure Azure CLI is logged in
Write-Host "🔐 Checking Azure CLI authentication..." -ForegroundColor Cyan
$account = az account show 2>$null | ConvertFrom-Json
if (-not $account) {
    Write-Host "❌ Not logged in to Azure CLI. Please run 'az login'" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Logged in as: $($account.user.name)" -ForegroundColor Green

# Set cloud environment
Write-Host "☁️  Setting cloud environment to $CloudEnvironment..." -ForegroundColor Cyan
az cloud set --name $CloudEnvironment | Out-Null
Write-Host "✅ Cloud environment set" -ForegroundColor Green

# Verify app service exists
Write-Host "🔍 Verifying App Service exists..." -ForegroundColor Cyan
$appExists = az webapp show --name $AppServiceName --resource-group $ResourceGroupName 2>$null
if (-not $appExists) {
    Write-Host "❌ App Service '$AppServiceName' not found in resource group '$ResourceGroupName'" -ForegroundColor Red
    exit 1
}
Write-Host "✅ App Service found" -ForegroundColor Green

# Clean up old deployment zip
if (Test-Path $deployZip) {
    Write-Host "🧹 Removing old deployment package..." -ForegroundColor Cyan
    Remove-Item $deployZip -Force
}

# Create deployment package
Write-Host "📦 Creating deployment package..." -ForegroundColor Cyan
Push-Location $backendDir
try {
    # Compress all files except excluded patterns
    $excludePatterns = @("*.git*", "*__pycache__*", "*.venv*", "*tests*", "*.azure*", "deploy.zip")

    # Get all files to include
    $files = Get-ChildItem -Recurse -File | Where-Object {
        $file = $_
        $include = $true
        foreach ($pattern in $excludePatterns) {
            if ($file.FullName -like "*$($pattern.Replace('*', ''))") {
                $include = $false
                break
            }
        }
        $include
    }

    Write-Host "  Including $($files.Count) files in deployment package" -ForegroundColor Gray

    # Create zip
    Compress-Archive -Path $files.FullName -DestinationPath "deploy.zip" -Force

    Write-Host "✅ Deployment package created: $('{0:N2}' -f ((Get-Item deploy.zip).Length / 1MB)) MB" -ForegroundColor Green
}
finally {
    Pop-Location
}

# Get publishing credentials
Write-Host "🔑 Getting publishing credentials..." -ForegroundColor Cyan
$credsJson = az webapp deployment list-publishing-credentials `
    --resource-group $ResourceGroupName `
    --name $AppServiceName `
    --query "{username:publishingUserName, password:publishingPassword}" -o json

$creds = $credsJson | ConvertFrom-Json
$username = $creds.username
$password = $creds.password

Write-Host "✅ Credentials retrieved" -ForegroundColor Green

# Deploy via ZipDeploy API
Write-Host "🚀 Deploying to Azure via ZipDeploy API..." -ForegroundColor Cyan
$scmDomain = if ($CloudEnvironment -eq "AzureUSGovernment") { "azurewebsites.us" } else { "azurewebsites.net" }
$zipDeployUrl = "https://$AppServiceName.scm.$scmDomain/api/zipdeploy?isAsync=true"

Write-Host "  Endpoint: $zipDeployUrl" -ForegroundColor Gray

# Create credential object
$securePassword = ConvertTo-SecureString $password -AsPlainText -Force
$credential = New-Object System.Management.Automation.PSCredential($username, $securePassword)

# Deploy
try {
    $response = Invoke-WebRequest -Uri $zipDeployUrl `
        -Method POST `
        -InFile $deployZip `
        -ContentType "application/zip" `
        -Credential $credential `
        -UseBasicParsing

    if ($response.StatusCode -eq 200 -or $response.StatusCode -eq 202) {
        Write-Host "✅ Deployment initiated successfully (Status: $($response.StatusCode))" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Unexpected status code: $($response.StatusCode)" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "❌ Deployment failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Wait for build completion
Write-Host "⏳ Waiting for Oryx build to complete..." -ForegroundColor Cyan
$deploymentUrl = "https://$AppServiceName.scm.$scmDomain/api/deployments/latest"
$maxAttempts = 60
$attempt = 0

while ($attempt -lt $maxAttempts) {
    $attempt++
    Start-Sleep -Seconds 5

    try {
        $deploymentStatus = Invoke-RestMethod -Uri $deploymentUrl `
            -Method GET `
            -Credential $credential `
            -UseBasicParsing

        $status = $deploymentStatus.status
        $statusText = switch ($status) {
            0 { "Pending" }
            1 { "Building" }
            2 { "Deploying" }
            3 { "Failed" }
            4 { "Success" }
            default { "Unknown ($status)" }
        }

        Write-Host "  Build status (attempt $attempt/$maxAttempts): $statusText" -ForegroundColor Gray

        if ($status -eq 4) {
            Write-Host "✅ Build completed successfully!" -ForegroundColor Green
            break
        }
        elseif ($status -eq 3) {
            Write-Host "❌ Build failed. Check App Service logs for details." -ForegroundColor Red
            Write-Host "  View logs: az webapp log tail --name $AppServiceName --resource-group $ResourceGroupName" -ForegroundColor Yellow
            exit 1
        }
    }
    catch {
        Write-Host "  Could not check deployment status: $($_.Exception.Message)" -ForegroundColor Gray
    }
}

if ($attempt -ge $maxAttempts) {
    Write-Host "⚠️  Deployment status check timed out after $($maxAttempts * 5) seconds" -ForegroundColor Yellow
    Write-Host "  The deployment may still succeed. Check the App Service logs." -ForegroundColor Yellow
}

# Clean up deployment zip
Write-Host "🧹 Cleaning up..." -ForegroundColor Cyan
if (Test-Path $deployZip) {
    Remove-Item $deployZip -Force
}

Write-Host ""
Write-Host "✅ Deployment process completed!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Check health endpoint: https://$AppServiceName.$scmDomain/health" -ForegroundColor Yellow
Write-Host "  2. View logs: az webapp log tail --name $AppServiceName --resource-group $ResourceGroupName" -ForegroundColor Yellow
Write-Host ""
