from django.shortcuts import redirect
from django.views.generic import TemplateView
from .models import CommissionType, Commission


def index(request):
    return redirect('requests/')


class RequestListView(TemplateView):
    model = Commission
    template_name = 'commissions/request_list.html'
    context_object_name = 'request_list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['requests'] = Commission.objects.all()
        return context


class RequestDetailView(TemplateView):
    model = Commission
    template_name = 'commissions/request_detail.html'
    context_object_name = 'request_detail'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['request'] = Commission.objects.get(
            id=self.kwargs['pk']
        )
        return context
