from flask import Flask, render_template_string
from flask_socketio import SocketIO, emit
import subprocess
import threading

app = Flask(__name__)
socketio = SocketIO(app)

# Store the subprocess for interacting with it later
process = None

def run_script():
    global process
    process = subprocess.Popen(
        ['python3', 'your_script.py'], 
        stdin=subprocess.PIPE, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE,
        text=True
    )
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            socketio.emit('output', {'data': output})

@app.route('/')
def index():
    return render_template_string("""
        <html>
            <head><title>Interactive Terminal</title></head>
            <body>
                <h1>Interactive Python Terminal</h1>
                <pre id="output"></pre>
                <input type="text" id="input" autofocus />
                <button onclick="sendInput()">Send</button>
                <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.1.3/socket.io.min.js"></script>
                <script>
                    const socket = io.connect('http://' + document.domain + ':' + location.port);
                    const outputElem = document.getElementById('output');
                    const inputElem = document.getElementById('input');

                    // Listen for output messages from the server
                    socket.on('output', function(data) {
                        outputElem.textContent += data.data;
                        outputElem.scrollTop = outputElem.scrollHeight;
                    });

                    // Send input to the server
                    function sendInput() {
                        const userInput = inputElem.value;
                        inputElem.value = ''; // Clear input field
                        socket.emit('input', {data: userInput});
                    }

                    // Focus input field
                    inputElem.addEventListener('keydown', function(event) {
                        if (event.key === 'Enter') {
                            sendInput();
                        }
                    });
                </script>
            </body>
        </html>
    """)

@socketio.on('input')
def handle_input(data):
    if process:
        process.stdin.write(data['data'] + '\n')
        process.stdin.flush()

if __name__ == '__main__':
    # Start the script in a separate thread
    threading.Thread(target=run_script).start()
    socketio.run(app, host="inventory-console.local", port=80)
