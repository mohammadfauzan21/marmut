from django.urls import path
from preboarding.views import konten

app_name = 'preboarding'
urlpatterns = [
    path('', konten, name='konten'),
]
