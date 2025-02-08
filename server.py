from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import subprocess
import threading

app = Flask(__name__)
socketio = SocketIO(app)

def run_script():
    process = subprocess.Popen(['python3', 'main.py'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    while True:
        output = process.stdout.readline()
        if output:
            socketio.emit('output', output)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('input')
def handle_input(data):
    # Send input to the subprocess
    process.stdin.write(data['data'])
    process.stdin.flush()

if __name__ == '__main__':
    threading.Thread(target=run_script).start()
    socketio.run(app, host='inventory-terminal.local', port=80)
