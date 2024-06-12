from datetime import datetime
import logging
import uuid
from django.http import HttpResponseBadRequest, HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from dashboardpodcaster.views import format_durasi
from dashboardreguser.query import *
from django.db import OperationalError, connection
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache

from dashboarduser.query import *

@never_cache
def kelolaplaylist(request, id_playlist):
    # Mendapatkan URL yang akan disimpan ke dalam sesi
    url_to_save = request.build_absolute_uri()

    # Menyimpan URL ke dalam sesi
    request.session['urlKelolaPlaylist'] = url_to_save

    list_lagu = request.session.get('list_lagu')
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
            query = user_info(user_email)
            cursor.execute(query)
            user_data = cursor.fetchone()

            # Fetch podcaster's podcast details from the database
            cursor.execute("""
                SELECT 
                    k.id AS id_konten,
                    k.judul AS judul_podcast, 
                    COUNT(e.id_episode) AS jumlah_episode, 
                    SUM(k.durasi) AS total_durasi 
                FROM 
                    podcast p 
                LEFT JOIN 
                    episode e ON p.id_konten = e.id_konten_podcast 
                LEFT JOIN 
                    konten k ON p.id_konten = k.id
                WHERE 
                    p.email_podcaster = %s 
                GROUP BY 
                    k.id, k.judul, p.id_konten
            """, [user_email])
            podcasts = cursor.fetchall()
            podcasts = [(id_konten, judul_podcast, jumlah_episode, format_durasi(total_durasi)) for id_konten, judul_podcast, jumlah_episode, total_durasi in podcasts]

            try:
                footer = [{
                    'judul_lagu': list_lagu[0],
                    'artist':list_lagu[1],
                }],
            except TypeError or IndexError:
                footer = []

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

            query_label = show_label()
            cursor.execute(query_label)
            labels = cursor.fetchall()
            print(labels)

            query_artist = show_artist()
            cursor.execute(query_artist)
            artists = cursor.fetchall()
            print(artists)

            query_songwriter = show_songwriter()
            cursor.execute(query_songwriter)
            songwriters = cursor.fetchall()
            print(songwriters)

            query_genre = show_genre()
            cursor.execute(query_genre)
            genres = cursor.fetchall()
            print(genres)

            query_album = show_album(user_email)
            cursor.execute(query_album)
            albums = cursor.fetchall()
            print(albums)

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
                'footer':footer,
                'detail_playlist_kelola': [{
                    'namaPlaylist': detail_playlist[2],
                    'jumlahLagu': detail_playlist[4],
                    'durasi': detail_playlist[7],
                    'id_playlist': detail_playlist[6],
                    'deskripsi':detail_playlist[3],
                    'id_user_playlist':detail_playlist[1]
                } for detail_playlist in playlist_akun],
                'albums':[{
                    'id': album[0],
                    'judul': album[1],
                    'jumlah_lagu': album[2],
                    'total_durasi': album[3]
                } for album in albums],
                'user_data': user_data, 
                'labels': [{
                    'id': label[0],
                    'nama':label[1],
                    'id_pemilik_hc':label[5],
                } for label in labels],
                'artists': [{
                    'id': artist[0],
                    'nama':artist[1],
                } for artist in artists],
                'songwriters':[{
                    'id':songwriter[0],
                    'nama':songwriter[1],
                } for songwriter in songwriters],
                'genres':[{
                    'id':genre[0],
                    'genre':genre[1],
                } for genre in genres],
                'podcasts': podcasts,
                'error_message': error_message
            }
            print(context)
            return render(request, 'kelolaplaylist.html', context)
    except OperationalError:
        return HttpResponseNotFound("Database connection error")

@never_cache
def playsong(request, id_konten):
    print("Masuk")
    list_lagu = request.session.get('list_lagu')
    user_email = request.session.get('user_email')
    if not user_email:
        return HttpResponseNotFound("User email not found in session")
    
    error_message = request.GET.get('error', None)
    try:
        with connection.cursor() as cursor:
            query = user_info(user_email)
            cursor.execute(query)
            user_data = cursor.fetchone()

            # Fetch podcaster's podcast details from the database
            cursor.execute("""
                SELECT 
                    k.id AS id_konten,
                    k.judul AS judul_podcast, 
                    COUNT(e.id_episode) AS jumlah_episode, 
                    SUM(k.durasi) AS total_durasi 
                FROM 
                    podcast p 
                LEFT JOIN 
                    episode e ON p.id_konten = e.id_konten_podcast 
                LEFT JOIN 
                    konten k ON p.id_konten = k.id
                WHERE 
                    p.email_podcaster = %s 
                GROUP BY 
                    k.id, k.judul, p.id_konten
            """, [user_email])
            podcasts = cursor.fetchall()
            podcasts = [(id_konten, judul_podcast, jumlah_episode, format_durasi(total_durasi)) for id_konten, judul_podcast, jumlah_episode, total_durasi in podcasts]

            try:
                footer = [{
                    'judul_lagu': list_lagu[0],
                    'artist':list_lagu[1],
                }],
            except TypeError or IndexError:
                footer = []

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

            query_label = show_label()
            cursor.execute(query_label)
            labels = cursor.fetchall()
            print(labels)

            query_artist = show_artist()
            cursor.execute(query_artist)
            artists = cursor.fetchall()
            print(artists)

            query_songwriter = show_songwriter()
            cursor.execute(query_songwriter)
            songwriters = cursor.fetchall()
            print(songwriters)

            query_genre = show_genre()
            cursor.execute(query_genre)
            genres = cursor.fetchall()
            print(genres)

            query_album = show_album(user_email)
            cursor.execute(query_album)
            albums = cursor.fetchall()
            print(albums)
            
            context = {
                "judul_lagu" : song_detail[0],
                "artist":song_detail[1],
                "genres_song":song_detail[2],
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
                'footer':footer,
                'detail_playlist_kelola': [{
                    'namaPlaylist': detail_playlist[2],
                    'jumlahLagu': detail_playlist[4],
                    'durasi': detail_playlist[7],
                    'id_playlist': detail_playlist[6],
                    'deskripsi':detail_playlist[3],
                    'id_user_playlist':detail_playlist[1]
                } for detail_playlist in playlist_akun],
                'albums':[{
                    'id': album[0],
                    'judul': album[1],
                    'jumlah_lagu': album[2],
                    'total_durasi': album[3]
                } for album in albums],
                'user_data': user_data, 
                'labels': [{
                    'id': label[0],
                    'nama':label[1],
                    'id_pemilik_hc':label[5],
                } for label in labels],
                'artists': [{
                    'id': artist[0],
                    'nama':artist[1],
                } for artist in artists],
                'songwriters':[{
                    'id':songwriter[0],
                    'nama':songwriter[1],
                } for songwriter in songwriters],
                'genres':[{
                    'id':genre[0],
                    'genre':genre[1],
                } for genre in genres],
                'podcasts': podcasts,
                'error_message': error_message,
            }
            return render(request, 'playsong.html', context)
    except OperationalError:
        return HttpResponseNotFound("Database connection error")

@never_cache
def userplaylist(request):
    # Mendapatkan URL yang akan disimpan ke dalam sesi
    url_to_save = request.build_absolute_uri()

    # Menyimpan URL ke dalam sesi
    request.session['urlUserPlaylist'] = url_to_save

    user_email = request.session.get('user_email')
    if not user_email:
        return HttpResponseNotFound("User email not found in session")
    try:
        with connection.cursor() as cursor:
            query = user_info(user_email)
            cursor.execute(query)
            user_data = cursor.fetchone()

            # Fetch podcaster's podcast details from the database
            cursor.execute("""
                SELECT 
                    k.id AS id_konten,
                    k.judul AS judul_podcast, 
                    COUNT(e.id_episode) AS jumlah_episode, 
                    SUM(k.durasi) AS total_durasi 
                FROM 
                    podcast p 
                LEFT JOIN 
                    episode e ON p.id_konten = e.id_konten_podcast 
                LEFT JOIN 
                    konten k ON p.id_konten = k.id
                WHERE 
                    p.email_podcaster = %s 
                GROUP BY 
                    k.id, k.judul, p.id_konten
            """, [user_email])
            podcasts = cursor.fetchall()
            podcasts = [(id_konten, judul_podcast, jumlah_episode, format_durasi(total_durasi)) for id_konten, judul_podcast, jumlah_episode, total_durasi in podcasts]

            query = get_user_playlist()
            cursor.execute(query)
            playlist_all_user = cursor.fetchall()
            
            query = get_playlist_akun(user_email)
            cursor.execute(query)
            playlist_akun = cursor.fetchall()

            query_label = show_label()
            cursor.execute(query_label)
            labels = cursor.fetchall()
            print(labels)

            query_artist = show_artist()
            cursor.execute(query_artist)
            artists = cursor.fetchall()
            print(artists)

            query_songwriter = show_songwriter()
            cursor.execute(query_songwriter)
            songwriters = cursor.fetchall()
            print(songwriters)

            query_genre = show_genre()
            cursor.execute(query_genre)
            genres = cursor.fetchall()
            print(genres)

            query_album = show_album(user_email)
            cursor.execute(query_album)
            albums = cursor.fetchall()
            print(albums)

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
                } for detail_playlist in playlist_akun],
                'albums':[{
                    'id': album[0],
                    'judul': album[1],
                    'jumlah_lagu': album[2],
                    'total_durasi': album[3]
                } for album in albums],
                'user_data': user_data, 
                'labels': [{
                    'id': label[0],
                    'nama':label[1],
                    'id_pemilik_hc':label[5],
                } for label in labels],
                'artists': [{
                    'id': artist[0],
                    'nama':artist[1],
                } for artist in artists],
                'songwriters':[{
                    'id':songwriter[0],
                    'nama':songwriter[1],
                } for songwriter in songwriters],
                'genres':[{
                    'id':genre[0],
                    'genre':genre[1],
                } for genre in genres],
                'podcasts': podcasts,
            }
            return render(request, 'userplaylist.html', context)
    except OperationalError:
        return HttpResponseNotFound("Database connection error")

def kelolaalbum(request, id_album):
    print("masuk kelola album")
    # Mendapatkan URL yang akan disimpan ke dalam sesi
    url_to_save = request.build_absolute_uri()

    # Menyimpan URL ke dalam sesi
    request.session['urlKelolaPlaylist'] = url_to_save
    list_lagu = request.session.get('list_lagu')
    user_email = request.session.get('user_email')
    if not user_email:
        return HttpResponseNotFound("User email not found in session")
    print("ngeprint email")
    print(user_email)
    print("id_laylist = ")
    print(id_album)
    error_message = request.GET.get('error', None)
    try:
        # current_url = request.build_absolute_uri()
        # request.session['prev_url'] = current_url
        # print("Session = " + request.session.get('prev_url', ''))
        with connection.cursor() as cursor:
            query_header = get_detail_album_header(id_album)
            cursor.execute(query_header)
            album_header = cursor.fetchone()
            print(album_header)

            if album_header is None:
                return HttpResponseNotFound("Album not found")
            
            # Fetch podcaster's podcast details from the database
            cursor.execute("""
                SELECT 
                    k.id AS id_konten,
                    k.judul AS judul_podcast, 
                    COUNT(e.id_episode) AS jumlah_episode, 
                    SUM(k.durasi) AS total_durasi 
                FROM 
                    podcast p 
                LEFT JOIN 
                    episode e ON p.id_konten = e.id_konten_podcast 
                LEFT JOIN 
                    konten k ON p.id_konten = k.id
                WHERE 
                    p.email_podcaster = %s 
                GROUP BY 
                    k.id, k.judul, p.id_konten
            """, [user_email])
            podcasts = cursor.fetchall()
            podcasts = [(id_konten, judul_podcast, jumlah_episode, format_durasi(total_durasi)) for id_konten, judul_podcast, jumlah_episode, total_durasi in podcasts]
            
            query = get_detail_album(id_album)
            cursor.execute(query)
            detail_album = cursor.fetchall()
            print("ini detail")
            print(detail_album)

            query = get_playlist_akun(user_email)
            cursor.execute(query)
            playlist_akun = cursor.fetchall()
            print("playlist_akun")
            
            query_label = show_label()
            cursor.execute(query_label)
            labels = cursor.fetchall()
            print(labels)

            query_artist = show_artist()
            cursor.execute(query_artist)
            artists = cursor.fetchall()
            print(artists)

            query_songwriter = show_songwriter()
            cursor.execute(query_songwriter)
            songwriters = cursor.fetchall()
            print(songwriters)

            query_genre = show_genre()
            cursor.execute(query_genre)
            genres = cursor.fetchall()
            print(genres)

            query_album = show_album(user_email)
            cursor.execute(query_album)
            albums = cursor.fetchall()
            print(albums)

            print("masuk if else")
            print(list_lagu)
            if list_lagu:
                context = {
                    'label' : album_header[0],
                    'durasi':album_header[1],
                    'jumlah_lagu': album_header[2],
                    'judul_album':album_header[3],
                    'detail_album': [{
                        "no":i+1,
                        "konten_id":detail[0],
                        "judul":detail[1],
                        "durasi":detail[2],
                        "total_play":detail[3],
                        "total_download":detail[4],
                    } for i, detail in enumerate(detail_album)],
                    'detail_playlist_kelola': [{
                        'namaPlaylist': detail_playlist[2],
                        'jumlahLagu': detail_playlist[4],
                        'durasi': detail_playlist[7],
                        'id_playlist': detail_playlist[6],
                        'deskripsi':detail_playlist[3],
                        'id_user_playlist':detail_playlist[1]
                    } for detail_playlist in playlist_akun],
                    'albums':[{
                        'id': album[0],
                        'judul': album[1],
                        'jumlah_lagu': album[2],
                        'total_durasi': album[3]
                    } for album in albums],
                    'footer': [{
                        'judul_lagu': list_lagu[0],
                        'artist':list_lagu[1],
                    }],
                    'labels': [{
                        'id': label[0],
                        'nama':label[1],
                        'id_pemilik_hc':label[5],
                    } for label in labels],
                    'artists': [{
                        'id': artist[0],
                        'nama':artist[1],
                    } for artist in artists],
                    'songwriters':[{
                        'id':songwriter[0],
                        'nama':songwriter[1],
                    } for songwriter in songwriters],
                    'genres':[{
                        'id':genre[0],
                        'genre':genre[1],
                    } for genre in genres],
                    'podcasts': podcasts,
                }
                print(context)
            else:
                context = {
                    'label' : album_header[0],
                    'durasi':album_header[1],
                    'jumlah_lagu': album_header[2],
                    'judul_album':album_header[3],
                    'detail_album': [{
                        "no":i+1,
                        "konten_id":detail[0],
                        "judul":detail[1],
                        "durasi":detail[2],
                        "total_play":detail[3],
                        "total_download":detail[4],
                    } for i, detail in enumerate(detail_album)],
                    'detail_playlist_kelola': [{
                        'namaPlaylist': detail_playlist[2],
                        'jumlahLagu': detail_playlist[4],
                        'durasi': detail_playlist[7],
                        'id_playlist': detail_playlist[6],
                        'deskripsi':detail_playlist[3],
                        'id_user_playlist':detail_playlist[1]
                    } for detail_playlist in playlist_akun],
                    'albums':[{
                        'id': album[0],
                        'judul': album[1],
                        'jumlah_lagu': album[2],
                        'total_durasi': album[3],
                    } for album in albums],
                    'footer': [],
                    'labels': [{
                        'id': label[0],
                        'nama':label[1],
                        'id_pemilik_hc':label[5],
                    } for label in labels],
                    'artists': [{
                        'id': artist[0],
                        'nama':artist[1],
                    } for artist in artists],
                    'songwriters':[{
                        'id':songwriter[0],
                        'nama':songwriter[1],
                    } for songwriter in songwriters],
                    'genres':[{
                        'id':genre[0],
                        'genre':genre[1],
                    } for genre in genres],
                    'podcasts': podcasts,
                }
            print("mau return kelolaalbum.html")
            return render(request, 'kelolaalbum.html', context)
    except OperationalError:
        return HttpResponseNotFound("Database connection error")

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
        
@never_cache
def putar_lagu(request, id_konten):
    if request.method == 'POST':
        try:
            with connection.cursor() as cursor:
                query_detail = get_detail_song(id_konten)
                cursor.execute(query_detail)
                song_detail = cursor.fetchone()
                print("masuk post")
                # Simpan detail lagu ke dalam sesi
                request.session['list_lagu'] = [song_detail[0], song_detail[1]]
            return redirect(f"{reverse('dashboardreguser:playsong', args=[id_konten])}")
        except OperationalError:
            return HttpResponseNotFound("Database connection error")
    print(list_lagu)

@csrf_exempt
@never_cache
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
@never_cache
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
@never_cache
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
                    cursor.execute(add_song_to_playlist(song_id, id_playlist))
                    return redirect(f"{reverse('dashboardreguser:kelolaplaylist', args=[id_playlist])}")
            except OperationalError:
                return HttpResponseNotFound("Database connection error")

@csrf_exempt
@never_cache
def add_song_playlist(request, id_song):
    if request.method == 'POST':
        id_playlist = request.POST.get('id_playlist')
        if id_playlist:
            try:
                with connection.cursor() as cursor:
                    cursor.execute(check_song(id_song, id_playlist))
                    if cursor.fetchone() is not None:
                        # If the song is already in the playlist, return an error message
                        return redirect(f"{reverse('dashboardreguser:playsong', args=[id_song])}?error=This+song+is+already+in+the+playlist.")
                    cursor.execute(add_song_to_playlist(id_song, id_playlist))
                    return redirect(f"{reverse('dashboardreguser:playsong', args=[id_song])}")
            except OperationalError:
                return HttpResponseNotFound("Database connection error")
            
def create_album(request):
    if request.method == 'POST':
        id_album = uuid.uuid4()
        print("id_album:")
        print(id_album)
        judul_album = request.POST.get('judulAlbum')
        # check_jumlah_lagu = ('buat def ke basis data')
        # if check_jumlah_lagu:
        #     jumlah_lagu = check_jumlah_lagu + 1
        # else:
        #     jumlah_lagu = 1
        id_label = request.POST.get('label')
        # check_total_durasi = ('buat def ke basis data')
        # if check_total_durasi:
        #     total_durasi = check_total_durasi + request.POST.get('durasiLagu')
        # else:
        #     total_durasi = request.POST.get('durasiLagu')
        try:
            with connection.cursor() as cursor:
                print("id_label:")
                print(id_label)
                print("judul_album:")
                print(judul_album)
                cursor.execute(create_new_album(id_album, judul_album, id_label))
                create_song(request, id_album)
                return redirect(f"{reverse('dashboarduser:homepage')}")
        except OperationalError:
            return HttpResponseNotFound("Database connection error")

def create_song(request, id_album):
    if request.method == 'POST' or request.method != 'POST':
        print('apa')
        print("id album:")
        print(id_album)
        #song
        id_konten = uuid.uuid4()
        print("id_konten:")
        print(id_konten)
        id_artist = request.POST.get('artist')
        user_email = request.session.get('user_email')
        print(user_email)
        print("id_artist:")
        print(id_artist)

        #konten
        judul_lagu = request.POST.get('judulLagu')
        tanggal_dibuat = datetime.now()
        durasi_menit = request.POST.get('durasiMenit')
        print(durasi_menit)
        durasi_detik = request.POST.get('durasiDetik')
        print(durasi_detik)
        durasi_fix = (int(durasi_menit)*60)+int(durasi_detik)
        print(durasi_fix)

        #genre and songwriter
        songwriters = request.POST.getlist('songwriter')
        genres = request.POST.getlist('genreSelect')
        print("songwriter:")
        print(songwriters)
        print(len(songwriters))
        print("genre:")
        print(genres)

        try:
            with connection.cursor() as cursor:
                cursor.execute(add_konten(id_konten, judul_lagu, tanggal_dibuat, durasi_fix))
                if id_artist == None:
                    cursor.execute(user_id_artist(user_email))
                    id_artist = cursor.fetchone()
                    print("id_artist:")
                    print(id_artist)
                for x in id_artist:
                    print(x)
                    cursor.execute(add_song_to_album(id_konten, x, id_album))
                if len(songwriters) < 1 :
                    cursor.execute(user_id_songwriter(user_email))
                    id_songwriter = cursor.fetchone()
                    print("id_songwriter:")
                    print(id_songwriter)
                for songwriter in id_songwriter:
                    cursor.execute(add_songwriter(songwriter, id_konten))
                for genre in genres:
                    cursor.execute(add_genre(id_konten, genre))

                #royalti
                print("royalti")
                query = get_artist_id_pemilik_hak_cipta(user_email)
                cursor.execute(query)
                artist_id_pemilik_hak_cipta = cursor.fetchone()
                query = get_songwriter_id_pemilik_hak_cipta(user_email)
                cursor.execute(query)
                songwriter_id_pemilik_hak_cipta = cursor.fetchone()
                if artist_id_pemilik_hak_cipta != None:
                    cursor.execute(add_royalti(artist_id_pemilik_hak_cipta[0], id_konten))
                if songwriter_id_pemilik_hak_cipta != None:
                    cursor.execute(add_royalti(songwriter_id_pemilik_hak_cipta[0], id_konten))

            if request.method == 'POST':
                return redirect(f"{reverse('dashboarduser:homepage')}")
        except OperationalError:
            return HttpResponseNotFound("Database connection error")

def delete_album(request, id_album):
    print("id di delete_album:")
    print(id_album)
    if request.method == 'POST':
        try:
            with connection.cursor() as cursor:
                print("delete_album_royalti")
                cursor.execute(delete_album_royalti(id_album))
                print("delete_album_downloaded_song")
                cursor.execute(delete_album_downloaded_song(id_album))
                print("delete_album_akun_play_song")
                cursor.execute(delete_album_akun_play_song(id_album))
                print("delete_album_playlist_song")
                cursor.execute(delete_album_playlist_song(id_album))
                print("delete_album_songwriter_write_song")
                cursor.execute(delete_album_songwriter_write_song(id_album))
                print("delete_song")
                cursor.execute(delete_song(id_album))
                print("operasi sudah selesai")

            print("diatas redirect")
            return redirect(reverse('dashboarduser:homepage'))
        except OperationalError:
            return HttpResponseNotFound("Database connection error")
    return HttpResponseNotFound("Invalid request method")