from django.urls import path
from dashboardsongwriter.views import homepagesongwriter, cekroyaltisongwriter, listsongsongwriter, detaillagusongwriter

app_name = 'dashboardsongwriter'
urlpatterns = [
    path('', homepagesongwriter, name='homepagesongwriter'),
    path('cekroyaltisongwriter', cekroyaltisongwriter, name='cekroyaltisongwriter'),
    path('listsongsongwriter', listsongsongwriter, name='listsongsongwriter'),
    path('detaillagusongwriter', detaillagusongwriter, name='detaillagusongwriter'),
]
