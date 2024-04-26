from django.shortcuts import render

# Create your views here.

def loginkonten(request):
    return render(request, 'login.html')