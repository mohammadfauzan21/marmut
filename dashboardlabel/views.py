from django.shortcuts import render

# Create your views here.

def homepagelabel(request):
    return render(request, 'homepagelabel.html')