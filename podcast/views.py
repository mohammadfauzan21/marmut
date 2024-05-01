from django.shortcuts import render
from datetime import datetime

# Create your views here.
def podcast_view(request):
    return render(request, 'podcast.html')

def detail_podcast(request):
    podcast_date = datetime.now()
    context = {'podcast_date': podcast_date}
    return render(request, 'detail_podcast.html', context)