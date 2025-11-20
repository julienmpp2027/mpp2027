from django.urls import path
from . import views

app_name = 'messagerie'

urlpatterns = [
    path('', views.boite_reception, name='inbox'),
    path('lire/<int:pk>/', views.lire_message, name='lire'),
    path('nouveau/', views.nouveau_message, name='nouveau'),
]