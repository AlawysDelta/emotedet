from time import sleep
from crawler import *
import string


# API tokens and keys for the Genius and Spotify APIs
token = "KuoqBlgcWX77V_hckwPnfMHi0PESMREOfS_5-WKFKTVXYyr0-PycVaPfkT6rfV2N"

spclientId = "6fcc5988e78340049c9f85e7cb7731be"

spSecret = "91361bad19aa4509a76a04670f0c8420"


# Getting authorization for Spotify APIs
spotify = spotifyAuth(spclientId, spSecret)

tracks = []
# Reading Artist name from environmental variable ARTIST and searching into Spotify
artistName = os.environ['ARTIST']
# Sanitize Artist name from all punctuation to ease search
artistName = artistName.lower().translate(str.maketrans(string.punctuation, ' '*len(string.punctuation)))

artistUri = searchArtist(artistName, spotify)


# exiting if Artist was not found
if(artistUri == None):
    exit(123)

# authorizing Genius APIs
genius = lg.Genius(token)

# Search for all the tracks of an artist every 30 seconds, until the program is stopped
while (True):
    # perform searches into Spotify to get all the tracks name
    albumUris = searchAlbums(artistUri, spotify)

    tracks = searchTracks(albumUris, spotify)

    tracks = sanitizeTracks(tracks)

    

    # for each track, gets the track data from Genius APis and save it into a JSON,
    # after getting sanitized, if it wasn't already saved, if the track is found.
    for track in tracks:
        if not trackExists(track):
            trackData = getTrackData(track, genius,artistName)
            if trackData == None:
                continue
            trackData = sanitizeTrackData(trackData)
            writeTrackData(trackData, track)
    # waits 30 seconds to start the search again
    print("Going to sleep...")
    sleep(30)
    print("Waking up...")
        

