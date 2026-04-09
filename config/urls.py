"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include, re_path
from django.views.static import serve
from django.contrib.auth import views as auth_views
from dashboard import views as dashboard_views
from django.http import HttpResponse

def google_verification(request):
    return HttpResponse("google-site-verification: googlee5ed8ef3b84d5965.html", content_type="text/html")

urlpatterns = [
    path('management-console/', admin.site.urls), # Renamed admin for security
    path('dashboard/', include('dashboard.urls')),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='dashboard/login.html'), name='login'),
    path('accounts/logout/', dashboard_views.logout_view, name='logout'),
    
    path('', include('core.urls')),
    path('contact/', include('contact.urls')),
    path('publications/', include('publications.urls')),
    path('googlee5ed8ef3b84d5965.html', google_verification),
]

# Serve media files in all environments
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {
            'document_root': settings.MEDIA_ROOT,
        }),
    ]
