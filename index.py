from flask import Flask, render_template, redirect, url_for, request
from flask_socketio import SocketIO, emit
import secrets
import threading
import time
from blurbs import BLURBS
from ai import analyzeAgreement  # Import the analyzeAgreement function

state_approvals = [False, False, False, False, False, False]

roundIndex = 0

collective_failures = 0

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_urlsafe(32)

socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

stateNames = ["New York", "Massachusetts", "Georgia", "South Carolina", "Pennsylvania", "Virginia"];
states = ['ny', 'ma', 'ga', 'sc', 'pa', 'va']
round_topics = ["Should the Electoral College exist or should it be a popular vote?", "Should slaves be counted in population data; therefore impacting state representation in Congress?", "Should we tax imports and exports, if yes, how so?", "How much control should the federal government have on trade and tariffs?", "Should the federal government take care of (“bail out”) the individual states’ war debts?"]
topic_names = ["Electoral College or Popular Vote?", "Slaves in Population Data", "Taxing Imports and Exports", "Federal Government Control on Trade", "Federal Government Bail out War Debt"]

ADMIN_PASSWORD = "Econ"

data = [[0 for _ in states] for _ in range(5)]

current_text = " "

current_phase = "Waiting for round to start."
time_remaining = 0
round_running = False  # Add a flag to track if a round is running
paused = False  # Add a flag to track if the round is paused
inconclusive_rounds = 0

round_phases = {
    0: [("Team Thinking Time", 120), ("Discuss & Draft Agreement", 300), ("Final Decisions", 45)],
    1: [("Team Thinking Time", 120), ("Discuss & Draft Agreement", 300), ("Final Decisions", 45)],
    2: [("Team Thinking Time", 120), ("Discuss & Draft Agreement", 300), ("Final Decisions", 45)],
    3: [("Team Thinking Time", 120), ("Discuss & Draft Agreement", 300), ("Final Decisions", 45)],
    4: [("Team Thinking Time", 120), ("Discuss & Draft Agreement", 300), ("Final Decisions", 45)],
}    

def run_round(round : int):
    global current_phase, time_remaining, round_running, paused, roundIndex
    roundIndex = round
    round_running = True
    for phase, duration in round_phases[round]:
        current_phase = phase
        time_remaining = duration
        while time_remaining > 0:
            if not round_running:  # Check if the round is still running
                return
            if not paused:
                socketio.emit('phase_update', {'phase': current_phase, 'time_remaining': time_remaining})
                time_remaining -= 1
            time.sleep(1)
    end_round()

def reset_scores():
    global data 
    data = [[0 for _ in states] for _ in range(5)]
    emit('data_update', {'data': data})

def end_round(mode="normal"):
    global round_running, current_text, state_approvals, collective_failures
    if mode != "exited by force":
        collective_failures += 1
        if collective_failures >= 2:
            send_notification("Two rounds have been inconclusive. Redirecting to the congratulations screen...")
            emit('redirect', {'url': url_for('congratulations')}, broadcast=True)
            return
    round_running = False  # Ensure the round stops running
    current_phase = "Round Ended."
    time_remaining = 0
    socketio.emit('phase_update', {'phase': current_phase, 'time_remaining': time_remaining})
    current_text = " "
    socketio.emit('text_update', data)
    for i in range(len(state_approvals)):
        state_approvals[i] = False
    socketio.emit('approval_granted', {'data': state_approvals})
        
def handle_submit_agreement():
    if not current_text or current_text.isspace():
        send_notification("Error: Agreement text cannot be empty!")
        return
        
    send_notification("Agreement submitted. Analyzing...")
    points = analyzeAgreement(round_topics[roundIndex], current_text)
    send_notification("Agreement evaluated. Updating scores...")
    if len(points) != len(states):
        emit('error', {'message': 'Invalid points received from analysis.'})
        return
    
    for i, point in enumerate(points):
        data[roundIndex][i] += point
    
    emit('data_update', {'data': data})
    end_round()

    # Check if the current round is the last round (roundIndex 4)
    if roundIndex == 4:
        send_notification("Game over! Redirecting to the congratulations screen...")
        emit('redirect', {'url': url_for('congratulations')}, broadcast=True)

def send_notification(message):
    emit('show_notification', {'message': message}, broadcast=True)

@socketio.on('request_congrats_data')
def handle_request_congrats_data():
    # Format data into a dictionary with state names as keys
    formatted_data = {}
    for i, state in enumerate(stateNames):
        formatted_data[state] = {
            1: data[0][i],
            2: data[1][i],
            3: data[2][i],
            4: data[3][i],
            5: data[4][i]
        }

    highest_total_indices = get_highest_total_column()
    winner_names = format_highest_total_columns(highest_total_indices)
    
    result = 'collective_failure' if collective_failures >= 2 else 'win'
    response_data = {
        'gameData': formatted_data,
        'winner': winner_names,
        'result': result
    }
    emit('congrats_data', response_data, to=request.sid)

@socketio.on('begin_round')
def handle_begin_round(round: int):
    send_notification(f"Round {round} has started.")
    roundIndex = round-1
    emit('topic_update', {'topic': topic_names[roundIndex]}, to=request.sid)
    if not round_running:
        for i in range(len(state_approvals)):
            state_approvals[i] = False
        thread = threading.Thread(target=run_round, args=(roundIndex,))
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
    emit('phase_update', {'phase': current_phase, 'time_remaining': time_remaining}, to=request.sid)

@socketio.on('connect')
def handle_connect():
    emit('text_update', {'text': current_text})
    emit('phase_update', {'phase': current_phase, 'time_remaining': time_remaining})
    emit('data_update', {'data': data}, to=request.sid)
    print("A new client has connected. Current text and phase sent.")
    
@socketio.on('text_update')
def handle_text_update(data):
    global current_text
    current_text = data.get('text', '')
    emit('text_update', data, broadcast=True, include_self=False)
    for i in range(len(state_approvals)):
        state_approvals[i] = False
    emit('approval_granted', {'data': state_approvals}, broadcast=True)

@socketio.on('approval_granted')
def handle_approval_granted(state):
    if round_running:
        state_approvals[int(state)] = True
        emit('approval_granted', {'data': state_approvals}, broadcast=True)
        if state_approvals.count(True) >= 5:
            for i in range(len(state_approvals)):
                state_approvals[i] = False
            handle_submit_agreement()

@socketio.on('request_approval_data')
def handle_request_approval_data():
    emit('approval_granted', {'data': state_approvals}, to=request.sid)

@socketio.on('verify_password')
def handle_verify_password(data):
    password = data.get('password', '')
    if password == ADMIN_PASSWORD:
        emit('password_verification', {'success': True})
    else:
        emit('password_verification', {'success': False})

@socketio.on('submit_agreement')
def handle_submit_agreement_event():
    handle_submit_agreement()

@socketio.on('request_topic_update')
def handle_request_topic_update():
    if roundIndex < len(round_topics):
        emit('topic_update', {'topic': topic_names[roundIndex]}, to=request.sid)
    else:
        print("No more topics available.")
        emit('topic_update', {'topic': 'No topic available'}, to=request.sid)

@socketio.on('reset_scores')
def handle_reset_scores():
    reset_scores()
    send_notification("Scores have been reset.")

@socketio.on('exit_round')
def handle_exit_round():
    send_notification("The current round has been exited.")
    end_round("exited by force")

@socketio.on('adjust_failures')
def handle_adjust_failures(data):
    global collective_failures
    new_failures = data.get('failures', collective_failures)
    if isinstance(new_failures, int) and new_failures >= 0:
        collective_failures = new_failures
        send_notification(f"Collective failures adjusted to {collective_failures}.")
    else:
        send_notification("Invalid value for collective failures.")
    if collective_failures >= 2:
        send_notification("Two rounds have been inconclusive. Redirecting to the congratulations screen...")
        emit('redirect', {'url': url_for('congratulations')}, broadcast=True)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/congratulations')
def congratulations():
    return render_template('congratulations.html')

def state_page(state):
    stateIndex = states.index(state)
    blurb = BLURBS[stateIndex]
    # Compute totals for each column
    if data:
        totals = [sum(col) for col in zip(*data)]
    else:
        totals = [0] * len(states)
    return render_template('state.html', state=stateIndex, states=states, data=data, blurb=blurb, totals=totals)

def get_highest_total_column():
    if not data:
        return None
    totals = [sum(col) for col in zip(*data)]
    highest_total = max(totals)
    highest_total_indices = [index for index, total in enumerate(totals) if total == highest_total]
    return highest_total_indices

def format_highest_total_columns(indices):
    if not indices:
        return ""
    names = [stateNames[index] for index in indices]
    if len(names) == 1:
        return names[0]
    return ", ".join(names[:-1]) + " and " + names[-1]

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
