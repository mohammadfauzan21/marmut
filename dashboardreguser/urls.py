from django.urls import path
from dashboardreguser.views import dashboarduser, kelolaplaylist, playsong, userplaylist, chart

app_name = 'dashboardreguser'
urlpatterns = [
    path('', dashboarduser, name='dashboarduser'),
    path('kelolaplaylist/', kelolaplaylist, name='kelolaplaylist'),
    path('playsong/', playsong, name='playsong'),
    path('userplaylist/', userplaylist, name='userplaylist'),
    path('chart/', chart, name='chart'),
]
