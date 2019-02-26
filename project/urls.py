from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    #path('siteaccounts/', include('django.contrib.auth.urls')),
    #path('siteaccounts/', include('siteaccounts.urls')),
    path('', views.IndexFormView.as_view(), name='home'),
    path('user/', include('user_auth.urls')),
    path('user/', include('social_django.urls', namespace='social')),
]
