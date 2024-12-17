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

$(document).ready(function() {
    $('#adminMenuButton').show(); // Make the button visible
    $('#adminMenu').hide(); // Ensure the admin menu starts invisible
    $('#passwordPrompt').hide(); // Ensure the password prompt starts invisible
    initiateConnection();

    $('#adminMenuButton').click(function() {
        $('#passwordPrompt').show();
    });

    $('#submitPasswordButton').click(function() {
        const password = $('#adminPassword').val();
        socket.emit('verify_password', { password: password });
    });

    $('#closePasswordPromptButton').click(function() {
        $('#passwordPrompt').hide();
    });

    socket.on('password_verification', (data) => {
        if (data.success) {
            $('#passwordPrompt').hide();
            $('#adminMenu').show();
        } else {
            alert('Incorrect password');
        }
    });

    $('.close-admin-menu-button').click(function() {
        $('#adminMenu').hide();
    });

    $('#beginRoundButton').click(function() {
        socket.emit('begin_round', 1);
    });

    $('#beginRound1Button').click(function() {
        socket.emit('begin_round', 1);
    });
    $('#beginRound2Button').click(function() {
        socket.emit('begin_round', 2);
    });
    $('#beginRound3Button').click(function() {
        socket.emit('begin_round', 3);
    });
    $('#beginRound4Button').click(function() {
        socket.emit('begin_round', 4);
    });
    $('#beginRound5Button').click(function() {
        socket.emit('begin_round', 5);
    });

    $('#pauseButton').click(function() {
        socket.emit('toggle_pause');
    });

    $('#submitAgreementButton').click(function() {
        socket.emit('submit_agreement');
    });

    $('#resetScoresButton').click(function() {
        if (confirm('Are you sure you want to reset all scores? This cannot be undone.')) {
            socket.emit('reset_scores');
        }
    });

    $('#exitRoundButton').click(function() {
        socket.emit('exit_round');
    });

    $('#adjustFailuresButton').click(function() {
        const newFailures = prompt("Enter the new value for collective failures:");
        if (newFailures !== null) {
            socket.emit('adjust_failures', { failures: parseInt(newFailures, 10) });
        }
    });

    // Set initial phase
    $('#currentPhase').text('Waiting for round to start.');

    socket.on('phase_update', (data) => {
        const currentPhase = document.getElementById('currentPhase');
        const timeRemaining = document.getElementById('timeRemaining');
        if (currentPhase && timeRemaining) {
            currentPhase.textContent = data.phase;
            const minutes = String(Math.floor(data.time_remaining / 60)).padStart(2, '0');
            const seconds = String(data.time_remaining % 60).padStart(2, '0');
            timeRemaining.textContent = `${minutes}:${seconds}`;
        }
        if (data.phase === 'Paused') {
            $('#pauseButton').text('Unpause');
        } else {
            $('#pauseButton').text('Pause');
        }
    });

    socket.on('redirect', (data) => {
        window.location.href = data.url;
    });

    socket.emit('request_topic_update');
});

socket.on('topic_update', (data) => {
    const currentTopic = document.getElementById('currentTopic');
    if (currentTopic) {
        currentTopic.textContent = data.topic;
    }
});

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

    socket.on('show_notification', (data) => {
        const notification = document.createElement('div');
        notification.className = 'notification';
        notification.textContent = data.message;
        document.body.appendChild(notification);

        setTimeout(() => {
            notification.classList.add('fade-out');
            notification.addEventListener('animationend', () => notification.remove());
        }, 3000);
    });
}