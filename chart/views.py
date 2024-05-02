from django.shortcuts import render
from datetime import datetime

# Create your views here.
def chart(request):
    release_date = datetime.now()
    context = {'release_date': release_date}
    return render(request, 'chart.html', context)

def detail_lagu(request):
    return render(request, 'detail_lagu.html')