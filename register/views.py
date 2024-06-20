from django.contrib import messages
from django.db import connection
from django.shortcuts import redirect, render
from datetime import datetime
import uuid
from django.views.decorators.csrf import csrf_exempt

from register.query import *


def registerkonten(request):
    return render(request, 'register.html')

@csrf_exempt
def registerlabel(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        nama = request.POST.get('nama')
        kontak = request.POST.get('kontak')

        # Generate UUID for the id column
        id_label = uuid.uuid4()
        id_pemilik_hak_cipta = uuid.uuid4()

        with connection.cursor() as cursor:
            query = check_email_label(email)
            cursor.execute(query)
            femail = cursor.fetchall()
            if len(femail) > 0 :
                context = {
                    'errorLabel':"Email telah digunakan"
                }
                return render(request, 'register.html', context)
            else:
                cursor.execute("INSERT INTO pemilik_hak_cipta (id, rate_royalti) VALUES (%s, %s)", [id_pemilik_hak_cipta, 0])
                cursor.execute("INSERT INTO label (id, email, password, nama, kontak, id_pemilik_hak_cipta) VALUES (%s, %s, %s, %s, %s, %s)", [id_label, email, password, nama, kontak, id_pemilik_hak_cipta])
                
                return redirect('login:loginkonten')
    else:
        # Jika bukan metode POST, kembalikan halaman register kosong
        return render(request, 'register.html')

@csrf_exempt
def registeruser(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        nama = request.POST.get('nama')
        tempat_lahir = request.POST.get('tempat_lahir')
        kota_asal = request.POST.get('kota_asal')
        tanggal_lahir_str = request.POST.get('tanggal_lahir')  # Ambil tanggal dalam format string
        if tanggal_lahir_str:
            tanggal_lahir = datetime.strptime(tanggal_lahir_str, '%Y-%m-%d').date()
        gender = request.POST.get('gender')
        
        # Initialize is_verified as False
        is_verified = False  
        # Ambil role dari multicheckbox
        roles = request.POST.getlist('role')
        print("Selected Roles:", roles) 

        with connection.cursor() as cursor:
            # Check email double
            query = check_email_pengguna(email)
            cursor.execute(query)
            femail = cursor.fetchall()
            if len(femail) > 0 :
                context = {
                    'errorPengguna':"Email telah digunakan"
                }
                return render(request, 'register.html', context)
            else:
                cursor.execute("INSERT INTO akun (email, password, nama, tempat_lahir, kota_asal, tanggal_lahir, gender, is_verified) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", [email, password, nama, tempat_lahir, kota_asal, tanggal_lahir, gender, is_verified])

                # Insert roles into respective tables (e.g., artist, songwriter, podcaster)
                for role in roles:
                    if role == 'artist':
                        id_pemilik_hak_cipta = uuid.uuid4()
                        cursor.execute("INSERT INTO pemilik_hak_cipta (id, rate_royalti) VALUES (%s, %s)", [id_pemilik_hak_cipta, 0])
                        cursor.execute("INSERT INTO artist (id, email_akun, id_pemilik_hak_cipta) VALUES (%s, %s, %s)", [uuid.uuid4(), email, id_pemilik_hak_cipta])
                    elif role == 'songwriter':
                        id_pemilik_hak_cipta = uuid.uuid4()
                        cursor.execute("INSERT INTO pemilik_hak_cipta (id, rate_royalti) VALUES (%s, %s)", [id_pemilik_hak_cipta, 0])
                        cursor.execute("INSERT INTO songwriter (id, email_akun, id_pemilik_hak_cipta) VALUES (%s, %s, %s)", [uuid.uuid4(), email, id_pemilik_hak_cipta])
                    elif role == 'podcaster':
                        cursor.execute("INSERT INTO podcaster (email) VALUES (%s)", [email])

                # If any role is selected, set is_verified to True
                if roles:
                    is_verified = True

                # Update is_verified in akun table
                cursor.execute("UPDATE akun SET is_verified = %s WHERE email = %s", [is_verified, email])
                return redirect('login:loginkonten')
    else:
        # Jika bukan metode POST, kembalikan halaman register kosong
        return render(request, 'register.html')
