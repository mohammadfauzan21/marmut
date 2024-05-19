from django.shortcuts import render, redirect
from django.db import connection
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def loginkonten(request):
    if 'user_email' in request.session:
        user_email = request.session.get('user_email')
        user_type = request.session.get('user_type')

        if user_type == 'verified' or user_type == 'unverified':
            user_roles = request.session.get('user_roles', [])
            return redirect('dashboarduser:homepage')  # Sesuaikan URL dengan yang ada di app dashboarduser
        elif user_type == 'label':
            return redirect('dashboardlabel:homepagelabel')
        else:
            return redirect('login')

    if request.method == 'POST':
        user_email = request.POST.get('email')
        user_password = request.POST.get('password')

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM akun WHERE email = %s AND password = %s", [user_email, user_password])
            akun_exists = cursor.fetchone()

            if akun_exists:
                request.session['user_email'] = akun_exists[0]
                cursor.execute("SELECT is_verified FROM akun WHERE email = %s", [user_email])
                is_verified = cursor.fetchone()[0]

                if not is_verified:
                    request.session['user_email'] = user_email
                    request.session['user_type'] = 'unverified'
                    return redirect('dashboarduser:homepage')
                else:
                    cursor.execute("SELECT * FROM artist WHERE email_akun = %s", [user_email])
                    is_artist = cursor.fetchone()
                    cursor.execute("SELECT * FROM songwriter WHERE email_akun = %s", [user_email])
                    is_songwriter = cursor.fetchone()
                    cursor.execute("SELECT * FROM podcaster WHERE email = %s", [user_email])
                    is_podcaster = cursor.fetchone()

                    user_roles = []
                    if is_artist:
                        user_roles.append('artist')
                    if is_songwriter:
                        user_roles.append('songwriter')
                    if is_podcaster:
                        user_roles.append('podcaster')

                    request.session['user_email'] = user_email
                    request.session['user_type'] = 'verified'
                    request.session['user_roles'] = user_roles

                    return redirect('dashboarduser:homepage')  # Sesuaikan URL dengan yang ada di app dashboarduser

            else:
                cursor.execute("SELECT * FROM label WHERE email = %s AND password = %s", [user_email, user_password])
                label_exist = cursor.fetchone()
                if label_exist:
                    request.session['user_email'] = user_email
                    request.session['user_type'] = 'label'
                    return redirect('dashboardlabel:homepagelabel')
                else:
                    error_message = "Username atau password belum terdaftar."
                    return render(request, 'login.html', {'error_message': error_message})

    else:
        return render(request, 'login.html')
