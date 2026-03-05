from django.urls import path

from paasify.views.NavigationViews import index
from security.views.SecurityViews import login, logout

app_name = "paasify"

urlpatterns = [
    path("login/", login, name="login"),
    path("logout/", logout, name="logout"),
    path("", index, name="index"),
]
