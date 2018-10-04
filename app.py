from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import threading, hashlib, time, os, json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'minecraftisthebest'
socketio = SocketIO(app)

FILE_HASH = ''
SCREEN_FILE_PATH = 'testing.data'

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('new_connection')
def handle_my_custom_event():
    socketio.emit('message', json.dumps({"data": read_file()}))

@socketio.on('command')
def run_command(command):
    enter = "$(printf '\\r')"
    os.system('screen -r -x -X stuff "%s%s"' % (command, enter))

def filechecker():
    global FILE_HASH
    while True:
        new_hash = file_checksum()
        if new_hash != FILE_HASH:
            FILE_HASH = new_hash
            socketio.emit('message', json.dumps({"data": read_file()}))
        time.sleep(1)

def file_checksum(path=SCREEN_FILE_PATH):
    hash_md5 = hashlib.md5()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_md5.update(chunk)
        return hash_md5.hexdigest()

def read_file(path=SCREEN_FILE_PATH):
    with open(path, 'r') as f:
        return f.readlines()

if __name__ == '__main__':
    thr = threading.Thread(target=filechecker)
    thr.start()
    socketio.run(app, host='0.0.0.0', port=5500, debug=True)