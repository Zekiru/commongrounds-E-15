from functools import wraps
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied


def role_required(role_code):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')

            if not hasattr(request.user, 'profile') or (
                request.user.profile.role != role_code
            ):
                raise PermissionDenied

            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
