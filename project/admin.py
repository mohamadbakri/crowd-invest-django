from django.contrib import admin
from .models import Project, ProjectDonator, CampaignImages, Rating, CampaignReport
# Register your models here.


admin.site.register(Project)
admin.site.register(ProjectDonator)
admin.site.register(CampaignImages)
admin.site.register(Rating)
admin.site.register(CampaignReport)
