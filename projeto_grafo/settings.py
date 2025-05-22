import os
from pathlib import Path

# Caminho base
BASE_DIR = Path(__file__).resolve().parent.parent

# DEBUG e SECRET_KEY
DEBUG = os.environ.get('DJANGO_DEBUG', 'True').lower() in ('true', '1', 't', 'yes')
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'fallback-inseguro-para-dev-troque-isto')

# ALLOWED_HOSTS
ALLOWED_HOSTS = []
render_hostname = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if render_hostname:
    ALLOWED_HOSTS.append(render_hostname)

custom_hosts = os.environ.get('DJANGO_ALLOWED_HOSTS')
if custom_hosts:
    ALLOWED_HOSTS.extend([host.strip() for host in custom_hosts.split(',') if host.strip()])

if DEBUG:
    ALLOWED_HOSTS.extend(['localhost', '127.0.0.1'])

ALLOWED_HOSTS = list(set(filter(None, ALLOWED_HOSTS)))

# Warnings
if not DEBUG and not ALLOWED_HOSTS:
    print("CRÍTICO: DEBUG=False e ALLOWED_HOSTS está vazio.")
    # ALLOWED_HOSTS = ['*']  # ⚠️ Apenas se estiver testando em emergência

# Banco de dados SQLite (Render com armazenamento persistente)
PERSISTENT_STORAGE_PATH = os.environ.get('PERSISTENT_STORAGE_PATH', os.path.join(BASE_DIR, 'local_persistent_data_for_sqlite'))
if not os.path.exists(PERSISTENT_STORAGE_PATH) and DEBUG:
    try:
        os.makedirs(PERSISTENT_STORAGE_PATH, exist_ok=True)
    except OSError as e:
        print(f"Erro criando diretório de persistência: {e}")
        PERSISTENT_STORAGE_PATH = BASE_DIR

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(PERSISTENT_STORAGE_PATH, 'db.sqlite3'),
    }
}

# Aplicações
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    'grafo_app',  # Altere conforme o nome da sua app
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# URLs e WSGI
ROOT_URLCONF = 'projeto_grafo.urls'  # Substitua pelo nome da sua pasta do projeto
WSGI_APPLICATION = 'projeto_grafo.wsgi.application'

# Templates
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

# Validação de senha
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internacionalização
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# Arquivos estáticos e mídia
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles_collected')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(PERSISTENT_STORAGE_PATH, 'mediafiles')
if not os.path.exists(MEDIA_ROOT) and DEBUG:
    try:
        os.makedirs(MEDIA_ROOT, exist_ok=True)
    except OSError as e:
        print(f"Erro criando diretório de mídia: {e}")

# Campo ID padrão
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CSRF Trusted Origins
csrf_env = os.environ.get('DJANGO_CSRF_TRUSTED_ORIGINS')
if csrf_env:
    CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in csrf_env.split(',')]
elif render_hostname:
    CSRF_TRUSTED_ORIGINS = [f'https://{render_hostname}']
else:
    CSRF_TRUSTED_ORIGINS = []

# Logs úteis
print(f"DEBUG: {DEBUG}")
print(f"ALLOWED_HOSTS: {ALLOWED_HOSTS}")
print(f"Database: {DATABASES['default']['NAME']}")
print(f"CSRF_TRUSTED_ORIGINS: {CSRF_TRUSTED_ORIGINS}")
