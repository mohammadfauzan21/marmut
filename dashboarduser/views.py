from django.db import OperationalError, connection
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import redirect, render

from dashboardreguser.query import get_playlist_akun


# Roles session untuk atur hak akses navbar
def roles_session(request):
    user_roles = request.session.get('user_roles')
    return render(request, 'roles_session.html', {'user_roles': user_roles})


def homepage(request):
    if 'user_email' in request.session:
        user_email = request.session.get('user_email')
        user_type = request.session.get('user_type')

    else:
        return render(request, 'login.html')


    user_data = None
    roles = []

    if user_type == "verified":
    # Query untuk pengguna yang telah terverifikasi
        query = """
            SELECT a.nama, a.email, a.kota_asal, 
                CASE WHEN a.gender = 0 THEN 'Laki-Laki' ELSE 'Perempuan' END AS gender,
                a.tempat_lahir,
                ar.id AS artist_id,
                sw.id AS songwriter_id,
                p.email AS podcaster_email
            FROM akun a
            LEFT JOIN artist ar ON a.email = ar.email_akun
            LEFT JOIN songwriter sw ON a.email = sw.email_akun
            LEFT JOIN podcaster p ON a.email = p.email
            WHERE a.email = %s
        """

        try:
            with connection.cursor() as cursor:
                cursor.execute(query, [user_email])
                user_data = cursor.fetchone()
                if user_data:
                    roles = []
                    if user_data[5]:  # artist_id
                        roles.append("Artist")
                    if user_data[6]:  # songwriter_id
                        roles.append("Songwriter")
                    if user_data[7]:  # podcaster_email
                        roles.append("Podcaster")
                        
                query = get_playlist_akun(user_email)
                print("Generated query:")
                print(query)

                if query:
                    print("masuk if")
                    cursor.execute(query)
                    playlist_akun = cursor.fetchall()
                    print("Result from database:")
                    print(playlist_akun)
                    if playlist_akun:
                        context = {
                            'detail_playlist_kelola': [{
                                'namaPlaylist': detail_playlist[2],
                                'jumlahLagu': detail_playlist[4],
                                'durasi': detail_playlist[7],
                                'id_playlist': detail_playlist[6],
                                'deskripsi':detail_playlist[3],
                                'id_user_playlist':detail_playlist[1]
                            } for detail_playlist in playlist_akun],
                            'user_data': user_data, 
                            'roles': roles,
                        }
                    else:
                        context = {
                            'detail_playlist_kelola': [],
                            'user_data': user_data, 
                            'roles': roles,
                        }
                else:
                    context = {
                        'detail_playlist_kelola': [],
                        'user_data': user_data, 
                        'roles': roles,
                    }
        except OperationalError:
            return HttpResponseNotFound("Database connection error")
        
    elif user_type == "unverified":
        # Query untuk pengguna yang belum terverifikasi
        query = """
            SELECT a.nama, a.email, a.kota_asal, 
                CASE WHEN a.gender = 0 THEN 'Laki-Laki' ELSE 'Perempuan' END AS gender,
                a.tempat_lahir,
                ''
            FROM akun a
            WHERE a.email = %s
        """
        with connection.cursor() as cursor:
            cursor.execute(query, [user_email])
            user_data = cursor.fetchone()
            if user_data:
                roles.append("Tidak ada Role")
            if query:
                print("masuk if")
                cursor.execute(query)
                playlist_akun = cursor.fetchall()
                print("Result from database:")
                print(playlist_akun)
                if playlist_akun:
                    context = {
                        'detail_playlist_kelola': [{
                            'namaPlaylist': detail_playlist[2],
                            'jumlahLagu': detail_playlist[4],
                            'durasi': detail_playlist[7],
                            'id_playlist': detail_playlist[6],
                            'deskripsi':detail_playlist[3],
                            'id_user_playlist':detail_playlist[1]
                        } for detail_playlist in playlist_akun],
                        'user_data': user_data, 
                        'roles': roles,
                    }
                else:
                    context = {
                        'detail_playlist_kelola': [],
                        'user_data': user_data, 
                        'roles': roles,
                    }
            else:
                context = {
                    'detail_playlist_kelola': [],
                    'user_data': user_data, 
                    'roles': roles,
                }
    return render(request, 'homepage.html', context)


def logout(request):
    # Hapus semua data sesi terkait dengan login pengguna
    request.session.pop('user_email', None)
    request.session.pop('user_type', None)
    request.session.pop('user_roles', None)

    info_message = "Anda telah logout."
    return render(request, 'login.html', {'info_message': info_message})

from django.shortcuts import render

def album_list_view(request):
    user_email = request.session.get('user_email')
    user_type = request.session.get('user_type')

    if user_type == "verified":
        albums = get_albums_by_artist_or_songwriter(user_email)
        return render(request, 'homepage.html', {'albums': albums})
    else:
        return render(request, 'login.html')
    
def get_albums_by_artist_or_songwriter(email):
    with connection.cursor() as cursor:
        query = """
        SELECT DISTINCT a.judul, l.nama, a.jumlah_lagu, a.total_durasi
        FROM album a
        LEFT JOIN label l ON a.id_label = l.id
        LEFT JOIN song s ON s.id_album = a.id
        LEFT JOIN artist ar ON ar.id = s.id_artist
        LEFT JOIN songwriter_write_song sws ON sws.id_song = s.id_konten
        LEFT JOIN songwriter sw ON sw.id = sws.id_songwriter
        WHERE ar.email_akun = %s OR sw.email_akun = %s
        """
        cursor.execute(query, [email, email])
        albums = cursor.fetchall()
    return albums

from django.db import connection

def add_album(judul, jumlah_lagu, total_durasi, id_label, email):
    with connection.cursor() as cursor:
        # Insert new album
        insert_album_query = """
        INSERT INTO album (id, judul, jumlah_lagu, id_label, total_durasi)
        VALUES (gen_random_uuid(), %s, %s, %s, %s)
        RETURNING id
        """
        cursor.execute(insert_album_query, [judul, jumlah_lagu, id_label, total_durasi])
        album_id = cursor.fetchone()[0]

        # Check if the user is an artist or songwriter
        check_artist_query = "SELECT id FROM artist WHERE email_akun = %s"
        cursor.execute(check_artist_query, [email])
        artist = cursor.fetchone()

        check_songwriter_query = "SELECT id FROM songwriter WHERE email_akun = %s"
        cursor.execute(check_songwriter_query, [email])
        songwriter = cursor.fetchone()

        if artist:
            artist_id = artist[0]
            # Link artist to the album by creating a song entry
            link_artist_query = """
            INSERT INTO song (id_konten, id_artist, id_album)
            VALUES (gen_random_uuid(), %s, %s)
            """
            cursor.execute(link_artist_query, [artist_id, album_id])
        elif songwriter:
            songwriter_id = songwriter[0]
            # Link songwriter to the album by creating a song entry through songwriter_write_song
            link_songwriter_query = """
            INSERT INTO song (id_konten, id_album)
            VALUES (gen_random_uuid(), %s)
            RETURNING id_konten
            """
            cursor.execute(link_songwriter_query, [album_id])
            song_id = cursor.fetchone()[0]
            
            link_songwriter_song_query = """
            INSERT INTO songwriter_write_song (id_songwriter, id_song)
            VALUES (%s, %s)
            """
            cursor.execute(link_songwriter_song_query, [songwriter_id, song_id])
        else:
            raise ValueError("User is neither an artist nor a songwriter.")


from django.shortcuts import render, redirect
from django.http import HttpResponse

def add_album_view(request):
    if 'user_email' in request.session:
        user_email = request.session.get('user_email')
        user_type = request.session.get('user_type')

        if user_type == "verified":
            if request.method == "POST":
                judul = request.POST.get('judul')
                jumlah_lagu = request.POST.get('jumlah_lagu')
                total_durasi = request.POST.get('total_durasi')
                id_label = request.POST.get('id_label')

                try:
                    add_album(judul, int(jumlah_lagu), int(total_durasi), id_label, user_email)
                    return redirect('success_page')  # Ganti dengan halaman sukses yang sesuai
                except Exception as e:
                    return HttpResponse(f"Error: {e}")

            # Ambil daftar label untuk dropdown
            labels = get_labels()  # Fungsi ini harus mengambil semua label dari database
            return render(request, 'add_album.html', {'labels': labels})
    else:
        return render(request, 'login.html')

def get_labels():
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, nama FROM label")
        labels = cursor.fetchall()
    return labels