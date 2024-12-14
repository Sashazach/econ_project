from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import secrets
import threading
import time
from interests import INTERESTS
from ai import analyzeAgreement  # Import the analyzeAgreement function

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_urlsafe(32)

socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

states = ['ny', 'ma', 'ga', 'sc', 'pa', 'va']
round_topics = ["Export Law", "Healthcare", "Education", "Infrastructure", "Climate Change"]


data = [[0 for _ in states] for _ in range(4)]

current_text = ""

current_phase = "Waiting for round to start."
time_remaining = 0
round_running = False  # Add a flag to track if a round is running
paused = False  # Add a flag to track if the round is paused

round_phases = {
    1: [("Opening Statements", 15), ("Discussion", 15), ("Voting", 20)],
    2: [("Opening Statements", 20), ("Discussion", 30), ("Voting", 25)],
    3: [("Opening Statements", 15), ("Discussion", 15), ("Voting", 20)],
    4: [("Opening Statements", 20), ("Discussion", 30), ("Voting", 25)],
    5: [("Opening Statements", 20), ("Discussion", 30), ("Voting", 25)],
}

def run_round(round : int):
    global current_phase, time_remaining, round_running, paused
    round_running = True
    for phase, duration in round_phases[round]:
        current_phase = phase
        time_remaining = duration
        while time_remaining > 0:
            if not paused:
                socketio.emit('phase_update', {'phase': current_phase, 'time_remaining': time_remaining})
                time_remaining -= 1
            time.sleep(1)
    current_phase = "Round Ended."
    time_remaining = 0
    socketio.emit('phase_update', {'phase': current_phase, 'time_remaining': time_remaining})
    round_running = False

@socketio.on('begin_round')
def handle_begin_round(round: int):
    global roundIndex
    roundIndex = round
    global round_running
    if not round_running:
        thread = threading.Thread(target=run_round, args=(round,))
        thread.start()
        emit('phase_update', {'phase': 'Round Started.', 'time_remaining': 0}, broadcast=True)
    else:
        emit('phase_update', {'phase': 'Round is already running.', 'time_remaining': time_remaining})

@socketio.on('toggle_pause')
def handle_toggle_pause():
    global paused
    paused = not paused
    emit('phase_update', {'phase': 'Paused' if paused else current_phase, 'time_remaining': time_remaining})

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
    emit('text_update', data, broadcast=True, include_self=False)

@socketio.on('submit_agreement')
def handle_submit_agreement(data):
    topic = data.get('topic', 'Default Topic')  # Adjust as needed
    points = analyzeAgreement(round_topics[roundIndex], data)
    
    if len(points) != len(states):
        emit('error', {'message': 'Invalid points received from analysis.'})
        return
    
    for i, point in enumerate(points):
        for row in data:
            row[i] += point
    
    emit('data_update', {'data': data}, broadcast=True)

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
    # Use socketio.run instead of app.run to properly handle SocketIO
    socketio.run(app, host="0.0.0.0", port=8080, debug=False)
