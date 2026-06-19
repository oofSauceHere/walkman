# walkman

<img width="1917" height="960" alt="image" src="https://github.com/user-attachments/assets/b98440a5-2246-4b8f-bed7-5c13f3fd6560" />

---

sometimes you like to work completely in the terminal and there's too much space on the right side of your screen because you pretend to uphold style guide rules and keep lines short (which, according to the example image, i didn't do) and that empty space bugs you. well, now you can use that space to see what you're currently listening to on spotify. does this exist already? i have no clue. i'll like you if you use it...

im too lazy to configure multiple users for a development mode spotify api app (and, frankly, i don't know how to take it out of development mode) so you'll need your own spotify api program, which you can create [here](developer.spotify.com). then, `vim .env` (or use the editor of your choice) and add these three lines:
```
SPOTIPY_CLIENT_ID='{client_id}'
SPOTIPY_CLIENT_SECRET='{client_secret}'
SPOTIPY_REDIRECT_URI='{redirect_uri}'
```
replace the curly brace stuff with the actual values, all of which you can find in the app settings once you create it. you'll make the redirect uri yourself, and 
you can read about that [here](https://developer.spotify.com/documentation/web-api/concepts/redirect_uri), but it's easy to simply use 127.0.0.1 with any valid 
port. you should do more research than me, though.

how to run:
1. create a virtual env using `python -m venv venv`
2. enter that virtual env using `source ./venv/bin/activate` (or `./venv/Scripts/activate.ps1` for Windows)
3. run `python main.py`

if you want to split-screen like in the example image, make sure you have tmux installed. run `tmux` and then enter Ctrl-B + % to split your screen vertically, then run the program using the above steps in the desired pane. for those who don't know venv, you don't need to repeat step 1 multiple times.

i will probably figure out how to automate opening tmux later... probably. im not a fan of things that require a lot of configuration involving going into multiple files, so if i decide this is worth using, ill make it easier to use. but feel free to modify it yourself!
