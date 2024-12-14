// Home page specific JavaScript can be added here
var socket = io();

$(window).bind("pageshow", function (event) {
    if (event.originalEvent.persisted) {
        if (socket) {
            socket.disconnect();
            socket = null;
        }
        initiateConnection();
    }
});

$(document).ready(initiateConnection);

function initiateConnection() {
    var socket = io(window.location.host, {
        rememberTransport: false,
        transports: ["websocket"],
    });

    socket.on('connect', () => {
        console.log('Successfully connected to the server');
        socket.emit('request_phase_update');
    });

    socket.on('phase_update', (data) => {
        const currentPhase = document.getElementById('currentPhase');
        const timeRemaining = document.getElementById('timeRemaining');
        if (currentPhase && timeRemaining) {
            currentPhase.textContent = data.phase;
            const minutes = String(Math.floor(data.time_remaining / 60)).padStart(2, '0');
            const seconds = String(data.time_remaining % 60).padStart(2, '0');
            timeRemaining.textContent = `${minutes}:${seconds}`;
        }
    });

    socket.on('reconnect', () => {
        console.log('Reconnected to the server');
        socket.emit('request_phase_update');
    });
}