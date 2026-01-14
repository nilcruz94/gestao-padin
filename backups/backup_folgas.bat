@echo off
REM ==============================
REM Configurações do Banco Render
REM ==============================
set DATABASE_URL=postgresql://folgas_user:BLS6AMWRXX0vuFBM6q7oHKKwJChaK8dk@dpg-cuece7hopnds738g0usg-a.virginia-postgres.render.com/folgas_3tqr?sslmode=require
set BACKUP_DIR=C:\Users\Neto\Desktop\Projetos\Em uso\folga_system

REM ==============================
REM Detecta versão instalada do PostgreSQL
REM ==============================
if exist "C:\Program Files\PostgreSQL\17\bin\pg_dump.exe" (
    set PGDUMP="C:\Program Files\PostgreSQL\17\bin\pg_dump.exe"
) else if exist "C:\Program Files\PostgreSQL\16\bin\pg_dump.exe" (
    set PGDUMP="C:\Program Files\PostgreSQL\16\bin\pg_dump.exe"
) else (
    echo ERRO: pg_dump nao encontrado em 16 ou 17.
    pause
    exit /b 1
)

REM ==============================
REM Pega a data no formato YYYY-MM-DD
REM ==============================
for /f "skip=1 tokens=1" %%x in ('wmic os get LocalDateTime') do if not defined mydate set mydate=%%x
set yyyy=%mydate:~0,4%
set mm=%mydate:~4,2%
set dd=%mydate:~6,2%

set BACKUP_FILE=%BACKUP_DIR%\backup-%yyyy%-%mm%-%dd%.sql

REM ==============================
REM Gera backup completo do banco
REM ==============================
echo Criando backup completo em "%BACKUP_FILE%" ...
%PGDUMP% "%DATABASE_URL%" > "%BACKUP_FILE%"

if %ERRORLEVEL%==0 (
    echo Backup concluido com sucesso!
) else (
    echo ERRO ao gerar backup.
)

pause
