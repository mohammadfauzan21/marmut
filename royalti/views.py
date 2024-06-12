from django.db import OperationalError, connection
from django.http import HttpResponseNotFound
from django.shortcuts import render

from dashboardpodcaster.views import format_durasi
from dashboardreguser.query import get_playlist_akun, show_album
from dashboarduser.query import show_artist, show_genre, show_label, show_songwriter, user_info
from royalti.query import *

# Create your views here.
def royalti(request):
    user_email = request.session.get('user_email')
    list_lagu = request.session.get('list_lagu')
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

            query = show_royalti_songwriter(user_email)
            cursor.execute(query)
            royalti_songwriter = cursor.fetchall()
            print("royalti songwriter")
            print(royalti_songwriter)

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
                    'royalti_artist':[{
                        "no":i+1,
                        'judul_song':royalti[0],
                        'judul_album':royalti[1],
                        'total_play':royalti[2],
                        'total_download':royalti[3],
                        'jumlah_royalti':royalti[4],
                    }for i, royalti in enumerate(royalti_artist)],
                    'royalti_songwriter':[{
                        "no":i+1,
                        'judul_song':royalti[0],
                        'judul_album':royalti[1],
                        'total_play':royalti[2],
                        'total_download':royalti[3],
                        'jumlah_royalti':royalti[4],
                    }for i, royalti in enumerate(royalti_songwriter)],
                    'detail_playlist_kelola':[{
                        'namaPlaylist': detail_playlist[2],
                        'jumlahLagu': detail_playlist[4],
                        'durasi': detail_playlist[7],
                        'id_playlist': detail_playlist[6],
                        'deskripsi': detail_playlist[3],
                        'id_user_playlist': detail_playlist[1]
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
                    'footer': [{
                        'judul_lagu': list_lagu[0],
                        'artist':list_lagu[1],
                    }],
                }
                print(context)
            else:
                context = {
                    'royalti_artist':[{
                        "no":i+1,
                        'judul_song':royalti[0],
                        'judul_album':royalti[1],
                        'total_play':royalti[2],
                        'total_download':royalti[3],
                        'jumlah_royalti':royalti[4],
                    }for i, royalti in enumerate(royalti_artist)],
                    'royalti_songwriter':[{
                        "no":i+1,
                        'judul_song':royalti[0],
                        'judul_album':royalti[1],
                        'total_play':royalti[2],
                        'total_download':royalti[3],
                        'jumlah_royalti':royalti[4],
                    }for i, royalti in enumerate(royalti_songwriter)],
                    'detail_playlist_kelola':[{
                        'namaPlaylist': detail_playlist[2],
                        'jumlahLagu': detail_playlist[4],
                        'durasi': detail_playlist[7],
                        'id_playlist': detail_playlist[6],
                        'deskripsi': detail_playlist[3],
                        'id_user_playlist': detail_playlist[1]
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
                    'footer': [],
                }
        return render(request, 'royalti.html', context)
    except OperationalError:
        return HttpResponseNotFound("Database connection error")