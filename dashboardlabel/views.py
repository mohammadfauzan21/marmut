from django.shortcuts import redirect, render
from django.db import OperationalError, connection
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from dashboardlabel.query import *
from dashboarduser.query import *
from kelola.views import *
from playlist.query import *

# @login_required(login_url='/login')
def check_session(request, required_user_type):
    # Ambil informasi pengguna dari session
    user_email = request.session.get('user_email')
    user_type = request.session.get('user_type')

    # Pastikan pengguna telah login
    if not user_email or user_type != required_user_type:
        # error_message = "Anda harus login terlebih dahulu."
        # return render(request, 'login.html', {'error_message': error_message})
        return redirect('login:loginkonten')

    return user_email

@login_required(login_url='/login')
def homepagelabel(request):
    #Mengambil url dari page yang sedang ditampilkan
    url_now = request.build_absolute_uri()
    request.session['url_now'] = url_now
    # Mengambil kata "dashboard" dari URL
    url_path = request.path
    # Menggunakan split untuk memisahkan segmen URL
    url_segments = url_path.split('/')
    print("url_segments")
    print(url_segments[1])
    # Menyimpan URL ke dalam sesi
    request.session['url'] = url_segments[1]

    user_email = check_session(request, 'label')
    if isinstance(user_email, HttpResponse):
        return redirect('login:loginkonten')

    try:
        with connection.cursor() as cursor:
            query = get_info_label(user_email)
            cursor.execute(query)
            info_label = cursor.fetchone()
            print(info_label)

            query = get_playlist_akun(user_email)
            print("Generated query:")
            print(query)
            cursor.execute(query)
            playlist_akun = cursor.fetchall()
            print("Result from database:")
            print(playlist_akun)

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
            print("albums:")
            print(albums)

            context = {
                'idlabel': info_label[0],
                'namalabel': info_label[1],
                'emaillabel': info_label[2],
                'kontaklabel': info_label[3],
                'detail_playlist_kelola':[{
                    'namaPlaylist': detail_playlist[2],
                    'jumlahLagu': detail_playlist[4],
                    'durasi': format_durasi_kelola(detail_playlist[7]),
                    'id_playlist': detail_playlist[6],
                    'deskripsi': detail_playlist[3],
                    'id_user_playlist': detail_playlist[1]
                } for detail_playlist in playlist_akun],
                'albums':[{
                    'id': album[0],
                    'judul': album[1],
                    'jumlah_lagu': album[2],
                    'total_durasi': format_durasi_kelola(album[3]),
                    'id_pemilik_hak_cipta':album[4],
                } for album in albums],
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
            return render(request, 'homepagelabel.html', context)
    except OperationalError:
        return HttpResponseNotFound("Database connection error")