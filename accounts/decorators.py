from django.shortcuts import redirect
from django.http import Http404
from functools import wraps


def role_required(required_role):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            if not hasattr(request.user, 'profile'):
                return redirect('login')
            if request.user.profile.role != required_role:
                raise Http404('You do not have permission to view this page.')
            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator
