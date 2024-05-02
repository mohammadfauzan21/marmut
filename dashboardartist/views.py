from django.shortcuts import render

# Create your views here.

def homepageartist(request):
    return render(request, 'homepageartist.html')


def cekroyaltiartist(request):
    return render(request, 'cekroyaltiartist.html')


def listsongartist(request):
    return render(request, 'listsongartist.html')


def detaillaguartist(request):
    return render(request, 'detaillaguartist.html')