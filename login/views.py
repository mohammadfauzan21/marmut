from django.shortcuts import render, redirect
from django.db import connection

def loginkonten(request):
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
                # Cek apakah verified PUSING BGT YAALLAH
                cursor.execute("SELECT is_verified FROM akun WHERE email = %s", [user_email])
                is_verified = cursor.fetchone()[0]

                # Kalau gak verified, berarti ya otomatis reguler user
                if not is_verified:
                    return redirect('dashboardreguser:dashboarduser')
                # Jika verified, maka cek email terdaftar di mana aja
                else:
                    # Cek email apakah terdaftar sebagai artist/songwriter, terdaftar sebagai podcaster, atau justru terdaftar sebagai artist/songwriter dan podcaster

                        # Check if the email is registered as an artist
                        cursor.execute("SELECT * FROM artist WHERE email_akun = %s", [user_email])
                        is_artist = cursor.fetchone()
                        # Check if the email is registered as a songwriter
                        cursor.execute("SELECT * FROM songwriter WHERE email_akun = %s", [user_email])
                        is_songwriter = cursor.fetchone()
                        # Check if the email is registered as a podcaster
                        cursor.execute("SELECT * FROM podcaster WHERE email = %s", [user_email])
                        is_podcaster = cursor.fetchone()

                        # registered as either artist or songwriter or both
                        if (is_artist or is_songwriter) and (is_artist and is_songwriter):
                            return redirect('dashboardartist:homepageartist')  # Redirect to the artist/songwriter dashboard
                        # INI BISA DIBUKA YAH. registered as both artist/songwriter and podcaster
                        # elif is_artist and is_songwriter and is_podcaster:
                        #     return redirect('dashboardmix:homepagemix')  # Redirect to a common dashboard page for both types
                        # registered as podcaster only
                        elif is_podcaster:
                            return redirect('dashboardpodcaster:homepagepodcaster')  # Redirect to the podcaster dashboard

                
            else:
                # Jika akun tidak ditemukan, coba cek kali aja akun Label
                cursor.execute("SELECT * FROM label WHERE email = %s AND password = %s", [user_email, user_password])
                label_exist = cursor.fetchone()
                if label_exist:
                    return redirect('dashboardlabel:homepagelabel')
                else:
                    # Tidak ditemukan di akun atau label
                    error_message = "Username atau password belum terdaftar."
                    return render(request, 'login.html', {'error_message': error_message})
                

    else:
        # Jika bukan metode POST, kembalikan halaman login kosong
        return render(request, 'login.html')
