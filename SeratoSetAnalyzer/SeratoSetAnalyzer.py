import os
import pdb
import re
import spotipyExt
import pandas as pd
import numpy  as np
import matplotlib.pyplot as plt

class SeratoSetAnalyzer:
    def __init__( self, username ):
        self.username = username

    def spotifyInit( self ):
        sp_scope = 'user-library-read playlist-read-private'
        self.sp = spotipyExt.initializeSpotifyToken( sp_scope, self.username )

    @staticmethod
    def generateEqualLines( string, fp):
        for line in fp:
            if string in line:
                yield line 
        return line
     
    #Apply filters to text list of songs to increase success likelihood of spotify search
    @staticmethod
    def applyFilters( songList ):
        songList = [ x.strip()                       for x in songList ] #remove whitespace/endl characters
        songList = [ re.sub( r'\[.*?\]', '', x )     for x in songList ] #remove []
        songList = [ re.sub( '[&]', '', x )          for x in songList ] #remove special characters that cause search to break
        songList = [ x.replace("(Original Mix)", "") for x in songList ] #remove original mix tag
        songList = [ x.replace("Original Mix", "")   for x in songList ] #without parens
     
        return songList
     
    #Restructure string containing track name for second search attempt
    def reorderSongName( self, songName ):
        strSplit = songName.split('-')
        strSplit.reverse()
        strSplit = ', '.join( strSplit )
        strSplit = strSplit.replace( ",", " " )
     
        return strSplit
     
     #Extract songs from set
    def extractSongListFromSet( self, fileName ):
        songs = list()
        with open( fileName ) as f:
            for line in self.generateEqualLines( "Writing Tags", f ):
                slash = line.rfind('\\')
                eol   = line.rfind('3')
                songs.append(line[slash+1:eol-3])
                print( line[slash+1:eol-3] )
     
            #Apply Filters for Spotify Search
            songs = self.applyFilters( songs )
     
            return songs
     
    def getTrackIdList( self, songs ):
        print( '\nSongs found:' )
        print( *songs, sep = "\n" )
     
        print( '\nSongs to add:' )
        trackIdList = list()
        for s in songs:
            srch = self.sp.search( s, limit=1, offset=0, type='track', market=None )
            try:
               print( srch['tracks']['items'][0]['name'] )
               trackIdList.append( srch['tracks']['items'][0]['id'] )
            except:
                try:
                    print( 'No results for: ', s )
                    print( 'Trying again...' )
     
                    strSplit = self.reorderSongName( s )
                    print( 'New String: ', strSplit )
     
                    srch = self.sp.search( strSplit, limit=1, offset=0, type='track', market=None ) 
                    trackIdList.append( srch['tracks']['items'][0]['id'] )
                    print("Found: ")
                    print( srch['tracks']['items'][0]['name'] )
                except: 
                    print( 'No spotify results found for: ', s )
     
        return trackIdList

    def getAllSetData( self, setDataFile ):
        self.spotifyInit()
        songs       = self.extractSongListFromSet( setDataFile )
        trackIdList = self.getTrackIdList( songs )
       
        features = self.sp.audio_features( trackIdList )

        dataFrame = pd.DataFrame( features, index=range( len( features ) ), columns=features[0].keys() )
        dataFrame.drop( ['type','uri'], axis=1 ) 
#        pd.plotting.scatter_matrix( dataFrame )
#        pd.plotting.andrews_curves( dataFrame )
#        pd.plotting.boxplot( dataFrame )
        ax = plt.gca()
        
        dataToPlot = dict.fromkeys( ['danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness', 'instrumentalness', 'tempo' ] )
        dataToPlot['danceability'] = ['very danceable', 'not danceable']

        xAxis = 'Song Number'

        for col in dataToPlot.keys():
            ax = dataFrame.plot( kind='line', y=col )
            plt.xlabel( xAxis )

#            fig, ax = plt.subplots()
            
            # We need to draw the canvas, otherwise the labels won't be positioned and 
            # won't have values yet.
#            fig.canvas.draw()
            
            if col == 'danceability':
                labels = [item.get_text() for item in ax.get_yticklabels()]
                labels[len(labels)-2] = dataToPlot[col][0]
                labels[1] = dataToPlot[col][1]
            
                ax.set_yticklabels(labels)

        plt.show()
        
        return trackIdList
