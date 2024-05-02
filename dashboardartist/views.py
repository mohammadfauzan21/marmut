from django.shortcuts import render

# Create your views here.

def homepageartist(request):
    return render(request, 'homepageartist.html')


def cekroyalti(request):
    return render(request, 'cekroyalti.html')


def listsong(request):
    return render(request, 'listsong.html')


def detaillagu(request):
    return render(request, 'detaillagu.html')