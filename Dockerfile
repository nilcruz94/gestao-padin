# Imagem menor e mais adequada para produção
FROM python:3.10-slim

# Evita .pyc e melhora logs em container
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Dependências de sistema necessárias para WeasyPrint (cairo/pango/gdk-pixbuf) + fontes
RUN apt-get update && apt-get install -y --no-install-recommends \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    shared-mime-info \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

# Diretório de trabalho
WORKDIR /app

# Instala dependências primeiro (melhor cache)
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do projeto
COPY . /app

# ❗️NÃO recomendo hardcode de DATABASE_URL no Dockerfile.
# Render injeta env vars no painel. Se você mantiver, ok, mas é um risco.
# Vou manter como estava, porém o ideal é remover e configurar no Render.
ENV DATABASE_URL="postgresql://folgas_user:1xrBtiUdWBbWnzW2gxY2h8CU2PRhQEir@dpg-cueaq3d2ng1s7386b3dg-a/folgas"

# Render usa a variável PORT. Mantemos compatibilidade.
EXPOSE 8000

# Produção: gunicorn (bem mais estável do que python app.py)
# Se seu Flask app é "app = Flask(...)" dentro de app.py, então app:app está correto.
CMD ["sh", "-c", "gunicorn -b 0.0.0.0:${PORT:-8000} app:app"]