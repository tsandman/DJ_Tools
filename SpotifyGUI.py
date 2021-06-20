import sys
import os
import time
import threading
import os.path

from SpotifyTools import SpotifyTools
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import QtGui

class SpotifySettings():
    username      = str()
    client_id     = str()
    client_secret = str()
    redirect_url  = str()

class SpotifyGUI( QWidget ):
    actionProgress = 0
    spotifySettings = SpotifySettings()

    def __init__(self, parent = None):
        super( SpotifyGUI, self ).__init__(parent)

        settings = QSettings( 'apps', 'settings' )
        if settings.value( 'not_first_time_auth' ):
        #if False:
            print( "\nNotFirstTimeAuth!" )
            
            self.spotifySettings.username      = settings.value( 'spotify_username' )
            self.spotifySettings.client_id     = settings.value( 'spotify_client_id' )
            self.spotifySettings.client_secret = settings.value( 'spotify_client_secret' )
            self.spotifySettings.redirect_url  = settings.value( 'spotify_redirect_url' )

        else:
            print( "\nFirstTimeAuth!" )
            settings.setValue( 'not_first_time_auth', True )

            choice = QMessageBox.question(self, 'Setup',
                                            "Start first time setup?",
                                            QMessageBox.Yes | QMessageBox.No)
            
            if choice == QMessageBox.Yes:
                self.spotifySettings.username ,      success = QInputDialog.getText( self, 'Setup', 'Enter Spotify Username:' )
                self.spotifySettings.client_id ,     success = QInputDialog.getText( self, 'Setup', 'Enter Spotify Client ID:' )
                self.spotifySettings.client_secret , success = QInputDialog.getText( self, 'Setup', 'Enter Spotify Client Secret:' )
                self.spotifySettings.redirect_url ,  success = QInputDialog.getText( self, 'Setup', 'Enter Spotify Redirect URL:' )

                settings.setValue( 'spotify_username',      self.spotifySettings.username      )
                settings.setValue( 'spotify_client_id',     self.spotifySettings.client_id     )
                settings.setValue( 'spotify_client_secret', self.spotifySettings.client_secret )
                settings.setValue( 'spotify_redirect_url',  self.spotifySettings.redirect_url  )

                
            else:
                sys.exit()

        if not settings.value( "youtube_dl_auth" ):
            continueSetup = QMessageBox.question (self, 'Setup',
                                            "Have you added the client_secret.json file?",
                                            QMessageBox.Yes | QMessageBox.No )
            
            if continueSetup == QMessageBox.Yes:
                if not os.path.isfile( "client_secret.json" ):
                    error_dialog = QErrorMessage()
                    error_dialog.showMessage('ERROR: No client secret file found!')
                    error_dialog.exec_()
                    sys.exit()
                else:
                    settings.setValue( 'youtube_dl_auth', True )
            else:
                sys.exit()



        #username = os.environ['SPOTIFY_USERNAME']
        username = self.spotifySettings.username
        scope = 'user-library-modify user-library-read user-library-read playlist-modify playlist-modify-private playlist-read-private playlist-read-collaborative'
        
        self.sp = SpotifyTools( self.spotifySettings.username, self.spotifySettings.client_id, self.spotifySettings.client_secret, self.spotifySettings.redirect_url, scope )
        playlists = self.sp.current_user_playlists()

        layout = QGridLayout()
        self.playlistActions = list()

        #Create Widgets
        self.label              = QLabel()
        self.cb                 = QComboBox()
        self.startActionButton  = QPushButton()
        self.playlistActions.append( QRadioButton("Download Playlist") )
        self.playlistActions.append( QRadioButton("Refresh Playlist")  )
        self.playlistActions.append( QRadioButton("Sort Playlist")     )
        self.progressBar        = QProgressBar()

        self.fileMenu = QMenuBar(self)
        self.fileMenu.addMenu("&File")
        self.fileMenu.addMenu("&Help")

        #Set Widget Defaults
        self.progressBar.setValue(0)
        self.playlistActions[0].setChecked(True) #isChecked() 
        
        self.label.setText( 'User Playlists: ' )
        self.startActionButton.setText( 'Start' )
        
        for p in playlists['items']:
            self.cb.addItem( p['name'] )

        #Set Callbacks 
        self.cb.currentIndexChanged.connect(self.selectionchange)
        #self.startActionButton.clicked.connect( self.performAction )
        self.startActionButton.clicked.connect( self.threadAction )

        layout.addWidget( self.fileMenu, 0, 0 )	

        widgetOffset = 4
        layout.addWidget( self.label, 0+widgetOffset, 0 )
        layout.addWidget( self.cb, 0+widgetOffset, 1 )
        for paIdx,pa in enumerate( self.playlistActions ):
            layout.addWidget( pa, 0+widgetOffset, paIdx + 2 )  
        layout.addWidget( self.startActionButton, 1+widgetOffset, 4 )
        layout.addWidget( self.progressBar, 1+widgetOffset, 1, 1, 3 )

        self.setLayout(layout)
        self.setWindowTitle("Spotify Playlist Tool")

        self.callbackDict = {
                                0: self.sp.downloadPlaylist,
                                1: self.sp.refreshPlaylist,
                                2: self.sp.sortPlaylist
                            }


    def selectionchange(self,i):
        print( "Items in the list are :" )
		
        for count in range(self.cb.count()):
            print( self.cb.itemText(count) )
        print( "Current index",i,"selection changed ",self.cb.currentText() )
        self.selectedPlaylistIdx = i
    
    def performAction( self ):
        for pIdx,p in enumerate( self.playlistActions ):
            if p.isChecked():
                self.callbackDict[pIdx]( self.cb.currentText() )
		
    def threadAction( self ):
        t = threading.Thread( target=self.performAction )
        t.start()

        progressPrev = 0.0
        while ( self.actionProgress < 1.0 ):
            self.actionProgress = self.sp.getActionProgress()
            #print( "\nProgress: " + str( self.actionProgress ) )
            if ( self.actionProgress != progressPrev ):
                self.progressBar.setValue( int( 100.0*self.actionProgress ) )
                QApplication.processEvents() 
                progressPrev = self.actionProgress
            time.sleep( 1 )

        t.join()


def main():
    app = QApplication(sys.argv)
    ex = SpotifyGUI()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()