from django.urls import path
from login.views import loginkonten

app_name = 'login'
urlpatterns = [
    path('', loginkonten, name='loginkonten'),
]
