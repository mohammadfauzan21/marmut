from django.shortcuts import render, redirect
from django.db import connection
from django.contrib import messages

def loginkonten(request):
    # Cek apakah sesi login sudah ada
    if 'user_email' in request.session:
        user_email = request.session.get('user_email')
        user_type = request.session.get('user_type')

        # Redirect ke dashboard sesuai peran pengguna
        if user_type == 'verified':
            user_roles = request.session.get('user_roles', [])
            if 'artist' in user_roles and 'songwriter' in user_roles:
                return redirect('dashboardartist:homepageartist')
            elif 'podcaster' in user_roles:
                return redirect('dashboardpodcaster:homepagepodcaster')
            else:
                return redirect('dashboardreguser:dashboarduser')
        elif user_type == 'label':
            return redirect('dashboardlabel:homepagelabel')
        else:
            return redirect('login')  # Jika sesi login ada tapi tidak valid, arahkan ke halaman login

    if request.method == 'POST':
        # Ambil email dan password dari data POST
        user_email = request.POST.get('email')
        user_password = request.POST.get('password')

        # Lakukan pengecekan apakah email dan password ada dalam tabel akun atau label
        with connection.cursor() as cursor:
            # Cek dalam tabel akun
            cursor.execute("SELECT * FROM akun WHERE email = %s AND password = %s", [user_email, user_password])
            akun_exists = cursor.fetchone()

            # Kirim data ke template tergantung pada apa yang ditemukan
            if akun_exists:
                # Cek apakah verified
                cursor.execute("SELECT is_verified FROM akun WHERE email = %s", [user_email])
                is_verified = cursor.fetchone()[0]

                # Kalau gak verified, berarti ya otomatis reguler user
                if not is_verified:
                    request.session['user_email'] = user_email
                    request.session['user_type'] = 'unverified'
                    return redirect('dashboardreguser:dashboarduser')
                # Jika verified, maka cek email terdaftar di mana aja
                else:
                    # Cek email apakah terdaftar sebagai artist/songwriter, terdaftar sebagai podcaster, atau justru terdaftar sebagai artist/songwriter dan podcaster
                    cursor.execute("SELECT * FROM artist WHERE email_akun = %s", [user_email])
                    is_artist = cursor.fetchone()
                    cursor.execute("SELECT * FROM songwriter WHERE email_akun = %s", [user_email])
                    is_songwriter = cursor.fetchone()
                    cursor.execute("SELECT * FROM podcaster WHERE email = %s", [user_email])
                    is_podcaster = cursor.fetchone()

                    user_roles = []

                    # Menyimpan informasi peran-peran pengguna dalam session
                    if is_artist:
                        user_roles.append('artist')
                    if is_songwriter:
                        user_roles.append('songwriter')
                    if is_podcaster:
                        user_roles.append('podcaster')

                    request.session['user_email'] = user_email
                    request.session['user_type'] = 'verified'
                    request.session['user_roles'] = user_roles

                    # Redirect ke halaman yang sesuai
                    if is_artist and is_songwriter:
                        return redirect('dashboardartist:homepageartist')
                    elif is_podcaster:
                        return redirect('dashboardpodcaster:homepagepodcaster')
                    else:
                        return redirect('dashboardreguser:dashboarduser')

            else:
                # Cek ada gak akun label
                cursor.execute("SELECT * FROM label WHERE email = %s AND password = %s", [user_email, user_password])
                label_exist = cursor.fetchone()
                if label_exist:
                    request.session['user_email'] = user_email
                    request.session['user_type'] = 'label'
                    return redirect('dashboardlabel:homepagelabel')
                else:
                # Jika akun tidak ditemukan, tampilkan pesan kesalahan
                    error_message = "Username atau password belum terdaftar."
                    return render(request, 'login.html', {'error_message': error_message})

    else:
        # Jika bukan metode POST, kembalikan halaman login kosong
        return render(request, 'login.html')
