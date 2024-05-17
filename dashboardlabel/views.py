from django.shortcuts import redirect, render

# Create your views here.


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
