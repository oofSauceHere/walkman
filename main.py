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
COLORS = [(0, 0, 0), (128, 0, 0), (0, 128, 0), (128, 128, 0), (0, 0, 128), (128, 0, 128), (0, 128, 128), (192, 192, 192), (128, 128, 128), (255, 0, 0), (0, 255, 0), (255, 255, 0), (0, 0, 255), (255, 0, 255), (0, 255, 255), (255, 255, 255), (0, 0, 0), (0, 0, 95), (0, 0, 135), (0, 0, 215), (0, 0, 255), (0, 95, 0), (0, 95, 175), (0, 95, 215), (0, 95, 255), (0, 135, 0), (0, 135, 95), (0, 135, 135), (0, 135, 215), (0, 135, 255), (0, 175, 135), (0, 175, 175), (0, 175, 215), (0, 175, 255), (0, 215, 0), (0, 215, 95), (0, 215, 175), (0, 215, 215), (0, 215, 255), (0, 255, 0), (0, 255, 95), (0, 255, 135), (0, 255, 175), (0, 255, 215), (0, 255, 255), (95, 0, 175), (95, 0, 215), (95, 0, 255), (95, 95, 95), (95, 95, 135), (95, 95, 215), (95, 95, 255), (95, 135, 0), (95, 135, 135), (95, 135, 175), (95, 135, 215), (95, 135, 255), (95, 175, 95), (95, 175, 175), (95, 175, 215), (95, 215, 0), (95, 215, 135), (95, 215, 175), (95, 215, 215), (95, 215, 255), (95, 255, 95), (95, 255, 175), (95, 255, 255), (135, 0, 0), (135, 0, 175), (135, 95, 0), (135, 95, 95), (135, 95, 135), (135, 95, 215), (135, 95, 255), (135, 135, 95), (135, 135, 135), (135, 135, 175), (135, 135, 215), (135, 135, 255), (135, 175, 0), (135, 175, 135), (135, 175, 215), (135, 175, 255), (135, 215, 0), (135, 215, 135), (135, 215, 215), (135, 215, 255), (135, 255, 0), (135, 255, 135), (135, 255, 215), (135, 255, 255), (175, 0, 95), (175, 0, 135), (175, 0, 215), (175, 0, 255), (175, 95, 175), (175, 95, 215), (175, 135, 0), (175, 135, 135), (175, 135, 175), (175, 135, 215), (175, 135, 255), (175, 175, 95), (175, 175, 135), (175, 175, 175), (175, 175, 215), (175, 175, 255), (175, 215, 95), (175, 215, 135), (175, 215, 215), (175, 215, 255), (175, 255, 0), (175, 255, 95), (175, 255, 135), (175, 255, 175), (175, 255, 255), (215, 0, 0), (215, 0, 135), (215, 0, 215), (215, 95, 0), (215, 95, 95), (215, 95, 135), (215, 95, 175), (215, 95, 215), (215, 135, 0), (215, 135, 95), (215, 135, 135), (215, 135, 175), (215, 135, 215), (215, 135, 255), (215, 175, 0), (215, 175, 95), (215, 175, 135), (215, 175, 175), (215, 175, 215), (215, 175, 255), (215, 215, 0), (215, 215, 95), (215, 215, 175), (215, 215, 215), (215, 215, 255), (215, 255, 0), (215, 255, 135), (215, 255, 175), (215, 255, 215), (215, 255, 255), (255, 0, 0), (255, 0, 95), (255, 0, 175), (255, 0, 215), (255, 0, 255), (255, 95, 0), (255, 95, 135), (255, 95, 215), (255, 95, 255), (255, 135, 0), (255, 135, 95), (255, 135, 135), (255, 135, 175), (255, 135, 215), (255, 135, 255), (255, 175, 0), (255, 175, 95), (255, 175, 135), (255, 175, 175), (255, 175, 215), (255, 175, 255), (255, 215, 0), (255, 215, 135), (255, 215, 175), (255, 215, 215), (255, 215, 255), (255, 255, 0), (255, 255, 95), (255, 255, 135), (255, 255, 175), (255, 255, 215), (255, 255, 255), (8, 8, 8), (18, 18, 18), (28, 28, 28), (38, 38, 38), (48, 48, 48), (58, 58, 58), (68, 68, 68), (78, 78, 78), (88, 88, 88), (98, 98, 98), (108, 108, 108), (118, 118, 118), (128, 128, 128), (138, 138, 138), (148, 148, 148), (158, 158, 158), (168, 168, 168), (178, 178, 178), (188, 188, 188), (198, 198, 198), (208, 208, 208), (218, 218, 218), (228, 228, 228), (238, 238, 238)]
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
                            color = IMG_COLORS[i][j//2]
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
            # i intended to manually find the closest supported color...
            # but i guess that's not needed

            # pix = small.getpixel((i, j))
            # closest_color = pix
            # dist = -1
            # for color in COLORS:
                # new_dist = reduce(lambda x, y: x + y, [(color[i]-pix[i])**2 for i in range(3)])
                # if dist == -1 or new_dist < dist:
                    # closest_color = color
                    # dist = new_dist
            # IMG_COLORS[i][j] = closest_color
            IMG_COLORS[i][j] = small.getpixel((i, j))

    app = MusicApp()
    app.run()

if __name__ == "__main__":
    main()
