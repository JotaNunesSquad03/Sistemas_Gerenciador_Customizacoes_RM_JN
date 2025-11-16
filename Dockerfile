FROM python:3.11-slim

# Evitar prompts
ENV DEBIAN_FRONTEND=noninteractive

# Instalar dependências básicas
RUN apt-get update && apt-get install -y curl gnupg2 unixodbc unixodbc-dev

# Importar chave GPG correta (novo método)
RUN curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /etc/apt/trusted.gpg.d/microsoft.gpg

# Adicionar repositório do MS SQL (ODBC 18 funciona no Debian 12)
RUN echo "deb [arch=amd64] https://packages.microsoft.com/debian/12/prod bookworm main" \
    > /etc/apt/sources.list.d/mssql-release.list

# Instalar msodbcsql18 + ferramentas SQL
RUN apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql18 mssql-tools18

# Adicionar sqlcmd no PATH
ENV PATH="$PATH:/opt/mssql-tools18/bin"

# Criar diretório da aplicação
WORKDIR /app

# Instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código para o container
COPY . .

# Expor porta do FastAPI
EXPOSE 8000

# Comando de inicialização
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
