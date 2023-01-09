import os
import subprocess

from flask import Flask, jsonify


# Configuration
AIRPLAY_ID = 'E0:2B:96:91:9A:FE'


# Synthesize play command
directory = os.path.dirname(__file__)
play_cmd = [f'{directory}/venv/bin/atvremote', '-i', AIRPLAY_ID]


# Create simple Flask web service
app = Flask(__name__)

app.now_playing = None


@app.route("/<song_id>")
def play_song(song_id):
    if app.now_playing:
        app.now_playing.terminate()

    filename = f'{song_id}.mp3'
    full_path = f'{directory}/songs/{filename}'

    if not os.path.exists(full_path):
        print(f'No song found for ID {song_id}')
        return jsonify({'success': False, 'song_id': song_id})

    cmd = ' '.join(play_cmd + [f'stream_file="{full_path}"'])
    app.now_playing = subprocess.Popen(cmd, shell=True)

    return jsonify({'success': True, 'playing': filename})
