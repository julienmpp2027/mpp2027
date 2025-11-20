from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Message
from .forms import MessageInterneForm


@login_required
def boite_reception(request):
    # On récupère les messages où JE suis le destinataire
    messages_recus = Message.objects.filter(destinataire=request.user)
    return render(request, 'messagerie/inbox.html', {'messages_recus': messages_recus})


@login_required
def lire_message(request, pk):
    message = get_object_or_404(Message, pk=pk)

    # Sécurité : Seul le destinataire ou l'expéditeur peut lire
    if request.user != message.destinataire and request.user != message.expediteur:
        messages.error(request, "Vous n'avez pas accès à ce message.")
        return redirect('messagerie:inbox')

    # Si je suis le destinataire, je marque comme lu
    if request.user == message.destinataire and not message.lu:
        message.lu = True
        message.save()

    return render(request, 'messagerie/detail.html', {'message': message})


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