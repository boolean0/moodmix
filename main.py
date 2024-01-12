from dotenv import load_dotenv
import os
import time
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask, request, url_for, session, redirect
from gpt import get_recs_from_gpt
load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
SESSION_KEY = os.getenv("SESSION_KEY")

app = Flask(__name__)

app.config['SESSION_COOKIE_NAME'] = 'cookie name'
app.secret_key = SESSION_KEY


@app.route("/")
def login():
     auth_url = create_spotify_oauth().get_authorize_url()
     return redirect(auth_url)

@app.route('/redirect')
def redirect_page(): 
     session.clear()
     code = request.args.get('code')
     token_info = create_spotify_oauth().get_access_token(code)
     session['token_info'] = token_info
     return redirect(url_for('song_search', external = True))

 
@app.route('/songSearch') #pass mood parameter
def song_search(): 
     track_ids = []
     try:
          token_info = get_token()
     except:
          print("not logged in")
          return redirect('/')
     cur_client = spotipy.Spotify(auth=token_info['access_token']) #loop w gpt responses here

     top_artists = get_top_artists_comma_sep(cur_client)
     artist_and_songs = get_recs_from_gpt('party', top_artists) # take input here
     for artist_and_song in artist_and_songs:
          artist, track_title = artist_and_song
          query = f'{track_title} artist:{artist}'
          tracks_returned = cur_client.search(q=query, limit=1, type='track')
          if tracks_returned and tracks_returned['tracks'] and tracks_returned['tracks']['items'] and tracks_returned['tracks']['items'][0] and tracks_returned['tracks']['items'][0]['id']:
               track_id = tracks_returned['tracks']['items'][0]['id']
               track_ids.append(track_id)
     if len(tracks_returned) == 0:
          return 'no tracks found'
     else:
          return create_playlist_with_recs(cur_client, track_ids)     
          

def create_playlist_with_recs(cur_client, track_ids):
     if len(track_ids) == 0:
          return 'no songs to create playlist with'
     else:
          user_id = cur_client.current_user()['id']
          playlist = cur_client.user_playlist_create(user_id, 'Test Playlist', True, False, 'test playlist')
          cur_client.user_playlist_add_tracks(user_id, playlist['id'], track_ids)
          return playlist['id']


def get_token():
     token_info = session.get('token_info', None)
     if not token_info: 
          redirect(url_for('login', external = False))
     
     now = int(time.time())
     # if expiring in < 2 min then refresh
     is_expired = token_info['expires_at'] - now < 120
     if (is_expired):
          spotify_oauth = create_spotify_oauth()
          token_info = spotify_oauth.refresh_access_token(token_info['refresh_token'])
     return token_info


def create_spotify_oauth():
     return SpotifyOAuth (
          client_id = CLIENT_ID,
          client_secret = CLIENT_SECRET,
          redirect_uri = url_for('redirect_page', _external = True), 
          scope = 'user-read-private user-library-read playlist-modify-public user-top-read'
     )

@app.route('/topArtists')
def get_top_artists_comma_sep(cur_client):
     cs_artists = ''
     top_artists = cur_client.current_user_top_artists(limit=10)
     if top_artists['items']:
          for artist_info in top_artists['items']:
               cs_artists = f'{cs_artists}, {artist_info["name"]}'
     
     if len(cs_artists) > 0: # rm extraneous comma
          cs_artists = cs_artists[1:]
     return cs_artists

     

app.run(debug=True)