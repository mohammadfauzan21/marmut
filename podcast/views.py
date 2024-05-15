from django.shortcuts import render
from datetime import datetime
from django.db import OperationalError, connection

# Create your views here.
def podcast_view(request):
    try:
        with connection.cursor() as cursor:
            # Fetch podcast details
            cursor.execute("""
                SELECT K.judul, array_agg(G.genre), A.nama, K.durasi, K.tanggal_rilis, K.tahun
                FROM KONTEN K
                JOIN PODCAST P ON K.id = P.id_konten
                JOIN PODCASTER Po ON P.email_podcaster = Po.email
                JOIN AKUN A ON Po.email = A.email
                JOIN GENRE G ON K.id = G.id_konten
                GROUP BY K.judul, A.nama, K.durasi, K.tanggal_rilis, K.tahun
            """)

            podcasts = cursor.fetchall()

        if podcasts:
            return render(request, 'podcast.html', {'podcasts': podcasts})
        else:
            return render(request, 'podcast.html', {'error_message': 'Tidak ada data podcast yang ditemukan.'})
    except OperationalError as e:
        return render(request, 'podcast.html', {'error_message': f'Terjadi kesalahan saat mengambil data dari database: {e}'})
    # return render(request, 'podcast.html')

def detail_podcast(request):
    podcast_date = datetime.now()
    context = {'podcast_date': podcast_date}
    return render(request, 'detail_podcast.html', context)