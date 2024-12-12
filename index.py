from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import os
import secrets
from interests import INTERESTS

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_urlsafe(32) # Important for security
socketio = SocketIO(app, cors_allowed_origins="*")

states = ['ny', 'ma', 'ga', 'sc', 'pa', 'va']

data = [
    [],
    [],
    [],
    [],
]

@socketio.on('message')
def handle_message(message):
    print('received message: ' + message)
    emit('response', 'Server received: ' + message)

for i in range(len(data)):
    for j in range(len(states)):
        data[i].append(0)

@app.route('/')
def home():
    return render_template('home.html')

def state(state):
    return_data = [states] + data
    return render_template('state.html', state=state, data = return_data, blurb=INTERESTS[states.index(state)])

@app.route('/ny')
def page1():
    return state('ny')

@app.route('/ma')
def page2():
    return state('ma')

@app.route('/ga')
def page3():
    return state('ga')

@app.route('/sc')
def page4():
    return state('sc')

@app.route('/pa')
def page5():
    return state('pa')

@app.route('/va')
def page6():
    return state('va')

if __name__ == '__main__':
    app.run(debug=True)
