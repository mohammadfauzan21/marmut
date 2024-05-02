from django.shortcuts import render

# Create your views here.

def homepagesongwriter(request):
    return render(request, 'homepagesongwriter.html')


def cekroyalti(request):
    return render(request, 'cekroyalti.html')


def listsong(request):
    return render(request, 'listsong.html')


def detaillagu(request):
    return render(request, 'detaillagu.html')