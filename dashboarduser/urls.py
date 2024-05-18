from django.urls import path
from dashboarduser.views import homepage, logout, roles_session

app_name = 'dashboarduser'
urlpatterns = [
    path('', homepage, name='homepage'),
    path('logout', logout, name='logout'),
    path('roles_session', roles_session, name='roles_session'),
]
