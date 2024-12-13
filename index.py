from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import secrets
import os
from interests import INTERESTS

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_urlsafe(32)

socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

states = ['ny', 'ma', 'ga', 'sc', 'pa', 'va']

data = [[0 for _ in states] for _ in range(4)]

current_text = ""

@socketio.on('message')
def handle_message(message):
    print('received message: ' + message)

@socketio.on('connect')
def handle_connect():
    emit('text_update', {'text': current_text})
    print("A new client has connected. Current text sent.")
    
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
    blurb = INTERESTS[states.index(state)]
    return render_template('state.html', state=state, data=return_data, blurb=blurb)

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
    socketio.run(app, debug=True, port=8080)
