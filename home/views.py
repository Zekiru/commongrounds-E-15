from django.views.generic import TemplateView


class HomeView(TemplateView):
    template_name = 'home.html'
    context_object_name = 'home'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
