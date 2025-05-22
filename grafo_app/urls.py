# D:\projeto-grafo\grafo_app\urls.py
from django.urls import path
from . import views # Importa as views do próprio aplicativo

urlpatterns = [
    # Esta linha diz: se a URL for vazia (ex: /grafo/ ), chame a função views.home
    path('', views.home, name='home'),
]