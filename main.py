# REMEMBER TO GIT PULL!!!

from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Label, Static
from textual.containers import Container, Horizontal, Vertical
from PIL import Image
from functools import reduce
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests
import io

SIZE = 20
IMG_COLORS = [[(255, 255, 255)]*SIZE for i in range(SIZE)]

SP = spotipy.Spotify(auth_manager=SpotifyOAuth(scope="user-read-currently-playing user-library-read"))
SONG_DATA = {
    "playing": "false",
    "name": None,
    "album": None,
    "artist": None,
    "progressPercentage": 0
}

class MusicApp(App):
    TITLE = "SPOTIFY"
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
    }}

    Label {{
        margin: 0;
    }}

    #songdata {{
        width: {SIZE*2};
        margin: 1;
        text-align: center;
    }}

    #progreess {{
        width: {SIZE*2};
    }}
    """

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        with Container():
            with Vertical():
                for i in range(SIZE):
                    with Horizontal():
                        for j in range(SIZE*2):
                            color = IMG_COLORS[j//2][i]
                            color_label = Label("\u2588")
                            color_label.styles.color = f"rgb({color[0]},{color[1]},{color[2]})"
                            yield color_label
            yield Static(f"[bold]{SONG_DATA['name']}[/]\n{SONG_DATA['artist']}", id="songdata")
            yield Static(f"[{"".join(["\u2588" if SONG_DATA['progressPercentage'] >= i/(SIZE*2-2) else " " for i in range(SIZE*2-2)])}]", id="progress")

    def action_toggle_dark(self) -> None:
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

def main():


    results = SP.current_user_playing_track()
    if(results["is_playing"]):
        SONG_DATA["playing"] = True
        SONG_DATA["name"] = results["item"]["name"]
        artist_string = ", ".join([artist["name"] for artist in results["item"]["artists"]])
        SONG_DATA["artist"] = artist_string if len(artist_string) < SIZE*2 else f"{artist_string[0:SIZE_2-3]}..."
        SONG_DATA["progressPercentage"] = results["progress_ms"] / results["item"]["duration_ms"]

    url = results["item"]["album"]["images"][0]["url"]
    response = requests.get(url)
    img = Image.open(io.BytesIO(response.content))
    rgb = img.convert("RGB")
    small = rgb.resize((SIZE, SIZE))

    for i in range(SIZE):
        for j in range(SIZE):
            IMG_COLORS[i][j] = small.getpixel((i, j))

    app = MusicApp()
    app.run()

if __name__ == "__main__":
    main()
