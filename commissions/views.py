from django.shortcuts import redirect
from django.views.generic import TemplateView
from .services import CommissionService


def index(request):
    return redirect('requests/')


class RequestListView(TemplateView):
    template_name = 'commissions/request_list.html'
    context_object_name = 'request_list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            context['requests'] = CommissionService.get_all_commissions()
        except Exception as e:
            print(f"Service Error: {str(e)}")

        return context


class RequestDetailView(TemplateView):
    template_name = 'commissions/request_detail.html'
    context_object_name = 'request_detail'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            context['request'] = CommissionService.get_commission(
                self.kwargs['pk']
            )
        except Exception as e:
            print(f"Service Error: {str(e)}")

        return context


# TO-DO: Add views for creating and updating requests

# class RequestCreateView(TemplateView):


# class RequestUpdateView(TemplateView):
