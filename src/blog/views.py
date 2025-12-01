from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib import messages
from django.views.generic import ListView, UpdateView, DetailView
from hitcount.views import HitCountDetailView
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import Article, Commentaire, Categorie
from .forms import CommentaireForm, ArticleForm, ContactForm
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from messagerie.models import Message
from users.models import CustomUser
from django.core.paginator import Paginator


# =============================================================================
#                AFFICHE TOUS LES ARTICLES PUBLIES
# =============================================================================
class ArticleListView(ListView):
    """
    C'est notre nouvelle vue pour la liste des articles.
    Elle hérite de la classe 'ListView' de Django.
    """

    # 1. Quel modèle doit-on lister ?
    # (ListView s'occupe de faire 'Article.objects.all()' pour nous)
    model = Article

    # 2. Quel template HTML doit-on utiliser ?
    template_name = 'blog/liste_articles.html'

    # 3. Sous quel nom la liste doit-elle être envoyée au template ?
    # (Si on ne met pas ça, Django l'appelle 'object_list' par défaut)
    context_object_name = 'articles'

    # Django va maintenant automatiquement couper la liste
    # en pages de 5 articles.
    paginate_by = settings.BLOG_ARTICLES_PAR_PAGE

    # 4. LA PARTIE LA PLUS IMPORTANTE :
    # Par défaut, ListView prend TOUS les articles.
    # On veut surcharger ça pour ne prendre QUE les 'PUBLISHED'.
    def get_queryset(self):
        """
        Cette fonction remplace notre 'Article.objects.filter(...)'.
        Elle retourne la liste d'objets que l'on veut VRAIMENT afficher.
        """
        # On récupère le queryset de base (qui est Article.objects.all())
        # et on lui applique notre filtre.
        return Article.objects.filter(statut=Article.Status.PUBLISHED)

    def get_context_data(self, **kwargs):
        """
        Enrichit le contexte pour envoyer des données supplémentaires au template.
        """
        context = super().get_context_data(**kwargs)

        # ANCIEN CODE (qui limitait) :
        # nb_articles_une = 7
        # context['articles_une'] = Article.objects.filter(...).order_by('est_a_la_une')[:nb_articles_une]

        # NOUVEAU CODE (Sans limite) :
        context['articles_une'] = Article.objects.filter(
            statut=Article.Status.PUBLISHED,
            est_a_la_une__isnull=False
        ).order_by('est_a_la_une')  # On a retiré le [:7] ou [:nb_articles_une] à la fin

        return context


# =============================================================================
#                AFFICHE UN SEUL ARTICLE
# =============================================================================
class ArticleDetailView(HitCountDetailView):
    """
    C'est la vue pour afficher UN SEUL article.
    """

    # Quel modèle ?
    model = Article

    # Quel template ? Si on ne précisait rien, Django chercherait 'article_detail.html'.
    template_name = 'blog/detail_article.html'

    # Sous quel nom l'envoyer au template ? Par défaut, c'est 'object'. On va utiliser 'article'.
    context_object_name = 'article'
    # pour compter les vues
    count_hit = True

    # Comment s'assurer qu'on ne voit pas les brouillons ?
    def get_queryset(self):
        """
        On retourne TOUT les article.
        La sécurité (brouillons visibles) sera gérée dans get_object().
        """
        return Article.objects.all()  # On cherche parmi TOUS les articles

    # Ajouter les commentaires au context envoyer au template

    def get_object(self, queryset=None):
        """
        On surcharge la méthode qui récupère l'objet
        pour y ajouter notre logique de sécurité.
        """
        #  On récupère l'article (publié OU brouillon) La méthode super() utilise le get_queryset() ci-dessus
        article = super().get_object(queryset)

        #  On vérifie la permission
        if article.statut == Article.Status.PUBLISHED:
            # C'est un article publié, tout le monde peut le voir.
            return article

        # Si on arrive ici, c'est un BROUILLON. On vérifie si le visiteur est l'auteur.
        if self.request.user == article.auteur:
            # C'est l'auteur ! On le laisse voir son brouillon.
            return article

        # C'est un brouillon, et le visiteur N'EST PAS l'auteur. On lève l'erreur 404 nous-mêmes.
        raise Http404("Cet article n'est pas publié et vous n'êtes pas son auteur.")

    def get_context_data(self, **kwargs):
        """
        Cette fonction est appelée pour préparer le 'dossier' de données
        (le context) à envoyer au template.
        """

        # On appelle la fonction parente pour récupérer le contexte de base (qui contient déjà notre 'article')
        context = super().get_context_data(**kwargs)

        # On récupère l'objet 'article' que la vue a déjà chargé
        article = self.get_object()

        #  On ajoute l'URL absolue pour le partage social.
        absolute_url = self.request.build_absolute_uri(article.get_absolute_url())
        context['absolute_url'] = absolute_url

        # On récupère les ID des catégories de l'article actuel
        cat_ids = article.categories.values_list('id', flat=True)

        # On cherche des articles publiés qui ont au moins une de ces catégories
        # On EXCLUT l'article actuel (.exclude(id=article.id))
        # On prend les 3 premiers distincts (.distinct()[:3])
        context['articles_suggeres'] = Article.objects.filter(
            categories__in=cat_ids,
            statut=Article.Status.PUBLISHED
        ).exclude(id=article.id).distinct()[:3]

        # On construit l'URL de l'image pour la carte
        if article.image_banniere:
            absolute_image_url = self.request.build_absolute_uri(
                article.image_banniere.url
            )
            context['absolute_image_url'] = absolute_image_url
        else:
            # Si pas d'image, on ne l'envoie pas.
            # On pourrait mettre une image par défaut plus tard.
            context['absolute_image_url'] = None

        # On utilise notre "related_name" pour trouver les commentaires
        # On filtre pour ne garder QUE ceux qui sont approuvés
        # (Le 'ordering' est déjà géré par notre 'Meta' dans models.py)
        commentaires = article.commentaires.filter(approuve=True)

        # On ajoute ces commentaires au dossier 'context'
        context['commentaires'] = commentaires

        # On ajoute une instance VIERGE de notre formulaire au contexte que le template pourra afficher.
        # On vérifie aussi si un formulaire invalide a été "passé" par la méthode POST, pour ré-afficher les erreurs.
        if 'comment_form' not in context:
            context['comment_form'] = CommentaireForm()
        # On renvoie le dossier complet
        return context

    def post(self, request, *args, **kwargs):
        """
        Cette fonction est appelée quand le navigateur envoie
        une requête POST (c'est-à-dire quand on soumet le formulaire).
        """

        # D'abord, on doit vérifier que l'utilisateur est connecté.
        # S'il ne l'est pas, on le jette.
        if not request.user.is_authenticated:
            # On pourrait rediriger vers la page de login,
            # mais pour l'instant, on interdit.
            return redirect('blog:liste-articles')  # Changez si vous avez un login

        # On récupère l'article en cours (celui qu'on commente)
        # 'self.get_object()' est la magie de DetailView
        article = self.get_object()

        # On crée une instance de notre formulaire et on la remplit
        # avec les données de la requête POST
        form = CommentaireForm(request.POST)

        if form.is_valid():
            # Le formulaire est valide !
            # On crée un objet Commentaire, mais on ne le sauvegarde PAS encore dans la base de données (commit=False).
            nouveau_commentaire = form.save(commit=False)

            # On doit "remplir les trous" que le formulaire ne connaît pas :
            nouveau_commentaire.article = article  # L'article, c'est celui de la page
            nouveau_commentaire.auteur = request.user  # L'auteur, c'est l'utilisateur connecté

            # Maintenant, on peut sauvegarder.
            nouveau_commentaire.save()

            # C'est une bonne pratique de rediriger après un POST réussi.
            # On redirige vers la page de l'article sur laquelle on est.
            # 'article.slug' est passé à l'URL 'blog:detail-article'
            return redirect('blog:detail-article', slug=article.slug)
        else:
            # Le formulaire n'est PAS valide (ex: champ vide)
            # On doit ré-afficher la page de détail.
            # Mais cette fois, on va lui passer le formulaire 'form'
            # (qui contient maintenant les messages d'erreur).

            # On récupère le contexte (comme dans get_context_data)
            context = self.get_context_data(**kwargs)
            # On remplace le formulaire vide par le formulaire invalide
            context['comment_form'] = form

            # Et on ré-affiche le template avec les erreurs.
            return self.render_to_response(context)


# =============================================================================
#                LISTE DES ARTICLES PAR CATÉGORIE
# =============================================================================
class CategorieArticleListView(ListView):
    """
    Vue pour afficher tous les articles (publiés)
    d'une catégorie spécifique.
    """
    model = Article
    template_name = 'blog/categorie_list.html'
    context_object_name = 'articles'
    paginate_by = settings.BLOG_ARTICLES_PAR_PAGE

    def get_queryset(self):
        """
        Filtre les articles par catégorie et gère le cas spécial 'programme'.
        """
        # 1. On récupère la catégorie et on la stocke dans self.categorie
        # (C'est indispensable pour que get_context_data puisse la récupérer ensuite)
        self.categorie = get_object_or_404(Categorie, slug=self.kwargs['slug_categorie'])

        # 2. Liste de base : Articles de la catégorie + Publiés
        queryset = Article.objects.filter(
            categories=self.categorie,
            statut=Article.Status.PUBLISHED
        )

        # 3. Filtre spécial pour la page "Programme"
        if self.categorie.slug == 'programme':
            # On ne garde que ceux qui ont une position définie et on trie
            queryset = queryset.filter(est_a_la_une__isnull=False).order_by('est_a_la_une')

        return queryset

    def get_context_data(self, **kwargs):
        """
        C'est cette méthode qui envoie la variable 'categorie' au template HTML.
        Sans elle, le titre reste vide !
        """
        context = super().get_context_data(**kwargs)
        # On passe l'objet catégorie (sauvegardé plus haut) au template
        context['categorie'] = self.categorie
        return context


# =============================================================================
#                LISTE DE TOUS LES ARTICLES (anté-chronologique)
# =============================================================================
class ToutesActualitesView(ListView):
    """
    Affiche TOUS les articles publiés, par ordre chronologique.
    (Page 'Actualités')
    """
    model = Article
    template_name = 'blog/all_articles.html'  # Nouveau template
    context_object_name = 'articles'
    paginate_by = settings.BLOG_ARTICLES_PAR_PAGE

    def get_queryset(self):
        # On prend tout ce qui est publié, du plus récent au plus vieux
        return Article.objects.filter(statut=Article.Status.PUBLISHED).order_by('-date_creation')


# =============================================================================
#            PROFIL PUBLIC D'UN AUTEUR
# =============================================================================
class AuteurProfileView(DetailView):
    """
    Affiche la page de profil publique d'un auteur,
    avec la liste de ses articles et commentaires.
    """

    # 1. Le modèle qu'on consulte
    model = CustomUser

    # 2. Le template qu'on va créer
    template_name = 'blog/auteur_profil.html'

    # 3. Le nom de la variable dans le template
    #    (Par défaut, ce serait 'object' ou 'customuser')
    context_object_name = 'auteur'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        auteur = self.get_object()
        is_owner = (self.request.user == auteur)

        # 1. RÉCUPÉRATION ET TRI (Plus récent au plus ancien)
        if is_owner:
            qs_articles = Article.objects.filter(auteur=auteur).order_by('-date_creation')
        else:
            qs_articles = Article.objects.filter(auteur=auteur, statut=Article.Status.PUBLISHED).order_by(
                '-date_creation')

        qs_comments = Commentaire.objects.filter(auteur=auteur, approuve=True).order_by('-date_creation')

        qs_comments = Commentaire.objects.filter(
            auteur=auteur,
            approuve=True,
            article__statut=Article.Status.PUBLISHED
        ).order_by('-date_creation')
        # 2. PAGINATION ARTICLES (5 par page)
        # On regarde si l'URL contient ?page_articles=2
        paginator_art = Paginator(qs_articles, 5)
        page_num_art = self.request.GET.get('page_articles')
        page_articles = paginator_art.get_page(page_num_art)

        # 3. PAGINATION COMMENTAIRES (5 par page)
        # On regarde si l'URL contient ?page_comments=2
        paginator_com = Paginator(qs_comments, 5)
        page_num_com = self.request.GET.get('page_comments')
        page_comments = paginator_com.get_page(page_num_com)

        # 4. ENVOI AU TEMPLATE
        context['page_articles'] = page_articles
        context['page_comments'] = page_comments
        context['is_owner'] = is_owner

        # On envoie aussi les "counts" globaux pour les stats de la sidebar
        context['total_articles'] = qs_articles.count()
        context['total_comments'] = qs_comments.count()
        # les 3 derniers commentaires, quelle que soit la page consultée.
        context['sidebar_comments'] = qs_comments[:3]
        return context


# =============================================================================
#                               CRÉER UN ARTICLE
# =============================================================================

@login_required  # L'utilisateur DOIT être connecté (ça, ça ne change pas)
def article_create_view(request):
    """
    Gère la création d'un nouvel article par N'IMPORTE QUEL
    utilisateur connecté. L'article est FORCÉ en "Brouillon".
    """

    # Logique du formulaire
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            # On appelle notre nouvelle méthode save()
            # et on lui passe l'utilisateur connecté
            article = form.save(commit=True, user=request.user)
            return redirect(article.get_absolute_url())
    else:

        form = ArticleForm()

    context = {
        'form': form
    }
    return render(request, 'blog/article_form.html', context)


# =============================================================================
#                          MODIFIER UN ARTICLE
# =============================================================================
class ArticleUpdateView(LoginRequiredMixin, UpdateView):
    """
    Vue "Classe" pour modifier un article (brouillon)
    existant depuis le frontend.
    """
    model = Article
    form_class = ArticleForm  # On réutilise notre formulaire !
    template_name = 'blog/article_form.html'  # On réutilise aussi ce template !

    def get_queryset(self):
        """
        Sécurité : On ne peut modifier que SES PROPRES articles.
        On ne peut pas modifier les articles des autres.
        """
        return Article.objects.filter(auteur=self.request.user)

    def get_context_data(self, **kwargs):
        """On ajoute un titre à la page"""
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Modifier mon article'
        return context

    def form_valid(self, form):
        """
        Appelé quand le formulaire est valide. On s'assure que l'auteur est bien l'utilisateur
        et que le statut reste "Brouillon".
        """
        article = form.save(commit=False, user=self.request.user)
        # (Notre méthode save() force déjà le statut DRAFT, c'est parfait)
        article.save()
        form.save_m2m()
        return redirect(article.get_absolute_url())


# =============================================================================
#                              PAGE DE CONTACT
# =============================================================================
# ancienne configuration avec gmail
"""def contact_view(request):
   
    Gère la page de contact et l'envoi d'email.
    
    if request.method == 'POST':
        # Le formulaire a été soumis
        form = ContactForm(request.POST)

        if form.is_valid():
            # Le formulaire est valide, on récupère les données
            nom = form.cleaned_data['nom']
            email_expediteur = form.cleaned_data['email']
            sujet = form.cleaned_data['sujet']
            message = form.cleaned_data['message']

            # On prépare l'email
            try:
                # On formate le message
                html_message = render_to_string('blog/email_template_contact.html', {
                    'nom': nom,
                    'email_expediteur': email_expediteur,
                    'sujet': sujet,
                    'message': message,
                })

                send_mail(
                    f"Nouveau message de contact : {sujet}",  # Sujet de l'email que VOUS recevez
                    '',  # Le message texte (on utilise le HTML)
                    settings.DEFAULT_FROM_EMAIL,  # L'expéditeur (configuré dans settings.py)
                    [settings.ADMIN_EMAIL],  # Le destinataire (VOUS !)
                    html_message=html_message  # Le message au format HTML
                )

                messages.success(request, 'Votre message a bien été envoyé ! Nous vous répondrons bientôt.')
                return redirect('blog:liste-articles')  # Redirige vers l'ACCUEIL

            except Exception as e:
                # Gérer une erreur d'envoi d'email
                messages.error(request, "Une erreur est survenue lors de l'envoi de votre message. Veuillez réessayer.")
                print(f"Erreur d'envoi d'email : {e}")  # Pour le débogage

    else:
        # C'est une visite normale (GET), on vérifie qui est là
        initial_data = {}  # On prépare un dictionnaire
        if request.user.is_authenticated:
            # Si l'utilisateur est connecté, on pré-remplit !
            initial_data['nom'] = request.user.pseudo or request.user.email
            initial_data['email'] = request.user.email

        # On crée le formulaire, en lui passant les données initiales
        form = ContactForm(initial=initial_data)

    context = {'form': form}
    return render(request, 'blog/contact.html', context) """


# config avec messagerie interne
# =============================================================================
#                              PAGE DE CONTACT (VERSION MESSAGERIE INTERNE)
# =============================================================================
def contact_view(request):
    """
    Gère la page de contact.
    Au lieu d'envoyer un email SMTP, on crée un Message interne
    destiné à l'administrateur du site.
    """
    if request.method == 'POST':
        form = ContactForm(request.POST)

        if form.is_valid():
            # 1. Récupération des données du formulaire
            nom = form.cleaned_data['nom']
            email_guest = form.cleaned_data['email']
            sujet = form.cleaned_data['sujet']
            contenu = form.cleaned_data['message']

            # 2. Qui est le destinataire ? (L'Admin Principal)
            # On cherche l'utilisateur avec votre email, ou le premier super-admin trouvé
            admin_user = CustomUser.objects.filter(email='julien.mpp2027@gmail.com').first()
            if not admin_user:
                admin_user = CustomUser.objects.filter(is_superuser=True).first()

            if admin_user:
                # 3. Création du message en base de données
                nouveau_message = Message(
                    destinataire=admin_user,
                    sujet=f"[Contact Site] {sujet}",  # On ajoute un préfixe pour repérer ces messages
                    contenu=contenu,
                    # Champs spécifiques pour les visiteurs non connectés
                    nom_guest=nom,
                    email_guest=email_guest
                )

                # Si l'utilisateur est connecté, on lie son compte (c'est plus propre)
                if request.user.is_authenticated:
                    nouveau_message.expediteur = request.user

                nouveau_message.save()

                messages.success(request, 'Votre message a bien été envoyé à l\'équipe !')
                return redirect('blog:liste-articles')

            else:
                # Cas rare : aucun admin n'existe dans la base
                messages.error(request, "Erreur : Aucun administrateur disponible pour recevoir le message.")

    else:
        # Pré-remplissage si l'utilisateur est connecté
        initial_data = {}
        if request.user.is_authenticated:
            initial_data['nom'] = request.user.pseudo or request.user.email
            initial_data['email'] = request.user.email

        form = ContactForm(initial=initial_data)

    context = {'form': form}
    return render(request, 'blog/contact.html', context)
