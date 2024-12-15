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

function updateDataTable(data) {
    // Skip the first row of data (headers)
    const dataRows = data.slice(1);
    
    // Update only the data cells, preserving headers
    dataRows.forEach((row, rowIndex) => {
        // Find existing row or create new one
        let tr = document.querySelector(`#dataTable tr:nth-child(${rowIndex + 2})`);
        if (!tr) {
            tr = document.createElement('tr');
            document.getElementById('dataTable').appendChild(tr);
        }
        
        // Add/update round header (R1, R2, etc.)
        let roundHeader = tr.querySelector('th');
        if (!roundHeader) {
            roundHeader = document.createElement('th');
            tr.appendChild(roundHeader);
        }
        roundHeader.textContent = `R${rowIndex + 1}`;
        
        // Update data cells
        row.forEach((item, colIndex) => {
            let td = tr.children[colIndex + 1];
            if (!td) {
                td = document.createElement('td');
                tr.appendChild(td);
            }
            td.textContent = item;
        });
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

    socket.on('data_update', (data) => {
        updateDataTable(data.data);
    });

    function approveFunction(state) {
        console.log('Approve button clicked with state:', state);
        socket.emit('approval_granted', state);
    }

    window.approveFunction = approveFunction;

    const agreementBox = document.getElementById('agreementBox');
    agreementBox.addEventListener('input', () => {  
        socket.emit('text_update', { text: agreementBox.value });
    });
}

const loadStateTitle = function(state) {
    const titleBox = document.getElementById('stateName');
    titleBox.textContent = STATES[state];
};