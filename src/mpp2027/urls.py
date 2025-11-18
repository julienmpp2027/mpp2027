"""
URL configuration for mpp2027 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', include('core.urls', namespace='core')),
    path('admin/', admin.site.urls),
    # On branche les URLs nécessaires pour CKEditor 5
    path('ckeditor5/', include('django_ckeditor_5.urls')),
    # Donne à allauth le contrôle sur 'accounts/login', 'accounts/logout',
    # 'accounts/google/login', etc.
    path('accounts/', include('allauth.urls')),
    path('blog/', include('blog.urls', namespace='blog')),
    path('comptes/', include('users.urls', namespace='users')),
]
"""
# Ne faites ceci qu'en mode DEBUG (JUSTE POUR DEVELOPPEMENT)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
"""

