from django.shortcuts import redirect, render
from django.db import connection
from django.contrib import messages


# def cekroyalti(request):
#     return render(request, 'cekroyalti.html')


from django.shortcuts import render
from django.db import connection

def listalbum(request):
    # Ambil informasi pengguna dari session
    user_email = request.session.get('user_email')
    # Pastikan pengguna telah login
    if not user_email:
        error_message = "Anda harus login terlebih dahulu."
        return render(request, 'login.html', {'error_message': error_message})
    
    # Eksekusi kueri SQL untuk mendapatkan daftar album
    with connection.cursor() as cursor:
        cursor.execute("SELECT judul FROM album INNER JOIN label ON album.id_label = label.id WHERE label.email = %s", [user_email])
        albums = cursor.fetchall()  # Mengambil semua hasil kueri

    # Kirim daftar album ke template untuk ditampilkan
    return render(request, 'listalbum.html', {'albums': albums})




def listsong(request):
    return render(request, 'listsong.html')

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


def cekroyalti(request):
    # Ambil informasi pengguna dari session
    user_email = request.session.get('user_email')
    
    # Pastikan pengguna telah login
    if not user_email:
        error_message = "Anda harus login terlebih dahulu."
        return render(request, 'login.html', {'error_message': error_message})

    return render(request, 'cekroyalti.html')
