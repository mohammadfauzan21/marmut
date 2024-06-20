from django.db import OperationalError, connection
from django.http import HttpResponseNotFound
from django.shortcuts import render

from kelola.views import format_durasi, format_durasi_kelola
from playlist.query import get_playlist_akun, show_album
from dashboarduser.query import show_artist, show_genre, show_label, show_songwriter, user_info
from royalti.query import *
from search.query import *

# Create your views here.
def search(request):
    user_email = request.session.get('user_email')
    query_search = request.GET.get('query')
    print("query_serach")
    print(query_search)
    try:
        with connection.cursor() as cursor:
            query = user_info(user_email)
            cursor.execute(query)
            user_data = cursor.fetchone()

            query_song = search_query_song(query_search)
            cursor.execute(query_song)
            search_song = cursor.fetchall()
            print("song")
            for i in search_song:
                print(i[3])

            query_album = search_query_album(query_search)
            cursor.execute(query_album)
            search_album = cursor.fetchall()

            query_playlist = search_query_playlist(query_search)
            cursor.execute(query_playlist)
            search_playlist = cursor.fetchall()

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
                'search_song':[{
                    'no':i+1,
                    'judulLagu': result[0],
                    'artist': result[1],
                    'tanggalRilis': result[2],
                    'totalPlay': result[3],
                    'idSong': result[4]
                } for i, result in enumerate(search_song)],
                'search_album':[{
                    'no':i+1,
                    'judulAlbum': result[0],
                    'label': result[1],
                    'jumlahLagu': result[2],
                    'durasi': format_durasi(result[3]),
                    'idAlbum': result[4]
                } for i, result in enumerate(search_album)],
                'search_playlist':[{
                    'no':i+1,
                    'judulPlaylist': result[0],
                    'pembuat': result[1],
                    'durasi': format_durasi(result[2]),
                    'tanggalBuat': result[3],
                    'idPlaylist': result[4]
                } for i, result in enumerate(search_playlist)],
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
        return render(request, 'search.html', context)
    except OperationalError:
        return HttpResponseNotFound("Database connection error")