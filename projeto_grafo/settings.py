# Em projeto_grafo/settings.py (ou no seu arquivo principal de settings)

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# CHAVE SECRETA
# Para produção, SEMPRE use uma variável de ambiente.
# Gere uma nova: https://djecrety.ir/
SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'django-insecure-seu-fallback-local-SUPER-SECRETO-altere-isto!' # ALTERE ou defina via .env local
)

# DEBUG
# Em produção, SEMPRE defina DJANGO_DEBUG="False" como variável de ambiente.
DEBUG_STR = os.environ.get('DJANGO_DEBUG', 'True') # Default para True se não definida para dev local
DEBUG = DEBUG_STR.lower() in ('true', '1', 't', 'yes')


# ALLOWED_HOSTS
render_hostname = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
allowed_hosts_env = os.environ.get('DJANGO_ALLOWED_HOSTS')
ALLOWED_HOSTS = []

if DEBUG:
    ALLOWED_HOSTS.extend(['localhost', '127.0.0.1'])
    if render_hostname: # Permite acesso via URL do Render mesmo em DEBUG local se a var estiver setada
        ALLOWED_HOSTS.append(render_hostname)

if allowed_hosts_env:
    ALLOWED_HOSTS.extend([host.strip() for host in allowed_hosts_env.split(',') if host.strip()])

if render_hostname and render_hostname not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(render_hostname)

if not DEBUG and not ALLOWED_HOSTS:
    print("CRÍTICO: DEBUG=False e ALLOWED_HOSTS está vazio. A aplicação não iniciará em produção.")
    print("Configure a variável de ambiente DJANGO_ALLOWED_HOSTS na sua plataforma de hospedagem.")
    # Para evitar que o build quebre AGORA se você estiver apenas testando o collectstatic localmente
    # com DEBUG=False e sem env vars, você pode temporariamente adicionar '*', mas remova para produção real.
    # ALLOWED_HOSTS = ['*'] # REMOVA ESTA LINHA PARA PRODUÇÃO REAL E CONFIGURE AS VARS DE AMBIENTE

if not ALLOWED_HOSTS and DEBUG: # Se ainda vazio e DEBUG, permita qualquer host para dev local.
    ALLOWED_HOSTS = ['*'] # OK para DEBUG=True local


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',      
    'django.contrib.messages',
    'whitenoise.runserver_nostatic', # Para WhiteNoise servir estáticos com runserver (DEBUG=True)
    'django.contrib.staticfiles',
    'grafo_app',                   # Sua aplicação
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # WhiteNoise: logo após SecurityMiddleware
    'django.contrib.sessions.middleware.SessionMiddleware', 
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'projeto_grafo.urls' # Substitua 'projeto_grafo' pelo nome da sua pasta de projeto principal

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')], 
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'projeto_grafo.wsgi.application' # Substitua 'projeto_grafo' se necessário


# Database (SQLite configurado para usar PERSISTENT_STORAGE_PATH)
PERSISTENT_STORAGE_PATH = os.environ.get('PERSISTENT_STORAGE_PATH', os.path.join(BASE_DIR, 'local_persistent_data_for_sqlite'))
if not os.path.exists(PERSISTENT_STORAGE_PATH) and DEBUG:
    try:
        os.makedirs(PERSISTENT_STORAGE_PATH, exist_ok=True)
        print(f"DEBUG: Criado diretório para persistência em {PERSISTENT_STORAGE_PATH}")
    except OSError as e:
        print(f"AVISO: Não foi possível criar o diretório de persistência {PERSISTENT_STORAGE_PATH}: {e}")
        PERSISTENT_STORAGE_PATH = BASE_DIR
            
# settings.py (exemplo da seção DATABASES)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'django_db'), # 'django_db'
        'USER': os.environ.get('DB_USER', 'user'),       # 'user'
        'PASSWORD': os.environ.get('DB_PASSWORD', 'password'), # 'password'
        'HOST': os.environ.get('DB_HOST', 'db'),         # 'db' (nome do serviço no docker-compose)
        'PORT': os.environ.get('DB_PORT', '5432'),     # Porta padrão
    }
}

if DEBUG: print(f"INFO: Usando banco de dados SQLite em: {DATABASES['default']['NAME']}")
if not DEBUG:
    print(f"INFO (Produção): Usando SQLite. Caminho: {DATABASES['default']['NAME']}")
    print(f"Lembrete: Gunicorn com '--workers 1' para SQLite.")


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# Internationalization
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'

# ***** MUDANÇA IMPORTANTE ABAIXO *****
# Diretório onde o collectstatic irá juntar todos os arquivos estáticos para deploy.
# Este caminho é DENTRO do container Docker.
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles_collected') # Ou apenas 'staticfiles' se preferir

# Configuração do WhiteNoise para servir estáticos em produção
# Certifique-se de que 'whitenoise.middleware.WhiteNoiseMiddleware' está em MIDDLEWARE
# e 'whitenoise.runserver_nostatic' em INSTALLED_APPS se quiser testar com runserver.
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Opcional: Diretórios adicionais onde o Django procurará por arquivos estáticos
# (além das pastas 'static' dentro de cada app).
# STATICFILES_DIRS = [
#     os.path.join(BASE_DIR, 'minha_pasta_global_de_estaticos'),
# ]
# ***** FIM DA MUDANÇA IMPORTANTE *****


# Media files (Uploads de Usuários)
MEDIA_URL = '/media/'
# MEDIA_ROOT também deve apontar para o disco persistente em produção no Render
MEDIA_ROOT = os.path.join(PERSISTENT_STORAGE_PATH, 'mediafiles') 
if not os.path.exists(MEDIA_ROOT) and DEBUG:
    try:
        os.makedirs(MEDIA_ROOT, exist_ok=True)
    except OSError as e:
        print(f"AVISO: Não foi possível criar o diretório de mídia {MEDIA_ROOT}: {e}")

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CSRF_TRUSTED_ORIGINS
CSRF_TRUSTED_ORIGINS_ENV = os.environ.get('DJANGO_CSRF_TRUSTED_ORIGINS')
if CSRF_TRUSTED_ORIGINS_ENV:
    CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in CSRF_TRUSTED_ORIGINS_ENV.split(',') if origin.strip()]
elif render_hostname:
    CSRF_TRUSTED_ORIGINS = [f'https://{render_hostname}']
else:
    CSRF_TRUSTED_ORIGINS = [] 
    if not DEBUG:
        print("AVISO: CSRF_TRUSTED_ORIGINS não definido para produção.")

# Adicione esta linha se não estiver usando HTTPS localmente e quiser testar POSTs
# Mas para produção no Render (que usa HTTPS), isso não deve ser necessário se CSRF_TRUSTED_ORIGINS estiver correto.
# if DEBUG:
#    CSRF_COOKIE_SECURE = False
#    SESSION_COOKIE_SECURE = False