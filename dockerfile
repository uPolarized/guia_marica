# D:\projeto-grafo\Dockerfile

# 1. MUDE A IMAGEM BASE para "bookworm" para ter uma versão mais recente do SQLite
FROM python:3.11-slim-bookworm

# Define variáveis de ambiente para Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Instala dependências do sistema
# - build-essential: Contém gcc, make, etc.
# - libgdal-dev & libspatialindex-dev: Para bibliotecas geoespaciais (OSMnx).
# - curl: Para depuração.
# - libpq-dev: É para PostgreSQL. Se você tem certeza que SÓ usará SQLite, pode remover esta linha.
#   Se houver chance de usar PostgreSQL no futuro ou se alguma dependência obscura o puxar, pode manter.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgdal-dev \
    libspatialindex-dev \
    curl \
    # libpq-dev \ # Remova ou comente esta linha se você tem certeza que não precisa de PostgreSQL
    && rm -rf /var/lib/apt/lists/*

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia o arquivo de dependências Python e instala as dependências
COPY requirements.txt /app/
# Certifique-se que psycopg2-binary NÃO está em requirements.txt se você vai usar SQLite.
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o código do projeto para o diretório de trabalho no container
COPY . /app/

# Coleta os arquivos estáticos do Django
RUN python manage.py collectstatic --noinput

# Expõe a porta que o Gunicorn vai usar dentro do container
EXPOSE 8000

# Comando para iniciar a aplicação usando Gunicorn
# SUBSTITUA "projeto_grafo" pelo nome real da pasta do seu projeto Django (que contém wsgi.py)
# 2. ADICIONADO --workers 1 (CRUCIAL PARA SQLITE)
CMD ["gunicorn", "--workers", "1", "--bind", "0.0.0.0:8000", "projeto_grafo.wsgi:application"]