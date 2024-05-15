from django.urls import path
from dashboardpodcaster.views import podcaster, episodes

app_name = 'dashboard'
urlpatterns = [
    path('', podcaster, name='podcaster'),
    path('episodes/', episodes, name='episodes'),
]
