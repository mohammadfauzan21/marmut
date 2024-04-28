from django.urls import path
from podcast.views import podcast_view

app_name = 'podcast'
urlpatterns = [
    path('', podcast_view, name='podcast'),  # Contoh URL untuk podcast.html
]
