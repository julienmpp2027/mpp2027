from django.views.generic import TemplateView


class LandingPageView(TemplateView):
    # On dit à la vue d'utiliser ce template (qu'on va créer)
    template_name = 'core/landing_page.html'
