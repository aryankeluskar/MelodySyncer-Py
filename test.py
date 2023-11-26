# shows track info for a URN or URL

from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import sys
from pprint import pprint


from dotenv import load_dotenv
load_dotenv()


sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

songID = input()
track = sp.track(songID)
print(track['name'])
print(track['album']['name'])
print(track['album']['artists'][0]['name'])
print(track['duration_ms'])