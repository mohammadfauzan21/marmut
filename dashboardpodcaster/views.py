from django.shortcuts import render
from datetime import datetime

# Create your views here.
def podcaster(request):
    return render(request, 'podcaster.html')

def episodes(request):
    episodes_date = datetime.now()
    context = {'episodes_date': episodes_date}
    return render(request, 'episodes.html', context)