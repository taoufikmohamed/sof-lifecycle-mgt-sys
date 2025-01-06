# Configuration
$DEPLOY_DIR = Join-Path $PSScriptRoot "deploy"
$MAX_RETRIES = 3
$RETRY_DELAY = 2
$PORT = 3000# Configuration
$DEPLOY_DIR = Join-Path $PSScriptRoot "deploy"
$MAX_RETRIES = 3
$RETRY_DELAY = 2
$PORT = 3000
$HEALTH_CHECK_URL = "http://localhost:$PORT/health"

function Test-HealthCheck {
    try {
        $response = Invoke-WebRequest -Uri $HEALTH_CHECK_URL -Method GET
        return $response.StatusCode -eq 200
    }
    catch {
        return $false
    }
}

function Start-NodeServer {
    try {
        $process = Start-Process -FilePath "node" -ArgumentList "server.js" -NoNewWindow -PassThru
        
        # Wait for server to start
        $retryCount = 0
        while ($retryCount -lt $MAX_RETRIES) {
            if (Test-HealthCheck) {
                Write-Host "Server started successfully"
                return $true
            }
            $retryCount++
            Start-Sleep -Seconds $RETRY_DELAY
        }
        
        Write-Error "Server failed to start after $MAX_RETRIES attempts"
        return $false
    }
    catch {
        Write-Error "Failed to start Node.js server: $_"
        return $false
    }
}

try {
    Write-Host "Starting deployment..."
    
    # Kill existing Node processes
    Get-Process -Name "node" -ErrorAction SilentlyContinue | Stop-Process -Force
    Start-Sleep -Seconds 2

    # Clean deployment directory
    if (Test-Path -Path $DEPLOY_DIR) {
        Remove-Item -Path $DEPLOY_DIR -Recurse -Force
    }
    New-Item -ItemType Directory -Path $DEPLOY_DIR -Force | Out-Null

    # Create application files
    Push-Location $DEPLOY_DIR
    
    # Setup package.json
    $packageJson = @{
        name = "health-check-app"
        version = "1.0.0"
        main = "server.js"
        scripts = @{ start = "node server.js" }
        dependencies = @{ express = "^4.18.2" }
    } | ConvertTo-Json
    Set-Content -Path "package.json" -Value $packageJson

    # Create server.js
    @'
const express = require('express');
const app = express();
const port = process.env.PORT || 3000;

app.get('/health', (req, res) => {
    res.status(200).json({ 
        status: 'healthy',
        timestamp: new Date().toISOString()
    });
});

const server = app.listen(port, () => {
    console.log(`Server running on http://localhost:${port}`);
});

process.on('SIGTERM', () => {
    server.close(() => {
        console.log('Server stopped');
        process.exit(0);
    });
});
'@ | Set-Content "server.js"

    # Install dependencies
    npm install --no-fund --silent
    
    # Start server and verify health
    if (-not (Start-NodeServer)) {
        throw "Failed to verify server health"
    }

    Write-Host "Deployment completed successfully"
    Pop-Location
    exit 0
}
catch {
    Write-Error "Deployment failed: $_"
    if (Test-Path -Path $DEPLOY_DIR) {
        Get-Process -Name "node" -ErrorAction SilentlyContinue | Stop-Process -Force
    }
    exit 1
}
$HEALTH_CHECK_URL = "http://localhost:$PORT/health"

function Test-HealthCheck {
    try {
        $response = Invoke-WebRequest -Uri $HEALTH_CHECK_URL -Method GET
        return $response.StatusCode -eq 200
    }
    catch {
        return $false
    }
}

function Start-NodeServer {
    try {
        $process = Start-Process -FilePath "node" -ArgumentList "server.js" -NoNewWindow -PassThru
        
        # Wait for server to start
        $retryCount = 0
        while ($retryCount -lt $MAX_RETRIES) {
            if (Test-HealthCheck) {
                Write-Host "Server started successfully"
                return $true
            }
            $retryCount++
            Start-Sleep -Seconds $RETRY_DELAY
        }
        
        Write-Error "Server failed to start after $MAX_RETRIES attempts"
        return $false
    }
    catch {
        Write-Error "Failed to start Node.js server: $_"
        return $false
    }
}

try {
    Write-Host "Starting deployment..."
    
    # Kill existing Node processes
    Get-Process -Name "node" -ErrorAction SilentlyContinue | Stop-Process -Force
    Start-Sleep -Seconds 2

    # Clean deployment directory
    if (Test-Path -Path $DEPLOY_DIR) {
        Remove-Item -Path $DEPLOY_DIR -Recurse -Force
    }
    New-Item -ItemType Directory -Path $DEPLOY_DIR -Force | Out-Null

    # Create application files
    Push-Location $DEPLOY_DIR
    
    # Setup package.json
    $packageJson = @{
        name = "health-check-app"
        version = "1.0.0"
        main = "server.js"
        scripts = @{ start = "node server.js" }
        dependencies = @{ express = "^4.18.2" }
    } | ConvertTo-Json
    Set-Content -Path "package.json" -Value $packageJson

    # Create server.js
    @'
const express = require('express');
const app = express();
const port = process.env.PORT || 3000;

app.get('/health', (req, res) => {
    res.status(200).json({ 
        status: 'healthy',
        timestamp: new Date().toISOString()
    });
});

const server = app.listen(port, () => {
    console.log(`Server running on http://localhost:${port}`);
});

process.on('SIGTERM', () => {
    server.close(() => {
        console.log('Server stopped');
        process.exit(0);
    });
});
'@ | Set-Content "server.js"

    # Install dependencies
    npm install --no-fund --silent
    
    # Start server and verify health
    if (-not (Start-NodeServer)) {
        throw "Failed to verify server health"
    }

    Write-Host "Deployment completed successfully"
    Pop-Location
    exit 0
}
catch {
    Write-Error "Deployment failed: $_"
    if (Test-Path -Path $DEPLOY_DIR) {
        Get-Process -Name "node" -ErrorAction SilentlyContinue | Stop-Process -Force
    }
    exit 1
}