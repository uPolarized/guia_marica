# Em projeto_grafo/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from grafo_app import views as grafo_app_views # <<< ADICIONE ESTA LINHA para importar as views da sua app

urlpatterns = [
    path('admin/', admin.site.urls),
    path('grafo/', include('grafo_app.urls')), # Sua app continua acessível em /grafo/
    path('', grafo_app_views.home, name='site_home'),  # <<< ADICIONE ESTA LINHA para o caminho raiz
]

# As linhas abaixo para servir arquivos de mídia e estáticos são apenas para DESENVOLVIMENTO (DEBUG=True).
# Em produção no Render, o WhiteNoise (para estáticos) e uma estratégia para mídia (ex: disco persistente + configuração no servidor web, ou serviço de nuvem) são necessários.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # A linha abaixo para servir STATIC_ROOT com runserver é geralmente desnecessária
    # se 'django.contrib.staticfiles' estiver em INSTALLED_APPS, pois o runserver já faz isso
    # para os diretórios estáticos das apps e definidos em STATICFILES_DIRS.
    # WhiteNoise também pode servir estáticos em desenvolvimento se configurado.
    # urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) # Pode remover se usar WhiteNoise ou o default do runserver.