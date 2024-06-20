from django.urls import path
from kelola.views import *

app_name = 'kelola'
urlpatterns = [
    path('playlist/<uuid:id_playlist>/', playlist, name='playlist'),
    path('album/<uuid:id_album>/', album, name='album'),
    path('podcast/<uuid:id_konten>/', podcast, name='podcast'),
    path('add_podcast/', add_podcast, name='add_podcast'),
    path('delete_podcast/<uuid:id_konten>/', delete_podcast, name='delete_podcast'),
    path('add_episodes/<uuid:id_konten>/', add_episodes, name='add_episodes'),
    path('delete_episode/<uuid:id_konten>/<uuid:id_episode>/', delete_episode, name='delete_episode'),
    path('update_podcast/<uuid:id_konten>/', update_podcast, name='update_podcast'),
    path('update_episode/<uuid:id_konten>/<uuid:id_episode>/', update_episode, name='update_episode'),
    path('delete_album/<uuid:id_album>/', delete_album, name='delete_album'),
    path('create_song/<uuid:id_album>/<uuid:id_pemilik_hak_cipta_label>', create_song, name='create_song'),
    path('create_album/', create_album, name='create_album'),
    path('delete_playlist/<uuid:id_user_playlist>/', delete_playlist, name='delete_playlist'),
    path('add_playlist/', add_playlist, name='add_playlist'),
    path('ubah_playlist/<uuid:id_playlist>/', ubah_playlist, name='ubah_playlist'),
    path('add_song_to_playlist/<uuid:id_playlist>/', add_song_to_playlist, name='add_song_to_playlist'),
    path('delete_song/<uuid:id_konten>/<uuid:id_playlist>/', delete_song_plylist, name='delete_song'),
]
