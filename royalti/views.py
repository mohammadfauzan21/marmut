from django.db import OperationalError, connection
from django.http import HttpResponseNotFound
from django.shortcuts import redirect, render

from kelola.views import format_durasi_kelola
from playlist.query import *
from dashboarduser.query import *
from royalti.query import *

# Create your views here.
def royalti(request):
    #Mengambil url dari page yang sedang ditampilkan
    url_now = request.build_absolute_uri()
    request.session['url_now'] = url_now
    # Mengambil kata "royalti" dari URL
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
    print(user_email)
    try:
        # current_url = request.build_absolute_uri()
        # request.session['prev_url'] = current_url
        # print("Session = " + request.session.get('prev_url', ''))
        with connection.cursor() as cursor:
            print("royalti")
            query = show_royalti_artist(user_email)
            cursor.execute(query)
            royalti_artist = cursor.fetchall()
            print("royalti artist")
            print(royalti_artist)

            query = total_royalti_artist(user_email)
            cursor.execute(query)
            total_royalti_art = cursor.fetchall()
            print("total_royalti_artist")
            print(total_royalti_art)

            query = show_royalti_songwriter(user_email)
            cursor.execute(query)
            royalti_songwriter = cursor.fetchall()
            print("royalti songwriter")
            print(royalti_songwriter)

            query = total_royalti_songwriter(user_email)
            cursor.execute(query)
            total_royalti_swrt = cursor.fetchall()
            print("total_royalti_songwriter")
            print(total_royalti_swrt)

            query = show_royalti_label(user_email)
            cursor.execute(query)
            royalti_label = cursor.fetchall()
            print("royalti label")
            print(royalti_label)

            query = total_royalti_label(user_email)
            cursor.execute(query)
            total_royalti_lab = cursor.fetchall()
            print("total_royalti_label")
            print(total_royalti_lab)

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
            context = {
                'royalti_artist':[{
                    "no":i+1,
                    'judul_song':royalti[0],
                    'judul_album':royalti[1],
                    'total_play':royalti[2],
                    'total_download':royalti[3],
                    'jumlah_royalti':royalti[4],
                }for i, royalti in enumerate(royalti_artist)],
                'total_royalti_artist':[{
                    'id_pemiliki_hak_cipta':total[0],
                    'total_royalti':total[1],
                }for total in total_royalti_art],
                'royalti_songwriter':[{
                    "no":i+1,
                    'judul_song':royalti[0],
                    'judul_album':royalti[1],
                    'total_play':royalti[2],
                    'total_download':royalti[3],
                    'jumlah_royalti':royalti[4],
                }for i, royalti in enumerate(royalti_songwriter)],
                'total_royalti_songwriter':[{
                    'id_pemiliki_hak_cipta':total[0],
                    'total_royalti':total[1],
                }for total in total_royalti_swrt],
                'royalti_label':[{
                    "no":i+1,
                    'judul_song':royalti[0],
                    'judul_album':royalti[1],
                    'total_play':royalti[2],
                    'total_download':royalti[3],
                    'jumlah_royalti':royalti[4],
                }for i, royalti in enumerate(royalti_label)],
                'total_royalti_label':[{
                    'id_pemiliki_hak_cipta':total[0],
                    'total_royalti':total[1],
                }for total in total_royalti_lab],
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
        return render(request, 'royalti.html', context)
    except OperationalError:
        return HttpResponseNotFound("Database connection error")