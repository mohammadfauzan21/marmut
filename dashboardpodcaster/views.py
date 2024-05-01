from django.shortcuts import render

# Create your views here.
def podcaster(request):
    return render(request, 'podcaster.html')