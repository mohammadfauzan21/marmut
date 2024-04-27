from django.shortcuts import render

# Create your views here.
def podcast_view(request):
    return render(request, 'podcast.html')