# migrate.ps1 - Gestionnaire de migrations Alembic pour Windows

param(
    [string]$Action,
    [string]$Message = "auto_migration"
)

switch ($Action) {
    "generate" {
        Write-Host "🔨 Génération migration..." -ForegroundColor Yellow
        alembic revision --autogenerate -m $Message
        Write-Host "✅ Migration générée - VÉRIFIER LE FICHIER!" -ForegroundColor Green
    }
    "upgrade" {
        Write-Host "⬆️  Application migrations..." -ForegroundColor Yellow
        alembic upgrade head
        Write-Host "✅ Migrations appliquées" -ForegroundColor Green
    }
    "downgrade" {
        Write-Host "⬇️  Rollback migration..." -ForegroundColor Yellow
        alembic downgrade -1
        Write-Host "✅ Rollback effectué" -ForegroundColor Green
    }
    "current" {
        Write-Host "📍 Version actuelle:" -ForegroundColor Cyan
        alembic current
    }
    "history" {
        Write-Host "📜 Historique migrations:" -ForegroundColor Cyan
        alembic history
    }
    default {
        Write-Host "Usage: .\migrate.ps1 {generate|upgrade|downgrade|current|history} [message]" -ForegroundColor Red
        exit 1
    }
}
