from django.shortcuts import render
from django.db import OperationalError, ProgrammingError, connection
from django.http import HttpResponseNotFound
from uuid import UUID

def format_durasi(menit):
    jam = menit // 60
    sisa_menit = menit % 60
    return f'{jam} jam {sisa_menit} menit' if jam > 0 else f'{sisa_menit} menit'

def podcast_view(request):
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
        
        formatted_podcasts = [(id_konten, judul, podcaster, format_durasi(durasi)) for id_konten, judul, podcaster, durasi in podcasts]
        return render(request, 'podcast.html', {'podcasts': enumerate(formatted_podcasts)})
    except OperationalError:
        return HttpResponseNotFound("Database connection error")

def detail_podcast(request, id_konten):
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
            } for episode in episodes]
        }
        
        return render(request, 'detail_podcast.html', context)
    except OperationalError:
        return HttpResponseNotFound("Database connection error")
    except ProgrammingError:
        return HttpResponseNotFound("Invalid query or database error")
    except ValueError as e:
        return HttpResponseNotFound(str(e))
