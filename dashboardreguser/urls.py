from django.urls import path
from dashboardreguser.views import dashboarduser

app_name = 'dashboardreguser'
urlpatterns = [
    path('', dashboarduser, name='dashboarduser'),
]
