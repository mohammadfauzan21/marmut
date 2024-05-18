from django.urls import path
from dashboardpodcaster.views import add_episodes, add_podcast, delete_episode, delete_podcast, episodes, podcaster, update_episode, update_podcast

app_name = 'dashboard'
urlpatterns = [
    path('', podcaster, name='podcaster'),
    path('add_podcast/', add_podcast, name='add_podcast'),
    path('delete_podcast/<uuid:id_konten>', delete_podcast, name='delete_podcast'),
    path('episodes/<uuid:id_konten>', episodes, name='episodes'),
    path('add_episodes/<uuid:id_konten>', add_episodes, name='add_episodes'),
    path('episodes/<uuid:id_konten>/delete_episode/<uuid:id_episode>/', delete_episode, name='delete_episode'),
    path('update_podcast/<uuid:id_konten>', update_podcast, name='update_podcast'),
    path('episodes/<uuid:id_konten>/update_episode/<uuid:id_episode>/', update_episode, name='update_episode')
]