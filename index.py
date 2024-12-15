from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import secrets
import threading
import time
from interests import INTERESTS
from ai import analyzeAgreement  # Import the analyzeAgreement function

state_approvals = [False, False, False, False, False, False]

global roundIndex
roundIndex = 0

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_urlsafe(32)

socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

states = ['ny', 'ma', 'ga', 'sc', 'pa', 'va']
round_topics = ["Export Law", "Healthcare", "Education", "Infrastructure", "Climate Change"]

ADMIN_PASSWORD = "Econ"

data = [[0 for _ in states] for _ in range(4)]

global current_text
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
    global current_phase, time_remaining, round_running, paused, roundIndex
    roundIndex = round
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

def handle_submit_agreement():
    print("Agreement submitted. Making API call...")
    points = analyzeAgreement(round_topics[roundIndex], current_text)
    send_notification("Agreement evaluated. Updating scores...")
    if len(points) != len(states):
        emit('error', {'message': 'Invalid points received from analysis.'})
        return
    
    for i, point in enumerate(points):
        data[roundIndex][i] += point
    
    emit('data_update', {'data': data}, broadcast=True)

def send_notification(message):
    emit('show_notification', {'message': message}, broadcast=True)

@socketio.on('begin_round')
def handle_begin_round(round: int):
    send_notification(f"Round {round} has started.")
    global roundIndex, round_running
    roundIndex = round
    if not round_running:
        for i in range(len(state_approvals)):
            state_approvals[i] = False
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
    for i in range(len(state_approvals)):
        state_approvals[i] = False

@socketio.on('approval_granted')
def handle_approval_granted(state):
    state_approvals[int(state)] = True
    print(state_approvals)
    if all(state_approvals):
        for i in range(len(state_approvals)):
            state_approvals[i] = False
        send_notification("Using Ai to evaluate agreement...")
        handle_submit_agreement()

@socketio.on('verify_password')
def handle_verify_password(data):
    password = data.get('password', '')
    if password == ADMIN_PASSWORD:
        emit('password_verification', {'success': True})
    else:
        emit('password_verification', {'success': False})

@app.route('/')
def home():
    return render_template('home.html')

def state_page(state):
    return_data = [states] + data
    stateIndex = states.index(state)
    blurb = INTERESTS[stateIndex]
    # Compute totals for each column
    if data:
        totals = [sum(col) for col in zip(*data)]
    else:
        totals = [0] * len(states)
    return render_template('state.html', state=stateIndex, data=return_data, blurb=blurb, totals=totals)

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
