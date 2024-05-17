import datetime
import uuid
from django.shortcuts import render, redirect
from django.db import OperationalError, ProgrammingError, connection
from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseNotFound, JsonResponse
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
        judul = request.POST['judul']
        genre = request.POST.getlist('genre')
        durasi = request.POST['durasi']

        # Buat UUID baru untuk podcast ini
        id_konten = uuid.uuid4()

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO KONTEN (id, judul, tanggal_rilis, tahun, durasi)
                VALUES (%s, %s, CURRENT_DATE, EXTRACT(YEAR FROM CURRENT_DATE), %s)
                RETURNING id
            """, [id_konten, judul, durasi])
            podcast_id = cursor.fetchone()[0]

            for g in genre:
                cursor.execute("""
                    INSERT INTO GENRE (id_konten, genre)
                    VALUES (%s, %s)
                """, [podcast_id, g])

        return redirect('dashboard:podcaster')

    return render(request, 'podcaster.html')


def delete_podcast(request, id_konten):
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("""
                DELETE FROM KONTEN
                WHERE id = %s
            """, [id_konten])

        return redirect('dashboard:podcaster')
    
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

def add_episodes(request,id_konten):
    if request.method == 'POST':
        # Buat ID unik untuk konten baru
        id_konten = uuid.uuid4()

        judul = request.POST['judul']
        deskripsi = request.POST['deskripsi']
        durasi = request.POST['durasi']

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO EPISODE (id_konten_podcast, judul, deskripsi, durasi)
                VALUES (%s, %s, %s, %s)
            """, [id_konten, judul, deskripsi, durasi])

        return redirect('dashboard:episodes', id_konten=id_konten)

    return render(request, 'episodes.html')

def delete_episode(request, id_konten):
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("""
                DELETE FROM EPISODE
                WHERE id = %s
            """, [id_konten])

        return redirect('episodes')