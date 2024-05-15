from django.shortcuts import render
from datetime import datetime
from django.db import ProgrammingError, connection
from uuid import UUID

# Create your views here.
def format_durasi(menit):
    jam = menit // 60
    sisa_menit = menit % 60
    return f'{jam} jam {sisa_menit} menit' if jam > 0 else f'{sisa_menit} menit'

def podcast_view(request):
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

from uuid import UUID
from django.db import ProgrammingError
from django.http import HttpResponseServerError

def detail_podcast(request, id_konten):
    try:
        id_konten = UUID(str(id_konten))  # Convert id_konten to UUID
    except ValueError:
        # Handle invalid UUID format
        return HttpResponseServerError("Invalid UUID format")

    with connection.cursor() as cursor:
        try:
            # Fetch podcast details including the year
            cursor.execute("""
                SELECT K.judul, array_agg(G.genre), A.nama, K.durasi, K.tanggal_rilis, K.tahun
                FROM KONTEN K
                JOIN PODCAST P ON K.id = P.id_konten
                JOIN PODCASTER Po ON P.email_podcaster = Po.email
                JOIN AKUN A ON Po.email = A.email
                JOIN GENRE G ON K.id = G.id_konten
                WHERE K.id = %s
                GROUP BY K.judul, A.nama, K.durasi, K.tanggal_rilis, K.tahun
            """, [id_konten])

            podcast = cursor.fetchone()

            # Fetch episode details
            cursor.execute("""
                SELECT E.judul, E.deskripsi, E.durasi, E.tanggal_rilis
                FROM episode E
                WHERE E.id_konten = %s;
            """, [id_konten])

            episodes = cursor.fetchall()

        except ProgrammingError as e:
            # Handle database query error
            return HttpResponseServerError(f"Database error: {e}")

    # Calculate total episodes and total duration
    total_episodes = len(episodes)
    total_duration = sum(episode[2] for episode in episodes)

    # Prepare context data for rendering
    context = {
        'judul_podcast': podcast[1],
        'podcaster': podcast[2],
        'total_episodes': total_episodes,
        'total_duration': total_duration,
        'genre': podcast[4],
        'tanggal_rilis': podcast[5],
        'tahun_podcast': podcast[6],  # Add the year to the context
        'episodes': [{
            'judul': episode[0],
            'deskripsi': episode[1],
            'durasi': episode[2],
            'tanggal_rilis': episode[3]
        } for episode in episodes]
    }

    return render(request, 'detail_podcast.html', context)
