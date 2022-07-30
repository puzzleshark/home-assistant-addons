import asyncio
import os

import librosa
import numpy as np

from forrest_spotify_curator import authentication
from forrest_spotify_curator import secrets


MP3_FOLDER = 'music'


def download_playlist(folder_name):
    print("creating folder")
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    print("created dirs")
    print("starting download")
    os.system(f'spotdl https://open.spotify.com/playlist/{secrets.PLAYLIST_ID} -o {folder_name}')
    print("finished download")
    return os.listdir(folder_name)


def get_filename(track, filenames):
    for filename in filenames:
        if track['name'].strip('?') in filename:
            return os.path.join("music", filename)


def song_in_tune(filename):
    y, sr = librosa.load(filename, duration=40)
    value = librosa.estimate_tuning(y=y, sr=sr)
    cents = round(value * 100)
    if cents < 0:
        print(f'{np.abs(cents)} cents flat')
    else:
        print(f'{np.abs(cents)} cents sharp')
    if np.abs(cents) > 9:  # needs to be better than 9 cents
        print("not good enough")
        return False
    else:
        return True


async def main():

    spotify_auth = authentication.SpotifyAuthenticator()
    spotify_auth.create_server()
    spotify = await spotify_auth.get_spotify()

    print("have spotify object")

    filenames = download_playlist(MP3_FOLDER)

    results = spotify.playlist_items(f"spotify:playlist:{secrets.PLAYLIST_ID}")

    print("have results")

    for item in results['items']:
        track = item['track']
        print("====================================================================")
        print('track    : ' + track['name'])
        print('audio    : ' + track['uri'])
        filename = get_filename(track, filenames)

        try:
            if not song_in_tune(filename):
                spotify.playlist_remove_all_occurrences_of_items(secrets.PLAYLIST_ID, [track['uri']])
                print("removed it")
        except:
            print("could not parse, need to figure this out")

asyncio.run(main())