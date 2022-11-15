import requests
from bs4 import BeautifulSoup
import re
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os

# Billboard Scraped

date = input("Which date do you want to travel to? Type the date in this format: YYYY-MM-DD \n")
URL = f"https://www.billboard.com/charts/hot-100/{date}/"
response = requests.get(URL)
website_html = response.text
soup = BeautifulSoup(website_html, "html.parser")
scrapped_songs = [item.getText() for item in soup.find_all(name="h3", class_="a-no-trucate")]
song_names = [(re.sub(r'[\t\n ]+', ' ', song)) for song in scrapped_songs]

# Spotify:

SPOTIPY_CLIENT_ID = os.environ.get("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.environ.get("SPOTIPY_CLIENT_SECRET")
SPOTIPY_REDIRECT_URI = os.environ.get("SPOTIPY_REDIRECT_URI")
scope = "playlist-modify-private"
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        scope=scope,
        redirect_uri=SPOTIPY_REDIRECT_URI,
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET,
        cache_path='token.txt',
        show_dialog=True,
    )
)
user_id = sp.current_user()["id"]
song_uris = []
year = date.split("-")[0]
for song in song_names:
    result = sp.search(q=f"track:{song} year:{year}", type="track")
    try:
        uri = result["tracks"]["items"][0]["uri"]
        song_uris.append(uri)
    except IndexError:
        print(f"{song} doesn't exist in Spotify. Skipped.")

playlist = sp.user_playlist_create(user=user_id, name=f"{date} Billboard 100", public=False)
sp.playlist_add_items(playlist_id=playlist["id"], items=song_uris)