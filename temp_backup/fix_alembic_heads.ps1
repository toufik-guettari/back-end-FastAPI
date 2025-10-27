# fix_alembic_heads.ps1
Write-Host "=== Correction des conflits Alembic ===" -ForegroundColor Cyan

Write-Host "1. Identification des tetes de revision..." -ForegroundColor Yellow
$heads = alembic heads
Write-Host "Heads detectes:" -ForegroundColor White
Write-Host $heads -ForegroundColor Gray

Write-Host "2. Fusion des revisions..." -ForegroundColor Yellow
alembic merge heads -m "merge_heads"

Write-Host "3. Verification de l'etat..." -ForegroundColor Yellow
alembic current
alembic heads

Write-Host "4. Application des migrations..." -ForegroundColor Yellow
.\migration_helper.ps1

Write-Host "=== CORRECTION TERMINEE ===" -ForegroundColor Green
