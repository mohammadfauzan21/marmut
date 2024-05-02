from django.urls import path
from dashboardartist.views import homepageartist, cekroyalti, listsong, detaillagu

app_name = 'dashboardartist'
urlpatterns = [
    path('', homepageartist, name='homepageartist'),
    path('cekroyalti', cekroyalti, name='cekroyalti'),
    path('listsong', listsong, name='listsong'),
    path('detaillagu', detaillagu, name='detaillagu'),
]
