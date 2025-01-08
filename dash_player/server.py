import subprocess
from flask import Flask, send_from_directory
from flask_cors import CORS
import configparser
import threading
import os

config = configparser.ConfigParser()
config.read('config.ini')

app = Flask(__name__, static_folder='output')
CORS(app) 

@app.route('/output/<path:filename>')
def dash_content(filename):
    """ Serve DASH content from the output directory. """
    return send_from_directory(app.static_folder, filename)

@app.route('/')
def index():
    """ Serve the main page. """
    return send_from_directory(app.root_path, 'index.html')

def run_ffmpeg():
    """ Run the FFmpeg command using the parameters from the config file in the 'output' directory. """
    os.chdir('./output')

    cmd = (
        f"ffmpeg -f dshow -i video=\"{config['FFMPEG']['camera_name']}\":"
        f"audio=\"{config['FFMPEG']['microphone_name']}\" -c:v libx264 -preset veryfast "
        "-s 640x480 -pix_fmt yuv420p -c:a aac -b:a 128k -ar 44100 -g 30 -f dash "
        "-remove_at_exit 1 -seg_duration 6 -use_template 1 -use_timeline 1 "
        "-init_seg_name init-$RepresentationID$.m4s "
        "-media_seg_name chunk-$RepresentationID$-$Number%05d$.m4s "
        "-adaptation_sets \"id=0,streams=v id=1,streams=a\" output.mpd"
    )
    subprocess.run(cmd, shell=True)

def run_flask():
    """ Run the Flask application. """
    app.run(debug=True, host=config['SERVER']['ip'], port=int(config['SERVER']['port']), use_reloader=False)

if __name__ == '__main__':
    flask_thread = threading.Thread(target=run_flask)
    ffmpeg_thread = threading.Thread(target=run_ffmpeg)
    flask_thread.start()
    ffmpeg_thread.start()
