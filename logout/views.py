from django.shortcuts import render

# Create your views here.

def logoutkonten(request):
    return render(request, 'preboarding:konten')