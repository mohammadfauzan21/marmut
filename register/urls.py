from django.urls import path
from register.views import registerkonten, registerlabel, registeruser

app_name = 'register'
urlpatterns = [
    path('', registerkonten, name='registerkonten'),
    path('registerlabel/', registerlabel, name='registerlabel'),
    path('registeruser/', registeruser, name='registeruser'),
]
