from django.shortcuts import render

# Create your views here.
def dashboarduser(request):
    return render(request, 'dashboard.html')

def kelolaplaylist(request):
    return render(request, 'kelolaplaylist.html')

def playsong(request):
    return render(request, 'playsong.html')

def userplaylist(request):
    return render(request, 'userplaylist.html')