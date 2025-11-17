from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # La racine (/) pointera vers notre vue
    path('', views.LandingPageView.as_view(), name='landing-page'),
]