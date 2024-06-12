import datetime
import uuid
from django.shortcuts import render, redirect
from django.db import OperationalError, ProgrammingError, connection
from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseNotFound, JsonResponse
from django.contrib import messages
from datetime import datetime
from django import template
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from dashboardpodcaster.query import *
from dashboardreguser.query import *
from dashboarduser.query import *

# Create your views here.
# register = template.Library()

# @register.filter
def format_durasi(menit):
    if menit is None:
        return '0 jam 0'
    else :
        jam = menit // 60
        sisa_menit = menit % 60
        if jam > 0:
            return f'{jam} jam {sisa_menit}'
        else :
            return sisa_menit

def add_podcast(request):
    if request.method == 'POST':
        email = request.session.get('user_email', None)
        judul = request.POST['judul']
        genre = request.POST.getlist('genreSelect')

        # Buat UUID baru untuk podcast ini
        id_konten = uuid.uuid4()

        with connection.cursor() as cursor:
            # Hitung durasi total dari semua episode
            cursor.execute("""
                SELECT SUM(durasi)
                FROM EPISODE
                WHERE id_konten_podcast = %s
            """, [id_konten])
            durasi = cursor.fetchone()[0] or 0

            cursor.execute("""
                INSERT INTO KONTEN (id, judul, tanggal_rilis, tahun, durasi)
                VALUES (%s, %s, CURRENT_DATE, EXTRACT(YEAR FROM CURRENT_DATE), %s)
                RETURNING id
            """, [id_konten, judul, format_durasi(durasi)])
            id_konten = cursor.fetchone()[0]
            print("id konten podcast")
            print(id_konten)

            cursor.execute("""
                INSERT INTO PODCAST (id_konten, email_podcaster)
                VALUES (%s, %s)
            """, [id_konten, email])

            for g in genre:
                cursor.execute("""
                    INSERT INTO GENRE (id_konten, genre)
                    VALUES (%s, %s)
                """, [id_konten, g])

        return redirect('dashboarduser:homepage')

@csrf_exempt
def delete_podcast(request, id_konten):
    if request.method == 'POST':
        with connection.cursor() as cursor:
            # Cek apakah podcast ada
            cursor.execute("""
                SELECT id FROM KONTEN
                WHERE id = %s
            """, [id_konten])
            podcast = cursor.fetchone()

            # Jika podcast ada, lanjutkan dengan penghapusan
            # Pertama, hapus semua genre yang terkait dengan podcast ini
            cursor.execute("""
                DELETE FROM GENRE
                WHERE id_konten = %s
            """, [id_konten])

            # Kedua, hapus semua episode yang terkait dengan podcast ini
            cursor.execute("""
                DELETE FROM EPISODE
                WHERE id_konten_podcast = %s
            """, [id_konten])

            # Ketiga, hapus podcast dari tabel PODCAST
            cursor.execute("""
                DELETE FROM PODCAST
                WHERE id_konten = %s
            """, [id_konten])

            # Keempat, hapus konten dari tabel KONTEN
            cursor.execute("""
                DELETE FROM KONTEN
                WHERE id = %s
            """, [id_konten])

        return redirect('dashboarduser:homepage')


def update_podcast(request, id_konten):
    if request.method == 'POST':
        print("masuk ke update_podcast")
        print("id_konten")
        print(id_konten)
        judul = request.POST['judul']
        genre = request.POST.getlist('genreSelect')

        with connection.cursor() as cursor:
            # Calculate the total duration of all episodes of the podcast
            cursor.execute(durasi_podcast(id_konten))
            durasi = cursor.fetchone()[0] or 0

            # Update konten
            cursor.execute("""
                UPDATE KONTEN
                SET judul = %s, durasi = %s
                WHERE id = %s
            """, [judul, format_durasi(durasi), id_konten])

            # Hapus genre lama
            cursor.execute(delete_genre(id_konten))

            # Tambahkan genre baru
            for g in genre:
                cursor.execute(add_genre(id_konten, g))

        return redirect('dashboarduser:homepage')

def add_episodes(request, id_konten):
    if request.method == 'POST':
        print(id_konten)
        # Buat ID unik untuk episode baru
        id_episode = uuid.uuid4()

        judul = request.POST['judul']
        deskripsi = request.POST['deskripsi']
        durasi = request.POST['durasi']

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO EPISODE (id_episode, id_konten_podcast, judul, deskripsi, durasi, tanggal_rilis)
                VALUES (%s, %s, %s, %s, %s, CURRENT_DATE)
            """, [id_episode, id_konten, judul, deskripsi, durasi])

        return redirect('dashboard:episodes', id_konten=id_konten)

    return render(request, 'episodes.html')

def delete_episode(request, id_konten, id_episode):
    if request.method == 'POST':
        if id_episode:  # Check if id_episode is not an empty string
            with connection.cursor() as cursor:
                cursor.execute("""
                    DELETE FROM EPISODE
                    WHERE id_episode = %s
                """, [id_episode])

            print(id_konten)
            print("masuk")
            return redirect('dashboard:episodes', id_konten=id_konten)
        else:
            print("gamasuk")
            # Handle case where id_episode is an empty string
            messages.error(request, 'Invalid episode id')
            return redirect('dashboard:episodes', id_konten=id_konten)

    else:
        print("bukan post")
        # Handle non-POST requests here
        messages.error(request, 'Invalid request method')
        return redirect('dashboard:episodes', id_konten=id_konten)

def update_episode(request, id_konten, id_episode):
    if request.method == 'POST':
        judul = request.POST['judul']
        deskripsi = request.POST['deskripsi']
        durasi = request.POST['durasi']

        with connection.cursor() as cursor:
            # Update episode
            cursor.execute("""
                UPDATE EPISODE
                SET judul = %s, deskripsi = %s, durasi = %s
                WHERE id_episode = %s AND id_konten_podcast = %s
            """, [judul, deskripsi, durasi, id_episode, id_konten])

        return redirect('dashboard:episodes', id_konten=id_konten)

    else:
        # Render form untuk update episode
        return render(request, 'episodes.html')
    
def episodes(request, id_konten):
    if 'user_email' in request.session:
        user_email = request.session.get('user_email')

    else:
        return render(request, 'login.html')
    print("masuk ke episode")
    print("id_konten")
    print(id_konten)
    try:
        # Fetch podcast details and its episodes from the database
        with connection.cursor() as cursor:
            query = user_info(user_email)
            cursor.execute(query)
            user_data = cursor.fetchone()
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
                    k.judul, a.nama, k.tanggal_rilis
            """, [id_konten])
            podcast_detail = cursor.fetchone()
            print("podcast detail")
            print(podcast_detail)
            print(podcast_detail[4])

            total_durasi = format_durasi(podcast_detail[4])

            cursor.execute(detail_episode(id_konten))
            episodes = cursor.fetchall()
            episodes = [(id_episode, judul, deskripsi, format_durasi(durasi), tanggal_rilis) for id_episode, judul, deskripsi, durasi, tanggal_rilis in episodes]
            print("len episode")
            print(len(episodes))

            query = get_playlist_akun(user_email)
            print("Generated query:")
            print(query)
            cursor.execute(query)
            playlist_akun = cursor.fetchall()
            print("Result from database:")
            print(playlist_akun)
            try:
                detail_playlist_kelola = [{
                    'namaPlaylist': detail_playlist[2],
                    'jumlahLagu': detail_playlist[4],
                    'durasi': detail_playlist[7],
                    'id_playlist': detail_playlist[6],
                    'deskripsi': detail_playlist[3],
                    'id_user_playlist': detail_playlist[1]
                } for detail_playlist in playlist_akun]
            except IndexError:
                detail_playlist_kelola = []

            # Fetch podcaster's podcast details from the database
            cursor.execute("""
                SELECT 
                    k.id AS id_konten,
                    k.judul AS judul_podcast, 
                    COUNT(e.id_episode) AS jumlah_episode, 
                    SUM(k.durasi) AS total_durasi 
                FROM 
                    podcast p 
                LEFT JOIN 
                    episode e ON p.id_konten = e.id_konten_podcast 
                LEFT JOIN 
                    konten k ON p.id_konten = k.id
                WHERE 
                    p.email_podcaster = %s 
                GROUP BY 
                    k.id, k.judul, p.id_konten
            """, [user_email])
            podcasts = cursor.fetchall()
            podcasts = [(id_konten, judul_podcast, jumlah_episode, format_durasi(total_durasi)) for id_konten, judul_podcast, jumlah_episode, total_durasi in podcasts]

            query_label = show_label()
            cursor.execute(query_label)
            labels = cursor.fetchall()
            print(labels)

            query_artist = show_artist()
            cursor.execute(query_artist)
            artists = cursor.fetchall()
            print(artists)

            query_songwriter = show_songwriter()
            cursor.execute(query_songwriter)
            songwriters = cursor.fetchall()
            print(songwriters)

            query_genre = show_genre()
            cursor.execute(query_genre)
            genres = cursor.fetchall()
            print(genres)

            query_album = show_album(user_email)
            cursor.execute(query_album)
            albums = cursor.fetchall()
            print("albums:")
            print(albums)

            # Prepare context data for rendering
            context = {
                'podcast_detail': podcast_detail,
                'genres_podcast' : list(set(podcast_detail[1])),  # Convert genres to a set to remove duplicates
                'total_durasi' : total_durasi,
                'episodes': episodes,
                'id_konten' : id_konten,
                'user_data': user_data,
                'detail_playlist_kelola':detail_playlist_kelola,
                'albums':[{
                    'id': album[0],
                    'judul': album[1],
                    'jumlah_lagu': album[2],
                    'total_durasi': album[3]
                } for album in albums],
                'labels': [{
                    'id': label[0],
                    'nama':label[1],
                    'id_pemilik_hc':label[5],
                } for label in labels],
                'artists': [{
                    'id': artist[0],
                    'nama':artist[1],
                } for artist in artists],
                'songwriters':[{
                    'id':songwriter[0],
                    'nama':songwriter[1],
                } for songwriter in songwriters],
                'genres':[{
                    'id':genre[0],
                    'genre':genre[1],
                } for genre in genres],
                'podcasts': podcasts,
            }
        return render(request, 'episodes.html', context)
    except OperationalError:
        return HttpResponseNotFound("Database connection error")
