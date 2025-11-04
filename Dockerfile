# Imagem oficial da Microsoft com o driver ODBC 17 já instalado
FROM mcr.microsoft.com/mssql-tools:latest

# Instala Python e dependências necessárias
RUN apt-get update && \
    apt-get install -y python3 python3-pip unixodbc-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Cria diretório da aplicação
WORKDIR /app

# Copia os arquivos do projeto
COPY . /app

# Instala dependências Python
RUN python -m pip install --upgrade pip && python -m pip install -r requirements.txt

# Expõe a porta do FastAPI
EXPOSE 10000

# Comando para iniciar o servidor
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000"]
