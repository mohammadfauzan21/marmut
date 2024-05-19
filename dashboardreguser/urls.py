from django.urls import path
from dashboardreguser.views import dashboarduser, kelolaplaylist, playsong, userplaylist, chart

app_name = 'dashboardreguser'
urlpatterns = [
    path('', dashboarduser, name='dashboarduser'),
    path('kelolaplaylist/<uuid:id_playlist>/', kelolaplaylist, name='kelolaplaylist'),
    path('playsong/<uuid:id_konten>/', playsong, name='playsong'),
    path('userplaylist/', userplaylist, name='userplaylist'),
    path('chart/', chart, name='chart'),
]
