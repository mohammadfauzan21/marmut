from django.urls import path
from dashboardlabel.views import homepagelabel, cekroyalti, detaillagu, logout, listsong, delete_album, delete_song

app_name = 'dashboardlabel'
urlpatterns = [
    path('', homepagelabel, name='homepagelabel'),
    path('cekroyalti', cekroyalti, name='cekroyalti'),
    path('listsong/<uuid:album_id>/', listsong, name='listsong'),
    path('detaillagu', detaillagu, name='detaillagu'),
    path('logout', logout, name='logout'),
    path('delete_album', delete_album, name='delete_album'),
    path('listsong/<uuid:album_id>/delete_song/<uuid:song_id>/', delete_song, name='delete_song')
]
