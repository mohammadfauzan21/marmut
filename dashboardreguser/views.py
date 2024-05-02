from django.shortcuts import render

# Create your views here.
def dashboarduser(request):
    return render(request, 'dashboard.html')


def chart(request):
    return render(request, 'chart.html')
