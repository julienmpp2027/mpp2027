from django.urls import path
from . import views

app_name = 'simulateur'

urlpatterns = [
    # Page d'accueil (Le Hub)
    path('', views.accueil, name='accueil'),

    # Simulateur Retraite
    path('retraite/', views.index, name='retraite'),
    path('api/calcul-retraite/', views.api_calcul, name='api_calcul'),

    # Simulateur Pouvoir d'Achat
    path('pouvoir-achat/', views.index_pa, name='pouvoir_achat'),
    path('api/calcul-pa/', views.api_calcul_pa, name='api_calcul_pa'),
]