# D:\projeto-grafo\Dockerfile
# Use uma imagem Python oficial baseada em Debian (Buster)
FROM python:3.11-slim-buster

# Define variáveis de ambiente para Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Instala dependências do sistema
# - build-essential: Contém gcc, make, etc., necessários para compilar algumas extensões Python.
# - libpq-dev: Necessário para psycopg2 (adaptador Python para PostgreSQL). Remova se não usar PostgreSQL.
# - libgdal-dev: Para a biblioteca GDAL, uma dependência comum de pacotes geoespaciais como Fiona, Geopandas (usados pelo OSMnx).
# - libspatialindex-dev: Para a biblioteca RTree, outra dependência comum do Geopandas.
# - curl: Mantido, já que você adicionou para depuração.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libgdal-dev \
    libspatialindex-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia o arquivo de dependências Python e instala as dependências
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o código do projeto para o diretório de trabalho no container
COPY . /app/

# Coleta os arquivos estáticos do Django para a pasta definida em STATIC_ROOT
# Certifique-se de que STATIC_ROOT está configurado em settings.py (ex: '/app/staticfiles')
# e que você está usando uma estratégia para servir estáticos em produção (ex: WhiteNoise).
RUN python manage.py collectstatic --noinput

# Expõe a porta que o Gunicorn vai usar dentro do container
EXPOSE 8000

# Comando para iniciar a aplicação usando Gunicorn
# SUBSTITUA "projeto_grafo" pelo nome real da pasta do seu projeto Django
# (a pasta que contém o seu arquivo wsgi.py)
# Ex: se seu wsgi.py está em "meu_projeto_django/wsgi.py", use "meu_projeto_django.wsgi:application"
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "projeto_grafo.wsgi:application"]