import datetime
import uuid
from django.shortcuts import render, redirect
from django.db import OperationalError, connection
from django.http import HttpResponseBadRequest, HttpResponseNotFound
from django.contrib import messages
from datetime import datetime
from django.urls import reverse
from django.views.decorators.cache import never_cache

from kelola.query import *
from playlist.query import *
from dashboarduser.query import *

def format_durasi(detik):
    if detik is None:
        return '0 jam 0 menit 0 detik'
    else:
        jam = detik // 3600
        sisa_detik = detik % 3600
        menit = sisa_detik // 60
        detik_akhir = sisa_detik % 60
        if jam == 0:
            if menit == 0:
                return f'{detik_akhir} detik'
            else:
                if detik_akhir == 0:
                    return f'{menit} menit'
                else:
                    return f'{menit} menit {detik_akhir} detik'
        else:
            if detik_akhir == 0:
                return f'{jam} jam {menit} menit'
            else:
                return f'{jam} jam {menit} menit {detik_akhir} detik'

def format_durasi_kelola(detik):
    if detik is None:
        return '0 jam 0 menit 0 detik'
    else:
        jam = detik // 3600
        sisa_detik = detik % 3600
        menit = sisa_detik // 60
        detik_akhir = sisa_detik % 60
        if jam < 10:
            if menit < 10:
                if detik_akhir < 10:
                    return f'0{jam}:0{menit}:0{detik_akhir}'
                else:
                    return f'0{jam}:0{menit}:{detik_akhir}'
            else:
                if detik_akhir < 10:
                    return f'0{jam}:{menit}:0{detik_akhir}'
                else:
                    return f'0{jam}:{menit}:{detik_akhir}'
        else:
            if menit < 10:
                if detik_akhir < 10:
                    return f'{jam}:0{menit}:0{detik_akhir}'
                else:
                    return f'{jam}:0{menit}:{detik_akhir}'
            else:
                if detik_akhir < 10:
                    return f'{jam}:{menit}:0{detik_akhir}'
                else:
                    return f'{jam}:{menit}:{detik_akhir}'

@never_cache
def add_podcast(request):
    email = request.session.get('user_email')
    if not email:
        return redirect('login:loginkonten')
    if request.method == 'POST':
        url_now = request.session.get('url_now')
        judul = request.POST['judul']
        if len(judul) > 100:
            messages.error(request, "Judul terlalu panjang. Maksimum 100 karakter.")
            return redirect(url_now)
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
            """, [id_konten, judul, durasi])
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

        return redirect(url_now)

# @csrf_exempt
@never_cache
def delete_podcast(request, id_konten):
    email = request.session.get('user_email')
    if not email:
        return redirect('login:loginkonten')
    if request.method == 'POST':
        url_now = request.session.get('url_now')
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

        return redirect(url_now)

@never_cache
def update_podcast(request, id_konten):
    email = request.session.get('user_email')
    if not email:
        return redirect('login:loginkonten')
    if request.method == 'POST':
        print("masuk ke update_podcast")
        url_now = request.session.get('url_now')
        print("id_konten")
        print(id_konten)
        judul = request.POST['judul']
        if len(judul) > 100:
            messages.error(request, "Judul terlalu panjang. Maksimum 100 karakter.")
            return redirect(url_now)
        
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
            """, [judul, durasi, id_konten])

            # Hapus genre lama
            cursor.execute(delete_genre(id_konten))

            # Tambahkan genre baru
            for g in genre:
                cursor.execute(add_genre(id_konten, g))

        return redirect(url_now)

@never_cache
def add_episodes(request, id_konten):
    email = request.session.get('user_email')
    if not email:
        return redirect('login:loginkonten')
    if request.method == 'POST':
        print("add_episode")
        print(id_konten)
        # Buat ID unik untuk episode baru
        id_episode = uuid.uuid4()

        judul = request.POST['judulEpisode']
        deskripsi = request.POST['deskripsi']
        durasi_menit = request.POST['durasiMenit']
        print(durasi_menit)
        durasi_detik = request.POST['durasiDetik']
        print(durasi_detik)
        durasi_fix = (int(durasi_menit)*60)+int(durasi_detik)
        print(durasi_fix)


        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO EPISODE (id_episode, id_konten_podcast, judul, deskripsi, durasi, tanggal_rilis)
                VALUES (%s, %s, %s, %s, %s, CURRENT_DATE)
            """, [id_episode, id_konten, judul, deskripsi, durasi_fix])

        return redirect('kelola:podcast', id_konten=id_konten)
    else:
        return render(request, 'episodes.html')

@never_cache
def delete_episode(request, id_konten, id_episode):
    email = request.session.get('user_email')
    if not email:
        return redirect('login:loginkonten')
    if request.method == 'POST':
        if id_episode:  # Check if id_episode is not an empty string
            with connection.cursor() as cursor:
                cursor.execute("""
                    DELETE FROM EPISODE
                    WHERE id_episode = %s
                """, [id_episode])

            print(id_konten)
            print("masuk")
            return redirect('kelola:podcast', id_konten=id_konten)
        else:
            print("gamasuk")
            # Handle case where id_episode is an empty string
            messages.error(request, 'Invalid episode id')
            return redirect('kelola:podcast', id_konten=id_konten)

    else:
        print("bukan post")
        # Handle non-POST requests here
        messages.error(request, 'Invalid request method')
        return redirect('kelola:podcast', id_konten=id_konten)

@never_cache
def update_episode(request, id_konten, id_episode):
    email = request.session.get('user_email')
    if not email:
        return redirect('login:loginkonten')
    if request.method == 'POST':
        judul = request.POST['judulEpisode']

        deskripsi = request.POST['deskripsi']
        durasi_menit = request.POST['durasiMenit']
        print(durasi_menit)
        durasi_detik = request.POST['durasiDetik']
        print(durasi_detik)
        durasi_fix = (int(durasi_menit)*60)+int(durasi_detik)
        print(durasi_fix)

        with connection.cursor() as cursor:
            # Update episode
            cursor.execute("""
                UPDATE EPISODE
                SET judul = %s, deskripsi = %s, durasi = %s
                WHERE id_episode = %s AND id_konten_podcast = %s
            """, [judul, deskripsi, durasi_fix, id_episode, id_konten])

        return redirect('kelola:podcast', id_konten=id_konten)

    else:
        # Render form untuk update episode
        return render(request, 'episodes.html')

def podcast(request, id_konten):
    #Mengambil url dari page yang sedang ditampilkan
    url_now = request.build_absolute_uri()
    request.session['url_now'] = url_now
    user_email = request.session.get('user_email')
    if not user_email:
        return redirect('login:loginkonten')
    
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
            if podcast_detail is None:
                if 'label' not in request.session.get('user_type'):
                    return redirect('dashboarduser:homepage')
                else:
                    return redirect('dashboardlabel:homepagelabel')
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
                    'durasi': format_durasi_kelola(detail_playlist[7]),
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
                    k.durasi AS total_durasi 
                FROM 
                    podcast p 
                LEFT JOIN 
                    konten k ON p.id_konten = k.id
                LEFT JOIN 
                    episode e ON p.id_konten = e.id_konten_podcast 
                WHERE 
                    p.email_podcaster = %s 
                GROUP BY 
                    k.id, k.judul, k.durasi
            """, [user_email])
            podcasts = cursor.fetchall()
            podcasts = [(id_konten, judul_podcast, jumlah_episode, format_durasi_kelola(total_durasi)) for id_konten, judul_podcast, jumlah_episode, total_durasi in podcasts]

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
                    'total_durasi': format_durasi_kelola(album[3]),
                    'id_pemilik_hak_cipta':album[4],
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

def album(request, id_album):
    #Mengambil url dari page yang sedang ditampilkan
    url_now = request.build_absolute_uri()
    request.session['url_now'] = url_now
    print("masuk kelola album")
    user_email = request.session.get('user_email')
    if not user_email:
        return redirect('login:loginkonten')
    print("ngeprint email")
    print(user_email)
    print("id_laylist = ")
    print(id_album)
    try:
        # current_url = request.build_absolute_uri()
        # request.session['prev_url'] = current_url
        # print("Session = " + request.session.get('prev_url', ''))
        with connection.cursor() as cursor:
            query = user_info(user_email)
            cursor.execute(query)
            user_data = cursor.fetchone()

            query_header = get_detail_album_header(id_album)
            cursor.execute(query_header)
            album_header = cursor.fetchone()
            print(album_header)

            if album_header is None:
                if 'label' not in request.session.get('user_type'):
                    return redirect('dashboarduser:homepage')
                else:
                    return redirect('dashboardlabel:homepagelabel')
            
            # Fetch podcaster's podcast details from the database
            cursor.execute("""
                SELECT 
                    k.id AS id_konten,
                    k.judul AS judul_podcast, 
                    COUNT(e.id_episode) AS jumlah_episode, 
                    k.durasi AS total_durasi 
                FROM 
                    podcast p 
                LEFT JOIN 
                    konten k ON p.id_konten = k.id
                LEFT JOIN 
                    episode e ON p.id_konten = e.id_konten_podcast 
                WHERE 
                    p.email_podcaster = %s 
                GROUP BY 
                    k.id, k.judul, k.durasi
            """, [user_email])
            podcasts = cursor.fetchall()
            podcasts = [(id_konten, judul_podcast, jumlah_episode, format_durasi_kelola(total_durasi)) for id_konten, judul_podcast, jumlah_episode, total_durasi in podcasts]
            
            query = get_detail_album(id_album)
            cursor.execute(query)
            detail_album = cursor.fetchall()
            print("ini detail")
            print(detail_album)

            query = get_playlist_akun(user_email)
            cursor.execute(query)
            playlist_akun = cursor.fetchall()
            print("playlist_akun")
            
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
            print(albums)

            context = {
                'label' : album_header[0],
                'durasi': format_durasi(album_header[1]),
                'jumlah_lagu': album_header[2],
                'judul_album':album_header[3],
                'detail_album': [{
                    "no":i+1,
                    "konten_id":detail[0],
                    "judul":detail[1],
                    "durasi":format_durasi(detail[2]),
                    "total_play":detail[3],
                    "total_download":detail[4],
                } for i, detail in enumerate(detail_album)],
                'detail_playlist_kelola': [{
                    'namaPlaylist': detail_playlist[2],
                    'jumlahLagu': detail_playlist[4],
                    'durasi': format_durasi_kelola(detail_playlist[7]),
                    'id_playlist': detail_playlist[6],
                    'deskripsi':detail_playlist[3],
                    'id_user_playlist':detail_playlist[1]
                } for detail_playlist in playlist_akun],
                'albums':[{
                    'id': album[0],
                    'judul': album[1],
                    'jumlah_lagu': album[2],
                    'total_durasi': format_durasi_kelola(album[3]),
                    'id_pemilik_hak_cipta':album[4],
                } for album in albums],
                'user_data': user_data, 
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
            print(context)
            return render(request, 'album.html', context)
    except OperationalError:
        return HttpResponseNotFound("Database connection error")

@never_cache
def create_album(request):
    email = request.session.get('user_email')
    if not email:
        return redirect('login:loginkonten')
    if request.method == 'POST':
        url_now = request.session.get('url_now')
        id_album = uuid.uuid4()
        print("id_album:")
        print(id_album)
        judul_album = request.POST.get('judulAlbum')

        if len(judul_album) > 100:
            messages.error(request, "Judul terlalu panjang. Maksimum 100 karakter.")
            return redirect(url_now)
        
        id_label = request.POST.get('label')
        try:
            with connection.cursor() as cursor:
                print("id_label:")
                print(id_label)
                print("judul_album:")
                print(judul_album)
                cursor.execute(get_id_pemilik_hak_cipta_label(id_label))
                id_pemilik_hak_cipta_label = cursor.fetchone()
                cursor.execute(create_new_album(), [id_album, judul_album, id_label])
                create_song(request, id_album, id_pemilik_hak_cipta_label[0])
                return redirect(url_now)
        except OperationalError:
            return HttpResponseNotFound("Database connection error")

@never_cache
def create_song(request, id_album, id_pemilik_hak_cipta_label):
    user_email = request.session.get('user_email')
    if not user_email:
        return redirect('login:loginkonten')
    if request.method == 'POST' or request.method != 'POST':
        print(id_pemilik_hak_cipta_label)
        url_now = request.session.get('url_now')
        print('apa')
        print("id album:")
        print(id_album)
        #song
        id_konten = uuid.uuid4()
        print("id_konten:")
        print(id_konten)
        id_artist = request.POST.get('artist')
        print(user_email)
        print("id_artist:")
        print(id_artist)

        #konten
        judul_lagu = request.POST.get('judulLagu')
        if len(judul_lagu) > 100:
            messages.error(request, "Judul terlalu panjang. Maksimum 100 karakter.")
            return redirect(url_now)
        
        tanggal_dibuat = datetime.now()
        durasi_menit = request.POST.get('durasiMenit')
        print(durasi_menit)
        durasi_detik = request.POST.get('durasiDetik')
        print(durasi_detik)
        durasi_fix = (int(durasi_menit)*60)+int(durasi_detik)
        print(durasi_fix)

        #genre and songwriter
        songwriters = request.POST.getlist('songwriter')
        genres = request.POST.getlist('genreSelect')
        print("songwriter:")
        print(songwriters)
        print(len(songwriters))
        print("genre:")
        print(genres)

        try:
            with connection.cursor() as cursor:
                cursor.execute(add_konten(id_konten, judul_lagu, tanggal_dibuat, durasi_fix))
                if id_artist == None:
                    cursor.execute(user_id_artist(user_email))
                    id_artist = cursor.fetchone()
                    print("id_artist:")
                    print(id_artist)
                    cursor.execute(add_song_to_album(id_konten, id_artist[0], id_album))
                else:
                    cursor.execute(add_song_to_album(id_konten, id_artist, id_album))
                if len(songwriters) < 1 :
                    cursor.execute(user_id_songwriter(user_email))
                    id_songwriter = cursor.fetchone()
                    print("id_songwriter:")
                    print(id_songwriter)
                for songwriter in songwriters:
                    cursor.execute(add_songwriter(songwriter, id_konten))
                for genre in genres:
                    cursor.execute(add_genre(id_konten, genre))

                #royalti
                print("royalti")
                query = get_artist_id_pemilik_hak_cipta(user_email)
                cursor.execute(query)
                artist_id_pemilik_hak_cipta = cursor.fetchone()
                print("artist_id_pemilik_hak_cipta")
                print(artist_id_pemilik_hak_cipta)

                query = get_songwriter_id_pemilik_hak_cipta(user_email)
                cursor.execute(query)
                songwriter_id_pemilik_hak_cipta = cursor.fetchone()
                print("songwriter_id_pemilik_hak_cipta")
                print(songwriter_id_pemilik_hak_cipta)

                if artist_id_pemilik_hak_cipta != None:
                    print("artist_id_pemilik_hak_cipta[0]")
                    print(artist_id_pemilik_hak_cipta[0])
                    cursor.execute(add_royalti(artist_id_pemilik_hak_cipta[0], id_konten))
                else:
                    cursor.execute(get_id_pemilik_hak_cipta_artist(id_artist))
                    id_pemilik_hak_cipta_artist = cursor.fetchone()
                    print("id_pemilik_hak_cipta_artist")
                    print(id_pemilik_hak_cipta_artist)
                    cursor.execute(add_royalti(id_pemilik_hak_cipta_artist[0], id_konten))

                if songwriter_id_pemilik_hak_cipta != None:
                    print("songwriter_id_pemilik_hak_cipta[0]")
                    print(songwriter_id_pemilik_hak_cipta[0])
                    cursor.execute(add_royalti(songwriter_id_pemilik_hak_cipta[0], id_konten))
                else:
                    for songwriter in songwriters:
                        cursor.execute(get_id_pemilik_hak_cipta_songwriter(songwriter))
                        id_pemilik_hak_cipta_songwriter = cursor.fetchone()
                        print("id_pemilik_hak_cipta_songwriter[0]")
                        print(id_pemilik_hak_cipta_songwriter[0])
                        cursor.execute(add_royalti(id_pemilik_hak_cipta_songwriter[0], id_konten))

                cursor.execute(add_royalti(id_pemilik_hak_cipta_label, id_konten))

            if request.method == 'POST':
                return redirect(url_now)
        except OperationalError:
            return HttpResponseNotFound("Database connection error")

@never_cache
def delete_album(request, id_album):
    user_email = request.session.get('user_email')
    if not user_email:
        return redirect('login:loginkonten')
    url_now = request.session.get('url_now')
    print(url_now)
    print("id di delete_album:")
    print(id_album)
    if request.method == 'POST':
        try:
            with connection.cursor() as cursor:
                print("delete_album_royalti")
                cursor.execute(delete_album_royalti(id_album))
                print("delete_album_downloaded_song")
                cursor.execute(delete_album_downloaded_song(id_album))
                print("delete_album_akun_play_song")
                cursor.execute(delete_album_akun_play_song(id_album))
                print("delete_album_playlist_song")
                cursor.execute(delete_album_playlist_song(id_album))
                print("delete_album_songwriter_write_song")
                cursor.execute(delete_album_songwriter_write_song(id_album))
                print("delete_song")
                cursor.execute(delete_song(id_album))
                print("delete_album")
                cursor.execute(delete_album_query(id_album))
                print("operasi sudah selesai")

            print("diatas redirect")
            return redirect(url_now)
        except OperationalError:
            return HttpResponseNotFound("Database connection error")
    return HttpResponseNotFound("Invalid request method")

def playlist(request, id_playlist):
    #Mengambil url dari page yang sedang ditampilkan
    url_now = request.build_absolute_uri()
    request.session['url_now'] = url_now
    user_email = request.session.get('user_email')
    if not user_email:
        return redirect('login:loginkonten')
    print("ngeprint email")
    print(user_email)
    print("id_laylist = ")
    print(id_playlist)
    error_message = request.GET.get('error', None)
    try:
        # current_url = request.build_absolute_uri()
        # request.session['prev_url'] = current_url
        # print("Session = " + request.session.get('prev_url', ''))
        with connection.cursor() as cursor:
            query = user_info(user_email)
            cursor.execute(query)
            user_data = cursor.fetchone()

            # Fetch podcaster's podcast details from the database
            cursor.execute("""
                SELECT 
                    k.id AS id_konten,
                    k.judul AS judul_podcast, 
                    COUNT(e.id_episode) AS jumlah_episode, 
                    k.durasi AS total_durasi 
                FROM 
                    podcast p 
                LEFT JOIN 
                    konten k ON p.id_konten = k.id
                LEFT JOIN 
                    episode e ON p.id_konten = e.id_konten_podcast 
                WHERE 
                    p.email_podcaster = %s 
                GROUP BY 
                    k.id, k.judul, k.durasi
            """, [user_email])
            podcasts = cursor.fetchall()
            podcasts = [(id_konten, judul_podcast, jumlah_episode, format_durasi_kelola(total_durasi)) for id_konten, judul_podcast, jumlah_episode, total_durasi in podcasts]

            query_header = get_detail_playlist_header(id_playlist)
            cursor.execute(query_header)
            playlist_header = cursor.fetchone()
            print(playlist_header)

            # Check if playlist is None
            if playlist_header is None:
                if 'label' not in request.session.get('user_type'):
                    return redirect('dashboarduser:homepage')
                else:
                    return redirect('dashboardlabel:homepagelabel')
            
            query = get_detail_playlist(id_playlist)
            cursor.execute(query)
            detail_playlist = cursor.fetchall()
            print("ini detail")
            print(detail_playlist)

            query = show_song()
            cursor.execute(query)
            list_song=cursor.fetchall()
            print(list_song)

            query = get_playlist_akun(user_email)
            cursor.execute(query)
            playlist_akun = cursor.fetchall()

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
            print(albums)

            context = {
                'pembuat' : playlist_header[0],
                'jumlah_lagu': playlist_header[1],
                'durasi':format_durasi(playlist_header[2]),
                'tanggal_buat':playlist_header[3],
                'judul_playlist':playlist_header[4],
                'deskripsi_playlist':playlist_header[5], 
                'id_playlist':id_playlist,
                'detail_playlist': [{
                    "no":i+1,
                    "judulLagu":detail[0],
                    "artist":detail[1],
                    "durasi":format_durasi(detail[2]),
                    "id_konten":detail[3]
                } for i, detail in enumerate(detail_playlist)],
                'list_song':[{
                    'id':song[0],
                    'judul':song[1],
                    'pembuat':song[2]
                }for song in list_song],
                'detail_playlist_kelola': [{
                    'namaPlaylist': detail_playlist[2],
                    'jumlahLagu': detail_playlist[4],
                    'durasi': format_durasi_kelola(detail_playlist[7]),
                    'id_playlist': detail_playlist[6],
                    'deskripsi':detail_playlist[3],
                    'id_user_playlist':detail_playlist[1]
                } for detail_playlist in playlist_akun],
                'albums':[{
                    'id': album[0],
                    'judul': album[1],
                    'jumlah_lagu': album[2],
                    'total_durasi': format_durasi_kelola(album[3]),
                    'id_pemilik_hak_cipta':album[4],
                } for album in albums],
                'user_data': user_data, 
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
                'error_message': error_message
            }
            print(context)
            return render(request, 'playlist.html', context)
    except OperationalError:
        return HttpResponseNotFound("Database connection error")
    
@never_cache
def delete_playlist(request, id_user_playlist):
    user_email = request.session.get('user_email')
    if not user_email:
        return redirect('login:loginkonten')
    if request.method == 'POST':
        url_now = request.session.get('url_now')
        try:
            with connection.cursor() as cursor:
                # Hapus akun_play_user_playlist
                cursor.execute(delete_akun_play_user_playlist(id_user_playlist))
                # Dapatkan id_playlist
                cursor.execute(get_id_playlist(id_user_playlist))
                id_playlist = cursor.fetchone()
                print("id_playlist")
                print(id_playlist)
                # Hapus user_playlist
                cursor.execute(delete_user_playlist(id_user_playlist))
                # Hapus playlist_song dan playlist
                for i in id_playlist:
                    print(i)
                    cursor.execute(delete_playlist_song(i))
                    cursor.execute(delete_playlist_query(i))
            return redirect(url_now)
        except OperationalError:
            return HttpResponseNotFound("Database connection error")

@never_cache
def add_playlist(request):
    user_email = request.session.get('user_email')
    if not user_email:
        return redirect('login:loginkonten')
    if request.method == 'POST':
        url_now = request.session.get('url_now')
        id_user_playlist = uuid.uuid4()
        print(id_user_playlist)
        # Mendapatkan nilai judul dan deskripsi dari permintaan POST
        judul = request.POST.get('judul')
        print(judul)
        deskripsi = request.POST.get('deskripsi')

        # Memeriksa apakah judul dan deskripsi ada dalam permintaan POST
        if not judul or not deskripsi:
            return HttpResponseBadRequest("Judul dan/atau deskripsi tidak ada dalam permintaan POST")
        
        if len(judul) > 100:
            messages.error(request, "Judul terlalu panjang. Maksimum 100 karakter.")
            return redirect(url_now)

        jumlah_lagu = 0
        tanggal_dibuat = datetime.now()
        total_durasi = 0

        try:
            with connection.cursor() as cursor:
                print("masuk")
                id_playlist = uuid.uuid4()
                print("masuk2")
                cursor.execute(insert_id_playlist(id_playlist))

                cursor.execute(insert_user_playlist(user_email, id_user_playlist, judul, deskripsi, jumlah_lagu, tanggal_dibuat, id_playlist, total_durasi))

            return redirect(url_now)
        except OperationalError:
            return HttpResponseNotFound("Database connection error")

@never_cache
def ubah_playlist(request, id_playlist):
    print("masuk ke ubah_playlist")
    print(id_playlist)
    user_email = request.session.get('user_email')
    if not user_email:
        return redirect('login:loginkonten')
    if request.method == 'POST':
        url_now = request.session.get('url_now')
        judul = request.POST.get('judul')
        deskripsi = request.POST.get('deskripsi')

        if len(judul) > 100:
            messages.error(request, "Judul terlalu panjang. Maksimum 100 karakter.")
            return redirect(url_now)

        # Memeriksa apakah judul dan deskripsi ada dalam permintaan POST
        if not judul or not deskripsi:
            return HttpResponseBadRequest("Judul dan/atau deskripsi tidak ada dalam permintaan POST")
        try:
            with connection.cursor() as cursor:
                cursor.execute(ubah_playlist_query(judul, deskripsi, id_playlist))
            return redirect(url_now)
        except OperationalError:
            return HttpResponseNotFound("Database connection error")
        
@never_cache
def add_song_to_playlist(request, id_playlist):
    user_email = request.session.get('user_email')
    if not user_email:
        return redirect('login:loginkonten')
    if request.method == 'POST':
        song_id = request.POST.get('song_id')
        print("song_id")
        print(song_id)
        print(id_playlist)
        if song_id:
            try:
                with connection.cursor() as cursor:
                    cursor.execute(check_song(song_id, id_playlist))
                    if cursor.fetchone() is not None:
                        # If the song is already in the playlist, return an error message
                        request.session['back'] = '2'
                        return redirect(f"{reverse('kelola:playlist', args=[id_playlist])}?error=Song+is+already+in+the+playlist.")
                    cursor.execute(add_song(song_id, id_playlist))
                    request.session['back'] = '2'
                    return redirect(f"{reverse('kelola:playlist', args=[id_playlist])}")
            except OperationalError:
                return HttpResponseNotFound("Database connection error")
            
@never_cache
def delete_song_plylist(request, id_konten, id_playlist):
    user_email = request.session.get('user_email')
    if not user_email:
        return redirect('login:loginkonten')
    if request.method == 'POST':
        try:
            with connection.cursor() as cursor:
                # Hapus playlist
                cursor.execute(delete_song_playlist(id_konten))
            return redirect(f"{reverse('kelola:playlist', args=[id_playlist])}")
        except OperationalError:
            return HttpResponseNotFound("Database connection error")