import os
from SpotifyTools import SpotifyTools

#Setup spotipy variables
username = '12134764203'
scope = 'user-library-modify user-library-read user-library-read playlist-modify playlist-modify-private playlist-read-private playlist-read-collaborative'

#Instantiate SpotifyTools object
st = SpotifyTools( username, scope )

#Refresh Desired Playlist
st.refreshPlaylist( "chill" )