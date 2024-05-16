from django.http import HttpResponseNotFound
from django.shortcuts import render
from dashboardreguser.query import *
from django.db import OperationalError, connection #ini penting dr ghana
#kata ghana buat file query.py untuk buat method ambil datanya dari database

# Create your views here.
def dashboarduser(request):
    return render(request, 'dashboard.html')

def kelolaplaylist(request, id_playlist):
    print("id_laylist = ")
    print(id_playlist)
    try:
        # current_url = request.build_absolute_uri()
        # request.session['prev_url'] = current_url
        # print("Session = " + request.session.get('prev_url', ''))
        with connection.cursor() as cursor:
            query_header = get_detail_playlist_header(id_playlist)
            cursor.execute(query_header)
            playlist_header = cursor.fetchone()
            print(playlist_header)

            # Check if podcast is None
            if playlist_header is None:
                return HttpResponseNotFound("Podcast not found")
            
            query = get_detail_playlist(id_playlist)
            cursor.execute(query)
            detail_playlist = cursor.fetchall()
            print(detail_playlist)
            
            context = {
            "pembuat" : playlist_header[0],
            "jumlah_lagu": playlist_header[1],
            "durasi":playlist_header[2],
            "tanggal_buat":playlist_header[3],
            "judul_playlist":playlist_header[4],
            "deskripsi_playlist":playlist_header[5], 
            'detail_podcast': [{
                "no":i+1,
                "judulLagu":detail[0],
                "artist":detail[1],
                "durasi":detail[2],
                "id_konten":detail[3]
            } for i, detail in enumerate(detail_playlist)]
            }
            return render(request, 'kelolaplaylist.html', context)
    except OperationalError:
        return HttpResponseNotFound("Database connection error")

def playsong(request, id_konten):
    print("Masuk")
    # Mendapatkan bagian terakhir dari URL yang dikunjungi pengguna
    # prev_url = request.session.get('prev_url', '')
    # print("prev_url = " + prev_url)
    # prev_path = prev_url.split('/')
    # print("halo")
    # kata_kunci = prev_path[-2] if prev_path[-1] == '' else prev_path[-1]  # Mengambil kata terakhir dari URL
    # print(kata_kunci)
    # return render(request, 'playsong.html', {'kata_kunci': kata_kunci})

    try:
        with connection.cursor() as cursor:
            query_detail = get_detail_song(id_konten)
            cursor.execute(query_detail)
            song_detail = cursor.fetchone()
            print(song_detail)

            # Check if podcast is None
            if song_detail is None:
                return HttpResponseNotFound("Song detail not found")
            
            query_writersong = get_songwriter_song(id_konten)
            cursor.execute(query_writersong)
            writersong = cursor.fetchall()
            print(writersong)
            
            context = {
            "judul_lagu" : song_detail[0],
            "artist":song_detail[1],
            "genres":song_detail[2],
            "durasi":song_detail[3],
            "tanggal_rilis":song_detail[4],
            "tahun":song_detail[5],
            "total_play":song_detail[6], 
            "total_download":song_detail[7], 
            "nama_album":song_detail[8],
            'songwriter': [{
                "name":name[0]
            } for name in writersong]
            }
            return render(request, 'playsong.html', context)
    except OperationalError:
        return HttpResponseNotFound("Database connection error")

def userplaylist(request):
    try:
        with connection.cursor() as cursor:
            i = 1;
            query = get_user_playlist()
            cursor.execute(query)
            playlist_all_user = cursor.fetchall()
            list_all_playlist = []
            for playlist in playlist_all_user:
                # print(playlist[0])
                list_all_playlist.append(
                    {"no":i,
                    "judulPlaylist":playlist[0],
                    "pembuat":playlist[1],
                    "durasi":playlist[2],
                    "id_playlist":playlist[3]
                    }
                )
                i = i + 1
            print(list_all_playlist)
            context = {'list_all_playlist' : list_all_playlist}
            return render(request, 'userplaylist.html', context)
    except OperationalError:
        return HttpResponseNotFound("Database connection error")
    # for playlist in playlist_all_user:
    #     print(playlist[0])
        # list_all_playlist.append(
        #     {"no":1,
        #     "judulPlaylist":playlist[0],
        #     "pembuat":playlist[1],
        #     "durasi":playlist[2]}
        # )

    # print(list_all_playlist)

#     # print(playlist_all_user[0])
#     # print(playlist_all_user[0][0])
#     # context = {'list_user_playlist':playlist_all_user}


def chart(request):
    current_url = request.build_absolute_uri()
    request.session['prev_url'] = current_url
    print("Session = " + request.session.get('prev_url', ''))
    return render(request, 'chart.html')

