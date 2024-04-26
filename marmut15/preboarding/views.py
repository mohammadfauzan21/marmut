from django.shortcuts import render

# Create your views here.

def konten(request):
    return render(request, 'preboarding.html')