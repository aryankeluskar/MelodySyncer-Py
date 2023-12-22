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


load_dotenv()


app = FastAPI()


async def make_request(session, url=None, method="GET", headers=None, data=None):
   #  print("making request", method, url, headers, data)
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


@app.get("/api/playlist")
async def hello_world(query: str = "", youtubeAPIKEY: str = ""):
    # start timer at start, end timer at end, print total time taken
    print("received playlist request for " + query)
    try:
        return await convertPlaylist(query, youtubeAPIKEY)
    except Exception as e:
        print("error occured: " + e)
        return "Check your playlist ID again"
    


@app.get("/api/song")
async def hello_world(query: str = "", youtubeAPIKEY: str = ""):
    # start timer at start, end timer at end, print total time taken

    t0 = time.time()
    try:
        print("received song request for " + query)
        #   currAnalytics_cor = getAnalytics()
        #   currAnalytics = await currAnalytics_cor
        #   setAnalytics(
        #       currAnalytics["document"]["totalCalls"] + 1,
        #       currAnalytics["document"]["songsConverted"],
        #       currAnalytics["document"]["playlistsConverted"],
        #   )
        sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
        song = sp.track(query)
        # if album type is a single, then name is in ["album"]["name"]
        if song["album"]["album_type"] == "single":
            vidID = searchTrackYT(
                song["name"],
                song["artists"][0]["name"],
                song["album"]["name"],
                song["duration_ms"],
                "NotRequired",
                youtubeAPIKEY,
            )

        else:
            vidID = searchTrackYT(
                song["name"],
                song["artists"][0]["name"],
                song["album"]["name"],
                song["duration_ms"],
                "NotRequired",
                youtubeAPIKEY,
            )

        t1 = time.time()
        print("Total time taken: " + str(t1 - t0))
        vidID_final = await vidID
        return "https://youtube.com/watch?v=" + str(vidID_final)

    except Exception as e:
        print("error occured: " + str(e))
        return "Check your song ID again"


#  except Exception as e:
#      return {"error": str(e)}


async def setAnalytics(
    newCalls: int = 0, newSongs: int = 0, newPlaylists: int = 0
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
            "$set": {
                "songsConverted": newSongs,
                "playlistsConverted": newPlaylists,
                "totalCalls": newCalls,
            }
        },
    }

    async with aiohttp.ClientSession() as session:
        async with aiohttp.ClientSession() as session:
            response = requests.post(
                session,
                os.getenv("MONGODB_UPDATEURL"),
                headers=headers,
                data=json.dumps(payload),
            )
    print("setting analytics\n")
    print(response.text)
    return response.text


async def getAnalytics() -> json:
    # Perform analytics calculations
    payload = json.dumps(
        {
            "collection": "SpotifyToYoutube",
            "database": "API_Analytics",
            "dataSource": "Cluster0",
            "projection": {
                "_id": 1,
                "songsConverted": 1,
                "playlistsConverted": 1,
                "totalCalls": 1,
            },
        }
    )
    headers = {
        "apiKey": os.getenv("MONGODP_APIKEY"),
        "Content-Type": "application/ejson",
        "Accept": "application/json",
    }

    async with aiohttp.ClientSession() as session:
        async with aiohttp.ClientSession() as session:
            response = await make_request(
                session,
                "POST",
                os.getenv("MONGODP_READURL"),
                headers=headers,
                data=payload,
            )

   #  print(response)


#  json_response = json.loads(response.text)
#  return json_response


async def convertPlaylist(playlistID, youtubeAPIKEY):
    t0 = time.time()
    print("received request for playlist ID " + playlistID)
    playlistResults = await getPlaylistTracksSP(playlistID)
    youtubeURLs = []
    tasks = []
    for song in playlistResults["items"]:
        task = asyncio.create_task(
            searchTrackYT(
                song["track"]["name"],
                song["track"]["artists"][0]["name"],
                song["track"]["album"]["name"],
                song["track"]["duration_ms"],
                youtubeURLs,
                youtubeAPIKEY,
            )
        )
        tasks.append(task)
    await asyncio.gather(*tasks)
    t1 = time.time()
    for i in range(len(youtubeURLs)):
        if youtubeURLs[i] != "":
            youtubeURLs[i] = "https://youtube.com/watch?v=" + str(youtubeURLs[i])
    print("Total time taken: " + str(t1 - t0))
    return youtubeURLs


async def searchTrackYT(
    songName, artistName, albumName, songDuration, youtubeURLs, youtubeAPIKEY
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

    async with aiohttp.ClientSession() as session:
        async with aiohttp.ClientSession() as session:
            response = await make_request(
                session,
                f"https://youtube.googleapis.com/youtube/v3/search?part=snippet&q={searchQuery}&type=video&key={youtubeAPIKEY}",
            )

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
                    videoID = item["id"]["videoId"]
                    currAccuracyScore = 0

                    if "Topic" in item["snippet"]["channelTitle"]:
                        currAccuracyScore += 2

                    if (
                        "Official Audio" in item["snippet"]["title"]
                        or "Full Audio Song" in item["snippet"]["title"]
                    ):
                        currAccuracyScore += 2

                    videoDuration_coroutine = getTrackDurationYT(session, videoID, youtubeAPIKEY)
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
                if "NotRequired" in youtubeURLs:
                    return str(mostAccurate)

                else:
                    youtubeURLs.append(mostAccurate)
                    return str(mostAccurate)


def run_sync(func, *args, **kwargs):
    loop = asyncio.get_running_loop()
    partial_func = partial(func, *args, **kwargs)
    return loop.run_in_executor(ThreadPoolExecutor(), partial_func)


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


async def getTrackDurationYT(session, videoID, youtubeAPIKEY) -> int:
    contentResponse = await make_request(
        session=session,
        url=f'https://youtube.googleapis.com/youtube/v3/videos?part=contentDetails&key={youtubeAPIKEY}&id={videoID}',
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


@app.get("/api/analytics")
async def getAnalytics():
    return "analytics"
