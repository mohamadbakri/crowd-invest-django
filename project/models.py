from django.db import models
from django.db.models import Sum, Avg
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import timedelta
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

# from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone
# from django.utils.translation import ugettext as _
from taggit.managers import TaggableManager

from django.contrib.contenttypes.fields import GenericRelation
from comment.models import Comment

from django.urls import reverse


def in_fourteen_days():
    return timezone.now() + timedelta(days=14)


# Create your models here.
# blog/models.py

class Project(models.Model):

    CATEGORIES = (
        ('MD', 'Medical'),
        ('EM', 'Emergency'),
        ('ED', 'Education'),
    )

    # slug = models.SlugField(max_length=250)
    title = models.CharField(max_length=250)
    details = models.TextField(max_length=1000)
    target = models.PositiveIntegerField()
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, default=None, related_name="campaigns")
    category = models.CharField(max_length=2, choices=CATEGORIES)
    tags = TaggableManager(blank=True)
    publish_date = models.DateTimeField(auto_now_add=True)
    campaign_start_date = models.DateTimeField(default=timezone.now)
    campaign_end_date = models.DateTimeField(default=in_fourteen_days)
    is_featured = models.BooleanField(default=False)
    donators = models.ManyToManyField(
        User, through='ProjectDonator', related_name='donations')
    # slug = models.SlugField(unique=True)
    comments = GenericRelation(Comment)

    class Meta:
        ordering = ['publish_date']
        # indexes = [
        #     models.Index(fields=['-publish']),
        # ]

    def clean(self):
        if (self.is_featured == True and Project.objects.filter(is_featured=True).exclude(id=self.id).count() >= 5):
            raise ValidationError(
                {'is_featured': _('You already have five featured campaigns.')})

    def get_absolute_url(sllf):
        return reverse('single_campaign', kwargs={'slug': self.slug})

    def average_rating(self) -> float:
        return Rating.objects.filter(project=self).aggregate(Avg("rating"))["rating__avg"] or 0

    def sum_rating(self) -> int:
        return Rating.objects.filter(project=self).aggregate(Sum("rating"))["rating__sum"] or 0

    @property
    def get_duration(self):
        dt = self.campaign_end_date - self.campaign_start_date
        # with dt you can get days and seconds and you can covert or format in week or hours whatever you want
        q, mod = divmod(dt.days, 30)
        return f'{q}m, {mod}d'    # returns number of days

    def __str__(self):
        # return f"{self.id}: {self.average_rating()}:  {self.sum_rating()}"
        # return f"{self.author.first_name}: {self.title}: {self.average_rating()}:  {self.sum_rating()}"
        return f"{ self.title}: {self.average_rating()}:  {self.sum_rating()}"


class CampaignImages(models.Model):
    poroject = models.ForeignKey(
        Project, on_delete=models.CASCADE, default=None, related_name="gallary")
    # images = models.ImageField(upload_to='image_filename',verbose_name='Image')
    images = models.ImageField(null=False, blank=False)

    def __str__(self):
        return str(self.poroject.title + ' images')


class ProjectDonator(models.Model):
    donator = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    donation_value = models.FloatField(null=True, blank=True)

    def __str__(self):
        return str(self.project.title + self.donator.first_name)
# class Meta:
#     unique_together = ('donator', 'project')


class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.project.title}: {self.rating}"


class CampaignReport(models.Model):
    details = models.TextField(max_length=2000)

    campaign = models.ForeignKey(Project, on_delete=models.CASCADE)
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, default=None)

    def __str__(self):
        return str(self.details)
