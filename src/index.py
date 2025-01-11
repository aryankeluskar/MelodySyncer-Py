import asyncio
from collections import defaultdict
import time
import aiohttp
from fastapi import FastAPI
from fastapi.responses import FileResponse
import os
import json

from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

load_dotenv()
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import dns.resolver
dns.resolver.default_timeout = 30  # Increase DNS resolver timeout

# Configure MongoDB client with better connection options
def get_mongo_client():
    try:
        client = MongoClient(
            os.getenv("MONGO_URI"),
            serverSelectionTimeoutMS=30000,  # Increase server selection timeout
            connectTimeoutMS=20000,          # Connection timeout
            socketTimeoutMS=20000,           # Socket timeout
            maxPoolSize=1,                   # Minimize connections for serverless
            retryWrites=True,               # Enable retry writes
            w='majority'                    # Write concern
        )
        # Force a connection to verify it works
        client.admin.command('ping')
        return client
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        print(f"Failed to connect to MongoDB: {e}")
        return None

app = FastAPI()

templates_dir = os.path.join(os.path.dirname(__file__), "templates")
print(templates_dir)
app.mount(
    "/templates",
    StaticFiles(
        directory=templates_dir,
    ),
    name="templates",
)

import base64
import requests

"""
route: "/"
description: "Home Page"
"""


@app.get("/", include_in_schema=False)
async def root():
    return FileResponse(templates_dir + "/index.html")


"""
route: "/help"
description: "Help Page with links to docs and github repo"
"""


@app.get("/help")
async def root():
    return "Refer to /docs for more geeky info on usage or refer to the README.md on the GitHub Page for simpler information"


"""
@param session: common session to save time and resources
@param url: url to make request
@param method: GET or POST
@param headers: headers to be sent with the request
@param data: data to be sent with the request
@description: makes a request to the given url with the given method, headers and data. common method for all to save time and resources
"""


async def make_request(session, url=None, method="GET", headers=None, data=None):
    #  print("making request", method, url, headers, data)
    #  try:
    if method == "GET":
        async with session.get(url=url, headers=headers, data=data) as response:
            # print("response received as ", response)
            if response.status == 200:
                return await response.json()
            else:
                print(f"Error: {response.status}")
                return f"Error: {response.status}"
    elif method == "POST":
        async with session.post(url, headers=headers, data=data) as response:
            if response.status == 200:
                return await response.json()
            else:
                print(f"Error: {response.status}")
                return f"Error: {response.status}"


"""
Uses one of my old APIs to convery ISO Duration to milliseconds
@param session: common session to save time and resources
@param videoID: videoID of the YouTube video
@param youtubeAPIKEY: YouTube API Key
@description: fetches video duration in ISO Duration and converts to milliseconds
"""


async def getTrackDurationYT(session, videoID, youtubeAPIKEY) -> int:
    contentResponse = await make_request(
        session=session,
        url=f"https://youtube.googleapis.com/youtube/v3/videos?part=contentDetails&key={youtubeAPIKEY}&id={videoID}",
    )

    #  print(contentResponse)

    while "Error" in str(contentResponse):
        print("Check your YouTube API key. Using alternate key")
        fixable = False

        if youtubeAPIKEY == str(os.getenv("YOUTUBE_API_KEY5")):
            print("API Limit Exceeded for every YouTube API Key")
            return -99

        if youtubeAPIKEY == str(os.getenv("YOUTUBE_API_KEY")):
            youtubeAPIKEY = str(os.getenv("YOUTUBE_API_KEY2"))
            fixable = True

        elif youtubeAPIKEY == str(os.getenv("YOUTUBE_API_KEY2")):
            youtubeAPIKEY = str(os.getenv("YOUTUBE_API_KEY3"))
            fixable = True

        elif youtubeAPIKEY == str(os.getenv("YOUTUBE_API_KEY3")):
            youtubeAPIKEY = str(os.getenv("YOUTUBE_API_KEY4"))
            fixable = True

        elif youtubeAPIKEY == str(os.getenv("YOUTUBE_API_KEY4")):
            youtubeAPIKEY = str(os.getenv("YOUTUBE_API_KEY5"))
            fixable = True

        else:
            return -99

        if fixable:
            contentResponse = await make_request(
                session=session,
                url=f"https://youtube.googleapis.com/youtube/v3/videos?part=contentDetails&key={youtubeAPIKEY}&id={videoID}",
            )

        else:
            return -99

    ISODuration = contentResponse["items"][0]["contentDetails"]["duration"]
    if "H" in ISODuration and "M" in ISODuration and "S" in ISODuration:
        videoDuration = (
            int(ISODuration[ISODuration.find("T") + 1 : ISODuration.find("H")])
            * 3600000
            + int(ISODuration[ISODuration.find("H") + 1 : ISODuration.find("M")])
            * 60000
            + int(ISODuration[ISODuration.find("M") + 1 : ISODuration.find("S")]) * 1000
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
            + int(ISODuration[ISODuration.find("H") + 1 : ISODuration.find("S")]) * 1000
        )
    elif "M" in ISODuration and "S" in ISODuration:
        videoDuration = (
            int(ISODuration[ISODuration.find("T") + 1 : ISODuration.find("M")]) * 60000
            + int(ISODuration[ISODuration.find("M") + 1 : ISODuration.find("S")]) * 1000
        )
    elif "H" in ISODuration:
        videoDuration = (
            int(ISODuration[ISODuration.find("T") + 1 : ISODuration.find("H")])
            * 3600000
        )
    elif "M" in ISODuration:
        videoDuration = (
            int(ISODuration[ISODuration.find("T") + 1 : ISODuration.find("M")]) * 60000
        )
    elif "S" in ISODuration:
        videoDuration = (
            int(ISODuration[ISODuration.find("T") + 1 : ISODuration.find("S")]) * 1000
        )
    else:
        videoDuration = 0

    return videoDuration


"""
The Big Brains of thie Project!!!
@param session: common session to save time and resources
@param songName: name of the song
@param artistName: name of the artist
@param albumName: name of the album
@param songDuration: duration of the song in milliseconds
@param youtubeAPIKEY: YouTube API Key
@description: searches for the song on YouTube and returns the most accurate result by utilizing a custom designed algorithm to maximise accuracy and minimise searching credits
"""


async def searchTrackYT(
    session, songName, artistName, albumName, songDuration, youtubeAPIKEY, spotify_id
):
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
    #  searchQuery = searchQuery.replace(" ", "%20")
    #  print("searching for " + searchQuery)

    response = await make_request(
        session,
        f"https://youtube.googleapis.com/youtube/v3/search?part=snippet&q={searchQuery}&type=video&key={youtubeAPIKEY}",
    )
    #  print("response received as ", response)
    while "Error" in str(response):
        print("Check your YouTube API key. Using alternate key")
        fixable = False

        if youtubeAPIKEY == str(os.getenv("YOUTUBE_API_KEY5")):
            print("API Limit Exceeded for all YouTube API Keys")
            return "API Limit Exceeded for all YouTube API Keys"

        if youtubeAPIKEY == str(os.getenv("YOUTUBE_API_KEY")):
            youtubeAPIKEY = str(os.getenv("YOUTUBE_API_KEY2"))
            fixable = True

        elif youtubeAPIKEY == str(os.getenv("YOUTUBE_API_KEY2")):
            youtubeAPIKEY = str(os.getenv("YOUTUBE_API_KEY3"))
            fixable = True

        elif youtubeAPIKEY == str(os.getenv("YOUTUBE_API_KEY3")):
            youtubeAPIKEY = str(os.getenv("YOUTUBE_API_KEY4"))
            fixable = True

        elif youtubeAPIKEY == str(os.getenv("YOUTUBE_API_KEY4")):
            youtubeAPIKEY = str(os.getenv("YOUTUBE_API_KEY5"))
            fixable = True

        else:
            return "API Limit Exceeded for all YouTube API Keys"

        if fixable:
            response = await make_request(
                session,
                f"https://youtube.googleapis.com/youtube/v3/search?part=snippet&q={searchQuery}&type=video&key={youtubeAPIKEY}",
            )

        else:
            return "API Limit Exceeded for all YouTube API Keys"

    try:
        data = response

    except:
        # remove every non-alphanumeric character from the value fields in response
        response = str(response)
        response = response.replace('"', "")
        response = response.replace("'", '"')
        response = response.replace("None", "null")
        response = response.replace("#", "")
        
        data = json.loads(response)

    if data:
        accuracyScore = 0
        mostAccurate = ""
        macName = ""

        for item in data["items"]:
            """It starts by checking if the title of video has 'Official Audio' in it, to eliminate music videos.
            Then, it checks whether the channel is a music channel by seeing ig channel title has 'Topic'.
            Example: Natalie Holt - Topic only publishes songs by Natalie Holt, and not any variations unless decided by the artist.
            Finally, it verifies the song duration by equating it to the original song duration to eliminate possibilities of a different version (margin of error = 2s)
            Returns the one which has the highest accuracy score."""

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

            if videoDuration == -99:
                return "API Limit Exceeded for all YouTube API Keys"

            if abs(int(videoDuration) - int(songDuration)) <= 2000:
                currAccuracyScore += 5

            # print(item["snippet"]["title"], currAccuracyScore)
            if currAccuracyScore > accuracyScore:
                accuracyScore = currAccuracyScore
                mostAccurate = videoID
                macName = item["snippet"]["title"]

        if mostAccurate == "":
            # print(data)
            if data["pageInfo"]["totalResults"] == 0:
                print("No accurate result found")
                return "dQw4w9WgXcQ"

            mostAccurate = data["items"][0]["id"]["videoId"]
            macName = data["items"][0]["snippet"]["title"]

        #   print(f"From Spotify: {songName} to YouTube: {macName}")
        return mostAccurate


"""
@param session: common session to save time and resources
@param query: songID on spotify to search for
@description: fetches song info from spotify
"""


async def getSongInfo(session, query):
    print("received song request for " + query)
    token = ""

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic "
        + base64.b64encode(
            (
                str(os.getenv("SPOTIPY_CLIENT_ID"))
                + ":"
                + str(os.getenv("SPOTIPY_CLIENT_SECRET"))
            ).encode()
        ).decode()
    }
    data = {"grant_type": "client_credentials"}

    response = await make_request(session, url, "POST", headers=headers, data=data)
    if response:
        token = response["access_token"]

    song = await make_request(
        session=session,
        url=f"https://api.spotify.com/v1/tracks/{query}",
        headers={"Authorization": f"Bearer {token}"},
    )
    if song:
        songName = song["name"]
        artistName = song["artists"][0]["name"]
        albumName = song["album"]["name"]
        songDuration = song["duration_ms"]
        return songName, artistName, albumName, songDuration
    else:
        return None, None, None, None


"""
@param session: common session to save time and resources
@param song: song object from spotify
@param youtubeAPIKEY: YouTube API Key
@param urlMap: map to store the songID and the YouTube URL
@param response: response object from spotify
@description: processes the song individually so that i can asynchronously process all the songs in the playlist
"""


async def process_indi_song(session, song, youtubeAPIKEY, urlMap, response, spotify_id):
    curr = searchTrackYT(
        session=session,
        songName=str(song["track"]["name"]),
        artistName=str(song["track"]["artists"][0]["name"]),
        albumName=str(song["track"]["album"]["name"]),
        songDuration=int(song["track"]["duration_ms"]),
        youtubeAPIKEY=str(youtubeAPIKEY),
        spotify_id=spotify_id,
    )
    curr_final = await curr
    curr_final = str(curr_final)

    # print(curr_final)
    # print(f"converted {song['track']['name']} and {song['track']['id']} to {curr_final}")
    # response["items"]
    urlMap[str(song["track"]["id"])] = "https://www.youtube.com/watch?v=" + str(
        curr_final
    )


"""
route: "/song"
description: "Converts a Spotify Song to a YouTube Song"
"""


@app.get("/song")
async def song(query: str = "nope", youtubeAPIKEY: str = "default"):
    try:
        if query == "nope":
            return {"status": "error", "message": "Please enter a valid Spotify song ID"}

        if youtubeAPIKEY == "default":
            youtubeAPIKEY = os.getenv("YOUTUBE_API_KEY")
            if not youtubeAPIKEY:
                return {"status": "error", "message": "No YouTube API key found in environment variables"}

        async with aiohttp.ClientSession() as session:
            try:
                songName, artistName, albumName, songDuration = await getSongInfo(
                    session=session, query=query
                )
                if not all([songName, artistName, albumName, songDuration]):
                    return {"status": "error", "message": "Could not fetch song information from Spotify. Please check if the song ID is valid."}

                songID = searchTrackYT(
                    session=session,
                    songName=songName,
                    artistName=artistName,
                    albumName=albumName,
                    songDuration=songDuration,
                    youtubeAPIKEY=youtubeAPIKEY,
                    spotify_id=query,
                )
                final_song = await songID

                if final_song == "API Limit Exceeded for all YouTube API Keys":
                    return {"status": "error", "message": "API Limit Exceeded for all YouTube API Keys. Please try again later or enter your own YouTube API Key."}

                if final_song == "dQw4w9WgXcQ":
                    return {"status": "error", "message": "No matching song found on YouTube"}

                try:
                    client = get_mongo_client()
                    if client:
                        try:
                            db = client[os.getenv("MONGO_DB")]
                            collection = db[os.getenv("MONGO_COLLECTION")]

                            collection.update_many(
                                {},
                                {
                                    "$inc": {
                                        "ISOtotalCalls": 5,
                                        "MESOtotalCalls": 1,
                                        "MESOsongsConverted": 1,
                                    }
                                },
                                upsert=True  # Create document if it doesn't exist
                            )
                        except Exception as mongo_error:
                            print(f"MongoDB Operation Error: {mongo_error}")
                        finally:
                            client.close()
                    else:
                        print("Skipping analytics due to MongoDB connection failure")
                except Exception as e:
                    print(f"MongoDB Setup Error: {e}")

                return {"status": "success", "url": "https://www.youtube.com/watch?v=" + str(final_song)}

            except aiohttp.ClientError as e:
                return {"status": "error", "message": f"Network error while fetching data: {str(e)}"}
            
    except Exception as e:
        print(f"Unexpected error in /song endpoint: {str(e)}")
        return {"status": "error", "message": "An unexpected error occurred. Please try again later."}


"""
route: "/playlist"
description: "Converts a Spotify Playlist to a YouTube Playlist"
"""


@app.get("/playlist")
async def playlist(
    query: str = "nope", youtubeAPIKEY: str = "default", give_length: str = "no"
):
    try:
        if query == "nope":
            return {"status": "error", "message": "Please enter a valid Spotify playlist ID"}

        if youtubeAPIKEY == "default":
            youtubeAPIKEY = os.getenv("YOUTUBE_API_KEY")
            if not youtubeAPIKEY:
                return {"status": "error", "message": "No YouTube API key found in environment variables"}

        async with aiohttp.ClientSession() as session:
            try:
                start = time.time()
                
                try:
                    url = "https://accounts.spotify.com/api/token"
                    headers = {
                        "Authorization": "Basic "
                        + base64.b64encode(
                            (
                                str(os.getenv("SPOTIPY_CLIENT_ID"))
                                + ":"
                                + str(os.getenv("SPOTIPY_CLIENT_SECRET"))
                            ).encode()
                        ).decode()
                    }
                    data = {"grant_type": "client_credentials"}

                    response = requests.post(url, headers=headers, data=data)
                    if response.status_code != 200:
                        return {"status": "error", "message": "Failed to authenticate with Spotify"}
                    
                    response = response.json()
                except requests.RequestException as e:
                    return {"status": "error", "message": f"Failed to connect to Spotify: {str(e)}"}

                try:
                    playlist_id = query
                    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
                    headers = {
                        "Authorization": "Bearer " + response["access_token"],
                        "Content-Type": "application/json",
                    }
                    playlist_response = requests.get(url, headers=headers)
                    
                    if playlist_response.status_code == 404:
                        return {"status": "error", "message": "Playlist not found. Please check if the playlist exists and is public."}
                    elif playlist_response.status_code != 200:
                        return {"status": "error", "message": "Failed to fetch playlist from Spotify"}
                        
                    response = playlist_response.json()
                except requests.RequestException as e:
                    return {"status": "error", "message": f"Failed to fetch playlist: {str(e)}"}

                if "error" in response:
                    return {"status": "error", "message": response.get("error", {}).get("message", "Unknown Spotify API error")}

                if not response.get("items"):
                    return {"status": "error", "message": "This playlist is empty"}

                urlMap = defaultdict()
                valid_songs = set()
                
                for key in response["items"]:
                    try:
                        if key.get("track", {}) and key["track"].get("name") and key["track"].get("id"):
                            urlMap[key["track"]["id"]] = None
                            valid_songs.add(key["track"]["id"])
                    except Exception as e:
                        print(f"Error processing song in playlist: {str(e)}")
                        continue

                if not valid_songs:
                    return {"status": "error", "message": "No valid songs found in playlist"}

                tasks = []
                for key in response["items"]:
                    try:
                        if (key.get("track", {}).get("name") 
                            and key["track"]["id"] in valid_songs):
                            task = asyncio.ensure_future(
                                process_indi_song(
                                    session=session,
                                    song=key,
                                    youtubeAPIKEY=youtubeAPIKEY,
                                    urlMap=urlMap,
                                    response=response,
                                    spotify_id=key["track"]["id"],
                                )
                            )
                            tasks.append(task)
                    except Exception as e:
                        print(f"Error creating task for song: {str(e)}")
                        continue

                try:
                    await asyncio.gather(*tasks)
                except Exception as e:
                    return {"status": "error", "message": f"Error processing songs: {str(e)}"}

                try:
                    client = get_mongo_client()
                    if client:
                        try:
                            db = client[os.getenv("MONGO_DB")]
                            collection = db[os.getenv("MONGO_COLLECTION")]

                            collection.update_many(
                                {},
                                {
                                    "$inc": {
                                        "ISOtotalCalls": 5 * len(response["items"]),
                                        "MESOtotalCalls": 1,
                                        "MESOsongsConverted": len(response["items"]),
                                        "MESOplaylistsConverted": 1,
                                    }
                                },
                                upsert=True  # Create document if it doesn't exist
                            )
                        except Exception as mongo_error:
                            print(f"MongoDB Operation Error: {mongo_error}")
                        finally:
                            client.close()
                    else:
                        print("Skipping analytics due to MongoDB connection failure")
                except Exception as e:
                    print(f"MongoDB Setup Error: {e}")

                end = time.time()
                print(f"Time taken: {end-start}")
                print(f"Time taken per song: {(end-start)/len(response['items'])} seconds")

                for i in urlMap:
                    if "API Limit Exceeded for all YouTube API" in str(urlMap[i]):
                        error_response = {
                            "status": "error",
                            "message": "API Limit Exceeded for all YouTube API Keys. Please try again later or enter your own YouTube API Key."
                        }
                        if give_length == "yes":
                            error_response["length"] = len(response["items"])
                        return error_response

                result = {
                    "status": "success",
                    "list": list(urlMap.values()),
                }
                if give_length == "yes":
                    result["length"] = len(response["items"])
                return result

            except aiohttp.ClientError as e:
                return {"status": "error", "message": f"Network error while processing playlist: {str(e)}"}
            
    except Exception as e:
        print(f"Unexpected error in /playlist endpoint: {str(e)}")
        return {"status": "error", "message": "An unexpected error occurred. Please try again later."}


@app.get("/analytics", include_in_schema=False)
async def analytics():
    try:
        client = get_mongo_client()
        if not client:
            return {"status": "error", "message": "Failed to connect to MongoDB"}

        try:
            db = client[os.getenv("MONGO_DB")]
            collection = db[os.getenv("MONGO_COLLECTION")]

            all_data = collection.find({})
            result = []
            for data in all_data:
                data.pop("_id")
                result.append(data)

            return {"status": "success", "data": result} if result else {"status": "success", "message": "No data found"}
        except Exception as e:
            return {"status": "error", "message": f"Failed to fetch analytics: {str(e)}"}
        finally:
            client.close()
    except Exception as e:
        return {"status": "error", "message": f"MongoDB setup error: {str(e)}"}

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse(templates_dir + "/favicon.ico")