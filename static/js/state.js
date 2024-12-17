var socket = io();

const STATES = ["New York", "Massachusetts", "Georgia", "South Carolina", "Pennsylvania", "Virginia"];
const states = ['ny', 'ma', 'ga', 'sc', 'pa', 'va']

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
    initiateConnection();
});

function updateDataTable(data) {
    // Clear existing data rows first
    const dataRows = $('#dataTable tr').length - 2;  // Subtract header and totals row
    while ($('#dataTable tr').length > 2) {  // Keep header and totals row
        $('#dataTable tr:eq(1)').remove();
    }

    // Add rows for all rounds
    for (let i = 0; i < data.length; i++) {
        const newRow = $('<tr>');
        newRow.append($(`<th>R${i + 1}</th>`));
        
        for (let j = 0; j < data[i].length; j++) {
            newRow.append($(`<td>${data[i][j]}</td>`));
        }
        
        $('#dataTable tr:last').before(newRow);
    }

    // Calculate and update totals
    const totals = Array(data[0].length).fill(0);
    for (let j = 0; j < data[0].length; j++) {
        for (let i = 0; i < data.length; i++) {
            totals[j] += data[i][j];
        }
    }

    // Update total row
    const maxTotal = Math.max(...totals);
    totals.forEach((total, index) => {
        const totalCell = $(`#dataTable tr:last td:eq(${index})`);
        totalCell.text(total);
        if (total === maxTotal) {
            totalCell.addClass('highest-total');
        } else {
            totalCell.removeClass('highest-total');
        }
    });
}

function initiateConnection() {
    var socket = io(window.location.host, {
        rememberTransport: false,
        transports: ["websocket"],
    });

    socket.on('connect', () => {
        console.log('Successfully connected to the server');
        socket.emit('request_phase_update');
        socket.emit('request_approval_data');
        socket.emit('request_topic_update');
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

    socket.on('data_update', function(msg) {
        if (msg.data) {
            updateDataTable(msg.data);
        }
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

    socket.on('redirect', (data) => {
        window.location.href = data.url;
    });

    socket.on('approval_granted', (data) => {
        handleStateApproval(data.data);
    });

    socket.on('topic_update', (data) => {
        const currentTopic = document.getElementById('currentTopic');
        if (currentTopic) {
            currentTopic.textContent = data.topic;
        }
    });

    function approveFunction(state) {
        socket.emit('approval_granted', state);
    }

    window.approveFunction = approveFunction;

    const agreementBox = document.getElementById('agreementBox');
    agreementBox.addEventListener('input', () => {  
        socket.emit('text_update', { text: agreementBox.value });
    });
}

function handleStateApproval(approvalStates) {    
    // Update each state's segment based on the approval array
    console.log(approvalStates);
    states.forEach((state, index) => {
        const stateSegment = document.getElementById(`approval-${state}`);
        if (stateSegment) {
            stateSegment.classList.remove('pending', 'approved');
            stateSegment.classList.add(approvalStates[index] ? 'approved' : 'pending');
            stateSegment.textContent = `${STATES[index]}: ${approvalStates[index] ? 'Approved' : 'Pending'}`;
        }
    });
}

const loadStateTitle = function(state) {
    const titleBox = document.getElementById('stateName');
    titleBox.textContent = STATES[state];
};