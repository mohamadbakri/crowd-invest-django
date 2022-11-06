from django.contrib.auth.models import User
# from account.models import Profile
#   function to check whether the input is an email address or not

import re


def is_email(email):
    regex = re.compile(
        '^([a-zA-Z0-9\-\.\_])+@([a-zA-Z0-9\-\.\_])+\.([a-zA-Z0-9]{2,4})$')
    return regex.match(email)


class EmailAuthBackend:
    """
    Authenticate using an e-mail address.
    """

    def authenticate(self, request, username=None, password=None):
        try:
            if is_email(username):
                user = User.objects.get(email=username)
            # Removing else only registration by email is valid
            else:
                user = User.objects.get(username=username)
            if user.check_password(password):
                return user
            return None
        except (User.DoesNotExist, User.MultipleObjectsReturned):
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


def create_profile(backend, user, *args, **kwargs):
    """
    Create user profile for social authentication
    """
    Profile.objects.get_or_create(user=user)
