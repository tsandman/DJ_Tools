from SeratoSetAnalyzer import SeratoSetAnalyzer

#Spotipy Auth
myUsername = 12134764203

fileName = "testSet.txt"

setAnalyzer = SeratoSetAnalyzer( myUsername )
trackIdList = setAnalyzer.getAllSetData( fileName )

print('\nSong IDs:')
print( *trackIdList, sep = '\n' )

