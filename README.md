# Most Accurate Spotify to Youtube API Ever! Presenting MelodySyncer (Beginning Public Operation in December '23)
Built using Python, FastAPI, hosted on Render.com <br> MelodySyncer, or MeSo for short, is a Simple-to-use **Web API** to convert Spotify songs or playlists to their Youtube equivalent. Most Accurate since I have developed an unique scoring system that minimizes searching credits and maximises accuracy by factoring in Artist Name, Song Length, Album Name, Channel Source, etc.
#### You get: _Skip manual searching, Directly get a List, Peace of Mind_ <br> I get _(hopefully): Star, Heart, Follow :)_

## Install (Only if local instance needed)
    Requirements: gh, pip, python 3.12+
    Run the following commands:
    gh repo clone aryankeluskar/MelodySyncer
    pip install -r requirements.txt


## Run the app (Only if local instance needed)
    uvicorn main:app --reload
Open your broswer at [http://localhost:8000](http://localhost:8000)

## Usage
Visit [MelodySyncer.onrender.com](https://MelodySyncer.onrender.com/) to access this API <br>
Visit [detailed API documentation here](https://MelodySyncer.onrender.com/docs) generated with OpenAPI.json <br>
Example: http://MelodySyncer.onrender.com/convertPlaylist/?playlistID=1YfR61247oUsV44CQg9Irf responds with [a List of YouTube Links](## "can't reveal links in README for copyright purposes") which can be processed with HttpRequest in Java, or requests.get in Python. This data can be stored in an Array or List for further processing.

### GET /
    Parameters: None 
    Response: (string) Displays the valid paths available, and frontend in the future
    
<hr>

### GET /convertSong
    Parameters: songID (string) Soptify ID of the Song
    Response: (string) Accurate Youtube ID of the song, neglecting any remix, cover, and music videos
    
<hr>

### GET /convertPlaylist
    Parameters: playlistID (string) Soptify ID of the Playlist
    Response: (list of str) List / Array of Strings, each element contains the Youtube URL for the song. The indices remain same from Spotify Playlist
    
## Support this project!
### This is my second ever API! Please consider leaving a 🌟 if this added value to your wonderful project
### Made with pure love and [freshman fascination](## "it's a real term i swear"). Visit my website at [aryankeluskar.github.io](https://aryankeluskar.github.io) <3