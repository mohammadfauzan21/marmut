from django.urls import path
from dashboardpodcaster.views import podcaster

app_name = 'dasboard_podcaster'
urlpatterns = [
    path('', podcaster, name='podcaster'),
]
