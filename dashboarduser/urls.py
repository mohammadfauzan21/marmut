from django.urls import path
from dashboarduser.views import homepage, logout, roles_session, get_albums_by_artist_or_songwriter, album_list_view, add_album, add_album_view

app_name = 'dashboarduser'
urlpatterns = [
    path('', homepage, name='homepage'),
    path('logout', logout, name='logout'),
    path('roles_session', roles_session, name='roles_session'),
    path('get_albums_by_artist_or_songwriter', get_albums_by_artist_or_songwriter, name='get_albums_by_artist_or_songwriter'),
    path('album_list_view', album_list_view, name='album_list_view'),
    path('add_album/', add_album_view, name='add_album_view'),
]
