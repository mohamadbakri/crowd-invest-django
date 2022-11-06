
from .models import Profile
from requests import request, HTTPError
from django.core.files.base import ContentFile


def save_profile_picture(backend, user, response, details, is_new=False, *args, **kwargs):
    # Save Facebook profile photo into a user profile, assuming a profile model
    # with a profile_photo file-type attribute
    if is_new and backend.name == 'facebook':
        # url = 'http://graph.facebook.com/{0}/picture'.format(response['id'])
        url = 'https://graph.facebook.com/{0}/picture/?type=large&access_token={1}'.format(
            response['id'], response['access_token'])
        try:
            response = request('GET', url, params={'type': 'large'})
            response.raise_for_status()
        except HTTPError:
            pass
        else:
            profile = Profile.objects.filter(user=user).first()
            profile.photo.save('{0}.jpg'.format(user.username),
                               ContentFile(response.content))
