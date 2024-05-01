from django.shortcuts import render

# Create your views here.

def registerkonten(request):
    return render(request, 'register.html')