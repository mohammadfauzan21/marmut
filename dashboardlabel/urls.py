from django.urls import path
from dashboardlabel.views import homepagelabel, cekroyalti, listalbum, detaillagu, logout, listsong, delete_album

app_name = 'dashboardlabel'
urlpatterns = [
    path('', homepagelabel, name='homepagelabel'),
    path('cekroyalti', cekroyalti, name='cekroyalti'),
    path('listalbum', listalbum, name='listalbum'),
    path('listsong', listsong, name='listsong'),
    path('detaillagu', detaillagu, name='detaillagu'),
    path('logout', logout, name='logout'),
    path('delete_album', delete_album, name='delete_album'),
]
