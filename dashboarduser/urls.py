from django.urls import path
from dashboarduser.views import homepage, logout

app_name = 'dashboarduser'
urlpatterns = [
    path('', homepage, name='homepage'),
    path('logout/', logout, name='logout')
]
