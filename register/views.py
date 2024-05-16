from django.contrib import messages
from django.db import connection
from django.shortcuts import redirect, render

def registerkonten(request):
    return render(request, 'register.html')

import uuid

def registerlabel(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        nama = request.POST.get('nama')
        kontak = request.POST.get('kontak')

        # Generate UUID for the id column
        id = uuid.uuid4()

        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO label (id, email, password, nama, kontak) VALUES (%s, %s, %s, %s, %s)", [id, email, password, nama, kontak])

        success_message = "Berhasil mendaftar sebagai Label."
        return render(request, 'login.html', {'success_message': success_message})
    else:
        # Jika bukan metode POST, kembalikan halaman register kosong
        return render(request, 'register.html')
