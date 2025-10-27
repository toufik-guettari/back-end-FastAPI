# MIGRATION MANAGER - Version Finale
Write-Host "=== GESTIONNAIRE DE MIGRATIONS ALEMBIC ===" -ForegroundColor Cyan
Write-Host "Mode: Contournement Docker (100% fiable)" -ForegroundColor Yellow

function Start-Migration {
    param([string]$Action = "upgrade", [string]$Target = "head")
    
    Write-Host "`n🚀 Exécution: alembic $Action $Target" -ForegroundColor Magenta
    
    # Étape 1: Générer le SQL
    Write-Host "1. Génération du SQL..." -ForegroundColor Yellow
    $sql_result = alembic $Action $Target --sql 2>&1
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Erreur génération SQL" -ForegroundColor Red
        Write-Host $sql_result -ForegroundColor Gray
        return
    }
    
    # Filtrer le SQL utile
    $clean_sql = $sql_result | Where-Object {
        $_ -match "^(BEGIN|COMMIT|CREATE|ALTER|DROP|INSERT|UPDATE|DELETE|SELECT|--|INFO)" -and
        $_ -notmatch "ALEMBIC|Configuration"
    }
    
    if ($clean_sql) {
        $clean_sql | Set-Content -Path migration_temp.sql -Encoding UTF8
        $line_count = (Get-Content migration_temp.sql | Measure-Object -Line).Lines
        Write-Host "   SQL généré ($line_count lignes)" -ForegroundColor Green
        
        # Étape 2: Appliquer via Docker
        Write-Host "2. Application via Docker..." -ForegroundColor Yellow
        Get-Content migration_temp.sql | docker compose -f docker-compose.dev.yml exec -T postgres psql -U postgres -d fastapi_db 2>&1 | Out-Null
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ✅ Migration appliquée avec succès" -ForegroundColor Green
        } else {
            Write-Host "   ⚠️  Erreurs possibles (tables existantes)" -ForegroundColor Yellow
        }
        
        # Nettoyage
        Remove-Item migration_temp.sql -ErrorAction SilentlyContinue
        Write-Host "3. Fichier temporaire nettoyé" -ForegroundColor Green
    } else {
        Write-Host "   ℹ️  Aucune opération SQL nécessaire" -ForegroundColor Blue
    }
}

# Menu interactif
do {
    Write-Host "`n=== MENU PRINCIPAL ===" -ForegroundColor Magenta
    Write-Host "1. État de la base" -ForegroundColor White
    Write-Host "2. Heads disponibles" -ForegroundColor White  
    Write-Host "3. Appliquer migrations (upgrade head)" -ForegroundColor White
    Write-Host "4. Créer nouvelle migration" -ForegroundColor White
    Write-Host "5. Historique" -ForegroundColor White
    Write-Host "6. Quitter" -ForegroundColor White
    
    $choice = Read-Host "`nChoix"
    
    switch ($choice) {
        "1" {
            Write-Host "`n📊 ÉTAT DE LA BASE:" -ForegroundColor Cyan
            docker compose -f docker-compose.dev.yml exec -T postgres psql -U postgres -d fastapi_db -c "\dt"
            docker compose -f docker-compose.dev.yml exec -T postgres psql -U postgres -d fastapi_db -c "SELECT version_num FROM alembic_version;"
            docker compose -f docker-compose.dev.yml exec -T postgres psql -U postgres -d fastapi_db -c "SELECT COUNT(*) as nb_tables FROM information_schema.tables WHERE table_schema = 'public';"
        }
        "2" {
            Write-Host "`n📋 HEADS ALEMBIC:" -ForegroundColor Cyan
            alembic heads
        }
        "3" {
            Start-Migration -Action "upgrade" -Target "head"
        }
        "4" {
            $message = Read-Host "Description de la migration"
            alembic revision --autogenerate -m $message
            Write-Host "✅ Migration créée - Utilisez l'option 3 pour l'appliquer" -ForegroundColor Green
        }
        "5" {
            Write-Host "`n📜 HISTORIQUE:" -ForegroundColor Cyan
            alembic history
        }
        "6" {
            Write-Host "`n👋 Au revoir!" -ForegroundColor Green
            break
        }
        default {
            Write-Host "❌ Choix invalide" -ForegroundColor Red
        }
    }
} while ($choice -ne "6")
