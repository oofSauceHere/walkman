from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Label, Static
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive
from PIL import Image
from functools import reduce
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests
import io
from dotenv import load_dotenv
import os
from threading import Thread, Lock
import time

load_dotenv()

SIZE = 20
CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI")
SP = spotipy.Spotify(auth_manager=SpotifyOAuth(
    scope="user-read-currently-playing",
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI
))

MUTEX = Lock()
IMG_COLORS = [[(0, 0, 0)]*SIZE for i in range(SIZE)]
SONG_DATA = {
    "playing": False,
    "name": "",
    "album": "",
    "artist": "",
    "progressPercentage": 0
}

class ImagePixel(Label):
    color = reactive((0, 0, 0))

    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
        super().__init__()

    def on_mount(self) -> None:
        self.set_interval(1, self.update_pixel)

    def update_pixel(self) -> None:
        with MUTEX:
            self.color = IMG_COLORS[self.x][self.y] if SONG_DATA["playing"] else (0, 0, 0)

    def watch_color(self, new_color) -> None:
        # with MUTEX:
            # self.styles.color = f"rgb({new_color[0]},{new_color[1]},{new_color[2]})" if SONG_DATA["playing"] else "auto"
        self.styles.background = "rgb(0,0,0)"
        self.styles.color = f"rgb({new_color[0]},{new_color[1]},{new_color[2]})"
        self.update("\u2593")

class Song(Label):
    song = reactive("No song playing")

    def on_mount(self) -> None:
        self.set_interval(1, self.update_song)

    def update_song(self) -> None:
        with MUTEX:
            self.song = SONG_DATA["name"] if SONG_DATA["playing"] else "No song playing"

    def watch_song(self, new_song) -> None:
        self.update(f"[bold]{new_song}[/]")

class Artist(Label):
    artist = reactive("...")

    def on_mount(self) -> None:
        self.set_interval(1, self.update_artist)

    def update_artist(self) -> None:
        with MUTEX:
            self.artist = SONG_DATA["artist"] if SONG_DATA["playing"] else "..."

    def watch_artist(self, new_artist) -> None:
        self.update(new_artist)

class Progress(Label):
    progress = reactive(0)

    def on_mount(self) -> None:
        self.set_interval(1, self.update_progress)

    def update_progress(self) -> None:
        with MUTEX:
            self.progress = SONG_DATA["progressPercentage"] if SONG_DATA["playing"] else 0

    def watch_progress(self, new_progress) -> None:
        self.update(f"{''.join(['\u2588' if new_progress > i/(SIZE*2) else '\u2591' for i in range(SIZE*2)])}")

class MusicApp(App):
    TITLE = "WALKMAN"
    BINDINGS = [("`", "toggle_dark", "dark mode")]
    CSS = f"""
    Screen {{
        align: center middle;
    }}

    Container {{
        height: auto;
        width: auto;
    }}

    Vertical {{
        height: {SIZE};
        width: {SIZE*2};
        margin-bottom: 1;
    }}

    Label {{
        margin: 0;
    }}

    .songdata {{
        width: {SIZE*2};
        text-align: center;
    }}

    #progress {{
        width: {SIZE*2};
        margin-top: 1;
    }}
    """

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        # perhaps should be grouped into one "Image" class
        with Container():
            with Vertical():
                for i in range(SIZE):
                    with Horizontal():
                        for j in range(SIZE*2):
                            yield ImagePixel(j//2, i)
            yield Song(classes="songdata")
            yield Artist(classes="songdata")
            yield Progress(id="progress")
            # no pause indicator
            # no controls

    def action_toggle_dark(self) -> None:
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

# this breaks after it runs for too long... why?
def get_spotify():
    while(True):
        results = SP.current_user_playing_track()

        with MUTEX:
            if(results):
                SONG_DATA["playing"] = True
                SONG_DATA["name"] = results["item"]["name"] or "[SONG]"
                artist_string = ", ".join([artist["name"] for artist in results["item"]["artists"]]) or "[ARTIST]"
                SONG_DATA["artist"] = artist_string if len(artist_string) < SIZE*2 else f"{artist_string[0:SIZE*2-3]}..."
                SONG_DATA["progressPercentage"] = results["progress_ms"] / results["item"]["duration_ms"]
            else:
                SONG_DATA["playing"] = False

        if results and len(results["item"]["album"]["images"]) > 0:
            url = results["item"]["album"]["images"][-1]["url"]
            response = requests.get(url)
            img = Image.open(io.BytesIO(response.content))
            rgb = img.convert("RGB")
            small = rgb.resize((SIZE, SIZE), resample=Image.Resampling.HAMMING)

        with MUTEX:
            for i in range(SIZE):
                for j in range(SIZE):
                    IMG_COLORS[i][j] = small.getpixel((i, j)) if results and len(results["item"]["album"]["images"]) > 0 else (0, 0, 0)
        time.sleep(1)

def main():
    t1 = Thread(target=get_spotify)
    t1.start()

    app = MusicApp()
    app.run()

    t1.join()

if __name__ == "__main__":
    main()
