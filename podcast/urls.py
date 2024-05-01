from django.urls import include,path
from podcast.views import podcast_view

app_name = 'podcast'
urlpatterns = [
    path('', podcast_view, name='podcast'),
]
