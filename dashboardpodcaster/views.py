import datetime
from django.shortcuts import render, redirect
from django.db import OperationalError, ProgrammingError, connection
from django.http import HttpResponse, HttpResponseNotFound
from django.contrib import messages

# Create your views here.
def format_durasi(menit):
    jam = menit // 60
    sisa_menit = menit % 60
    return f'{jam} jam {sisa_menit} menit' if jam > 0 else f'{sisa_menit} menit'

def podcaster(request):
    # Fetch podcaster's podcast details from the database
    email = request.session.get('user_email', None)
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                k.id AS id_konten,
                a.nama AS nama_podcaster,
                k.judul AS judul_podcast, 
                COUNT(e.id_episode) AS jumlah_episode, 
                SUM(k.durasi) AS total_durasi 
            FROM 
                podcast p 
            LEFT JOIN 
                episode e ON p.id_konten = e.id_konten_podcast 
            LEFT JOIN 
                konten k ON p.id_konten = k.id
            LEFT JOIN 
                akun a ON p.email_podcaster = a.email
            WHERE 
                p.email_podcaster = %s 
            GROUP BY 
                k.id, a.nama, k.judul, p.id_konten
        """, [email])
        podcasts = cursor.fetchall()
    
    podcasts = [(id_konten, nama_podcaster, judul_podcast, jumlah_episode, format_durasi(total_durasi)) for id_konten, nama_podcaster, judul_podcast, jumlah_episode, total_durasi in podcasts]

    # Prepare context data for rendering
    context = {
        'nama_podcaster' : podcasts[0],
        'podcasts': podcasts,
    }

    return render(request, 'podcaster.html', context)

def add_podcast(request):
    if request.method == 'POST':
        # Ambil data dari formulir
        podcast_title_id = request.POST.get('podcastTitleId')
        selected_genres = request.POST.getlist('genreSelect')
        podcaster_email = request.session.get('user_email', None)

        # Ambil judul podcast dari tabel konten
        with connection.cursor() as cursor:
            cursor.execute("SELECT judul FROM konten WHERE id = %s", [podcast_title_id])
            row = cursor.fetchone()
            if row:
                podcast_title = row[0]
            else:
                messages.error(request, 'Judul podcast tidak ditemukan')
                return redirect('podcaster')

        # Tambahkan podcast baru ke tabel podcast di Supabase
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO podcast (podcast_title, podcaster_email) VALUES (%s, %s)", [podcast_title, podcaster_email])

        # Ambil id podcast yang baru ditambahkan
        with connection.cursor() as cursor:
            cursor.execute("SELECT id FROM podcast WHERE podcast_title = %s AND podcaster_email = %s", [podcast_title, podcaster_email])
            podcast_id = cursor.fetchone()[0]

        # Tambahkan genre yang dipilih ke tabel podcast_genre di Supabase
        for genre_id in selected_genres:
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO podcast_genre (podcast_id, genre_id) VALUES (%s, %s)", [podcast_id, genre_id])

        messages.success(request, 'Podcast berhasil ditambahkan!')
        return redirect('podcaster')
    
def delete_podcast(request, id_konten):
    if request.method == 'POST':
        with connection.cursor() as cursor:
            # Delete the associated records from the akun_play_user_playlist table
            cursor.execute("DELETE FROM akun_play_user_playlist WHERE id_user_playlist = %s", [id_konten])
            # Then delete the playlist from the user_playlist table
            cursor.execute("DELETE FROM user_playlist WHERE id_user_playlist = %s", [id_konten])

        return redirect('podcaster')
    
def episodes(request, id_konten):
    # Fetch podcast details and its episodes from the database
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                k.judul AS judul_podcast, 
                array_agg(g.genre) AS genre_podcast,
                a.nama AS nama_podcaster,
                COUNT(e.id_episode) AS total_episode,
                SUM(e.durasi) AS total_durasi,
                k.tanggal_rilis AS tanggal_rilis_podcast,
                EXTRACT(YEAR FROM k.tanggal_rilis) AS tahun_podcast
            FROM 
                konten k
            LEFT JOIN 
                podcast p ON k.id = p.id_konten
            LEFT JOIN 
                episode e ON p.id_konten = e.id_konten_podcast
            LEFT JOIN 
                akun a ON p.email_podcaster = a.email
            JOIN 
                genre g ON k.id = g.id_konten
            WHERE 
                k.id = %s
            GROUP BY 
                k.judul, g.genre, a.nama, k.tanggal_rilis
        """, [id_konten])
        podcast_detail = cursor.fetchone()

        total_durasi = format_durasi(podcast_detail[4])

        cursor.execute("""
            SELECT 
                judul, deskripsi, durasi, tanggal_rilis
            FROM 
                episode
            WHERE 
                id_konten_podcast = %s
        """, [id_konten])
        episodes = cursor.fetchall()

        episodes = [(judul, deskripsi, format_durasi(durasi), tanggal_rilis) for judul, deskripsi, durasi, tanggal_rilis in episodes]
        
    # Prepare context data for rendering
    context = {
        'podcast_detail': podcast_detail,
        'total_durasi' : total_durasi,
        'episodes': episodes,
    }

    return render(request, 'episodes.html', context)
