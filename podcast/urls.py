from django.urls import path
from podcast.views import podcast_view, detail_podcast

app_name = 'podcast'
urlpatterns = [
    path('', podcast_view, name='podcast'),
    path('detail_podcast/<uuid:id_konten>', detail_podcast, name='detail_podcast'),
]
