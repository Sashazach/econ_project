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

$(document).ready(initiateConnection);

function updateDataTable(data) {
    console.log(data);
    // Skip the first row of data (headers)
    const dataRows = data.filter(row => row.some(val => val !== 0));
    const table = document.getElementById('dataTable');
    
    // Update only the data rows that have non-zero values
    dataRows.forEach((row, rowIndex) => {
        // Skip row 1 if it already exists
        if (rowIndex === 0 && table.querySelector('tr:nth-child(2)')) {
            return;
        }

        // Find existing row or create new one
        let tr = table.querySelector(`tr:nth-child(${rowIndex + 2})`);
        if (!tr) {
            tr = document.createElement('tr');
            table.appendChild(tr);
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

    // Add totals row
    let totalsRow = document.querySelector('#dataTable tr.totals-row');
    if (!totalsRow) {
        totalsRow = document.createElement('tr');
        totalsRow.className = 'totals-row';
        document.getElementById('dataTable').appendChild(totalsRow);
    }

    // Add "Total" header cell
    let totalHeader = totalsRow.querySelector('th');
    if (!totalHeader) {
        totalHeader = document.createElement('th');
        totalsRow.appendChild(totalHeader);
    }
    totalHeader.textContent = 'Total';

    // Calculate and update totals
    if (dataRows.length > 0) {
        const columnCount = dataRows[0].length;
        let maxTotal = -Infinity;
        let totals = new Array(columnCount).fill(0);

        // Calculate totals for each column
        for (let col = 0; col < columnCount; col++) {
            totals[col] = dataRows.reduce((sum, row) => sum + Number(row[col]), 0);
            maxTotal = Math.max(maxTotal, totals[col]);
        }

        // Update totals cells
        totals.forEach((total, colIndex) => {
            let td = totalsRow.children[colIndex + 1];
            if (!td) {
                td = document.createElement('td');
                totalsRow.appendChild(td);
            }
            td.textContent = total;
            td.className = total === maxTotal ? 'highest-total' : '';
        });
    }
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