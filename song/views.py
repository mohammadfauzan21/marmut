from django.shortcuts import render
from django.http import HttpResponseNotFound
from django.shortcuts import redirect, render
from kelola.views import format_durasi, format_durasi_kelola
from playlist.query import *
from django.db import OperationalError, connection
from django.views.decorators.cache import never_cache
from dashboarduser.query import *
from django.urls import reverse

# Create your views here.
@never_cache
def song(request, id_konten):
    #Mengambil url dari page yang sedang ditampilkan
    url_now = request.build_absolute_uri()
    request.session['url_now'] = url_now
    print("Masuk")
    user_email = request.session.get('user_email')
    if not user_email:
        return redirect('login:loginkonten')
    
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
            podcasts = [(id_konten, judul_podcast, jumlah_episode, format_durasi_kelola(total_durasi)) for id_konten, judul_podcast, jumlah_episode, total_durasi in podcasts]

            query_detail = get_detail_song(id_konten)
            cursor.execute(query_detail)
            song_detail = cursor.fetchone()
            print(song_detail)

            # Check if podcast is None
            if song_detail is None:
                return redirect('dashboarduser:homepage')
            
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
                "durasi":format_durasi(song_detail[3]),
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
                'error_message': error_message,
            }
            return render(request, 'song.html', context)
    except OperationalError:
        return HttpResponseNotFound("Database connection error")

@never_cache
def add_song_playlist(request, id_song):
    user_email = request.session.get('user_email')
    if not user_email:
        return redirect('login:loginkonten')
    if request.method == 'POST':
        id_playlist = request.POST.get('id_playlist')
        if id_playlist:
            try:
                with connection.cursor() as cursor:
                    cursor.execute(check_song(id_song, id_playlist))
                    if cursor.fetchone() is not None:
                        # If the song is already in the playlist, return an error message
                        return redirect(f"{reverse('song:song', args=[id_song])}?error=Song+is+already+in+the+playlist.")
                    cursor.execute(add_song(id_song, id_playlist))
                    return redirect(f"{reverse('song:song', args=[id_song])}?success=true")
            except OperationalError:
                return HttpResponseNotFound("Database connection error")