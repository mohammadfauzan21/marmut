from django.urls import path
from dashboardlabel.views import homepagelabel

app_name = 'dashboardlabel'
urlpatterns = [
    path('', homepagelabel, name='homepagelabel'),
]
