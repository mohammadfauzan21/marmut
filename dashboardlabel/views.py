from django.shortcuts import redirect, render
from django.db import connection
from django.contrib import messages


def cekroyalti(request):
    return render(request, 'cekroyalti.html')


def listsong(request):
    return render(request, 'listsong.html')


def detaillagu(request):
    return render(request, 'detaillagu.html')

from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection

def homepagelabel(request):
    # Ambil informasi pengguna dari session
    user_email = request.session.get('user_email')
    
    # Pastikan pengguna telah login
    if not user_email:
        error_message = "Anda harus login terlebih dahulu."
        return render(request, 'login.html', {'error_message': error_message})

    # Query untuk mengambil data label berdasarkan email pengguna
    query = "SELECT id, nama, email, kontak FROM label WHERE email = %s"
    with connection.cursor() as cursor:
        cursor.execute(query, [user_email])
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

    # Render template dan kirim data ke template
    return render(request, 'homepagelabel.html', {'label_info': label_info})


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

    # Query untuk mengambil data label berdasarkan email pengguna
    query_label = "SELECT id FROM label WHERE email = %s"
    with connection.cursor() as cursor:
        cursor.execute(query_label, [user_email])
        label_id = cursor.fetchone()

    # Pastikan label_data tidak kosong
    if not label_id:
        error_message = "Data label tidak ditemukan."
        return render(request, 'login.html', {'error_message': error_message})

    # Query untuk mengambil royalti terkait dengan label
    query_royalti = """
        SELECT k.judul, a.judul, r.jumlah, (s.total_play + s.total_download) * phc.rate_royalti AS total_royalti
        FROM konten k
        INNER JOIN song s ON k.id = s.id_konten
        INNER JOIN royalti r ON s.id_konten = r.id_song
        INNER JOIN pemilik_hak_cipta phc ON r.id_pemilik_hak_cipta = phc.id
        INNER JOIN album a ON s.id_album = a.id
        WHERE s.id_artist IN (
            SELECT id
            FROM artist
            WHERE id_pemilik_hak_cipta = %s
        ) OR s.id_artist IN (
            SELECT id
            FROM songwriter
            WHERE id_pemilik_hak_cipta = %s
        )
    """
    with connection.cursor() as cursor:
        cursor.execute(query_royalti, [label_id, label_id])
        royalti_data = cursor.fetchall()

    # Persiapkan data yang akan ditampilkan di template
    royalti_info = []
    for row in royalti_data:
        royalti_info.append({
            'judul_lagu': row[0],
            'judul_album': row[1],
            'jumlah': row[2],
            'total_royalti': row[3],
        })

    # Render template dan kirim data ke template
    return render(request, 'cekroyalti.html', {'royalti_info': royalti_info})
