from django.urls import path
from playlist.views import *

app_name = 'playlist'
urlpatterns = [
    path('', userplaylist, name='userplaylist'),
    path('<uuid:id_playlist>/', kelolaplaylist, name='kelolaplaylist'),
    path('putar_lagu/<uuid:id_konten>/', putar_lagu, name='putar_lagu'),
    # path('add_song_to_playlist/<uuid:id_playlist>/', add_song_to_playlist, name='add_song_to_playlist'),
    # path('add_song_playlist/<uuid:id_song>/', add_song_playlist, name='add_song_playlist'),
    # path('delete_album/<uuid:id_album>/', delete_album, name='delete_album'),
    # path('create_song/<uuid:id_album>/', create_song, name='create_song'),
    # path('create_album/', create_album, name='create_album'),
    # path('kelolaalbum/<uuid:id_album>/', kelolaalbum, name='kelolaalbum'),
]