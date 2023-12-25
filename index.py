import json
from fastapi import FastAPI
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
import spotipy
from dotenv import load_dotenv
import requests
import os
import time
import aiohttp
import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import partial
import starlette
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# import pymongo


load_dotenv()


app = FastAPI()
app.mount("/app", StaticFiles(directory="app"), name="app")


# """
# @route: /
# @description: the root route
# @returns: a welcome message
# """
# @app.get("/")
# async def root() -> str:
#     return "Welcome to MelodySyncer! Transfer your Spotify Playlist to an amazing Youtube Playlist. Refer to /docs for more geeky info on usage or refer to the README.md on the GitHub Page for simpler information"


@app.get("/")
async def root():
    return starlette.responses.RedirectResponse("/app/index.html")


"""
@route: /api/help
@description: the help route
@returns: a help message
"""


@app.get("/api/help")
async def root() -> str:
    return "Refer to /docs for more geeky info on usage or refer to the README.md on the GitHub Page for simpler information"


"""
@name: make_request
@description: a single function to make requests in order to reduce latency
@params: session - the aiohttp session
@params: url - the url to make the request to
@params: method - the method of the request (GET or POST)
@params: headers - the headers of the request
@params: data - the data to send in the request
@returns: the response of the request if successful, None otherwise
"""


async def make_request(session, url=None, method="GET", headers=None, data=None):
    #  print("making request", method, url, headers, data)
    try:
        if method == "GET":
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    print(f"Error: {response.status}")
                    return None
        elif method == "POST":
            async with session.post(url, headers=headers, data=data) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    print(f"Error: {response.status}")
                    return None
    except Exception as e:
        print("error occured: " + str(e))
        return "ERROR"


"""
Route: /api/playlist
Description: Takes in a playlist ID and returns a list of youtube URLs
Params: query - the playlist ID
Params: youtubeAPIKEY - the youtube API key
Returns: a list of youtube URLs
"""


@app.get("/api/playlist")
async def hello_world(query: str = "", youtubeAPIKEY: str = ""):
    # start timer at start, end timer at end, print total time taken
    # verify if youtubeAPIKEY is given, otherwise return string saying check your API key
    if youtubeAPIKEY == "":
        return "Check your API key again"
    if youtubeAPIKEY == "default":
        youtubeAPIKEY = os.getenv("YOUTUBE_API_KEY")

    print("received playlist request for " + query)
    try:
        async with aiohttp.ClientSession() as session:
            t0 = time.time()
            print("received request for playlist ID " + query)
            playlistResults = await getPlaylistTracksSP(query)
            youtubeURLs = ["" for _ in range(len(playlistResults["items"]))]
            res_task = asyncio.ensure_future(
                setAnalytics(session, 1, len(playlistResults["items"]), 1)
            )
            print(
                "setting analytics: "
                + str(len(playlistResults["items"]))
                + " songs, 1 playlist, 1 call"
            )
            tasks = []
            for i, song in enumerate(playlistResults["items"]):
                task = asyncio.create_task(
                    searchTrackYT(
                        session,
                        song["track"]["name"],
                        song["track"]["artists"][0]["name"],
                        song["track"]["album"]["name"],
                        song["track"]["duration_ms"],
                        youtubeURLs,
                        youtubeAPIKEY,
                        i,
                    )
                )
                tasks.append(task)
            await asyncio.gather(*tasks)
            res = await res_task
            print(res)
            t1 = time.time()
            for i in range(len(youtubeURLs)):
                if youtubeURLs[i] == "Check your YouTube API key":
                    return "Check your YouTube API key"
                if youtubeURLs[i] != "":
                    youtubeURLs[i] = "https://youtube.com/watch?v=" + str(
                        youtubeURLs[i]
                    )
            print("Total time taken: " + str(t1 - t0))
            return youtubeURLs
    except Exception as e:
        print("error occured: " + str(e))
        return "Check your playlist ID again"


"""
Route: /api/song
Description: Takes in a song ID and returns a youtube URL
Params: query - the song ID
Params: youtubeAPIKEY - the youtube API key
Returns: a youtube URL
"""


@app.get("/api/song")
async def hello_world(query: str = "", youtubeAPIKEY: str = ""):
    # start timer at start, end timer at end, print total time taken
    # verify if youtubeAPIKEY is given, otherwise return string saying check your API key
    if youtubeAPIKEY == "":
        return "Check your API key again"
    if youtubeAPIKEY == "default":
        youtubeAPIKEY = os.getenv("YOUTUBE_API_KEY")

    t0 = time.time()
    try:
        async with aiohttp.ClientSession() as session:
            print("received song request for " + query)
            sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
            song = sp.track(query)

            res_task = asyncio.ensure_future(setAnalytics(session, 1, 1, 0))

            # if album type is a single, then name is in ["album"]["name"]
            if song["album"]["album_type"] == "single":
                vidID = searchTrackYT(
                    session,
                    song["name"],
                    song["artists"][0]["name"],
                    song["album"]["name"],
                    song["duration_ms"],
                    "NotRequired",
                    youtubeAPIKEY,
                    -1,
                )
                print(vidID)
                if vidID == "Check your YouTube API key":
                    return "Check your YouTube API key"

            else:
                vidID = searchTrackYT(
                    session,
                    song["name"],
                    song["artists"][0]["name"],
                    song["album"]["name"],
                    song["duration_ms"],
                    "NotRequired",
                    youtubeAPIKEY,
                    -1,
                )
                print(vidID)
                if vidID == "Check your YouTube API key":
                     return "Check your YouTube API key"
                        
            vidID_final = await vidID
            res = await res_task
            print(res)
            t1 = time.time()
            print("Total time taken: " + str(t1 - t0))
            return "https://youtube.com/watch?v=" + str(vidID_final)

    except Exception as e:
        print("error occured: " + str(e))
        return "Check your song ID again"


#  except Exception as e:
#      return {"error": str(e)}

"""
@name setAnalytics
@description: updates the analytics database
@params: session - the aiohttp session
@params: newCalls - the number of new calls to add
@params: newSongs - the number of new songs to add
@params: newPlaylists - the number of new playlists to add
@returns: the response of the request if successful, None otherwise
"""


async def setAnalytics(
    session, newCalls: int = 0, newSongs: int = 0, newPlaylists: int = 0
) -> str:
    headers = {
        "apiKey": os.getenv("MONGODP_APIKEY"),
        "Content-Type": "application/ejson",
        "Accept": "application/json",
    }
    payload = {
        "dataSource": "Cluster0",
        "database": "API_Analytics",
        "collection": "SpotifyToYoutube",
        "filter": {"_id": {"$oid": os.getenv("MONGO_OID")}},
        "update": {
            "$inc": {
                "MESOsongsConverted": newSongs,
                "MESOplaylistsConverted": newPlaylists,
                "MESOtotalCalls": newCalls,
                "ISOtotalCalls": newSongs * 5,
            }
        },
    }

    response = await make_request(
        session,
        os.getenv("MONGODB_UPDATEURL"),
        "POST",
        headers=headers,
        data=json.dumps(payload),
    )
    if response:
        print(response)
        # print("setting analytics\n")
        #  print(response.text)
        #  return response.text
    return response


# async def convertPlaylist(session, playlistID, youtubeAPIKEY):

"""
CORE OF THE API!!!
@name: searchTrackYT
@description: searches youtube for the most accurate track
@params: session - the aiohttp session
@param songName: Name of the song.
@param artistName: Name of the artist.
@param albumName: Name of the album.
@param songDuration: Duration of the song in milliseconds.
@param youtubeURLs: List of YouTube URLs of the tracks in the playlist, "NotRequired" if not required.
@param youtubeAPIKEY: YouTube API Key.
@param index: Index of the track in the Spotify playlist, "-1" if not required.
@return mostAccurate: YouTube Video ID of the most accurate track.
@description: Uses YouTube Data API to search for the track, and returns the most accurate track. Working is explained in the function, yet here is a simple explanation:
Determines an accuracy score for each of the top 5 tracks based on song length, publisher name and video title
Returns the track with the highest accuracy score.
"""


async def searchTrackYT(
    session,
    songName,
    artistName,
    albumName,
    songDuration,
    youtubeURLs,
    youtubeAPIKEY,
    index,
) -> str:
    searchQuery = (
        str(songName)
        + " "
        + str(albumName)
        + " "
        + str(artistName)
        + " "
        + "Official Audio"
    )
    #  print(searchQuery)
    searchQuery = searchQuery.replace(" ", "%20")
    #  print("searching for " + searchQuery)

    response = await make_request(
        session,
        f"https://youtube.googleapis.com/youtube/v3/search?part=snippet&q={searchQuery}&type=video&key={youtubeAPIKEY}",
    )
    if response == "ERROR":
         return "Check your YouTube API key"

    # print(response)

    if response:
        #  with open("response.json", "w") as file:
        #      json.dump(response, file)
        #  print((response["items"][0]["id"]["videoId"]))

        accuracyScore = 0
        mostAccurate = ""
        # response_json = await response.json()
        #  mostAccurate = response["items"][0]["id"]["videoId"]
        #  print("searching for " + str(response))
        for item in response["items"]:
            # Firstly, it checks if the title of video has 'Official Audio' in it, to eliminate music videos.
            # Secondly, it checks whether the channel is a music channel by seeing ig channel title has 'Topic'.
            # Example: Natalie Holt - Topic only publishes songs by Natalie Holt, and not any variations unless decided by the artist.
            # Thirdly, it verifies the song duration by equating it to the original song duration to eliminate possibilities of a different version (margin of error = 2s)
            # Returns the one which has the highest accuracy score.
            # print(item['id'])
            videoID = item["id"]["videoId"]
            currAccuracyScore = 0

            if "Topic" in item["snippet"]["channelTitle"]:
                currAccuracyScore += 2

            if (
                "Official Audio" in item["snippet"]["title"]
                or "Full Audio Song" in item["snippet"]["title"]
            ):
                currAccuracyScore += 2

            videoDuration_coroutine = getTrackDurationYT(
                session, videoID, youtubeAPIKEY
            )
            videoDuration_res = await videoDuration_coroutine
            #  print(str(videoDuration_res))
            videoDuration = int(videoDuration_res)

            if abs(int(videoDuration) - songDuration) <= 2000:
                currAccuracyScore += 5

            if currAccuracyScore > accuracyScore:
                accuracyScore = currAccuracyScore
                mostAccurate = videoID

        # mostAccurate = "youtube.com/watch?v="+str(mostAccurate)
        # print(mostAccurate)
        if "NotRequired" in youtubeURLs or index == -1:
            return str(mostAccurate)
        else:
            youtubeURLs[index] = str(mostAccurate)


"""
@name: run_sync
@description: runs a function synchronously
@params: func - the function to run
@params: *args - the arguments to pass to the function
@params: **kwargs - the keyword arguments to pass to the function
@returns: the result of the function
"""


def run_sync(func, *args, **kwargs):
    loop = asyncio.get_running_loop()
    partial_func = partial(func, *args, **kwargs)
    return loop.run_in_executor(ThreadPoolExecutor(), partial_func)


"""
@name: getPlaylistTracksSP
@description: gets the tracks of a playlist from Spotify
@params: UserPlaylistID - the ID of the playlist
@returns: the tracks of the playlist
"""


def getPlaylistTracksSP(UserPlaylistID) -> json:
    scope = "user-library-read"
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

    return run_sync(
        sp.playlist_tracks,
        UserPlaylistID,
        fields="items(track(name, duration_ms, album(name), artists(name)))",
        limit=100,
        offset=0,
        market=None,
    )


"""
uses my own API key to get the duration of a video
API is iso-duration-converter.onrender.com/ (more info on https://github.com/aryankeluskar/ISO-Duration-Converter)
@name getTrackDurationYT
@description: gets the duration of a video from YouTube
@params: session - the aiohttp session
@params: videoID - the ID of the video
@params: youtubeAPIKEY - the youtube API key
@returns: the duration of the video in milliseconds instead of ISO format
"""


async def getTrackDurationYT(session, videoID, youtubeAPIKEY) -> int:
    contentResponse = await make_request(
        session=session,
        url=f"https://youtube.googleapis.com/youtube/v3/videos?part=contentDetails&key={youtubeAPIKEY}&id={videoID}",
    )

    if contentResponse:
        ISODuration = contentResponse["items"][0]["contentDetails"]["duration"]
        if "H" in ISODuration and "M" in ISODuration and "S" in ISODuration:
            videoDuration = (
                int(ISODuration[ISODuration.find("T") + 1 : ISODuration.find("H")])
                * 3600000
                + int(ISODuration[ISODuration.find("H") + 1 : ISODuration.find("M")])
                * 60000
                + int(ISODuration[ISODuration.find("M") + 1 : ISODuration.find("S")])
                * 1000
            )
        elif "H" in ISODuration and "M" in ISODuration:
            videoDuration = (
                int(ISODuration[ISODuration.find("T") + 1 : ISODuration.find("H")])
                * 3600000
                + int(ISODuration[ISODuration.find("H") + 1 : ISODuration.find("M")])
                * 60000
            )
        elif "H" in ISODuration and "S" in ISODuration:
            videoDuration = (
                int(ISODuration[ISODuration.find("T") + 1 : ISODuration.find("H")])
                * 3600000
                + int(ISODuration[ISODuration.find("H") + 1 : ISODuration.find("S")])
                * 1000
            )
        elif "M" in ISODuration and "S" in ISODuration:
            videoDuration = (
                int(ISODuration[ISODuration.find("T") + 1 : ISODuration.find("M")])
                * 60000
                + int(ISODuration[ISODuration.find("M") + 1 : ISODuration.find("S")])
                * 1000
            )
        elif "H" in ISODuration:
            videoDuration = (
                int(ISODuration[ISODuration.find("T") + 1 : ISODuration.find("H")])
                * 3600000
            )
        elif "M" in ISODuration:
            videoDuration = (
                int(ISODuration[ISODuration.find("T") + 1 : ISODuration.find("M")])
                * 60000
            )
        elif "S" in ISODuration:
            videoDuration = (
                int(ISODuration[ISODuration.find("T") + 1 : ISODuration.find("S")])
                * 1000
            )
        else:
            videoDuration = 0
    return videoDuration


"""
just a dummy route to test the analytics
"""
# @app.get("/api/analytics")
# async def getAnalytics():
#     async with aiohttp.ClientSession() as session:
#         res = await setAnalytics(session, 10, 3, 1)
#         print(res)
#         return "analytics"


"""
following code is my 13th reason
a star would be appreciated!
"""
#  async with aiohttp.ClientSession() as session:
#      async with aiohttp.ClientSession() as session:
#          response = requests.post(
#              session,
#              os.getenv("MONGODB_UPDATEURL"),
#              headers=headers,
#              data=json.dumps(payload),
#          )


# async def getAnalytics() -> json:
#     # Perform analytics calculations
#     payload = json.dumps(
#         {
#             "collection": "SpotifyToYoutube",
#             "database": "API_Analytics",
#             "dataSource": "Cluster0",
#             "projection": {
#                 "_id": 1,
#                 "songsConverted": 1,
#                 "playlistsConverted": 1,
#                 "totalCalls": 1,
#             },
#         }
#     )
#     headers = {
#         "apiKey": os.getenv("MONGODP_APIKEY"),
#         "Content-Type": "application/ejson",
#         "Accept": "application/json",
#     }

#     async with aiohttp.ClientSession() as session:
#         async with aiohttp.ClientSession() as session:
#             response = await make_request(
#                 session,
#                 "POST",
#                 os.getenv("MONGODP_READURL"),
#                 headers=headers,
#                 data=payload,
#             )


#  print(response)


#  json_response = json.loads(response.text)
#  return json_response
