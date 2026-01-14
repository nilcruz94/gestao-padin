$ErrorActionPreference = "Stop"

# =========================
# CONFIG
# =========================
$BackupDir = "C:\Users\Neto\Desktop\Projetos\Em uso\folga_system\backups"
$RetentionDays = 30

# PostgreSQL 16 tools
$PgDump = "C:\Program Files\PostgreSQL\16\bin\pg_dump.exe"
$PgRestore = "C:\Program Files\PostgreSQL\16\bin\pg_restore.exe"

# =========================
# VALIDATIONS
# =========================
New-Item -ItemType Directory -Force -Path $BackupDir | Out-Null

if (-not (Test-Path $PgDump)) {
    throw "pg_dump não encontrado em: $PgDump. Ajuste o caminho para o PostgreSQL 16."
}

# URL do Render deve estar em variável de ambiente
# Exemplo (você executa localmente): setx RENDER_DATABASE_URL "postgresql://user:pass@host:5432/dbname"
$DbUrl = $env:RENDER_DATABASE_URL
if (-not $DbUrl) {
    throw "Variável RENDER_DATABASE_URL não definida. Defina com setx e abra um novo PowerShell."
}

# =========================
# BACKUP
# =========================
$ts = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$outFile = Join-Path $BackupDir ("render_backup_{0}.dump" -f $ts)

Write-Host "Iniciando backup..."
Write-Host "Destino: $outFile"

& $PgDump `
  --dbname="$DbUrl" `
  --format=custom `
  --file="$outFile" `
  --no-owner `
  --no-privileges

Write-Host "Backup concluído."

# =========================
# QUICK INTEGRITY CHECK (list first lines)
# =========================
if (Test-Path $PgRestore) {
    Write-Host "Validando dump (listagem rápida)..."
    & $PgRestore -l "$outFile" | Select-Object -First 10 | ForEach-Object { Write-Host $_ }
    Write-Host "Validação OK (dump legível)."
} else {
    Write-Host "pg_restore não encontrado em: $PgRestore (validação ignorada)."
}

# =========================
# RETENTION (delete older dumps)
# =========================
Write-Host "Aplicando retenção: removendo arquivos com mais de $RetentionDays dias..."
Get-ChildItem $BackupDir -Filter "*.dump" |
  Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-$RetentionDays) } |
  Remove-Item -Force

Write-Host "Finalizado."
