from django.urls import path
from register.views import registerkonten

app_name = 'register'
urlpatterns = [
    path('', registerkonten, name='registerkonten'),
]
