from __future__                import unicode_literals
import os
import yt_dlp as youtube_dl
from threading import Lock
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from oauth2client              import client
from oauth2client              import tools
from oauth2client.file         import Storage

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret.
CLIENT_SECRETS_FILE = "client_secret.json" #This is the name of your JSON file

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

class YtDownloader():
    mutex = Lock()
    downloadProgress = 0.0

    def __init__( self ):
        # Google Auth
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
        self.service = self.get_authenticated_service()

    def getDownloadProgress( self ):
        with self.mutex:
            return self.downloadProgress

    #Set up one-time auth
    @staticmethod
    def get_authenticated_service():
        credential_path = os.path.join('./', 'credential_sample.json')
        store = Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(CLIENT_SECRETS_FILE, SCOPES)
            credentials = tools.run_flow(flow, store)
        return build(API_SERVICE_NAME, API_VERSION, credentials=credentials)
    
    #Function that creates song information string
    def makeStringName( self, track ):
        return track['name'] + ' - ' + ' - '.join([artist['name'] for artist in track['artists']])

    def setOutputDir( self ):
        self.outputDir = 'C:/Users/tyler/Music/dlFromDjTool_2023-12-31/'

    def downloadTracks( self, tracks ):
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': self.outputDir+'%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
    
        numTracksToDownload = len( tracks['items'] )
        tracksDownloaded = list()

        for count, track in enumerate( tracks['items'] ):
            trackName = self.makeStringName( track['track'] )
    
            query_result = self.service.search().list(
                part = 'snippet',
                q = trackName,
                order = 'relevance', # You can consider using viewCount
                maxResults = 1,
                type = 'video', # Channels might appear in search results
                relevanceLanguage = 'en',
                safeSearch = 'moderate',
                ).execute()
    
            print( "Searchs " + str(count) )
            trackURL = "http://www.youtube.com/watch?v=" + query_result['items'][0]['id']['videoId']
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download( [trackURL] )
            
            with self.mutex:
                self.downloadProgress = ( count + 1 ) / numTracksToDownload
            
            tracksDownloaded.append( track['track']['id'] )
        
        return tracksDownloaded