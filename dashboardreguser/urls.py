from django.urls import path
from dashboardreguser.views import dashboarduser,chart

app_name = 'dashboardreguser'
urlpatterns = [
    path('', dashboarduser, name='dashboarduser'),
    path('chart', chart, name='chart'),
]
