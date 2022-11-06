"""crowdfunding URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from .views import *
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', home, name="home"),
    path('campaigns/', campaigns, name="campaigns"),
    path('single_campaign/<int:project_id>',
         single_campaign, name="single_campaign"),
    path('create_campaign/', create_campaign, name="create_campaign"),
    path('delete_campaign/<int:campaign_id>',
         delete_campaign, name="delete_campaign"),
    path('invest/<int:project_id>',
         invest, name="invest"),
    path('search/', search_campaigns, name="search_campaigns"),
    path('rate/<int:project_id>/<int:rating>/', rate, name='rate_project'),
    path('report/<int:campaign_id>', report_campaign, name='report_campaign'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
