from threading import Thread

import os
import urllib.parse
import subprocess
import pathlib

from flask import Flask, jsonify


# Configuration
AIRPLAY_ID = '192.168.7.160'
directory = os.path.dirname(__file__)


def get_playlist_songs(m3u8):
    '''
    Parse m3u8 playlist files and return a collection of songs.

    Note: for my use case, I have playlists that refer to m4a versions of
    the songs, and RAOP works better with MP3, so I change the references.
    '''

    with open(m3u8) as f:
        for line in f.readlines():
            line = urllib.parse.unquote(line.strip()).replace('.m4a', '.mp3')
            if line and not line.startswith('#'):
                yield pathlib.Path(directory) / "music" / line


class StreamJob(Thread):
    '''
    A worker thread which plays a queue of songs in order.
    Is safely able to be terminated to stop the job.
    '''

    def __init__(self, queue):
        self.queue = queue
        self.current_process = None
        self.stop = False
        super().__init__()

    def run(self):
        for song in self.queue:
            if not self.stop:
                self.current_process = self.play(song)
                self.current_process.wait()

    def play(self, song):
        print(f'Playing "{song}"')
        cmd = [f'{directory}/stream', AIRPLAY_ID, song]
        return subprocess.Popen(cmd, shell=False)

    def terminate(self):
        self.stop = True
        if self.current_process:
            self.current_process.terminate()


# Create simple Flask web service
app = Flask(__name__)
app.now_playing = None


@app.route("/<tag_id>")
def play(tag_id):
    # stop existing stream jobs
    if app.now_playing:
        app.now_playing.terminate()

    # check to see if there is a playlist or song matching the tag
    path = pathlib.Path(directory) / "music"
    playlist = path / f'{tag_id}.m3u8'
    song = path / f'{tag_id}.mp3'

    if playlist.exists():
        print(f'Playing playlist ->', playlist)
        songs = get_playlist_songs(playlist)
        app.now_playing = StreamJob(songs)
        app.now_playing.start()
        return jsonify({'success': True, 'playing': str(playlist)})

    elif song.exists():
        print(f'Playing song ->', song)
        app.now_playing = StreamJob([song])
        app.now_playing.start()
        return jsonify({'success': True, 'playing': str(song)})

    print(f'Playlist or song not found for tag id "{tag_id}"')
    return jsonify({'success': False, 'tag_id': tag_id})

