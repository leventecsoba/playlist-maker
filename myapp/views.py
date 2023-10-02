from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.db.models import F

from .models import UserProfile

from spotipy.oauth2 import SpotifyOAuth
from spotipy.exceptions import SpotifyException
import spotipy

import environ

env = environ.Env()  
environ.Env.read_env()

client_id = env('CLIENT_ID')
client_secret = env('CLIENT_SECRET')
scope = env('SCOPE')

def spotify_login(request):
    sp_auth = SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri='http://127.0.0.1:8000/spotify_callback',
        scope=scope
    )
    auth_url = sp_auth.get_authorize_url()
    return redirect(auth_url)

def spotify_callback(request):
    code = request.GET.get('code')
    sp_auth = SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri='http://127.0.0.1:8000/spotify_callback',
        scope=scope
    )
    token_info = sp_auth.get_access_token(code=code)

    # store spotify acces token in session
    request.session['access_token'] = token_info['access_token']
    return redirect('index')

def index(request):
    access_token = request.session.get('access_token')
    file_data = request.session.get('file_data')

    context = {
        'user': None,
        'file_data': file_data
    }

    if access_token is not None:
        try:
            sp = spotipy.Spotify(auth=access_token)
            try:
                user = sp.current_user()
                context['user'] = user
                UserProfile.objects.get_or_create(id=user['id'])
            except:
                pass
        # spotify access token expired
        except SpotifyException:
            request.session['access_token'] = None
            return redirect('index')

    return render(request, "myapp/index.html", context)

def upload(request):
    if request.method == 'POST':
        files = request.FILES.getlist('files')
        if files:
            file_data = []
            for file in files:
                file_data.append({'name': file.name[:-4], 'is_processed': False})
            request.session['file_data'] = file_data
    return redirect('index')
    
def files(request, file_idx):
    access_token = request.session.get('access_token')
    if access_token is not None:
        try:
            file_data = request.session.get('file_data')
            if file_idx >= len(file_data):
                return redirect('index')
            file = file_data[file_idx]

            sp = spotipy.Spotify(auth=access_token)
            playlists = sp.current_user_playlists()
            user = sp.current_user()
            results = sp.search(q=file['name'], limit=10, type='track')

            for idx, item in enumerate(results['tracks']['items']):
                seconds, item['duration_ms'] = divmod(item['duration_ms'], 1000)
                minutes, seconds = divmod(seconds, 60)
                results['tracks']['items'][idx]['duration'] = f"{minutes}:{seconds:02d}"

            return render(request, "myapp/files.html", {
                'file': file,
                'file_idx': file_idx,
                'user': user,
                'playlists': playlists['items'],
                'tracks': results['tracks']['items']
            })
        except SpotifyException:
            request.session['access_token'] = None
            return redirect('index')
    return redirect('index')
    
def add_track(request, file_idx):
    if(request.method == "POST"):
        access_token = request.session.get('access_token')
        if access_token is not None:
            try:
                sp = spotipy.Spotify(auth=access_token)
                try:
                    user = sp.current_user()
                    sp.user_playlist_add_tracks(user['display_name'], request.POST.get('playlists'), [request.POST.get('tracks')])
                    
                    UserProfile.objects.update_or_create(
                        id=user['id'],
                        defaults={'files_processed': F('files_processed') + 1},
                    )

                    file_data = request.session.get('file_data')
                    if file_idx + 1 < len(file_data):
                        return redirect('/files/' + str(file_idx + 1)) 
                except:
                    return redirect('/files/' + str(file_idx)) 
            except:
                request.session['access_token'] = None
                return redirect('index')
    return redirect('index')

def user(request):
    access_token = request.session.get('access_token')
    if access_token is not None:
        try:
            sp = spotipy.Spotify(auth=access_token)
            user = sp.current_user()
            user_profile, created = UserProfile.objects.get_or_create(id=user['id'])

            return render(request, "myapp/user.html", {
                'user': user,
                'user_profile': user_profile
            })
        except:
            request.session['access_token'] = None
    return redirect('index')

def user_logout(request):
    logout(request)
    return redirect('index')