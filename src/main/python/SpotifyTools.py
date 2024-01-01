import spotipyExt
import os
import threading
from threading import Lock
import time
import spotipy.util as util

from YtDownloader import YtDownloader

'''
    SpotifyTools is an extension of the SpotifyExt class. It provides additional functionality to the library 
    tailored to Spotify power users who like to organize their library and playlists
'''
class SpotifyTools( spotipyExt.SpotifyExt ):
    #Member Variables
    _genreList      = list()
    _genreTrackDict = dict()
    _actionProgress = 0.0
    _mutex = Lock()

    #def __init__( self, username, scope ):
    def __init__( self, *args ):

        #Get spotify user parameters
        if len( args ) < 3:
            spotify_username = args[0]
            spotify_scope    = args[1]
            
            #Authenticate through spotipy
            token = util.prompt_for_user_token( spotify_username, spotify_scope, client_id=os.environ['SPOTIFY_CLIENT_ID'], client_secret=os.environ['SPOTIFY_CLIENT_SECRET'], redirect_uri=os.environ['SPOTIFY_REDIRECT_URI'] )
        else:
            spotify_username      = args[0]
            spotify_client_id     = args[1]
            spotify_client_secret = args[2]
            spotify_redirect_uri  = args[3]
            spotify_scope         = args[4]
        
            #Authenticate through spotipy
            token = util.prompt_for_user_token( spotify_username, spotify_scope, client_id=spotify_client_id, client_secret=spotify_client_secret, redirect_uri=spotify_redirect_uri )
        
        #Call spotifyExt class constructor
        super().__init__( token )
        self.username = spotify_username

    def getActionProgress( self ):
        with self._mutex:
            ret = self._actionProgress
        return ret

    #Returns playlist ID given playlist name
    def _getPlaylistId( self, playlistName ):
        usrPlaylists = self.current_user_playlists()

        for playlistItr in usrPlaylists['items']:
            #import pdb; pdb.set_trace()
            if playlistItr['name'] == playlistName:
                playlistId = playlistItr['id']
                break
        return playlistId

    #Takes genreTrackDict and makes playlists accordingly
    def _createGenrePlaylists( self, username, desiredGenres ):
        
        #Create playlist for each genre in playlists
        playlistDict = dict()
        for genre in desiredGenres:
            playlistDict[genre] = self.user_playlist_create( user=username, name=genre, public=True )
        
        #Add tracks to playlists
        for track in self._genreTrackDict:
            self.user_playlist_add_tracks( user=username, playlist_id=playlistDict[self._genreTrackDict[track]]['id'], tracks=[track], position=None)

    #Sorts a users spotify library into different genres and creates a genre-track dictionary
    def _sortLibrary( self, limit, offset, desiredGenres ):

        houseGenres = []

        results = self.current_user_saved_tracks( limit, offset )

        for item in results['items']:
            track     = item['track']
            trackID   = track['id']
            trackName = track['name']
            artist    = track['artists'][0]['name']
            data      = self.search( q='artist:' + track['artists'][0]['name'], type='artist' )

            if not data['artists']['items'][0]['genres']:
                thisGenre = ['NA']
            else:
                thisGenre = data['artists']['items'][0]['genres']

            for genre in thisGenre:
                genreTokens = genre.split(' ')

                for idx, g in enumerate(genreTokens):
                    if g == 'tech':
                        if genreTokens[idx+1] == 'house':
                            gg = 'tech house'
                    else:
                        gg = g

                    if gg in desiredGenres:
                        self._genreTrackDict[trackID] = gg

                if genre not in self._genreList and genre != 'NA':
                    self._genreList.append( genre )

            print( track['name'] + ' - ' + track['artists'][0]['name'] + ' - ' + ', '.join( thisGenre ) )

    #Public Interface
    def createGenrePlaylistsFromLib( self, username, desiredGenres, libraryStartIdx, libraryEndIdx ):
        ''' 
            Creates playlists from list of genres and sorts library into the desired genre playlists
    
            Parameters:
                -- desiredGenres   - list of genres the user wants the tool to create a playlist for
                -- libraryStartIdx - library index to start sorting at (zero-based)
                -- libraryEndIdx   - library index to end sorting at (zero-based)
        '''
        #Get function inputs 
        offset = libraryStartIdx
        limit = libraryEndIdx - libraryEndIdx

        #Call member functions to create track-genre dictionary and create playlists
        self._sortLibrary( limit, offset, desiredGenres )
        self._createGenrePlaylists( username, desiredGenres )

    def sortPlaylist( self, playlistName, sortType, sortOrder ):
        ''' Sorts a playlist given a sort parameter and creates a new playlist

            Parameters:
                -- playlistName - playlist to be sorted
                -- sortType     - sorting parameter
                -- sortOrder    - ascending or descending sort order
        '''
        trackDict    = dict()

        #Get playlist information
        playlistId     = self._getPlaylistId( playlistName )
        playlistHandle = self.user_playlist( user=self.username, playlist_id=playlistId, fields=None, market=None )

        #Loop through playlist
        for idx,track in enumerate( playlistHandle['tracks']['items'] ):
            trackId = track['track']['id']
            trackFeatures = self.audio_features( trackId )[0]
            trackDict[trackId] = dict()
            trackDict[trackId] = trackFeatures

        #Set up sorted playlist (creates new playlist)
        sortedPlaylistName = playlistName+'_'+sortType+'_'+sortOrder
        self.user_playlist_create( user=self.username, name = sortedPlaylistName, public = True, description = 'sorted via python' )
        sortedPlaylistId = self._getPlaylistId( sortedPlaylistName )

        #Populate new playlist with sorted tracks
        for newIdx,track in enumerate( sorted( trackDict.items(), key=lambda x: x[1][sortType], reverse=sortOrder=='ascending' ) ):
            id = track[0]
            self.user_playlist_add_tracks( user=self.username, playlist_id = sortedPlaylistId, tracks=[id], position=0 )
    
    def refreshPlaylist( self, playlistName ):
        ''' Reads a playlist and replaces all songs with new songs that are similar in style and energy
            in order to keep a playlist fresh and listenable

            Parameters:
                - playlistName: name of Spotify playlist
        '''
        #Get playlist information
        playlistId = self._getPlaylistId( playlistName )
        playlistHandle = self.user_playlist( user=self.username, playlist_id=playlistId, fields=None, market=None )

        #Create container for 'refreshed' tracks
        newTracks = list()

        #Loop through playlist
        for idx,track in enumerate( playlistHandle['tracks']['items'] ):
            trackId = track['track']['id']
            
            #Get reccomendation based on track from specified playlist
            recs = self.recommendations( seed_artists=None, seed_genres=None, seed_tracks=[trackId], limit=1, country=None )

            #Add to new tracks container
            if ( recs['tracks'] ):
                newTracks.append( recs['tracks'][0]['id'] )

        #Create new playlist for 'refreshed' tracks
        refreshedPlaylistName = ( playlistName + '_refreshed' )
        self.user_playlist_create( user=self.username, name = refreshedPlaylistName, public = True, description = 'created via SpotfiyTools by Tyler Sandman' )
        refreshedPlaylistId = self._getPlaylistId( refreshedPlaylistName )
        
        #Add tracks to new playlist
        self.user_playlist_add_tracks( user=self.username, playlist_id = refreshedPlaylistId, tracks=newTracks, position=0 )

    def getPlaylistIdFromName( self, playlistName ):
        playlists = self.user_playlists(self.username, limit=50, offset=0)
        for playlist in playlists['items']:
            if playlist['name'] == playlistName:
                return playlist['id']
        return 0
        
    def downloadPlaylist( self, playlistName, removeFromPlaylist=False ):
        self.yt = YtDownloader()
        self.yt.setOutputDir() #todo

        dlTracks = self.getTracksFromPlaylistName(playlistName)
        dlTrackIds = [val.get('track').get('id') for val in dlTracks['items']]

        t = threading.Thread( target=self.yt.downloadTracks, args=[dlTracks] )
        t.start()
        while ( self._actionProgress < 1.0 ):
            self._mutex.acquire()
            self._actionProgress = self.yt.getDownloadProgress()
            self._mutex.release()
            time.sleep( 1 )
        t.join()

        if removeFromPlaylist:
            id = self.getPlaylistIdFromName( playlistName )
            if id != 0:
                self.user_playlist_remove_all_occurrences_of_tracks( user=self.username, playlist_id=id, tracks=dlTrackIds, snapshot_id=None )