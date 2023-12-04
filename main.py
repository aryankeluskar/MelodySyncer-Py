from fastapi import FastAPI
from spotipy.oauth2 import SpotifyClientCredentials
import json
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import requests

load_dotenv()

'''
    @param UserPlaylistID: Spotify Playlist ID of the user's playlist.
    @return playlistResults: JSON object containing the tracks in the playlist.
    @description: Uses Spotipy to get the tracks in the user's playlist.
'''
def getPlaylistTracksSP(UserPlaylistID):
    scope = "user-library-read"

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

    playlistResults = sp.playlist_tracks(playlist_id=UserPlaylistID, fields='items(track(name, duration_ms, album(name), artists(name)))', limit=100, offset=0, market=None)
    # print(playlistResults)


    for song in playlistResults['items']:
        pass
        # print(song['track']['name']+" "+song['track']['album']['name'])

    return playlistResults


'''
    @param videoID: YouTube Video ID of the track.
    @return videoDuration: Duration of the track in milliseconds.
    @description: Uses YouTube Data API to get the duration of the track in ISO Format, converts it to milliseconds and returns.
    Reason for using Youtube API again: YouTube search API wont give duration, therefore I need call the videos API to get the duration.
'''
def getTrackDurationYT(videoID):
    contentResponse = requests.get(f'https://youtube.googleapis.com/youtube/v3/videos?part=contentDetails&key={os.getenv("YOUTUBE_API_KEY")}&id={videoID}')
    # print(contentResponse.json())
    ISODuration = contentResponse.json()['items'][0]['contentDetails']['duration']
    # print(ISODuration)
    return requests.get(f'https://iso-duration-converter.onrender.com/convertFromISO/?duration={ISODuration}').json()
     


'''
    @param songName: Name of the song.
    @param artistName: Name of the artist.
    @param albumName: Name of the album.
    @param songDuration: Duration of the song in milliseconds.
    @return mostAccurate: YouTube Video ID of the most accurate track.
    @description: Uses YouTube Data API to search for the track, and returns the most accurate track. Working is explained in the function, yet here is a simple explanation:
    Determines an accuracy score for each of the top 5 tracks based on song length, publisher name and video title
    Returns the track with the highest accuracy score.
'''
def searchTrackYT(songName, artistName, albumName, songDuration):
    searchQuery = str(songName)+" "+str(albumName)+" "+str(artistName)+" "+"Official Audio"
    # print(searchQuery)
    searchQuery.replace(" ", "%20")  

    # Make an HTTP GET request to the API
    response = requests.get(f'https://youtube.googleapis.com/youtube/v3/search?part=snippet&q={searchQuery}&type=video&key={os.getenv("YOUTUBE_API_KEY")}')

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Print the response data
        # print(response.json())
        pass
        
    else:
        # Print an error message if the request failed
        print('Error:', response.status_code)
        return None
    
    accuracyScore = 0
    
    # print(response.json()['items'])
    mostAccurate = response.json()['items'][0]['id']['videoId'] # Default value is first video
    

    for item in response.json()['items']:
        # Firstly, it checks if the title of video has 'Official Audio' in it, to eliminate music videos.
        # Secondly, it checks whether the channel is a music channel by seeing ig channel title has 'Topic'. 
        # Example: Natalie Holt - Topic only publishes songs by Natalie Holt, and not any variations unless decided by the artist.
        # Thirdly, it verifies the song duration by equating it to the original song duration to eliminate possibilities of a different version (margin of error = 2s)
        # Returns the one which has the highest accuracy score.
        # print(item['id'])

        videoID = item['id']['videoId']
        currAccuracyScore = 0
        if 'Topic' in item['snippet']['channelTitle']:
            currAccuracyScore += 2
        # Not getting from Vevo channels since they tend to contain music videos.

        if 'Official Audio' in item['snippet']['title'] or 'Full Audio Song' in item['snippet']['title']:
            currAccuracyScore += 5
    
        videoDuration = getTrackDurationYT(videoID)
        
        # print(videoDuration, abs(int(videoDuration) - songDuration))
        if abs(int(videoDuration) - songDuration) <= 2000:
            currAccuracyScore += 2
        
        if currAccuracyScore > accuracyScore:
            accuracyScore = currAccuracyScore
            mostAccurate = videoID

        # print("Reahced 99")
        print(item['snippet']['channelTitle'], currAccuracyScore, videoID)

    return str(mostAccurate)

'''
    @param playlistID: Spotify Playlist ID of the user's playlist.
    @return youtubeURLs: List of YouTube URLs of the tracks in the playlist.
    @description: Calls getPlaylistTracksSP() to get the tracks in the user's playlist, and then calls searchTrackYT() to get the YouTube URL of the track.
'''
def convertPlaylist(playlistID):
    playlistResults = getPlaylistTracksSP(playlistID)
    youtubeURLs = []
    for song in playlistResults['items']:
        # print(song['track']['name']+" "+song['track']['album']['name'])
        currYTURL = str("https://youtube.com/watch?v="+str(searchTrackYT(song['track']['name'], song['track']['artists'][0]['name'], song['track']['album']['name'], song['track']['duration_ms'])))
        youtubeURLs.append(currYTURL)
        print(song['track']['name']+" "+currYTURL)
    # print(youtubeURLs)
    return youtubeURLs

# outFile = open("sample.json", "w")
# json.dump(getPlaylistTracksSP('7s6tR8GAGubasdzEDmNdXn'), outFile, indent=0)
# outFile.close()

def buildPlaylistFromList(name="New Playlist", description="Playlist transferred from Spotify with use of MelodySyncer", listOfIDs=[]):
   # Future Feature
    pass
    

# InPlaylistID = input("Enter playlist ID: ")
# print(convertPlaylist(InPlaylistID))


app = FastAPI()


@app.get("/")
async def root():
    return "Welcome to MelodySyncer! Transfer your Spotify Playlist to an amazing Youtube Playlist. Refer to /docs for more geeky info on usage or refer to the README.md on the GitHub Page for simpler information"

@app.get("/help")
async def root():
    return "Refer to /docs for more geeky info on usage or refer to the README.md on the GitHub Page for simpler information"

@app.get("/convertSong/")
async def read_item(songID: str = ''):
   if(len(songID)) == 0:
      return "Invalid Song ID"
   sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
   track = sp.track(songID)
   return str("https://youtube.com/watch?v="+str(searchTrackYT(track['name'], track['artists'][0]['name'], track['album']['name'], track['duration_ms'])))
   # return str("https://youtube.com/watch?v="+str((track['name'], track['artists'][0]['name'], track['album']['name'], track['duration_ms'])))

@app.get("/convertPlaylist/")
async def read_item(playlistID: str = '2zVaxB54fNngkbWs5uZnla'):
   return convertPlaylist(playlistID)

# print("https://youtube.com/watch?v="+searchTrackYT("OHMAMI","Chase Atlantic", "OHMAMI", 226835))
# print("https://youtube.com/watch?v="+searchTrackYT("Poker Face","Lady Gaga", "The Name", 237200))
