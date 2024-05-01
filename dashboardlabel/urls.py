from django.urls import path
from dashboardlabel.views import homepagelabel, cekroyalti

app_name = 'dashboardlabel'
urlpatterns = [
    path('', homepagelabel, name='homepagelabel'),
    path('royalti', homepagelabel, name='royalti'),
]
