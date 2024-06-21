from django.db import connection
from django.shortcuts import redirect, render
from kelola.views import format_durasi_kelola
from playlist.query import get_playlist_akun, show_album

from dashboarduser.query import *

def chart(request):
    #Mengambil url dari page yang sedang ditampilkan
    url_now = request.build_absolute_uri()
    request.session['url_now'] = url_now
    # Mengambil kata "chart" dari URL
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

        context = {
            'user_data': user_data, 
            'chart_types': chart_types, 
            'chart_details': chart_details,
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