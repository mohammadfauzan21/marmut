from django.shortcuts import render

# Create your views here.

def homepagesongwriter(request):
    return render(request, 'homepagesongwriter.html')


def cekroyaltisongwriter(request):
    return render(request, 'cekroyaltisongwriter.html')


def listsongsongwriter(request):
    return render(request, 'listsongsongwriter.html')


def detaillagusongwriter(request):
    return render(request, 'detaillagusongwriter.html')