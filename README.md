# MelodySyncer - The Fastest Spotify to Youtube API Ever.

MelodySyncer is a **Web API** to convert Spotify songs or playlists to their Youtube equivalent. It is also the **most accurate** since it uses a unique scoring system that minimizes searching credits and maximises accuracy by factoring in song metadata. Takes less than **100 milliseconds** per song! Built using Async Python + FastAPI, hosted on Vercel.

#### You get: _Skip manual searching, Directly get a List, Peace of Mind_ <br> I get _(hopefully): Star, Heart, Follow :)_

## Usage

Visit [dub.sh/melodysyncer](https://dub.sh/melodysyncer) to access this API. Check out detailed API documentation [here](https://melodysyncer.aryankeluskar.com/docs) generated with OpenAPI <br>

**Example**: `https://melodysyncer.aryankeluskar.com/playlist?query=7fITt66rmO4QIeNs2LPRDj` responds with [a list of YouTube Links](## "can't reveal links in README for copyright purposes") which can be processed with `HttpRequest` in Java, or `requests.get` in Python. This data can be stored in an Array or List for further processing.

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
