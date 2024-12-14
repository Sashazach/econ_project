from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import secrets
import os
import threading
import time
from interests import INTERESTS

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_urlsafe(32)

socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

states = ['ny', 'ma', 'ga', 'sc', 'pa', 'va']

data = [[0 for _ in states] for _ in range(4)]

current_text = ""

current_phase = ""
time_remaining = 0

phases = [
    ("Think with Group", 60),
    ("Present Ideas", 180),
    ("Reflect Silently", 60),
    ("Voting", 30)
]

def run_round():
    global current_phase, time_remaining
    while True:
        for phase, duration in phases:
            current_phase = phase
            time_remaining = duration
            while time_remaining > 0:
                socketio.emit('phase_update', {'phase': current_phase, 'time_remaining': time_remaining})
                time_remaining -= 1
                time.sleep(1)

@socketio.on('message')
def handle_message(message):
    print('received message: ' + message)

@socketio.on('request_phase_update')
def handle_request_phase_update():
    emit('phase_update', {'phase': current_phase, 'time_remaining': time_remaining})

@socketio.on('connect')
def handle_connect():
    emit('text_update', {'text': current_text})
    emit('phase_update', {'phase': current_phase, 'time_remaining': time_remaining})
    print("A new client has connected. Current text and phase sent.")
    
@socketio.on('text_update')
def handle_text_update(data):
    global current_text
    current_text = data.get('text', '')
    print("Received update to box:", current_text)
    emit('text_update', data, broadcast=True, include_self=False)

@app.route('/')
def home():
    return render_template('home.html')

def state_page(state):
    return_data = [states] + data
    stateIndex = states.index(state)
    blurb = INTERESTS[stateIndex]
    return render_template('state.html', state=stateIndex, data=return_data, blurb=blurb)

# Define routes for each state
@app.route('/ny')
def page_ny():
    return state_page('ny')

@app.route('/ma')
def page_ma():
    return state_page('ma')

@app.route('/ga')
def page_ga():
    return state_page('ga')

@app.route('/sc')
def page_sc():
    return state_page('sc')

@app.route('/pa')
def page_pa():
    return state_page('pa')

@app.route('/va')
def page_va():
    return state_page('va')

if __name__ == '__main__':
    print("test")
    # Start the round system in a separate thread
    round_thread = threading.Thread(target=run_round)
    round_thread.daemon = True
    round_thread.start()
    
    # Use socketio.run instead of app.run to properly handle SocketIO
    socketio.run(app, host="0.0.0.0", port=8080, debug=False)
