from django.urls import include, path
from preboarding.views import konten

app_name = 'preboarding'
urlpatterns = [
    path('', konten, name='konten'),
    path('login/', include('login.urls')),
    path('register/', include('register.urls')),
    path('logout/', include('logout.urls')),
]
