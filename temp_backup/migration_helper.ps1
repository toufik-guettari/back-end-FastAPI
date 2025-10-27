# migration_helper.ps1
Write-Host "=== Assistant de Migration Alembic ===" -ForegroundColor Cyan

# Vérifier d'abord l'état
Write-Host "1. Verification de l'etat Alembic..." -ForegroundColor Yellow
alembic current
$heads = alembic heads

if (($heads -split "`n").Count -gt 1) {
    Write-Host "ATTENTION: Multiple heads detectes!" -ForegroundColor Red
    Write-Host "Execution de la correction automatique..." -ForegroundColor Yellow
    .\fix_alembic_heads.ps1
    exit
}

# Générer le SQL
Write-Host "2. Generation du SQL..." -ForegroundColor Yellow
try {
    # Essayer d'abord avec head spécifique
    $revision = ($heads -split " ")[0]
    Write-Host "   Utilisation de la revision: $revision" -ForegroundColor Gray
    $output = alembic upgrade $revision --sql 2>&1
} catch {
    # Fallback vers heads
    Write-Host "   Utilisation de 'heads'..." -ForegroundColor Gray
    $output = alembic upgrade heads --sql 2>&1
}

if ($LASTEXITCODE -eq 0) {
    # Extraire le SQL proprement
    $sql_lines = $output | Where-Object { 
        $_ -notmatch "INFO|ALEMBIC|WARNING" -and 
        $_ -notmatch "Context|Generating|Will assume" -and
        $_.Trim() -ne ""
    }
    
    if ($sql_lines) {
        $sql_content = $sql_lines -join "`n"
        $sql_content | Out-File -FilePath migration.sql -Encoding UTF8
        
        $line_count = (Get-Content migration.sql | Measure-Object -Line).Lines
        Write-Host "   SQL genere ($line_count lignes)" -ForegroundColor Green

        # Appliquer via Docker
        Write-Host "3. Application via Docker..." -ForegroundColor Yellow
        Get-Content migration.sql | docker compose -f docker-compose.dev.yml exec -T postgres psql -U postgres -d fastapi_db 2>&1 | Out-Null
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   Application reussie" -ForegroundColor Green
        } else {
            Write-Host "   Avertissement: erreurs possibles (tables existantes)" -ForegroundColor Yellow
        }

        # Nettoyer
        Remove-Item migration.sql -ErrorAction SilentlyContinue
        
        # Verification
        Write-Host "4. Verification finale..." -ForegroundColor Yellow
        docker compose -f docker-compose.dev.yml exec -T postgres psql -U postgres -d fastapi_db -c "\dt"
        
        Write-Host "=== MIGRATION TERMINEE ===" -ForegroundColor Green
    } else {
        Write-Host "ERREUR: Aucun SQL genere" -ForegroundColor Red
    }
} else {
    Write-Host "ERREUR Generation SQL:" -ForegroundColor Red
    Write-Host $output -ForegroundColor Gray
}
