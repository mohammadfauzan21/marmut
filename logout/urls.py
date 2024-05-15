from django.urls import path
from logout.views import logoutkonten

app_name = 'logout'
urlpatterns = [
    path('logout/', logoutkonten, name='logoutkonten'),
]
