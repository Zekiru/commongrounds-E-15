from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied


class RoleRequiredMixin(UserPassesTestMixin):
    required_role = None

    def has_required_role(self):
        user = self.request.user
        return (
            user.is_authenticated and
            hasattr(user, 'profile') and
            user.profile.role == self.required_role
        )

    def test_func(self):
        return self.has_required_role()

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            raise PermissionDenied
        return super().handle_no_permission()
