import asyncio
from collections import defaultdict
import time
import aiohttp
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import os
from src.dtos.ISayHelloDto import ISayHelloDto
from dotenv import load_dotenv
load_dotenv()
from pymongo import MongoClient
import json
import re

app = FastAPI()

import base64
import requests


"""
route just for testing purposes
"""
# @app.get("/token")
# async def token():
#    print("env file check: "+str(os.getenv("YOUTUBE_API_KEY")))
#    print("env file check: "+str(os.getenv("SPOTIPY_CLIENT_ID")))
#    print("env file check: "+str(os.getenv("SPOTIPY_CLIENT_SECRET")))
   
#    client_id = str(os.getenv("SPOTIPY_CLIENT_ID"))
#    client_secret = str(os.getenv("SPOTIPY_CLIENT_SECRET"))

#    url = "https://accounts.spotify.com/api/token"
#    headers = {
#       "Authorization": "Basic "
#       + base64.b64encode(
#          (
#                str(os.getenv("SPOTIPY_CLIENT_ID"))
#                + ":"
#                + str(os.getenv("SPOTIPY_CLIENT_SECRET"))
#          ).encode()
#       ).decode()
#    }
#    data = {"grant_type": "client_credentials"}

#    response = requests.post(url, headers=headers, data=data).json()

#    # curl --request GET \
#    #   --url https://api.spotify.com/v1/playlists/3cEYpjA9oz9GiPac4AsH4n/tracks \
#    #   --header 'Authorization: Bearer 1POdFZRZbvb...qqillRxMr2z'

#    playlist_id = "3cEYpjA9oz9GiPac4AsH4n"
#    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
#    headers = {
#          "Authorization": "Bearer " + response["access_token"],
#          "Content-Type": "application/json",
#       }
#    response = requests.get(url, headers=headers).json()

#    tracklist = []
#    # print(response)
#    for i in response["items"]:
#       # print(i["track"]["name"])
#       tracklist.append(i["track"]["name"])

#    return {"message": tracklist}

"""
route: "/"
description: "Home Page"
"""
@app.get("/")
async def root():
   homeHTML = """
<!-- FILEPATH: /media/aryank/Tech AFOGA/nextjs-fastapi-starter/app/page.html -->
<!DOCTYPE html>
<html lang="en">

<head>
   <meta charset="UTF-8">
   <meta name="viewport" content="width=device-width, initial-scale=1.0">
   <title>MelodySyncer</title>
   <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
   <link rel="stylesheet" href="globals.css">
</head>

<style>
   /* @tailwind base;
   @tailwind components;
   @tailwind utilities; */

   :root {
      --foreground-rgb: 0, 0, 0;
      --background-rgb: 235, 235, 235;
   }

   body {
      background: linear-gradient(180deg, rgba(var(--background-start-rgb), 1) 0%, rgba(var(--background-end-rgb), 1) 80%);
      background-size: 100% 200%;
      /* animation: gradientAnimation 10s ease infinite; */
   }
</style>

<body>

   <main class="flex min-h-screen flex-col items-center justify-between p-24">
      <div class="z-10 w-full max-w-5xl items-center justify-between font-mono text-sm lg:flex">
         <p
            class="fixed left-0 top-0 flex w-full justify-center border-b border-gray-300 bg-gradient-to-b from-zinc-200 pb-6 pt-8 backdrop-blur-2xl dark:border-neutral-800 dark:bg-zinc-800/30 dark:from-inherit lg:static lg:w-auto  lg:rounded-xl lg:border lg:bg-gray-200 lg:p-4 lg:dark:bg-zinc-800/30">
            Developed byㅤ
            <a href="https://github.com/aryankeluskar">
               <code class="font-mono font-bold">Aryan Keluskar</code>
            </a>
         </p>
         <div
            class="fixed bottom-0 left-0 flex h-48 w-full items-end justify-center bg-gradient-to-t from-white via-white dark:from-black dark:via-black lg:static lg:h-auto lg:w-auto lg:bg-none">
            <a class="pointer-events-none flex place-items-center gap-2 p-8 lg:pointer-events-auto lg:p-0"
               target="_blank" rel="noopener noreferrer">
               Hosted on
               <svg class="h-200 w-[100px]" xmlns="http://www.w3.org/2000/svg" width="100" height="24"
                  viewBox="0 0 100 25" fill="none">
                  <path
                     d="M34.5741 3.38068C37.7677 3.38068 39.8439 5.33244 39.8439 8.4672C39.8439 10.7623 38.623 12.4677 36.7089 13.1955L40.4613 20.1292H37.678L34.1774 13.55H30.3113V20.1292H27.9143V3.38068H34.5741ZM30.3078 5.71309V11.2437H34.4602C36.364 11.2437 37.3469 10.0943 37.3469 8.4672C37.3469 6.80279 36.3675 5.71309 34.4602 5.71309H30.3078Z"
                     fill="currentColor"></path>
                  <path
                     d="M46.5589 8.0343C49.7525 8.0343 51.8287 10.6018 51.8287 13.7739C51.8287 14.1433 51.8046 14.5277 51.739 14.9084H43.2411C43.3445 16.6847 44.7482 18.0804 46.6416 18.0804C48.0108 18.0804 49.1041 17.4498 49.9249 16.0578L51.5907 17.3677C50.5768 19.3418 48.5799 20.3793 46.6416 20.3793C43.3342 20.3793 40.9027 17.7371 40.9027 14.2217C40.9027 10.6876 43.241 8.0343 46.5589 8.0343ZM49.5352 13.0798C49.3973 11.4154 48.1108 10.2398 46.5347 10.2398C44.8586 10.2398 43.579 11.4116 43.2962 13.0798H49.5352Z"
                     fill="currentColor"></path>
                  <path
                     d="M53.9256 20.1292V8.2806H56.195V9.77335C56.5605 9.16879 57.5987 8.0343 59.5611 8.0343C62.5719 8.0343 64.1584 10.057 64.1584 12.9342V20.1292H61.8994V13.453C61.8994 11.49 60.9061 10.3555 59.2058 10.3555C57.54 10.3555 56.1846 11.49 56.1846 13.453V20.1292H53.9256Z"
                     fill="currentColor"></path>
                  <path
                     d="M71.5183 8.0343C73.3772 8.0343 74.6084 8.77321 75.4189 9.8965V2.75H77.6779V20.1292H75.4189V18.5133C74.6084 19.6366 73.3772 20.3755 71.5183 20.3755C68.4039 20.3755 66.0208 17.7819 66.0208 14.1433C66.0208 10.5011 68.4039 8.0343 71.5183 8.0343ZM68.2763 14.1433C68.2763 16.3265 69.68 18.1775 71.7907 18.1775C73.9014 18.1775 75.4051 16.3265 75.4051 14.1433C75.4051 11.9602 73.8876 10.2324 71.7907 10.2324C69.68 10.2286 68.2763 11.9565 68.2763 14.1433Z"
                     fill="currentColor"></path>
                  <path
                     d="M85.2482 8.0343C88.4418 8.0343 90.518 10.6018 90.518 13.7739C90.518 14.1433 90.4939 14.5277 90.4284 14.9084H81.9304C82.0338 16.6847 83.4375 18.0804 85.331 18.0804C86.7001 18.0804 87.7934 17.4498 88.6143 16.0578L90.2801 17.3677C89.2661 19.3418 87.2692 20.3793 85.331 20.3793C82.0235 20.3793 79.5921 17.7371 79.5921 14.2217C79.5886 10.6876 81.9269 8.0343 85.2482 8.0343ZM88.2246 13.0798C88.0866 11.4154 86.8002 10.2398 85.224 10.2398C83.5479 10.2398 82.2684 11.4116 81.9856 13.0798H88.2246Z"
                     fill="currentColor"></path>
                  <path
                     d="M92.7012 20.1292V8.2806H94.9705V9.8965C95.5879 8.60154 96.626 8.0343 97.8227 8.0343C98.678 8.0343 99.3299 8.32912 99.3299 8.32912L99.0919 10.5757C98.9677 10.5272 98.4746 10.3033 97.7572 10.3033C96.5466 10.3033 94.974 10.9937 94.974 13.6731V20.1292H92.7012Z"
                     fill="currentColor"></path>
                  <path
                     d="M14.1714 0.00568544C11.7434 -0.117466 9.70165 1.77458 9.35331 4.26746C9.33952 4.38315 9.31882 4.4951 9.30158 4.60706C8.76011 7.71196 6.23899 10.063 3.21089 10.063C2.1314 10.063 1.11743 9.76448 0.234523 9.24202C0.127608 9.17858 0 9.26068 0 9.39129V10.0593V20.1241H9.29813V12.5783C9.29813 11.19 10.3397 10.063 11.6227 10.063H13.9472C16.5787 10.063 18.6963 7.70077 18.5928 4.82724C18.4997 2.24107 16.5614 0.128837 14.1714 0.00568544Z"
                     fill="currentColor"></path>
               </svg>
            </a>
         </div>
      </div>

      <div class="flex flex-col items-center justify-center w-full text-center">
         <span class="text-5xl font-bold text-black">
            MelodySyncer
         </span>
      </div>

      <div class="flex flex-col items-center justify-center w-full text-center">
         <span class="text-2xl font-bold text-black">
            MelodySyncer, or MeSo for short, is a Simple-to-use Web API to convert Spotify songs or playlists to their
            Youtube equivalent.
         </span>
         <a href="./trial">
            <button
               class="mt-4 px-6 py-3 text-lg font-semibold text-black bg-whitesmoke border-2 border-black rounded-lg hover:bg-black hover:text-white transition-colors duration-300">
               Try It!
            </button>
         </a>
      </div>



      <div class="mb-32 grid text-center lg:mb-0 lg:grid-cols-3 lg:text-left">
         <a href="https://github.com/aryankeluskar/MelodySyncer"
            class="group rounded-lg border border-transparent px-5 py-4 transition-colors hover:border-gray-300 hover:bg-gray-100 hover:dark:border-neutral-700 hover:dark:bg-neutral-800/30"
            target="_blank" rel="noopener noreferrer">
            <h2 class="mb-3 text-2xl font-semibold">
               Docs
               <span class="inline-block transition-transform group-hover:translate-x-1 motion-reduce:transform-none">
                  -&gt;
               </span>
            </h2>
            <p class="m-0 max-w-[30ch] text-sm opacity-50">
               Find in-depth information about the features and API of MelodySyncer.
            </p>
         </a>

         <a href="https://github.com/aryankeluskar/MelodySyncer"
            class="group rounded-lg border border-transparent px-5 py-4 transition-colors hover:border-gray-300 hover:bg-gray-100 hover:dark:border-neutral-700 hover:dark:bg-neutral-800 hover:dark:bg-opacity-30"
            target="_blank" rel="noopener noreferrer">
            <h2 class="mb-3 text-2xl font-semibold">
               Usage
               <span class="inline-block transition-transform group-hover:translate-x-1 motion-reduce:transform-none">
                  -&gt;
               </span>
            </h2>
            <p class="m-0 max-w-[30ch] text-sm opacity-50">
               You get: Skip manual searching, Directly get a List, Peace of Mind
               <br>
               I get (hopefully): Star, Heart, Follow :)
            </p>
         </a>

         <a href="https://github.com/aryankeluskar/MelodySyncer"
            class="group rounded-lg border border-transparent px-5 py-4 transition-colors hover:border-gray-300 hover:bg-gray-100 hover:dark:border-neutral-700 hover:dark:bg-neutral-800/30"
            target="_blank" rel="noopener noreferrer">
            <h2 class="mb-3 text-2xl font-semibold">
               GitHub
               <span class="inline-block transition-transform group-hover:translate-x-1 motion-reduce:transform-none">
                  -&gt;
               </span>
            </h2>
            <p class="m-0 max-w-[30ch] text-sm opacity-50">
               Explore the GitHub repository for MelodySyncer.
            </p>
         </a>
      </div>
   </main>
</body>

</html>   
"""
   
   return HTMLResponse(content=homeHTML, status_code=200)


"""
route: "/help"
description: "Help Page with links to docs and github repo"
"""
@app.get("/help")
async def root():
    return "Refer to /docs for more geeky info on usage or refer to the README.md on the GitHub Page for simpler information"

"""
route: "/trial"
description: "Trial Page with basic HTML and JS to convert a Spotify URL to a YouTube URL"
"""
@app.get("/trial")
async def root():
    trialHTML = """
<!DOCTYPE html>
<html lang="en">

<head>
   <meta charset="UTF-8">
   <meta name="viewport" content="width=device-width, initial-scale=1.0">
   <title>MelodySyncer Trial</title>
   <style>
      body {
         font-family: Arial, sans-serif;
         margin: 0;
         padding: 0;
         background-color: #f2f2f2;
      }

      header {
         background-color: #333;
         color: white;
         padding: 10px;
         text-align: center;
      }

      nav {
         display: flex;
         justify-content: center;
         background-color: #444;
         padding: 10px;
      }

      nav a {
         color: white;
         text-decoration: none;
         margin: 0 20px;
      }

      main {
         display: flex;
         justify-content: center;
         align-items: center;
         height: 80vh;
      }

      .content-container {
         display: flexbox;
         width: 60%;
         background-color: white;
         border-radius: 10px;
         overflow: hidden;
         box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
      }

      .left-section {
         flex: 1;
         padding: 20px;
      }

      .right-section {
         flex: 1;
         padding: 20px;
         background-color: #f2f2f2;
      }

      .textbox {
         width: 100%;
         padding: 10px;
         margin-bottom: 10px;
         box-sizing: border-box;
      }

      .label {
         font-weight: bold;
      }

      .button {
         background-color: #333;
         color: white;
         padding: 10px;
         border: none;
         cursor: pointer;
         border-radius: 5px;
      }

      .textarea {
         width: 100%;
         height: 100px;
         padding: 10px;
         box-sizing: border-box;
      }

      #outputURL {
         height: 50px;
         margin-bottom: 10px;
      }

      .progress-container {
         display: none;
         width: 100%;
         height: 20px;
         border-radius: 5px;
         overflow: hidden;
         margin-top: 10px;
      }

      .progress-bar {
         height: 100%;
         width: 0;
         background: linear-gradient(to right, lightgreen, darkgreen);
         animation: progressBarAnimation 2s linear;
         /* Default animation duration for tracks */
      }

      @keyframes progressBarAnimation {
         to {
            width: 100%;
         }
      }

      /* if width is below 700 then make content container has 90% width */
      @media (max-width: 700px) {
         .content-container {
            width: 90%;
         }
      }
   </style>
</head>

<body>

   <header>
      <h1>MelodySyncer</h1>
   </header>

   <nav>
      <a href="melodysyncer.vercel.app">Home</a>
      <a href="https://www.postman.com/aryankeluskar/workspace/all-apis-developed-by-aryan-keluskar/api/ef1cb49f-367a-4fad-8f81-6ea101c05057?action=share&creator=31514208" target="_blank">Try in Postman</a>
      <a href="https://github.com/aryankeluskar/MelodySyncer" target="_blank">GitHub Repo</a>
   </nav>

   <main>
      <div class="content-container">
         <div class="left-section">
            <input id="inputQuery" type="text" class="textbox" placeholder="Paste the URL From Spotify...">
            <input id="inputAPIKEY" type="text" class="textbox"
               placeholder="Provide YouTube API Key (Optional but recommended since the trial is limited)">
            <!-- <label class="label">Description:</label> -->
            <p>The URL should be of a track or a playlist (can be verified by checking if the url
               contains track or playlist) </p>
            <button onclick="convert(document.getElementById('inputQuery'))" class="button">Convert!</button>
            <!-- <div class="progress-container">
               <div class="progress-bar" id="progressBar"></div>
            </div> -->

         </div>
         <div class="right-section">
            <textarea class="textarea" id="outputURL" disabled="false"
               placeholder="The URL Request will be displayed here"></textarea>

               
            <textarea class="textarea" id="outputArea" disabled="false"
               placeholder="The output will be displayed here"></textarea>
         </div>

      </div>
   </main>

</body>

<script>
   function convert(inputQuery) {
      currURL = window.location.href;
      console.log(currURL);
      // var progressBar = document.getElementById("progressBar");
      // var progressContainer = document.querySelector(".progress-container");
      // progressContainer.style.display = "block";


      if (inputQuery.value.includes("open.spotify.com")) {
         if (inputQuery.value.includes("track")) {
            // progressBar.style.animation = "progressBarAnimation 2s linear";
            if (document.getElementById("inputAPIKEY").value == "") {
               let query = inputQuery.value.substring(inputQuery.value.indexOf("track/") + 6);
               if (query.includes("?si")) {
                  query = query.substring(0, query.indexOf("?si"));
               }
               backendQuery = "./song?query=" + query + "&youtubeAPIKEY=default";
            }
            else {
               let query = inputQuery.value.substring(inputQuery.value.indexOf("track/") + 6);
               if (query.includes("?si")) {
                  query = query.substring(0, query.indexOf("?si"));
               }
               backendQuery = "./song?query=" + query + "&youtubeAPIKEY=" + document.getElementById("inputAPIKEY").value;
            }
         }

         else if (inputQuery.value.includes("playlist")) {
            // if api input is empty, then the backend will use the default api key which is stored in .env

            if (document.getElementById("inputAPIKEY").value == "") {
               let query = inputQuery.value.substring(inputQuery.value.indexOf("playlist/") + 9);
               if (query.includes("?si")) {
                  query = query.substring(0, query.indexOf("?si"));
               }
               backendQuery = "./playlist?query=" + query + "&youtubeAPIKEY=default";
            }
            else {
               let query = inputQuery.value.substring(inputQuery.value.indexOf("playlist/") + 9);
               if (query.includes("?si")) {
                  query = query.substring(0, query.indexOf("?si"));
               }
               backendQuery = "./playlist?query=" + query + "&youtubeAPIKEY=" + document.getElementById("inputAPIKEY").value;
            }
         }

         var xhr = new XMLHttpRequest();
         console.log(backendQuery);
         document.getElementById("outputURL").value = "https://melodysyncer.vercel.app/"+backendQuery.substring(2);
         // console.log(backendQuery);
         xhr.open("GET", backendQuery, false);
         // xhr.onload = function () {
         //    // Hide the progress bar after receiving the response
         //    progressContainer.style.display = "none";
         // };
         xhr.send();

         document.getElementById("outputArea").value = xhr.responseText;
      } else {
         alert("Invalid URL")
      }

   }
</script>

</html>
"""
    return HTMLResponse(content=trialHTML, status_code=200)

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
                return None
    elif method == "POST":
        async with session.post(url, headers=headers, data=data) as response:
            if response.status == 200:
                return await response.json()
            else:
                print(f"Error: {response.status}")
                return None


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
    session,
    songName,
    artistName,
    albumName,
    songDuration,
    youtubeAPIKEY
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
    if "Error" in str(response):
        return "Check your YouTube API key"

    try: 
      data = response
        
    except:
      response = str(response)
      response = response.replace('"', '')
      response = response.replace("'", '"')
      response = response.replace("None", "null")
      response = response.replace("#", "")
      # remove every non-alphanumeric character from the value fields in response
      # response = re.sub(r'(?<=[{,])\s*([^"]+?)\s*:', lambda m: '"{}":'.format(re.sub(r'\W+', '', m.group(1))), response)
    
      # with open("response.txt", "w") as file:
      #       file.write(response)
      
      data = json.loads(response)


   #  with open("response.json", "w") as file:
   #       json.dump(data, file)


    if data:
      #   print(f"Response received as {response}")
        #  with open("response.json", "w") as file:
        #      json.dump(response, file)
        #  print((response["items"][0]["id"]["videoId"]))

        accuracyScore = 0
        mostAccurate = ""
        macName = ""
        # response_json = await response.json()
        #  mostAccurate = response["items"][0]["id"]["videoId"]
        #  print("searching for " + str(response))
        for item in data["items"]:
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

            if abs(int(videoDuration) - int(songDuration)) <= 2000:
                currAccuracyScore += 5

            # print(item["snippet"]["title"], currAccuracyScore) 
            if currAccuracyScore > accuracyScore:
                accuracyScore = currAccuracyScore
                mostAccurate = videoID
                macName = item["snippet"]["title"]

        if mostAccurate == "":
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

   response = await make_request(
         session, url, "POST", headers=headers, data=data
   )
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
async def process_indi_song(session, song, youtubeAPIKEY, urlMap, response):
   curr = searchTrackYT(session=session, songName=str(song["track"]["name"]), artistName=str(song["track"]["artists"][0]["name"]), albumName=str(song["track"]["album"]["name"]), songDuration=int(song["track"]["duration_ms"]), youtubeAPIKEY=str(youtubeAPIKEY))
   curr_final = await curr
   curr_final = str(curr_final)
   # print(curr_final)
   # print(f"converted {song['track']['name']} and {song['track']['id']} to {curr_final}")
   # response["items"]
   urlMap[str(song["track"]["id"])] = "https://www.youtube.com/watch?v="+str(curr_final)

"""
route: "/song"
description: "Converts a Spotify Song to a YouTube Song"
"""
@app.get("/song")
async def song(query: str="nope", youtubeAPIKEY: str="default"):
   if query == "nope":
      return "Please enter a query and try again"
   if youtubeAPIKEY == "default":
       youtubeAPIKEY = os.getenv("YOUTUBE_API_KEY")
   async with aiohttp.ClientSession() as session:
      # print("did this work")
      songName, artistName, albumName, songDuration = await getSongInfo(session=session, query=query)
      # print(songName, artistName, albumName, songDuration)
      songID = searchTrackYT(session=session, songName=songName, artistName=artistName, albumName=albumName, songDuration=songDuration, youtubeAPIKEY=youtubeAPIKEY)
      final_song = await songID
      client = MongoClient(os.getenv("MONGO_URI"))
    
      # Select the database and collection
      db = client[os.getenv("MONGO_DB")]
      collection = db[os.getenv("MONGO_COLLECTION")]

      collection.update_many({}, {'$inc': 
                                  {'ISOtotalCalls': 5, 
                                   'MESOtotalCalls': 1, 
                                   'MESOsongsConverted': 1}})

      client.close()
      # print(final_song)
      return "https://www.youtube.com/watch?v="+str(final_song)
   
"""
route: "/playlist"
description: "Converts a Spotify Playlist to a YouTube Playlist"
""" 
@app.get("/playlist")
async def playlist(query: str="nope", youtubeAPIKEY: str="default"):
    if query == "nope":
      return "Please enter a query and try again"
    if youtubeAPIKEY == "default":
         youtubeAPIKEY = os.getenv("YOUTUBE_API_KEY")
   #  print(os.getenv("YOUTUBE_API_KEY"))
    async with aiohttp.ClientSession() as session:
      start = time.time()
      # print("did this work")
      client_id = str(os.getenv("SPOTIPY_CLIENT_ID"))
      client_secret = str(os.getenv("SPOTIPY_CLIENT_SECRET"))

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

      response = requests.post(url, headers=headers, data=data).json()

      # curl --request GET \
      #   --url https://api.spotify.com/v1/playlists/3cEYpjA9oz9GiPac4AsH4n/tracks \
      #   --header 'Authorization: Bearer 1POdFZRZbvb...qqillRxMr2z'

      playlist_id = query
      url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
      headers = {
            "Authorization": "Bearer " + response["access_token"],
            "Content-Type": "application/json",
         }
      response = requests.get(url, headers=headers).json()

      urlMap = defaultdict()
      c=1
      for key in response['items']:
         # print(c, key['track']['name'], len(key['track']['name']))
         c+=1
         # if key['track']['id'] contains alphanumeric characters
         if len(key['track']['name']) > 0:
            urlMap[key['track']['id']] = None

      tasks = []
      for song in response["items"]:
         if len(key['track']['name']) > 0:
            task = asyncio.ensure_future(process_indi_song(session=session, song=song, youtubeAPIKEY=youtubeAPIKEY, urlMap=urlMap, response=response))
            tasks.append(task)

      await asyncio.gather(*tasks)   
      client = MongoClient(os.getenv("MONGO_URI"))
    
      # Select the database and collection
      db = client[os.getenv("MONGO_DB")]
      collection = db[os.getenv("MONGO_COLLECTION")]

      collection.update_many({}, {'$inc': 
                                  {'ISOtotalCalls': 5*len(response['items']), 
                                   'MESOtotalCalls': 1, 
                                   'MESOsongsConverted': len(response['items']), 
                                   'MESOplaylistsConverted': 1}})

      client.close()
      end = time.time()
      print(f"Time taken: {end-start}")
      print(f"Time taken per song: {(end-start)/len(response['items'])} seconds")      
      return list(urlMap.values())
    