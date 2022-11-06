
# Get all users authenticated list in django
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model  # Required to get user_id
from django.db.models import Q  # Query required to find email or user


class Email_OR_Username(BaseBackend):
    # Get user by user_id
    def get_user(self, user_id):
        try:
            return get_user_model().objects.get(pk=user_id)
        except get_user_model().DoesNotExist:
            return None
    # Authentication (email or username)

    def authentication(self, request, username=None, password=None):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(
                Q(username__iexact=username) | Q(email__iexact=username))
            if user.check_password(password):
                return user
        except UserModel.DoseNotExist:
            return None
