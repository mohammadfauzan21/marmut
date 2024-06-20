from django.db import OperationalError, connection
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import redirect, render

from kelola.views import format_durasi, format_durasi_kelola
from playlist.query import get_playlist_akun, show_album
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

from dashboarduser.query import *


# Roles session untuk atur hak akses navbar
def roles_session(request):
    user_roles = request.session.get('user_roles')
    return render(request, 'roles_session.html', {'user_roles': user_roles})


def homepage(request):
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

    if 'user_email' in request.session:
        user_email = request.session.get('user_email')
        user_type = request.session.get('user_type')

    else:
        return render(request, 'login.html')

    print(request.session.get('user_roles'))
    user_data = None
    roles = []

    if user_type == "verified":
    # Query untuk pengguna yang telah terverifikasi
        query = """
            SELECT a.nama, a.email, a.kota_asal, 
                CASE WHEN a.gender = 0 THEN 'Laki-Laki' ELSE 'Perempuan' END AS gender,
                a.tempat_lahir,
                ar.id AS artist_id,
                sw.id AS songwriter_id,
                p.email AS podcaster_email
            FROM akun a
            LEFT JOIN artist ar ON a.email = ar.email_akun
            LEFT JOIN songwriter sw ON a.email = sw.email_akun
            LEFT JOIN podcaster p ON a.email = p.email
            WHERE a.email = %s
        """

        try:
            with connection.cursor() as cursor:
                cursor.execute(query, [user_email])
                user_data = cursor.fetchone()
                if user_data:
                    roles = []
                    if user_data[5]:  # artist_id
                        roles.append("Artist")
                    if user_data[6]:  # songwriter_id
                        roles.append("Songwriter")
                    if user_data[7]:  # podcaster_email
                        roles.append("Podcaster")
                        
                query = get_playlist_akun(user_email)
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
                    'user_data': user_data, 
                    'roles': roles,
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
        except OperationalError:
            return HttpResponseNotFound("Database connection error")
        
    elif user_type == "unverified":
        # Query untuk pengguna yang belum terverifikasi
        with connection.cursor() as cursor:
            query = user_info(user_email)
            cursor.execute(query)
            user_data = cursor.fetchone()
            if user_data:
                roles.append("Tidak ada Role")
                
            cursor.execute(get_playlist_akun(user_email))
            playlist_akun = cursor.fetchall()
            print("playlist_akun:")
            print(playlist_akun)

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
                    'total_durasi': format_durasi_kelola(album[3])
                } for album in albums],
                'user_data': user_data, 
                'roles': roles,
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
            }
    return render(request, 'homepage.html', context)


def logout(request):
    # Hapus semua data sesi terkait dengan login pengguna
    request.session.pop('user_email', None)
    request.session.pop('user_type', None)
    request.session.pop('user_roles', None)

    info_message = "Anda telah logout."
    return render(request, 'login.html', {'info_message': info_message})