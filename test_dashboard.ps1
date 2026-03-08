# Quick test script
Write-Host "Testing Navedas CX Dashboard..."
Write-Host ""

# Check files exist
$files = @("server.py", "ecommerce_cx_hub_v10 (3).html", "navedas_cx_1000 (1).xlsx")
foreach ($f in $files) {
    if (Test-Path $f) {
        Write-Host "OK: $f found"
    } else {
        Write-Host "ERROR: $f missing"
    }
}

Write-Host ""
Write-Host "Starting server in background..."
$server = Start-Process python -ArgumentList "server.py" -PassThru -WindowStyle Hidden

Write-Host "Waiting 4 seconds for server startup..."
Start-Sleep -Seconds 4

Write-Host ""
Write-Host "Testing API endpoint..."
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8080/api/data" -ErrorAction Stop
    $data = $response.Content | ConvertFrom-Json

    Write-Host "SUCCESS - API responding:"
    Write-Host "  - Tickets: $($data.all_tickets.Count)"
    Write-Host "  - Months: $($data.monthly_data.Count)"
    Write-Host "  - Agents: $($data.agent_data.Count)"
    Write-Host ""
    Write-Host "Dashboard ready at: http://localhost:8080"
} catch {
    Write-Host "ERROR: API not responding - $($_.Exception.Message)"
}

Write-Host ""
Write-Host "Stopping test server..."
Stop-Process -Id $server.Id -ErrorAction SilentlyContinue
