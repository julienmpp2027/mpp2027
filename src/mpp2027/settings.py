import os
from pathlib import Path
from decouple import config
import certifi
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

# On lit la variable d'environnement 'ALLOWED_HOSTS'.
# Si elle n'existe pas (comme en local), on met '127.0.0.1' par défaut.
# La méthode .split(',') sépare notre "mpp2027.onrender.com,.onrender.com"
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='127.0.0.1,localhost').split(',')

# Application definition

INSTALLED_APPS = [
    'users.apps.UsersConfig',
    'blog.apps.BlogConfig',
    'core',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',

    'django.contrib.staticfiles',
    # --- BLOC POUR ALLAUTH ---
    'django.contrib.sites',  # Requis par allauth
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    # Le "fournisseur" spécifique qu'on veut
    'allauth.socialaccount.providers.google',
    # --- FIN DU BLOC ALLAUTH ---
    'django_ckeditor_5',
    'hitcount',
    'storages',
    'messagerie',
    'simulateur',
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
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'mpp2027.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'blog.context_processors.nav_links',
                'blog.context_processors.unread_messages_count',
            ],
        },
    },
]

WSGI_APPLICATION = 'mpp2027.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

# On crée une variable vide
DATABASES = {}

# On vérifie si on est en production (sur Render)
if 'DATABASE_URL' in os.environ:
    # Si oui, on utilise l'URL de la BDD de Render
    DATABASES['default'] = dj_database_url.config(
        conn_max_age=600,
        ssl_require=True  # Render exige une connexion SSL
    )
else:
    # Si non (on est en local), on utilise notre config habituelle
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'mpp2027_db',
        'USER': 'mpp2027_admin',
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': 'localhost',
        'PORT': '5432',
    }
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'mediafiles'

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

# mpp2027/src/mpp2027/settings.py

# ... (Après le reste de votre configuration)

# =============================================================================
# FICHIERS STATIQUES & MEDIAS (SÉPARATION LOCAL/PROD)
# RÉSOUD : Erreur "Invalid endpoint" en local.
# =============================================================================

# Configuration Statiques
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static', ]
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Configuration Médias (Chemin de base)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'mediafiles'

# --- 1. CONFIGURATION LOCALE PAR DÉFAUT (RÉSOUD LE CONFLIT) ---
# En l'absence d'autre instruction, Django utilise ceci (mode local)
STORAGES = {
    # DEFAULT STORAGE (MEDIA/UPLOADS) : Utilise le disque dur local
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    # STATICFILES : Utilise le stockage simple de Django pour le développement
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    }
}

# --- 2. OVERRIDE EN MODE PRODUCTION (RENDER) ---
if not DEBUG:
    # Variables B2/S3 (lues depuis l'environnement Render)
    AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_ENDPOINT_URL = config('AWS_S3_ENDPOINT_URL')

    # Paramètres B2
    AWS_S3_SIGNATURE_VERSION = 's3v4'
    AWS_DEFAULT_ACL = 'public-read'
    AWS_LOCATION = 'media'

    # Remplacement du MEDIA_URL par l'URL publique B2/S3
    MEDIA_URL = f'{AWS_S3_ENDPOINT_URL}/{AWS_STORAGE_BUCKET_NAME}/{AWS_LOCATION}/'

    # Remplacement du backend MEDIA (default) par B2/S3
    STORAGES["default"] = {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
        "OPTIONS": {
            "access_key": AWS_ACCESS_KEY_ID,
            "secret_key": AWS_SECRET_ACCESS_KEY,
            "bucket_name": AWS_STORAGE_BUCKET_NAME,
            "endpoint_url": AWS_S3_ENDPOINT_URL,
            "default_acl": 'public-read',
            "object_parameters": {
                'CacheControl': 'max-age=86400',
            },
        },
    }

    # Remplacement du backend STATICFILES par WhiteNoise (pour la production)
    STORAGES["staticfiles"] = {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    }

    # Règle le DEFAULT_FILE_STORAGE pour utiliser la config 'default' ci-dessus (B2)
    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

# =============================================================================
# FIN DE LA CONFIGURATION STOCKAGE
# =============================================================================


# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# =============================================================================
# GESTION DE L'AUTHENTIFICATION (DJANGO + ALLAUTH)
# =============================================================================

# 1. Moteur d'authentification
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]


# =============================================================================
# CONFIGURATION DJANGO-ALLAUTH (Version "Zéro Warning, cette fois c'est la bonne")
# =============================================================================

# 1. Comportement de connexion et d'inscription
ACCOUNT_LOGIN_METHODS = ['email']
ACCOUNT_SIGNUP_FIELDS = ['email']
ACCOUNT_EMAIL_VERIFICATION = 'optional'

# 2. Configuration de notre CustomUser (le plus important)
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_EMAIL_FIELD = 'email'

# 3. Nos adaptateurs
ACCOUNT_ADAPTER = 'users.adapter.MyAccountAdapter'
SOCIALACCOUNT_ADAPTER = 'users.adapter.MySocialAccountAdapter'

# On supprime la page de confirmation "Continue"
SOCIALACCOUNT_LOGIN_ON_GET = True
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        # 'SCOPE' est la liste des permissions que nous demandons à Google
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    }
}
# =============================================================================

# =============================================================================

# =============================================================================
# 2. Notre modèle utilisateur
AUTH_USER_MODEL = 'users.CustomUser'

# 3. Redirections (déclarées UNE SEULE FOIS)
LOGIN_REDIRECT_URL = 'blog:liste-articles'
LOGOUT_REDIRECT_URL = 'blog:liste-articles'

# =============================================================================
# AUTRES CONFIGURATIONS (BLOG, MEDIA, ETC.)
# =============================================================================

# Site ID pour allauth
SITE_ID = 1

# Pagination du blog
BLOG_ARTICLES_PAR_PAGE = 5

# =============================================================================
#                   CONFIGURATION DES EMAILS (PRODUCTION)
# =============================================================================

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')

# C'est l'email qui apparaîtra comme "expéditeur"
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
# C'est l'email qui recevra les messages de contact
ADMIN_EMAIL = config('ADMIN_EMAIL')
# ==============================================================================
# FIX POUR LE BUG DE CERTIFICAT SSL POSTGRESQL
# (Doit être à la fin pour s'exécuter après l'import de 'certifi')
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
os.environ['SSL_CERT_FILE'] = certifi.where()

# =============================================================================
#                   CONFIGURATION DE CKEDITOR 5
# =============================================================================

# On spécifie la langue (français)
CKEDITOR_5_CONFIGS = {
    'default': {
        'language': 'fr',
        'toolbar': [
            'heading', '|',
            'bold', 'italic', 'underline', 'link', '|',
            'fontColor', 'fontBackgroundColor', '|',
            'bulletedList', 'numberedList', 'alignment', '|',
            'outdent', 'indent', 'blockQuote', '|',
            'undo', 'redo'
        ],
    }
}

