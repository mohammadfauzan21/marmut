import datetime
import uuid
from django.shortcuts import render, redirect
from django.db import OperationalError, ProgrammingError, connection
from django.http import HttpResponse, HttpResponseNotFound
from django.contrib import messages
from datetime import datetime

from django.urls import reverse

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
        email = request.session['user_email']
        judul = request.POST['judul']
        # Ambil pilihan genre yang dipilih
        genre = request.POST.getlist('genre')

        # Buat podcast baru
        id_podcast = uuid.uuid4()
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO podcast (id) VALUES (%s)", [id_podcast])

        # Simpan informasi podcast ke dalam database
        id_user_podcast = uuid.uuid4()
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO user_podcast 
                (email, id_user_podcast, judul, id_podcast) 
                VALUES (%s, %s, %s, %s, %s)
            """, [email, id_user_podcast, judul, id_podcast])

        # Simpan genre yang dipilih ke dalam database
        with connection.cursor() as cursor:
            for genre_id in genre:
                cursor.execute("""
                    INSERT INTO konten 
                    (id_konten, genre) 
                    VALUES (%s, %s)
                """, [id_podcast, genre_id])

        return redirect('podcast')

    return render(request, 'addpodcast.html', {'daftar_genre': genre})

    
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
        'id_konten' : id_konten,
    }

    print(context)
    return render(request, 'episodes.html', context)

def add_episodes(request, id_konten):
    if request.method == 'POST':
        id_episode = uuid.uuid4()
        judul = request.POST.get('judul')
        deskripsi = request.POST.get('deskripsi')
        durasi = int(request.POST.get('durasi'))

        # Simpan data episode ke dalam database
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO episode (id_episode, judul, deskripsi, durasi, tanggal_rilis)
                VALUES (%s, %s, %s, %s, CURRENT_DATE)
            """, [id_episode, judul, deskripsi, durasi])

        id_konten = request.POST.get('id_konten')
        # Redirect ke halaman yang sesuai setelah berhasil menambahkan episode
        return redirect('episodes', id_konten=id_konten)
    
    with connection.cursor() as cursor:
        cursor.execute(""" 
            SELECT 
                e.id_konten_podcast, 
                k.judul AS judul_podcast, 
                e.judul AS judul_episode, 
                e.deskripsi AS deskripsi_episode, 
                e.durasi AS durasi_episode, 
                e.tanggal_rilis AS tanggal_rilis_episode
            FROM 
                episode e 
            JOIN 
                konten k ON s.id_konten = k.id 
            JOIN 
                podcast p ON e.id_konten_podcast = p.id 
            JOIN 
                akun a ON p.email_akun = a.email
            JOIN 
                episode e ON e.id_konten = e.id_konten_podcast
            WHERE 
                e.tanggal_rilis <= CURRENT_DATE;

                        """)
        eps = cursor.fetchall()  # Get all songs

    return render(request, 'addsong.html', {'eps': eps})
