from django.shortcuts import render

# Create your views here.

def homepagelabel(request):
    return render(request, 'homepagelabel.html')


def cekroyalti(request):
    return render(request, 'cekroyalti.html')