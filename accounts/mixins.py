from django.shortcuts import redirect
from django.http import Http404


class RoleRequiredMixin():
    required_role = None

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not hasattr(request.user, 'profile'):
            return redirect('login')
        if request.user.profile.role != self.required_role:
            raise Http404('You do not have permission to view this page.')

        return super().dispatch(request, *args, **kwargs)
