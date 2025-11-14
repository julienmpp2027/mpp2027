from django.urls import path
from .views import (ArticleListView, ArticleDetailView, CategorieArticleListView, AuteurProfileView,
                    article_create_view, ArticleUpdateView,contact_view)


# On donne un "espace de nom" à notre app
# C'est une bonne pratique pour plus tard
app_name = 'blog'

urlpatterns = [
    # Quand on arrive à la racine de l'app (ex: /blog/)...
    # ... on lance la fonction "liste_articles" de nos vues.
    # Le 'name' nous permet de l'appeler par son nom (très utile)
    path('', ArticleListView.as_view(), name='liste-articles'),
    path('ecrire/', article_create_view, name='article-create'),
    path('categorie/<slug:slug_categorie>/', CategorieArticleListView.as_view(), name='articles-par-categorie'),
    path('auteur/<int:pk>/', AuteurProfileView.as_view(), name='auteur-profil'),
    path('modifier/<slug:slug>/', ArticleUpdateView.as_view(), name='article-update'),
    path('contact/', contact_view, name='contact'),
    path('<slug:slug>/', ArticleDetailView.as_view(), name='detail-article'),

]