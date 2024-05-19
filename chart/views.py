from django.db import connection
from django.http import HttpResponseNotFound
from django.shortcuts import render

from dashboardreguser.query import get_playlist_akun

def chart(request):
    user_email = request.session.get('user_email')
    if not user_email:
        return HttpResponseNotFound("User email not found in session")
    chart_types = []
    chart_details = {}

    with connection.cursor() as cursor:
        # Fetch chart types
        cursor.execute("SELECT DISTINCT tipe FROM Chart")
        chart_types_raw = cursor.fetchall()

        query = get_playlist_akun(user_email)
        cursor.execute(query)
        playlist_akun = cursor.fetchall()
        
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
        context = {
            'chart_types': chart_types, 
            'chart_details': chart_details,
            'detail_playlist_kelola': [{
                'namaPlaylist': detail_playlist[2],
                'jumlahLagu': detail_playlist[4],
                'durasi': detail_playlist[7],   
                'id_playlist': detail_playlist[6],
                'deskripsi':detail_playlist[3],
                'id_user_playlist':detail_playlist[1]
            } for detail_playlist in playlist_akun]

        }
    # Render the chart template with chart types and details
    return render(request, 'chart.html', context)