from django.db import connection
from django.http import HttpResponseNotFound
from django.shortcuts import render
from dashboardpodcaster.views import format_durasi
from dashboardreguser.query import get_playlist_akun, show_album
from django.views.decorators.cache import never_cache

from dashboarduser.query import *

@never_cache
def chart(request):
    # Mendapatkan URL yang akan disimpan ke dalam sesi
    url_to_save = request.build_absolute_uri()

    # Menyimpan URL ke dalam sesi
    request.session['url'] = url_to_save

    user_email = request.session.get('user_email')
    if not user_email:
        return HttpResponseNotFound("User email not found in session")
    chart_types = []
    chart_details = {}

    with connection.cursor() as cursor:
        query = user_info(user_email)
        cursor.execute(query)
        user_data = cursor.fetchone()

        # Fetch chart types
        cursor.execute("SELECT DISTINCT tipe FROM Chart")
        chart_types_raw = cursor.fetchall()

        query = get_playlist_akun(user_email)
        cursor.execute(query)
        playlist_akun = cursor.fetchall()
        print("playlist akun:")
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
        
        # Convert raw chart types into a list
        chart_types = [chart_type[0] for chart_type in chart_types_raw]

        # Fetch chart details for each chart type
        for chart_type in chart_types:
            cursor.execute("""
                SELECT C.tipe, K.judul AS title, A.id AS artist_id, AK.nama AS artist_name, AK.email AS artist_email, K.tanggal_rilis AS release_date, S.total_play AS plays, k.id AS id_konten
                FROM CHART C
                JOIN PLAYLIST_SONG PS ON C.id_playlist = PS.id_playlist
                JOIN SONG S ON PS.id_song = S.id_konten
                JOIN KONTEN K ON S.id_konten = K.id
                JOIN ARTIST A ON S.id_artist = A.id
                JOIN AKUN AK ON A.email_akun = AK.email
                WHERE C.tipe = %s AND S.total_play > 0
                ORDER BY S.total_play DESC
                LIMIT 20
            """, [chart_type])
            # Fetch all rows
            rows = cursor.fetchall()
            
            # Create a list of dictionaries for each row
            chart_details[chart_type] = [{'tipe': row[0], 'title': row[1], 'artist_id': row[2], 'artist_name': row[3], 'artist_email': row[4], 'release_date': row[5], 'plays': row[6], 'id_konten':row[7],} for row in rows]
        print(chart_details)

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

        context = {
            'user_data': user_data, 
            'chart_types': chart_types, 
            'chart_details': chart_details,
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
    # Render the chart template with chart types and details
    return render(request, 'chart.html', context)