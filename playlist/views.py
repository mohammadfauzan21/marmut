from datetime import datetime
import uuid
from django.http import HttpResponseBadRequest, HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from dashboarduser.query import *
from kelola.views import format_durasi, format_durasi_kelola
from playlist.query import *
from django.db import OperationalError, connection
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache

# @never_cache
def kelolaplaylist(request, id_playlist):
    #Mengambil url dari page yang sedang ditampilkan
    url_now = request.build_absolute_uri()
    request.session['url_now'] = url_now

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
                    k.durasi AS total_durasi 
                FROM 
                    podcast p 
                LEFT JOIN 
                    konten k ON p.id_konten = k.id
                LEFT JOIN 
                    episode e ON p.id_konten = e.id_konten_podcast 
                WHERE 
                    p.email_podcaster = %s 
                GROUP BY 
                    k.id, k.judul, k.durasi
            """, [user_email])
            podcasts = cursor.fetchall()
            podcasts = [(id_konten, judul_podcast, jumlah_episode, format_durasi_kelola(total_durasi)) for id_konten, judul_podcast, jumlah_episode, total_durasi in podcasts]

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
                'durasi':format_durasi(playlist_header[2]),
                'tanggal_buat':playlist_header[3],
                'judul_playlist':playlist_header[4],
                'deskripsi_playlist':playlist_header[5], 
                'id_playlist':id_playlist,
                'detail_playlist': [{
                    "no":i+1,
                    "judulLagu":detail[0],
                    "artist":detail[1],
                    "durasi":format_durasi(detail[2]),
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
                    'durasi': format_durasi_kelola(detail_playlist[7]),
                    'id_playlist': detail_playlist[6],
                    'deskripsi':detail_playlist[3],
                    'id_user_playlist':detail_playlist[1]
                } for detail_playlist in playlist_akun],
                'albums':[{
                    'id': album[0],
                    'judul': album[1],
                    'jumlah_lagu': album[2],
                    'total_durasi': format_durasi_kelola(album[3]),
                    'id_pemilik_hak_cipta':album[4],
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

# @never_cache
def userplaylist(request):
    #Mengambil url dari page yang sedang ditampilkan
    url_now = request.build_absolute_uri()
    request.session['url_now'] = url_now
    
    # Mengambil kata "playlist" dari URL
    url_path = request.path
    # Menggunakan split untuk memisahkan segmen URL
    url_segments = url_path.split('/')
    print("url_segments")
    print(url_segments[1])

    # Menyimpan URL ke dalam sesi
    request.session['url'] = url_segments[1]

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
                    k.durasi AS total_durasi 
                FROM 
                    podcast p 
                LEFT JOIN 
                    konten k ON p.id_konten = k.id
                LEFT JOIN 
                    episode e ON p.id_konten = e.id_konten_podcast 
                WHERE 
                    p.email_podcaster = %s 
                GROUP BY 
                    k.id, k.judul, k.durasi
            """, [user_email])
            podcasts = cursor.fetchall()
            podcasts = [(id_konten, judul_podcast, jumlah_episode, format_durasi_kelola(total_durasi)) for id_konten, judul_podcast, jumlah_episode, total_durasi in podcasts]

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
                    "durasi":format_durasi(playlist[2]),
                    "id_playlist":playlist[3]
                }for i, playlist in enumerate(playlist_all_user)],
                'detail_playlist_kelola': [{
                    'namaPlaylist': detail_playlist[2],
                    'jumlahLagu': detail_playlist[4],
                    'durasi': format_durasi_kelola(detail_playlist[7]),
                    'id_playlist': detail_playlist[6],
                    'deskripsi':detail_playlist[3],
                    'id_user_playlist':detail_playlist[1]
                } for detail_playlist in playlist_akun],
                'albums':[{
                    'id': album[0],
                    'judul': album[1],
                    'jumlah_lagu': album[2],
                    'total_durasi': format_durasi_kelola(album[3]),
                    'id_pemilik_hak_cipta':album[4],
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
            return redirect(f"{reverse('playlist:playsong', args=[id_konten])}")
        except OperationalError:
            return HttpResponseNotFound("Database connection error")