from django.db import connection
from django.shortcuts import render

# def chart(request):
#     chart_types = []
#     chart_details = {}

#     with connection.cursor() as cursor:
#         # Fetch chart types
#         cursor.execute("SELECT DISTINCT tipe FROM Chart")
#         chart_types_raw = cursor.fetchall()
        
#         # Convert raw chart types into a list
#         chart_types = [chart_type[0] for chart_type in chart_types_raw]

#         # Fetch chart details for each chart type
#         for chart_type in chart_types:
#             cursor.execute("""
#                 SELECT C.tipe, K.judul AS title, A.id AS artist_id, AK.nama AS artist_name, AK.email AS artist_email, K.tanggal_rilis AS release_date, S.total_play AS plays
#                 FROM CHART C
#                 JOIN PLAYLIST_SONG PS ON C.id_playlist = PS.id_playlist
#                 JOIN SONG S ON PS.id_song = S.id_konten
#                 JOIN KONTEN K ON S.id_konten = K.id
#                 JOIN ARTIST A ON S.id_artist = A.id
#                 JOIN AKUN AK ON A.email_akun = AK.email
#                 WHERE C.tipe = %s
#                 ORDER BY S.total_play DESC
#                 LIMIT 20
#             """, [chart_type])
#             # Fetch all rows
#             rows = cursor.fetchall()
            
#             # Create a list of dictionaries for each row
#             chart_details[chart_type] = [{'tipe': row[0], 'title': row[1], 'artist_id': row[2], 'artist_name': row[3], 'artist_email': row[4], 'release_date': row[5], 'plays': row[6]} for row in rows]

#     # Render the chart template with chart types and details
#     return render(request, 'nyimpen.html', {'chart_types': chart_types, 'chart_details': chart_details})


def chart(request):
    chart_types = []
    chart_details = {}

    with connection.cursor() as cursor:
        # Fetch chart types
        cursor.execute("SELECT DISTINCT tipe FROM Chart")
        chart_types_raw = cursor.fetchall()
        
        # Convert raw chart types into a list
        chart_types = [chart_type[0] for chart_type in chart_types_raw]

        # Fetch chart details for each chart type
        for chart_type in chart_types:
            cursor.execute("""
                SELECT C.tipe, K.judul AS title, A.id AS artist_id, AK.nama AS artist_name, AK.email AS artist_email, K.tanggal_rilis AS release_date, S.total_play AS plays
                FROM CHART C
                JOIN PLAYLIST_SONG PS ON C.id_playlist = PS.id_playlist
                JOIN SONG S ON PS.id_song = S.id_konten
                JOIN KONTEN K ON S.id_konten = K.id
                JOIN ARTIST A ON S.id_artist = A.id
                JOIN AKUN AK ON A.email_akun = AK.email
                WHERE C.tipe = %s
                ORDER BY S.total_play DESC
                LIMIT 20
            """, [chart_type])
            # Fetch all rows
            rows = cursor.fetchall()
            
            # Create a list of dictionaries for each row
            chart_details[chart_type] = [{'tipe': row[0], 'title': row[1], 'artist_id': row[2], 'artist_name': row[3], 'artist_email': row[4], 'release_date': row[5], 'plays': row[6]} for row in rows]

    # Render the chart template with chart types and details
    return render(request, 'chart.html', {'chart_types': chart_types, 'chart_details': chart_details})