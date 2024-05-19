from django.shortcuts import render
from django.db import OperationalError, ProgrammingError, connection
from django.http import HttpResponseNotFound
from uuid import UUID

from dashboardreguser.query import get_playlist_akun

def format_durasi(menit):
    if menit is None:
        return '0 jam 0 menit'
    else :
        jam = menit // 60
        sisa_menit = menit % 60
        if jam > 0:
            return f'{jam} jam {sisa_menit} menit'
        else :
            return f'{sisa_menit} menit'

def podcast_view(request):
    user_email = request.session.get('user_email')
    if not user_email:
        return HttpResponseNotFound("User email not found in session")
    try:
        with connection.cursor() as cursor:
            # Fetch podcast details
            cursor.execute("""
                SELECT K.id AS id_konten, K.judul AS judul_podcast, A.nama AS nama_podcaster, K.durasi AS durasi_podcast
                FROM podcast P
                JOIN konten K ON P.id_konten = K.id
                JOIN podcaster Po ON P.email_podcaster = Po.email
                JOIN akun A ON Po.email = A.email;
            """)

            podcasts = cursor.fetchall()
            query = get_playlist_akun(user_email)
            cursor.execute(query)
            playlist_akun = cursor.fetchall()
        
        formatted_podcasts = [(id_konten, judul, podcaster, format_durasi(durasi)) for id_konten, judul, podcaster, durasi in podcasts]
        context = {
            'podcasts': enumerate(formatted_podcasts),
            'detail_playlist_kelola': [{
                'namaPlaylist': detail_playlist[2],
                'jumlahLagu': detail_playlist[4],
                'durasi': detail_playlist[7],
                'id_playlist': detail_playlist[6],
                'deskripsi':detail_playlist[3],
                'id_user_playlist':detail_playlist[1]
            } for detail_playlist in playlist_akun]
        }
        return render(request, 'podcast.html', context)
    except OperationalError:
        return HttpResponseNotFound("Database connection error")

def detail_podcast(request, id_konten):
    user_email = request.session.get('user_email')
    if not user_email:
        return HttpResponseNotFound("User email not found in session")
    try:
        with connection.cursor() as cursor:
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

            podcast = cursor.fetchone()
            

            print(podcast)

            # Check if podcast is None
            if podcast is None:
                return HttpResponseNotFound("Podcast not found")

            # Fetch episode details
            cursor.execute("""
                SELECT E.judul, E.deskripsi, E.durasi, E.tanggal_rilis
                FROM EPISODE E
                WHERE E.id_konten_podcast = %s
                ORDER BY E.tanggal_rilis DESC
            """, [id_konten])

            episodes = cursor.fetchall()
            
            query = get_playlist_akun(user_email)
            cursor.execute(query)
            playlist_akun = cursor.fetchall()

        # Calculate total episodes and total duration
        total_episodes = len(episodes)

        # Prepare context data for rendering
        context = {
            'judul_podcast': podcast[1],
            'genres': podcast[2],
            'podcaster': podcast[3],
            'total_episodes': total_episodes,
            'total_duration': format_durasi(podcast[4]),
            'tanggal_rilis': podcast[5],
            'tahun_podcast': podcast[6],  # Add the year to the context
            'episodes': [{
                'judul': episode[0],
                'deskripsi': episode[1],
                'durasi': format_durasi(episode[2]),
                'tanggal_rilis': episode[3]
            } for episode in episodes],
            'detail_playlist_kelola': [{
                'namaPlaylist': detail_playlist[2],
                'jumlahLagu': detail_playlist[4],
                'durasi': detail_playlist[7],
                'id_playlist': detail_playlist[6],
                'deskripsi':detail_playlist[3],
                'id_user_playlist':detail_playlist[1]
            } for detail_playlist in playlist_akun]
        }
        
        return render(request, 'detail_podcast.html', context)
    except OperationalError:
        return HttpResponseNotFound("Database connection error")
    except ProgrammingError:
        return HttpResponseNotFound("Invalid query or database error")
    except ValueError as e:
        return HttpResponseNotFound(str(e))