import lyricsgenius as lg
import spotipy as spy
from spotipy.oauth2 import SpotifyClientCredentials

import os





def spotifyAuth(spclient, spsecret, ):
    """Function to get the access to the Spotify API"""
    spotify_access = SpotifyClientCredentials(spclient, spsecret)
    return spy.Spotify(client_credentials_manager=spotify_access)



def searchArtist(artistName, spotify):
    """Function to search the artist on Spotify, given the name
    
    The function search the given name from the variable artistName
    accessing the APIs through the spotify object. The resulting JSON
    after the call to the search({artistName}) function is parsed to get
    the names found in the search, then returns the artist's URI on Spotify
    """
    result = spotify.search('{' + artistName + '}',type="artist")
    return result['artists']['items'][0]['uri']


def searchAlbums(artistUri, spotify):
    """Function to get all the albums of a given artist

    The function gets the albums from an artist using the URI on Spotify,
    using the function artist_albums(artistUri, album_type) from Spotify APIs,
    then for each album found, appends the album's URI to a list, which is
    returned at the end of the function.
    """
    album_uris = []
    sp_albums = spotify.artist_albums(artistUri)

    for i in range(len(sp_albums['items'])):
        album_uris.append(sp_albums['items'][i]['uri'])
    return album_uris


def searchTracks(albumUris, spotify):
    """Function to get all the tracks titles from a list of albums

    The functiom, using a list of albums URIs (albumUris), calls the
    Spotify APIs function album_tracks. The resulting JSON is parsed to get
    all the tracks title from the albums, and then returned as a List of tracks
    """
    trackList = []
    for uri in albumUris:
        albumTracks = spotify.album_tracks(uri)
        for n in range(len(albumTracks['items'])):
            if albumTracks['items'][n]['name'] not in trackList:
                trackList.append(albumTracks['items'][n]['name'])
    return trackList


def sanitizeTracks(trackList):
    """Function to sanitize the tracks names, removing remixes and live sessions


    The function, given the track list (trackList), first removes all the unwanted tracks
    using list comprehension and a blacklist of words, then removes from each track name
    words in parentheses, which often makes the search for the lyrics difficult, using
    splits. If the track name starts with a parenthese, it will not remove them. 
    """
    blacklist = ['Remix', 'Live', 'Session', 'Mix', 'Bonus Track', '- Bonus Track', '/']
    trackNoBlacklist = [name for name in trackList if not any(black in name for black in blacklist)]
    trackSanitized = []
    for track in trackNoBlacklist:
        if(track[0] == ('(')):
            continue
        if (track.split('(')[0])[-1] == " ": 
            trackSanitized.append((track.split('(')[0])[:-1])
        else:
            trackSanitized.append((track.split('(')[0]))
    return trackSanitized

def trackExists(track):
    """Function to check if the JSON with a track data already exists."""
    filename = "/opt/tracks/" + track + ".json"
    if not os.path.exists(filename):
        return False
    return True

def getTrackData(track, genius, artistName):
    """Function to get all the track data through the Genius APIs

    The function calls the Genius APIs to search for the track data, 
    that is then returned as a JSON if the track was found. 
    If the track wasn't found, it will return None.
    """
    trackData = genius.search_song(title=track, artist=artistName)
    if trackData != None:
        return trackData.to_json()
    else:
        return None

def sanitizeTrackData(trackData):
    """Function to sanitize the JSON track data, removing newlines from easy reading by Logstash, Kafka and Spark"""
    return trackData.replace("\n", "")

def writeTrackData(trackData, track):
    """Function to write the track data by saving a JSON file with the track name in /opt/track/track.json"""
    filename = "/opt/tracks/" + track + ".json"
    file = open(filename, 'w')
    file.write(trackData)
    file.close()