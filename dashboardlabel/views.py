from django.shortcuts import redirect, render
from django.db import connection
from django.contrib import messages


# def cekroyalti(request):
#     return render(request, 'cekroyalti.html')


from django.shortcuts import render
from django.db import connection

def cekroyalti(request):
    # Ambil informasi pengguna dari session
    user_email = request.session.get('user_email')
    
    # Pastikan pengguna telah login
    if not user_email:
        error_message = "Anda harus login terlebih dahulu."
        return render(request, 'login.html', {'error_message': error_message})

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
            SELECT a.id, a.judul, a.jumlah_lagu, a.total_durasi
            FROM album a
            WHERE a.id_label = %s
        """
        cursor.execute(album_query, [label_info['id']])
        albums_data = cursor.fetchall()  # Ambil semua hasil dari kueri

        # Menyusun data album menjadi list of tuples (id, judul, jumlah_lagu, total_durasi)
        albums = [(id, judul, jumlah_lagu, total_durasi) for id, judul, jumlah_lagu, total_durasi in albums_data]

    # Render template dan kirim data ke template
    return render(request, 'cekroyalti.html', {'label_info': label_info, 'albums': albums})

def listsong(request, album_id):
    # Ambil informasi pengguna dari session
    user_email = request.session.get('user_email')
    
    # Pastikan pengguna telah login
    if not user_email:
        error_message = "Anda harus login terlebih dahulu."
        return render(request, 'login.html', {'error_message': error_message})

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



def detaillagu(request):
    return render(request, 'detaillagu.html')


from django.shortcuts import render, redirect
from django.db import connection
from django.http import HttpResponse

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









def homepagelabel(request):
    # Ambil informasi pengguna dari session
    user_email = request.session.get('user_email')
    
    # Pastikan pengguna telah login
    if not user_email:
        error_message = "Anda harus login terlebih dahulu."
        return render(request, 'login.html', {'error_message': error_message})

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
            SELECT a.id, a.judul, a.jumlah_lagu, a.total_durasi
            FROM album a
            WHERE a.id_label = %s
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

