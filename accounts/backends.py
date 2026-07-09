"""
Custom authentication backend.
Allows login with student_id instead of username.
US-02: ورود با شماره دانشجویی/کارمندی/استادی
"""

from django.contrib.auth.backends import BaseBackend
from .models import User


class StudentIDBackend(BaseBackend):
    """Authenticate using student_id and password."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(student_id=username)
            if user.check_password(password) and user.is_active:
                return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
