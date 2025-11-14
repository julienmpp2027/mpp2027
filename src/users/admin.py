from django.contrib import admin

# Register your models here.

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    # C'est la config de l'admin
    model = CustomUser

    # Quels champs afficher dans la liste des utilisateurs
    list_display = ('email', 'pseudo', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_active', 'date_joined')

    # Quels champs pour la création/modification
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Infos Personnelles', {'fields': ('pseudo', 'description', 'profile_picture')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Dates Importantes', {'fields': ('last_login', 'date_joined')}),
    )

    # Champs de recherche
    search_fields = ('email', 'pseudo')
    ordering = ('email',)


# On "enregistre" notre modèle avec sa config
admin.site.register(CustomUser, CustomUserAdmin)