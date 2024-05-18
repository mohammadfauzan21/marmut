from django.db import connection
from django.http import HttpResponse
from django.shortcuts import redirect, render


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

    return render(request, 'homepage.html', {'user_data': user_data, 'roles': roles})


def logout(request):
    # Hapus semua data sesi terkait dengan login pengguna
    request.session.pop('user_email', None)
    request.session.pop('user_type', None)
    request.session.pop('user_roles', None)

    info_message = "Anda telah logout."
    return render(request, 'login.html', {'info_message': info_message})

