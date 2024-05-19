from django.shortcuts import redirect, render
from django.db import connection
from django.views.decorators.csrf import csrf_exempt

def check_session(request, required_user_type):
    # Ambil informasi pengguna dari session
    user_email = request.session.get('user_email')
    user_type = request.session.get('user_type')

    # Pastikan pengguna telah login
    if not user_email or user_type != required_user_type:
        error_message = "Anda harus login terlebih dahulu."
        return render(request, 'login.html', {'error_message': error_message})

    return user_email

def homepagelabel(request):
    user_email = check_session(request, 'label')
    if isinstance(user_email, HttpResponse):
        return user_email  # Jika error message, langsung kembalikan response

    # Query untuk mengambil data label berdasarkan email pengguna
    label_query = "SELECT id, nama, email, kontak FROM label WHERE email = %s"
    with connection.cursor() as cursor:
        cursor.execute(label_query, [user_email])
        label_data = cursor.fetchone()

        # Pastikan label_data tidak kosong
        if not label_data:
            error_message = "Data label tidak ditemukan."
            return render(request, 'login.html', {'error_message': error_message})

        # Persiapkan data yang akan ditampilkan di template
        label_info = {
            'id': label_data[0],
            'nama': label_data[1],
            'email': label_data[2],
            'kontak': label_data[3],
        }

        # Query untuk mengambil daftar album label
        # Query untuk mengambil daftar album label beserta total durasi dan jumlah lagunya
        album_query = """
            SELECT a.id, a.judul, a.jumlah_lagu, COALESCE(SUM(k.durasi), 0) AS total_durasi
            FROM album a
            LEFT JOIN song s ON a.id = s.id_album
            LEFT JOIN konten k ON s.id_konten = k.id
            WHERE a.id_label = %s
            GROUP BY a.id, a.judul, a.jumlah_lagu
        """

        cursor.execute(album_query, [label_info['id']])
        albums_data = cursor.fetchall()  # Ambil semua hasil dari kueri

        # Menyusun data album menjadi list of tuples (id, judul, jumlah_lagu, total_durasi)
        albums = [(id, judul, jumlah_lagu, total_durasi) for id, judul, jumlah_lagu, total_durasi in albums_data]
        

    # Render template dan kirim data ke template
    return render(request, 'homepagelabel.html', {'label_info': label_info, 'albums': albums})


def logout(request):
    # Hapus semua data sesi terkait dengan login pengguna
    request.session.pop('user_email', None)
    request.session.pop('user_type', None)
    request.session.pop('user_roles', None)

    info_message = "Anda telah logout."
    return render(request, 'login.html', {'info_message': info_message})

def cekroyalti(request):
    # Ambil informasi pengguna dari session
    user_email = check_session(request, 'label')
    if isinstance(user_email, HttpResponse):
        return user_email  # Jika error message, langsung kembalikan response

    # Query untuk mengambil data label berdasarkan email pengguna
    label_query = "SELECT id, nama, email, kontak, id_pemilik_hak_cipta FROM label WHERE email = %s"
    
    with connection.cursor() as cursor:
        cursor.execute(label_query, [user_email])
        label_data = cursor.fetchone()

        # Pastikan label_data tidak kosong
        if not label_data:
            error_message = "Data label tidak ditemukan."
            return render(request, 'login.html', {'error_message': error_message})

        # Persiapkan data yang akan ditampilkan di template
        label_info = {
            'id': label_data[0],
            'nama': label_data[1],
            'email': label_data[2],
            'kontak': label_data[3],
            'id_pemilik_hak_cipta': label_data[4],
        }

        # Query untuk mengambil daftar album label beserta total durasi dan jumlah lagunya
        album_query = """
            SELECT id, judul, jumlah_lagu, total_durasi
            FROM album
            WHERE id_label = %s
        """
        cursor.execute(album_query, [label_info['id']])
        albums_data = cursor.fetchall()  # Ambil semua hasil dari kueri

        # Menyusun data album menjadi list of tuples (id, judul, jumlah_lagu, total_durasi)
        albums = [(id, judul, jumlah_lagu, total_durasi) for id, judul, jumlah_lagu, total_durasi in albums_data]
        
        # Mendapatkan cursor baru setelah eksekusi query
        cursor = connection.cursor()

        # Query untuk mengambil data royalti
        query = """
        SELECT k.judul, a.judul AS judul_album, s.total_play, s.total_download, (p.rate_royalti * s.total_play) AS total_royalti
        FROM song s
        INNER JOIN konten k ON s.id_konten = k.id
        LEFT JOIN album a ON s.id_album = a.id
        INNER JOIN label l ON a.id_label = l.id
        INNER JOIN pemilik_hak_cipta p ON l.id_pemilik_hak_cipta = p.id
        WHERE l.id_pemilik_hak_cipta = %s
        """

        # Eksekusi query royalti
        cursor.execute(query, [label_info['id_pemilik_hak_cipta']])

        # Mendapatkan hasil query royalti
        royalti_data = cursor.fetchall()

    # Render template dan kirim data ke template
    return render(request, 'cekroyalti.html', {'label_info': label_info, 'albums': albums, 'royalti_data': royalti_data})


def listsong(request, album_id):
    user_email = check_session(request, 'label')
    if isinstance(user_email, HttpResponse):
        return user_email  # Jika error message, langsung kembalikan response

    # Query untuk mengambil data label berdasarkan email pengguna
    label_query = "SELECT id, nama, email, kontak FROM label WHERE email = %s"
    with connection.cursor() as cursor:
        cursor.execute(label_query, [user_email])
        label_data = cursor.fetchone()

        # Pastikan label_data tidak kosong
        if not label_data:
            error_message = "Data label tidak ditemukan."
            return render(request, 'login.html', {'error_message': error_message})

        # Persiapkan data yang akan ditampilkan di template
        label_info = {
            'id': label_data[0],
            'nama': label_data[1],
            'email': label_data[2],
            'kontak': label_data[3],
        }

        # Query untuk mengambil detail album berdasarkan album_id
        album_query = """
            SELECT id, judul, jumlah_lagu, total_durasi
            FROM album
            WHERE id = %s
        """
        cursor.execute(album_query, [album_id])
        album_data = cursor.fetchone()

        # Jika album tidak ditemukan, kembalikan pesan kesalahan
        if not album_data:
            error_message = "Album tidak ditemukan."
            return render(request, 'listsong.html', {'label_info': label_info, 'error_message': error_message})

        # Persiapkan data album yang akan ditampilkan di template
        album_info = {
            'id': album_data[0],
            'judul': album_data[1],
            'jumlah_lagu': album_data[2],
            'total_durasi': album_data[3]
        }

        # Query untuk mengambil daftar lagu dari album yang dipilih
        song_query = """
            SELECT k.judul, k.durasi, s.total_play, s.total_download, k.id
            FROM song s
            INNER JOIN konten k ON s.id_konten = k.id
            WHERE s.id_album = %s
        """
        cursor.execute(song_query, [album_id])
        songs_data = cursor.fetchall()
        

        # Menyusun data lagu menjadi list of tuples (judul, durasi, total_play, total_download)
        songs = [(judul, durasi, total_play, total_download, id) for judul, durasi, total_play, total_download, id in songs_data]

        # Mengatur total durasi gak jadi diambil dari album_info, melainkan dari penjumlahan durasi lagu di songs
        total_durasi = 0
        for song in songs:
            total_durasi += song[1]  # Index 1 mengacu pada durasi lagu
        album_info['total_durasi'] = total_durasi


    # Render template dan kirim data ke template
    return render(request, 'listsong.html', {'label_info': label_info, 'album_info': album_info, 'songs': songs, 'album_id': album_id})

@csrf_exempt
def detaillagu(request, album_id, song_id):
    if request.method == 'POST':
        # Query untuk mengambil detail lagu berdasarkan song_id
        song_query = song_query = """
    SELECT 
    k.judul AS judul_lagu,
    k.tahun,
    k.durasi,
    a.judul AS judul,
    STRING_AGG(DISTINCT ak_artist.nama, ', ') AS artist,
    STRING_AGG(DISTINCT ak_songwriter.nama, ', ') AS songwriter,
    k.tanggal_rilis,
    s.total_play,
    s.total_download
FROM 
    public.konten k
JOIN 
    public.song s ON k.id = s.id_konten
JOIN 
    public.album a ON s.id_album = a.id
LEFT JOIN 
    public.artist art ON s.id_artist = art.id
LEFT JOIN 
    public.akun ak_artist ON art.email_akun = ak_artist.email
LEFT JOIN 
    public.songwriter_write_song sws ON s.id_konten = sws.id_song
LEFT JOIN 
    public.songwriter sw ON sws.id_songwriter = sw.id
LEFT JOIN 
    public.akun ak_songwriter ON sw.email_akun = ak_songwriter.email
WHERE 
    k.id = %s
GROUP BY 
    k.judul, k.tahun, k.durasi, a.judul, k.tanggal_rilis, s.total_play, s.total_download;

"""


        with connection.cursor() as cursor:
            cursor.execute(song_query, [song_id])
            song_data = cursor.fetchone()

            # Jika lagu tidak ditemukan, kembalikan pesan kesalahan
            if not song_data:
                error_message = "Lagu tidak ditemukan."
                return render(request, 'error.html', {'error_message': error_message})

            # Persiapkan data lagu yang akan ditampilkan di template
            song_info = {
                'judul': song_data[0],
                'tahun': song_data[1],
                'durasi': song_data[2],
                'judul_album': song_data[3],
                'artist': song_data[4],
                'songwriter': song_data[5],
                'tanggal': song_data[6],
                'total_play': song_data[7],
                'total_download': song_data[8]
            }

        # Render template dan kirim data ke template
        return render(request, 'detaillagu.html', {'song_info': song_info})
    else:
        # Jika tidak ada metode POST, redirect ke halaman sebelumnya atau halaman lain yang sesuai
        return redirect('dashboardlabel:listsong', album_id=album_id)


from django.shortcuts import render, redirect
from django.db import connection
from django.http import HttpResponse

@csrf_exempt
def delete_album(request):
    if request.method == 'POST':
        album_id = request.POST.get('album_id')  # Mendapatkan ID album dari permintaan POST
        if not album_id:
            return HttpResponse("ID album tidak valid", status=400)

        try:
            with connection.cursor() as cursor:
                # Lakukan penghapusan album
                cursor.execute("DELETE FROM album WHERE id = %s", [album_id])
                # Jika berhasil, kembalikan respons berhasil
                return redirect('dashboardlabel:homepagelabel')
        except Exception as e:
            # Tangani kesalahan yang mungkin terjadi
            return HttpResponse(str(e), status=500)
    else:
        # Jika bukan permintaan POST, kembalikan respons metode tidak diizinkan
        return HttpResponse("Metode tidak diizinkan", status=405)
    
from django.shortcuts import redirect

@csrf_exempt
def delete_song(request, album_id, song_id):
    if request.method == 'POST':
        try:
            # Lakukan penghapusan entri yang merujuk ke lagu tersebut pada tabel lain
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM songwriter_write_song WHERE id_song = %s", [song_id])
                cursor.execute("DELETE FROM royalti WHERE id_song = %s", [song_id])
                cursor.execute("DELETE FROM playlist_song WHERE id_song = %s", [song_id])
                cursor.execute("DELETE FROM downloaded_song WHERE id_song = %s", [song_id])
                cursor.execute("DELETE FROM akun_play_song WHERE id_song = %s", [song_id])

                # Hapus lagu dari tabel "song" setelah referensi dihapus dari tabel lain
                cursor.execute("DELETE FROM song WHERE id_konten = %s", [song_id])

            # Jika berhasil, kembalikan respons berhasil
            return redirect('dashboardlabel:listsong', album_id=album_id)
        except Exception as e:
            # Tangani kesalahan yang mungkin terjadi
            return HttpResponse(str(e), status=500)
    else:
        # Jika bukan permintaan POST, kembalikan respons metode tidak diizinkan
        return HttpResponse("Metode tidak diizinkan", status=405)








