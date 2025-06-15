# MelodySyncer - Archive of the Old API

> [!note]
> When I was 17, I wrote this API to help out an indie music app. It took less than 100 milliseconds per song, which was already **30-50x** faster than every other conversion API, but I knew I could do better. Therefore, I took the ultimate decision of re-writing this API in Rust, which you can find at [dub.sh/melodysyncer](https://dub.sh/melodysyncer).

> I am truly humbled by all of the 31,000 requests this API has received over the past year. This project represented a big leap in my journey, and I hope to continue to make more projects like this in the future ❤️

#### You get: Skip manual searching, Directly get a List, Peace of Mind <br> I get (hopefully): Star, Heart, Follow :)

## Usage-Old

This version is built using Async Python + FastAPI. It was the fastest Spotify to Youtube API ever at the time which could convert Spotify songs or playlists to their Youtube equivalent. It is also the **most accurate** by factoring in song metadata. Visit [dub.sh/old-melodysyncer](https://dub.sh/old-melodysyncer) to access this API. Check out detailed API documentation [here](https://old-melodysyncer.aryankeluskar.com/docs) generated with OpenAPI <br>

**Example**: `https://old-melodysyncer.aryankeluskar.com/playlist?query=7fITt66rmO4QIeNs2LPRDj` responds with [a list of YouTube Links](## "can't reveal links in README for copyright purposes") which can be processed with `HttpRequest` in Java, or `requests.get` in Python. This data can be stored in an Array or List for further processing.

### GET /

    Parameters: None
    Response: (html) API Home Page for testing.

<hr>

### GET /song

    Parameters:
    - query (string): ID of the song in Spotify
    - X-YouTube-API-Key (header, optional): Google Cloud API Key with YouTube Data v3 enabled
    Response: (string) Accurate Youtube ID of the song, neglecting any remix, cover, and music videos

<hr>

### GET /playlist

    Parameters:
    - query (string): ID of the playlist in Spotify
    - X-YouTube-API-Key (header, optional): Google Cloud API Key with YouTube Data v3 enabled
    Response: (list of str) List / Array of Strings, each element contains the Youtube URL for the song. The indices remain same from Spotify Playlist

## API Key Usage

You can provide the YouTube API key in two ways:

1. As a header (Preferred): `X-YouTube-API-Key: YOUR_API_KEY`
2. As a query parameter: `?youtubeAPIKEY=YOUR_API_KEY`

If no API key is provided, the server will use its default API key which has a limited trial.

## Install & Run Locally

Requirements: gh, pip, python <= 3.8

```bash
    gh repo clone aryankeluskar/MelodySyncer
    pip install -r requirements.txt
```

Add the required details in .env, then

```bash
    uvicorn src.index:app
```

## Support this project!

This is my second ever API! Please consider leaving a 🌟 if this added value to your wonderful project. Made with pure love and [freshman fascination](## "it's a real term i swear"). Visit my website at [aryankeluskar.com](https://aryankeluskar.com) <3
