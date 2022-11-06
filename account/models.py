from django.db import models
from django.conf import settings
from django.urls import reverse

from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE)

    is_email_verified = models.BooleanField(default=False)
    date_of_birth = models.DateField(blank=True, null=True)
    phone = models.CharField(max_length=15, verbose_name='phone')
    country = models.CharField(
        max_length=20, blank=True, default='',  verbose_name='country')
    photo = models.ImageField(
        upload_to='users/', blank=True, default='default/avatar.jpeg',)

    def __str__(self):
        return f'Profile of {self.user.first_name + " " + self.user.last_name}'

    def get_absolute_url(self):
        return reverse('profile_show')


@receiver(post_save, sender=User)
def update_profile_signal(sender, instance, created, **kwargs):
    if instance.username != 'admin':
        if created:
            Profile.objects.update_or_create(
                user=instance, photo='users/{0}.jpg'.format(instance.username))
        instance.profile.save()
