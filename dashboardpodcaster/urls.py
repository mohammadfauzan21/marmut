from django.urls import path
from dashboardpodcaster.views import add_episodes, add_podcast, episodes, podcaster

app_name = 'dashboard'
urlpatterns = [
    path('', podcaster, name='podcaster'),
    path('add_podcast/', add_podcast, name='add_podcast'),
    # path('delete_podcast/<uuid:id_konten>', )
    path('episodes/<uuid:id_konten>', episodes, name='episodes'),
    path('add_episodes/', add_episodes, name='add_episodes'),
]