"""
URL configuration for prbmg project.

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
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from clustering.views import login_page, update_user, logout_user, home, signup_page, upload_file, download_file,dashboard_predictions

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/',login_page,name="login"),
    path("",home, name="home"),
    path("update_user/", update_user,name="update_user"),
    path('logout/', logout_user, name="logout"),
    path('signup/', signup_page,name="signup"), 
    path('clustering/', upload_file,name="clustering"),
    path('download/<str:file_path>/', download_file, name='download_file'),
    path('dashboard_predictions/', dashboard_predictions, name='dashboard_predictions'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

