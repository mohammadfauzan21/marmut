import datetime
from django.shortcuts import render, redirect
from django.db import connection
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required

@login_required
# Create your views here.
def podcaster(request):
    if request.method == 'GET':
        # Fetch podcaster's podcast details from the database
        email = request.user.email
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM podcast WHERE email_podcaster = %s", [email])
            podcasts = cursor.fetchall()

        # Prepare context data for rendering
        context = {
            'podcasts': podcasts,
        }

        return render(request, 'podcaster.html', context)
    elif request.method == 'POST':
        email = request.user.email
        # Handle form submission for adding a new podcast
        podcast_title = request.POST.get('podcastTitle')
        genre = request.POST.get('genreSelect')

        # Insert new podcast into the database
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO podcast (podcast_title, genre, podcaster_email) VALUES (%s, %s, %s)",
                           [podcast_title, genre, email])

        messages.success(request, 'Podcast added successfully!')
        return redirect('podcaster')

    return HttpResponse("Method not allowed")


def episodes(request):
    episodes_date = datetime.now()
    context = {'episodes_date': episodes_date}
    return render(request, 'episodes.html', context)