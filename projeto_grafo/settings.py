# settings.py
import os
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent # Ajuste conforme sua estrutura

# DEBUG deve ser False em produção.
# Configure a variável de ambiente DJANGO_DEBUG="False" no Render.
DEBUG_STR = os.environ.get('DJANGO_DEBUG', 'True') # Default para True se não definida
DEBUG = DEBUG_STR.lower() in ('true', '1', 't', 'yes')

ALLOWED_HOSTS = []
render_hostname = os.environ.get('RENDER_EXTERNAL_HOSTNAME') # Injetado pelo Render

if render_hostname:
    ALLOWED_HOSTS.append(render_hostname)

# Lê hosts customizados da variável de ambiente DJANGO_ALLOWED_HOSTS
# Ex: DJANGO_ALLOWED_HOSTS="meusite.com,www.meusite.com"
django_allowed_hosts_env = os.environ.get('DJANGO_ALLOWED_HOSTS')
if django_allowed_hosts_env:
    ALLOWED_HOSTS.extend([host.strip() for host in django_allowed_hosts_env.split(',') if host.strip()])

if DEBUG:
    # Em desenvolvimento, adicione localhost e o host do Docker se estiver usando.
    ALLOWED_HOSTS.extend(['localhost', '127.0.0.1'])
    # Se você estiver rodando Docker localmente e acessando via um nome de serviço, adicione-o também.
    # Ex: ALLOWED_HOSTS.append('web')

# Garante que não haja duplicatas e remove entradas vazias se houver
ALLOWED_HOSTS = list(set(filter(None, ALLOWED_HOSTS)))

if not DEBUG and not ALLOWED_HOSTS:
    print("CRÍTICO: DEBUG=False e ALLOWED_HOSTS está vazio. A aplicação não iniciará.")
    print("Por favor, defina a variável de ambiente DJANGO_ALLOWED_HOSTS na sua plataforma de hospedagem (ex: Render).")
    # Em um cenário real, você pode querer levantar um ImproperlyConfiguredError aqui
    # from django.core.exceptions import ImproperlyConfigured
    # raise ImproperlyConfigured("ALLOWED_HOSTS não pode estar vazio em produção (DEBUG=False). Defina DJANGO_ALLOWED_HOSTS.")
    # Para permitir que suba para você ver os logs (NÃO FAÇA ISSO EM PRODUÇÃO REAL SEM SABER):
    # ALLOWED_HOSTS = ['*'] # Apenas para depuração extrema, remova isso o mais rápido possível.

print(f"DEBUG: ALLOWED_HOSTS configurado para: {ALLOWED_HOSTS}")
print(f"DEBUG: DEBUG está definido como: {DEBUG}")

# ... (resto do seu settings.py, incluindo SECRET_KEY, DATABASES, etc.) ...
# Certifique-se que SECRET_KEY também vem de uma variável de ambiente em produção.
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'fallback-inseguro-para-dev-troque-isto')

# ... (Configuração do DATABASES para SQLite usando PERSISTENT_STORAGE_PATH como discutido) ...
PERSISTENT_STORAGE_PATH = os.environ.get('PERSISTENT_STORAGE_PATH', os.path.join(BASE_DIR, 'local_persistent_data_for_sqlite'))
if not os.path.exists(PERSISTENT_STORAGE_PATH) and DEBUG: # Apenas cria em modo DEBUG se não existir
    try:
        os.makedirs(PERSISTENT_STORAGE_PATH, exist_ok=True)
        print(f"DEBUG: Criado diretório para persistência em {PERSISTENT_STORAGE_PATH}")
    except OSError as e:
        print(f"AVISO: Não foi possível criar o diretório de persistência {PERSISTENT_STORAGE_PATH}: {e}")
        PERSISTENT_STORAGE_PATH = BASE_DIR # Fallback

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(PERSISTENT_STORAGE_PATH, 'db.sqlite3'),
    }
}
if DEBUG:
    print(f"INFO: Usando banco de dados SQLite em: {DATABASES['default']['NAME']}")
if not DEBUG:
    print(f"AVISO: Usando SQLite em ambiente de produção (DEBUG=False).")
    print(f"Certifique-se que Gunicorn está com '--workers 1'. O caminho do banco é: {DATABASES['default']['NAME']}")

# ... (resto do seu settings.py: INSTALLED_APPS, MIDDLEWARE, STATIC_ROOT, etc.) ...
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic', # Para servir estáticos com runserver em DEBUG=True
    'django.contrib.staticfiles',
    'grafo_app', # Sua app
]

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

ROOT_URLCONF = 'projeto_grafo.urls' # Substitua 'projeto_grafo' pelo nome da sua pasta de projeto
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
WSGI_APPLICATION = 'projeto_grafo.wsgi.application' # Substitua 'projeto_grafo'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles_collected')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(PERSISTENT_STORAGE_PATH, 'mediafiles') # Mídia também no disco persistente
if not os.path.exists(MEDIA_ROOT) and DEBUG: # Apenas cria em modo DEBUG se não existir
    try:
        os.makedirs(MEDIA_ROOT, exist_ok=True)
    except OSError as e:
        print(f"AVISO: Não foi possível criar o diretório de mídia {MEDIA_ROOT}: {e}")


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CSRF_TRUSTED_ORIGINS
CSRF_TRUSTED_ORIGINS_ENV = os.environ.get('DJANGO_CSRF_TRUSTED_ORIGINS')
if CSRF_TRUSTED_ORIGINS_ENV:
    CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in CSRF_TRUSTED_ORIGINS_ENV.split(',') if origin.strip()]
elif render_hostname:
    CSRF_TRUSTED_ORIGINS = [f'https://{render_hostname}']
else:
    CSRF_TRUSTED_ORIGINS = [] # Deixe vazio se não houver, mas configure em produção