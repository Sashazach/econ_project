var socket = io();

const STATES = ["New York", "Massachusetts", "Georgia", "South Carolina", "Pennsylvania", "Virginia"];

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

    socket.on('connect_error', (err) => {
        console.error('Connection error:', err);
    });

    socket.on('message', (message) => {
        const messagesDiv = document.getElementById('messages');
        if (messagesDiv) {
            messagesDiv.innerHTML += `<p>${message}</p>`;
        }
    });

    socket.on('text_update', (data) => {
        const agreementBox = document.getElementById('agreementBox');
        if (agreementBox) {
            agreementBox.value = data.text;
        }
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

    const approveButton = document.getElementById('approveButton');
    approveButton.addEventListener('click', function() {
        console.log('Approve button clicked!');
        socket.emit('message', 'test');
    });

    const agreementBox = document.getElementById('agreementBox');
    agreementBox.addEventListener('input', () => {  
        socket.emit('text_update', { text: agreementBox.value });
    });
}

const loadStateTitle = function(state) {
    const titleBox = document.getElementById('stateName');
    console.log('test');
    titleBox.textContent = STATES[state];
};