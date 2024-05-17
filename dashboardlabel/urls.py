from django.urls import path
from dashboardlabel.views import homepagelabel, cekroyalti, listsong, detaillagu, logout

app_name = 'dashboardlabel'
urlpatterns = [
    path('', homepagelabel, name='homepagelabel'),
    path('cekroyalti', cekroyalti, name='cekroyalti'),
    path('listsong', listsong, name='listsong'),
    path('detaillagu', detaillagu, name='detaillagu'),
    path('logout', logout, name='logout'),
]
