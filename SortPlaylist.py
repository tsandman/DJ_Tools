import os
from SpotifyTools import SpotifyTools

#Setup spotipy variables
username = '12134764203'
scope = 'user-library-modify user-library-read user-library-read playlist-modify playlist-modify-private playlist-read-private playlist-read-collaborative'

#Instantiate SpotifyTools object
st = SpotifyTools( username, scope )

#Sort Desired Playlist
#Sort options: danceability, energy, key, loudness, speechiness, acousticness, instrumentalness, liveness, valence, tempo
st.sortPlaylist( "chill", "energy", "ascending")