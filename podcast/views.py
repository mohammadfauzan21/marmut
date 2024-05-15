from django.shortcuts import render
from datetime import datetime
from django.db import OperationalError, connection

# Create your views here.
def podcast_view(request):
    try:
        with connection.cursor() as cursor:
            # Fetch podcast details
            cursor.execute("""
                SELECT K.judul AS judul_podcast, A.nama AS nama_podcaster, K.durasi AS durasi_podcast
                FROM podcast P
                JOIN konten K ON P.id_konten = K.id
                JOIN podcaster Po ON P.email_podcaster = Po.email
                JOIN akun A ON Po.email = A.email;
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