from django.urls import path
from dashboardartist.views import homepageartist, cekroyaltiartist, listsongartist, detaillaguartist, playlistartist, podcastartist, chartartist

app_name = 'dashboardartist'
urlpatterns = [
    path('', homepageartist, name='homepageartist'),
    path('cekroyaltiartist', cekroyaltiartist, name='cekroyaltiartist'),
    path('listsongartist', listsongartist, name='listsongartist'),
    path('detaillaguartist', detaillaguartist, name='detaillaguartist'),
    path('chartartist', chartartist, name='chartartist'),
    path('playlistartist', playlistartist, name='playlistartist'),
    path('podcastartist', podcastartist, name='podcastartist'),
]
