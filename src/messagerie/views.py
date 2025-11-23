from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Message
from .forms import MessageInterneForm
from django.db.models import Q  # Pour des requêtes plus complexes si besoin

login_required


@login_required
def boite_reception(request):
    # 1. Récupération
    discussions_qs = Message.objects.filter(
        (Q(destinataire=request.user) | Q(expediteur=request.user)),
        parent__isnull=True
    )

    # 2. Tri et Pré-calcul du statut "Non lu"
    discussions = sorted(
        discussions_qs,
        key=lambda m: m.get_last_message_date(),
        reverse=True
    )

    # --- AJOUT MAGIQUE ---
    # On ajoute un attribut 'is_unread' à chaque objet discussion AVANT de l'envoyer au template
    for disc in discussions:
        disc.is_unread = disc.is_thread_unread(request.user)

    return render(request, 'messagerie/inbox.html', {'discussions': discussions})


@login_required
def lire_message(request, pk):
    message = get_object_or_404(Message, pk=pk)

    # Sécurité
    if request.user != message.destinataire and request.user != message.expediteur:
        # On vérifie aussi si c'est une réponse d'une conversation où on est
        if message.parent and (
                request.user == message.parent.destinataire or request.user == message.parent.expediteur):
            pass  # C'est bon
        else:
            messages.error(request, "Accès interdit.")
            return redirect('messagerie:inbox')

    # Si c'est une réponse, on redirige vers le parent pour voir toute la conversation
    if message.parent:
        return redirect('messagerie:lire', pk=message.parent.pk)

    # --- MISE À JOUR DU STATUT "LU" ---

    # 1. On marque le message racine si je suis le destinataire
    if request.user == message.destinataire and not message.lu:
        message.lu = True
        message.save()

    # 2. On marque TOUTES les réponses non lues de ce fil destinées à moi
    # C'est cette ligne qui met à jour votre compteur rouge dans la navbar
    message.reponses.filter(destinataire=request.user, lu=False).update(lu=True)

    # ----------------------------------

    # Récupérer toutes les réponses (du plus vieux au plus récent, style chat)
    reponses = message.reponses.all().order_by('date_envoi')

    # Formulaire de réponse
    if request.method == 'POST':
        contenu = request.POST.get('contenu_reponse')
        if contenu:
            # On crée la réponse
            Message.objects.create(
                expediteur=request.user,
                # L'autre personne est le destinataire
                destinataire=message.expediteur if request.user == message.destinataire else message.destinataire,
                sujet=f"Re: {message.sujet}",
                contenu=contenu,
                parent=message  # ON LIE AU MESSAGE PARENT
            )
            messages.success(request, "Réponse envoyée !")
            return redirect('messagerie:lire', pk=message.pk)

    return render(request, 'messagerie/detail.html', {'message': message, 'reponses': reponses})

@login_required
def nouveau_message(request):
    # 1. On regarde si l'URL contient un paramètre "to" (ex: /nouveau/?to=5)
    destinataire_id = request.GET.get('to')

    if request.method == 'POST':
        form = MessageInterneForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.expediteur = request.user
            msg.save()
            messages.success(request, "Message envoyé !")
            return redirect('messagerie:inbox')
    else:
        # 2. Si on a un ID dans l'URL, on prépare les données initiales
        initial_data = {}
        if destinataire_id:
            initial_data['destinataire'] = destinataire_id

        # On crée le formulaire avec ces données pré-remplies
        form = MessageInterneForm(initial=initial_data)

    return render(request, 'messagerie/form.html', {'form': form})