from datetime import datetime
import uuid
from django.http import HttpResponseBadRequest, HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from dashboardreguser.query import *
from django.db import OperationalError, connection
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt


# Create your views here.
def dashboarduser(request):
    user_email = request.session.get('user_email')
    if not user_email:
        return HttpResponseNotFound("User email not found in session")
    print("ngeprint email")
    print(user_email)
    try:
        with connection.cursor() as cursor:
            query = get_playlist_akun(user_email)
            print("Generated query:")
            print(query)

            if query:
                print("masuk if")
                cursor.execute(query)
                playlist_akun = cursor.fetchall()
                print("Result from database:")
                print(playlist_akun)
                if playlist_akun:
                    context = {
                        'detail_playlist_kelola': [{
                            'namaPlaylist': detail_playlist[2],
                            'jumlahLagu': detail_playlist[4],
                            'durasi': detail_playlist[7],
                            'id_playlist': detail_playlist[6],
                            'deskripsi':detail_playlist[3],
                            'id_user_playlist':detail_playlist[1]
                        } for detail_playlist in playlist_akun]
                    }
                else:
                    context = {
                        'detail_playlist_kelola': []
                    }
            else:
                context = {
                    'detail_playlist_kelola': []
                }
            return render(request, 'dashboard.html', context)
    except OperationalError:
        return HttpResponseNotFound("Database connection error")


def kelolaplaylist(request, id_playlist):
    user_email = request.session.get('user_email')
    if not user_email:
        return HttpResponseNotFound("User email not found in session")
    print("ngeprint email")
    print(user_email)
    print("id_laylist = ")
    print(id_playlist)
    error_message = request.GET.get('error', None)
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
                return HttpResponseNotFound("Playlist not found")
            
            query = get_detail_playlist(id_playlist)
            cursor.execute(query)
            detail_playlist = cursor.fetchall()
            print("ini detail")
            print(detail_playlist)

            query = show_song()
            cursor.execute(query)
            list_song=cursor.fetchall()
            print(list_song)

            query = get_playlist_akun(user_email)
            cursor.execute(query)
            playlist_akun = cursor.fetchall()
            if playlist_akun:
                context = {
                    'pembuat' : playlist_header[0],
                    'jumlah_lagu': playlist_header[1],
                    'durasi':playlist_header[2],
                    'tanggal_buat':playlist_header[3],
                    'judul_playlist':playlist_header[4],
                    'deskripsi_playlist':playlist_header[5], 
                    'id_playlist':id_playlist,
                    'detail_playlist': [{
                        "no":i+1,
                        "judulLagu":detail[0],
                        "artist":detail[1],
                        "durasi":detail[2],
                        "id_konten":detail[3]
                    } for i, detail in enumerate(detail_playlist)],
                    'list_song':[{
                        'id':song[0],
                        'judul':song[1],
                        'pembuat':song[2]
                    }for song in list_song],
                    'detail_playlist_kelola': [{
                        'namaPlaylist': detail_playlist[2],
                        'jumlahLagu': detail_playlist[4],
                        'durasi': detail_playlist[7],
                        'id_playlist': detail_playlist[6],
                        'deskripsi':detail_playlist[3],
                        'id_user_playlist':detail_playlist[1]
                    } for detail_playlist in playlist_akun],
                    'error_message': error_message
                }
            else:
                context = {
                    "pembuat" : playlist_header[0],
                    "jumlah_lagu": playlist_header[1],
                    "durasi":playlist_header[2],
                    "tanggal_buat":playlist_header[3],
                    "judul_playlist":playlist_header[4],
                    "deskripsi_playlist":playlist_header[5], 
                    'id_playlist':id_playlist,
                    'detail_playlist': [{
                        "no":i+1,
                        "judulLagu":detail[0],
                        "artist":detail[1],
                        "durasi":detail[2],
                        "id_konten":detail[3]
                    } for i, detail in enumerate(detail_playlist)],
                    'detail_playlist_kelola': {},
                    'error_message': error_message
                }
            print(context)
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

    user_email = request.session.get('user_email')
    if not user_email:
        return HttpResponseNotFound("User email not found in session")
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

            query = get_playlist_akun(user_email)
            cursor.execute(query)
            playlist_akun = cursor.fetchall()
            
            if playlist_akun:
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
                    'id_song':song_detail[9],
                    'songwriter': [{
                        "name":name[0]
                    } for name in writersong],
                    'detail_playlist_kelola': [{
                                'namaPlaylist': detail_playlist[2],
                                'jumlahLagu': detail_playlist[4],
                                'durasi': detail_playlist[7],
                                'id_playlist': detail_playlist[6],
                                'deskripsi':detail_playlist[3],
                                'id_user_playlist':detail_playlist[1]
                    } for detail_playlist in playlist_akun]
                }
            else:
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
                    'id_song':song_detail[9],
                    'songwriter': [{
                        "name":name[0]
                    } for name in writersong],
                    'detail_playlist_kelola': {}
                }
            return render(request, 'playsong.html', context)
    except OperationalError:
        return HttpResponseNotFound("Database connection error")

def userplaylist(request):
    user_email = request.session.get('user_email')
    if not user_email:
        return HttpResponseNotFound("User email not found in session")
    try:
        with connection.cursor() as cursor:
            i = 1;
            query = get_user_playlist()
            cursor.execute(query)
            playlist_all_user = cursor.fetchall()
            
            query = get_playlist_akun(user_email)
            cursor.execute(query)
            playlist_akun = cursor.fetchall()
            if playlist_akun:
                context = {
                    'list_all_playlist': [{
                        "no":i+1,
                        "judulPlaylist":playlist[0],
                        "pembuat":playlist[1],
                        "durasi":playlist[2],
                        "id_playlist":playlist[3]
                    }for i, playlist in enumerate(playlist_all_user)],
                    'detail_playlist_kelola': [{
                        'namaPlaylist': detail_playlist[2],
                        'jumlahLagu': detail_playlist[4],
                        'durasi': detail_playlist[7],
                        'id_playlist': detail_playlist[6],
                        'deskripsi':detail_playlist[3],
                        'id_user_playlist':detail_playlist[1]
                    } for detail_playlist in playlist_akun]
                }
            else:
                context = {
                    'list_all_playlist': [{
                        "no":i+1,
                        "judulPlaylist":playlist[0],
                        "pembuat":playlist[1],
                        "durasi":playlist[2],
                        "id_playlist":playlist[3]
                    }for i, playlist in enumerate(playlist_all_user)],
                    'detail_playlist_kelola': {}
                }

            # list_all_playlist = []
            # for playlist in playlist_all_user:
            #     # print(playlist[0])
            #     list_all_playlist.append(
            #         {"no":i,
            #         "judulPlaylist":playlist[0],
            #         "pembuat":playlist[1],
            #         "durasi":playlist[2],
            #         "id_playlist":playlist[3]
            #         }
            #     )
            #     i = i + 1
            # print(list_all_playlist)
            # context = {'list_all_playlist' : list_all_playlist}
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

@csrf_exempt
def delete_playlist(request, id_user_playlist):
    if request.method == 'POST':
        try:
            with connection.cursor() as cursor:
                # Nonaktifkan triger sebelum penghapusan playlist
                cursor.execute("ALTER TABLE user_playlist DISABLE TRIGGER song_update_playlist_stats")
                
                # Hapus playlist
                cursor.execute(delete_akun_play_user_playlist(id_user_playlist))
                cursor.execute(delete_user_playlist(id_user_playlist))
                
                # Aktifkan kembali triger setelah penghapusan selesai
                cursor.execute("ALTER TABLE user_playlist ENABLE TRIGGER song_update_playlist_stats")

            return redirect(reverse('dashboarduser:homepage' ))
        except OperationalError:
            return HttpResponseNotFound("Database connection error")

@csrf_exempt
def add_playlist(request):
    if request.method == 'POST':
        user_email = request.session.get('user_email')
        if not user_email:
            return HttpResponseNotFound("User email not found in session")
        id_user_playlist = uuid.uuid4()
        print(id_user_playlist)
        # Mendapatkan nilai judul dan deskripsi dari permintaan POST
        judul = request.POST.get('judul')
        print(judul)
        deskripsi = request.POST.get('deskripsi')

        # Memeriksa apakah judul dan deskripsi ada dalam permintaan POST
        if not judul or not deskripsi:
            return HttpResponseBadRequest("Judul dan/atau deskripsi tidak ada dalam permintaan POST")
        jumlah_lagu = 0
        tanggal_dibuat = datetime.now()
        total_durasi = 0

        try:
            with connection.cursor() as cursor:
                print("masuk")
                id_playlist = uuid.uuid4()
                # Nonaktifkan triger sebelum penghapusan playlist
                cursor.execute("ALTER TABLE user_playlist DISABLE TRIGGER check_duplicate_song_in_playlist_trigger")
                cursor.execute("ALTER TABLE user_playlist DISABLE TRIGGER song_update_playlist_stats")
                print("masuk2")
                cursor.execute(insert_id_playlist(id_playlist))

                cursor.execute(insert_user_playlist(user_email, id_user_playlist, judul, deskripsi, jumlah_lagu, tanggal_dibuat, id_playlist, total_durasi))
                print("masuk3")
                cursor.execute("ALTER TABLE user_playlist ENABLE TRIGGER check_duplicate_song_in_playlist_trigger")
                print("masuk4")
                cursor.execute("ALTER TABLE user_playlist ENABLE TRIGGER song_update_playlist_stats")

            return redirect(f"{reverse('dashboarduser:homepage' )}")
        except OperationalError:
            return HttpResponseNotFound("Database connection error")

@csrf_exempt
def ubah_playlist(request, id_playlist):
    print("masuk ke ubah_playlist")
    print(id_playlist)
    if request.method == 'POST':
        judul = request.POST.get('judul')
        deskripsi = request.POST.get('deskripsi')

        # Memeriksa apakah judul dan deskripsi ada dalam permintaan POST
        if not judul or not deskripsi:
            return HttpResponseBadRequest("Judul dan/atau deskripsi tidak ada dalam permintaan POST")
        try:
            with connection.cursor() as cursor:
                cursor.execute(ubah_playlist_query(judul, deskripsi, id_playlist))
            return redirect(f"{reverse('dashboarduser:homepage' )}")
        except OperationalError:
            return HttpResponseNotFound("Database connection error")

@csrf_exempt
@require_POST
def add_song_to_playlist(request, id_playlist):
    if request.method == 'POST':
        song_id = request.POST.get('song_id')
        if song_id:
            try:
                with connection.cursor() as cursor:
                    cursor.execute(check_song(song_id, id_playlist))
                    if cursor.fetchone() is not None:
                        # If the song is already in the playlist, return an error message
                        return redirect(f"{reverse('dashboardreguser:kelolaplaylist', args=[id_playlist])}?error=This+song+is+already+in+the+playlist.")
                    cursor.execute(add_song(song_id, id_playlist))
                    return redirect(f"{reverse('dashboardreguser:kelolaplaylist', args=[id_playlist])}")
            except OperationalError:
                return HttpResponseNotFound("Database connection error")

@csrf_exempt
@require_POST
def add_song_playlist(request, id_song):
    if request.method == 'POST':
        id_playlist = request.POST.get('id_playlist')
        if id_playlist:
            try:
                with connection.cursor() as cursor:
                    cursor.execute(check_song(id_song, id_playlist))
                    if cursor.fetchone() is not None:
                        # If the song is already in the playlist, return an error message
                        return redirect(f"{reverse('dashboardreguser:kelolaplaylist', args=[id_playlist])}?error=This+song+is+already+in+the+playlist.")
                    cursor.execute(add_song(id_song, id_playlist))
                    return redirect(f"{reverse('dashboardreguser:kelolaplaylist', args=[id_playlist])}")
            except OperationalError:
                return HttpResponseNotFound("Database connection error")