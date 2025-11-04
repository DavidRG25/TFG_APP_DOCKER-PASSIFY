from django.urls import path, include
from paasify.views.NavigationViews import *
from security.views.SecurityViews import *
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', login, name="login"),
    path('logout/', logout, name="logout"),
    path('', index, name="index"),

    # Agrega esta línea:
    path('containers/', include('containers.urls')),
]

# This resolves the admin namespace warning
admin.site.site_url = None
admin.site.site_header = 'PaaSify Administration'
admin.site.site_title = 'PaaSify Admin'