from django.shortcuts import redirect, render
from django.db import OperationalError, ProgrammingError, connection
from django.http import HttpResponseNotFound
from uuid import UUID
from django.contrib.auth.decorators import login_required

from kelola.views import format_durasi, format_durasi_kelola
from playlist.query import *
from dashboarduser.query import *
from podcast.query import *

def podcast_view(request):
    #Mengambil url dari page yang sedang ditampilkan
    url_now = request.build_absolute_uri()
    request.session['url_now'] = url_now
    # Mengambil kata "podcast" dari URL
    url_path = request.path
    # Menggunakan split untuk memisahkan segmen URL
    url_segments = url_path.split('/')
    print("url_segments")
    print(url_segments[1])

    # Menyimpan URL ke dalam sesi
    request.session['url'] = url_segments[1]

    user_email = request.session.get('user_email')
    if not user_email:
        return redirect('login:loginkonten')
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
            kelola_podcasts = cursor.fetchall()
            print("kelola_podcast")
            print(kelola_podcasts)
            kelola_podcasts = [(id_konten, judul_podcast, jumlah_episode, format_durasi_kelola(total_durasi)) for id_konten, judul_podcast, jumlah_episode, total_durasi in kelola_podcasts]

            # Fetch podcast details
            cursor.execute(podcast())
            podcasts = cursor.fetchall()

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
        
            formatted_podcasts = [(id_konten, judul, podcaster, format_durasi(durasi)) for id_konten, judul, podcaster, durasi in podcasts]

            context = {
                'all_podcasts': enumerate(formatted_podcasts),
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
                'podcasts': kelola_podcasts,
            }
        return render(request, 'podcast.html', context)
    except OperationalError:
        return HttpResponseNotFound("Database connection error")

def detail_podcast(request, id_konten):
    #Mengambil url dari page yang sedang ditampilkan
    url_now = request.build_absolute_uri()
    request.session['url_now'] = url_now
    user_email = request.session.get('user_email')
    if not user_email:
        return redirect('login:loginkonten')
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
            kelola_podcasts = cursor.fetchall()
            print("kelola_podcast")
            print(kelola_podcasts)
            kelola_podcasts = [(id_konten, judul_podcast, jumlah_episode, format_durasi_kelola(total_durasi)) for id_konten, judul_podcast, jumlah_episode, total_durasi in kelola_podcasts]

            # Fetch podcast details including the year
            cursor.execute("""
                SELECT K.id, K.judul, array_agg(G.genre), A.nama, K.durasi, K.tanggal_rilis, K.tahun
                FROM KONTEN K
                JOIN PODCAST P ON K.id = P.id_konten
                JOIN PODCASTER Po ON P.email_podcaster = Po.email
                JOIN AKUN A ON Po.email = A.email
                JOIN GENRE G ON K.id = G.id_konten
                WHERE K.id = %s       
                GROUP BY K.id, K.judul, A.nama, K.durasi, K.tanggal_rilis, K.tahun
            """, [id_konten])
            detail_podcast = cursor.fetchone()
            print("mau ngeprint detail podcast")
            print(detail_podcast)

            # Check if podcast is None
            if detail_podcast is None:
                return HttpResponseNotFound("Podcast not found")

            # Fetch episode details
            cursor.execute("""
                SELECT E.judul, E.deskripsi, E.durasi, E.tanggal_rilis
                FROM EPISODE E
                WHERE E.id_konten_podcast = %s
                ORDER BY E.tanggal_rilis DESC
            """, [id_konten])
            episodes = cursor.fetchall()
            total_episodes = len(episodes)
            
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
                'judul_podcast': detail_podcast[1],
                'genres_podcast': detail_podcast[2],
                'podcaster': detail_podcast[3],
                'total_episodes': total_episodes,
                'total_duration': format_durasi(detail_podcast[4]),
                'tanggal_rilis': detail_podcast[5],
                'tahun_podcast': detail_podcast[6],  # Add the year to the context
                'episodes': [{
                    'judul': episode[0],
                    'deskripsi': episode[1],
                    'durasi': format_durasi(episode[2]),
                    'tanggal_rilis': episode[3]
                } for episode in episodes],
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
                'podcasts': kelola_podcasts,
            }
        return render(request, 'detail_podcast.html', context)
    except OperationalError:
        return HttpResponseNotFound("Database connection error")
    except ProgrammingError:
        return HttpResponseNotFound("Invalid query or database error")
    except ValueError as e:
        return HttpResponseNotFound(str(e))