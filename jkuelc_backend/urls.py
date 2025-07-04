"""
URL configuration for jkuelc_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.authtoken import views as token_views
from rest_framework.documentation import include_docs_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', token_views.obtain_auth_token),
    path('api/docs/', include_docs_urls(title='JKUELC Connect Hub API')),
    
    # App URLs
    path('api/users/', include('users.urls')),
    path('api/membership/', include('membership.urls')),
    path('api/blog/', include('blog.urls')),
    path('api/events/', include('events.urls')),
    path('api/gallery/', include('gallery.urls')),
    path('api/merchandise/', include('merchandise.urls')),
    path('api/payment/', include('payment.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
