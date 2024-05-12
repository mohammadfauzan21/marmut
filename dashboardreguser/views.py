from django.shortcuts import render
from django.urls import resolve

# Create your views here.
def dashboarduser(request):
    return render(request, 'dashboard.html')

def kelolaplaylist(request):
    current_url = request.build_absolute_uri()
    request.session['prev_url'] = current_url
    print("Session = " + request.session.get('prev_url', ''))
    return render(request, 'kelolaplaylist.html')

def playsong(request):
    print("Masuk")
    # Mendapatkan bagian terakhir dari URL yang dikunjungi pengguna
    prev_url = request.session.get('prev_url', '')
    print("prev_url = " + prev_url)
    prev_path = prev_url.split('/')
    print("halo")
    kata_kunci = prev_path[-2] if prev_path[-1] == '' else prev_path[-1]  # Mengambil kata terakhir dari URL
    print(kata_kunci)
    return render(request, 'playsong.html', {'kata_kunci': kata_kunci})
    # return render(request, 'playsong.html')

def userplaylist(request):
    return render(request, 'userplaylist.html')


def chart(request):
    current_url = request.build_absolute_uri()
    request.session['prev_url'] = current_url
    print("Session = " + request.session.get('prev_url', ''))
    return render(request, 'chart.html')