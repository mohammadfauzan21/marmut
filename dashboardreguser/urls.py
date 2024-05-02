from django.urls import path
from dashboardreguser.views import dashboarduser, kelolaplaylist, playsong, userplaylist

app_name = 'dashboardreguser'
urlpatterns = [
    path('', dashboarduser, name='dashboarduser'),
    path('kelolaplaylist/', kelolaplaylist, name='kelolaplaylist'),
    path('playsong/', playsong, name='playsong'),
    path('userplaylist/', userplaylist, name='userplaylist'),
]
