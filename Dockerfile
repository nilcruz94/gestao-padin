# Usa a imagem oficial do Python
FROM python:3.10

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia todos os arquivos do diretório local para o container
COPY . .

# Instala as dependências do projeto
RUN pip install --no-cache-dir -r requirements.txt

# Define a variável de ambiente para o banco de dados
ENV DATABASE_URL="postgresql://folgas_user:1xrBtiUdWBbWnzW2gxY2h8CU2PRhQEir@dpg-cueaq3d2ng1s7386b3dg-a/folgas"

# Expõe a porta 8000 para acesso externo
EXPOSE 8000

# Comando para rodar a aplicação
CMD ["python", "app.py"]
