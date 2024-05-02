from django.urls import path
from dashboardsongwriter.views import homepagesongwriter, cekroyalti, listsong, detaillagu

app_name = 'dashboardsongwriter'
urlpatterns = [
    path('', homepagesongwriter, name='homepagesongwriter'),
    path('cekroyalti', cekroyalti, name='cekroyalti'),
    path('listsong', listsong, name='listsong'),
    path('detaillagu', detaillagu, name='detaillagu'),
]
