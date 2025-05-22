from django.contrib import admin
from django.urls import path, include
from django.conf import settings # Importe settings
from django.conf.urls.static import static # Importe static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('grafo/', include('grafo_app.urls')), # ESTA LINHA É CRUCIAL!
]

# Adicione estas linhas para servir arquivos de mídia e estáticos durante o desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # A linha abaixo é útil para servir arquivos estáticos de apps
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)