const STATES = ["New York", "Massachusetts", "Georgia", "South Carolina", "Pennsylvania", "Virginia"];

document.addEventListener('DOMContentLoaded', () => {
    // Festive color palette
    const colors = [
        '#FF6B6B', // coral
        '#4ECDC4', // turquoise
        '#FFD93D', // yellow
        '#FF8C42', // orange
        '#6C5CE7', // purple
        '#A8E6CF', // mint
        '#FDFFAB', // light yellow
        '#FF99C8'  // pink
    ];

    // Initial confetti burst
    confetti({
        particleCount: 150,
        spread: 100,
        colors: colors,
        origin: { y: 0.6 }
    });

    // Continuous confetti
    function randomInRange(min, max) {
        return Math.random() * (max - min) + min;
    }

    (function frame() {
        confetti({
            particleCount: 3,
            angle: 60,
            spread: 55,
            origin: { x: 0 },
            colors: colors
        });
        confetti({
            particleCount: 3,
            angle: 120,
            spread: 55,
            origin: { x: 1 },
            colors: colors
        });

        requestAnimationFrame(frame);
    }());

    // Send request_congrats_data event to the server
    const socket = io();
    socket.emit('request_congrats_data');

    // Handle the response from the server
    socket.on('congrats_data', (data) => {
        console.log("Received congrats data:", data);
        if (data && data.gameData) {
            handleCongratsData(data.gameData);
            // Update winner name
            const winnerNameElement = document.getElementById('winnerName');
            if (winnerNameElement && data.winner) {
                winnerNameElement.textContent = data.winner;
            }
        }
    });
});

function handleCongratsData(data) {
    console.log("Processing game data:", data);
    if (!data) {
        console.error('No data received');
        return;
    }

    const tbody = document.querySelector('#gameResults tbody');
    if (!tbody) {
        console.error('Table body not found');
        return;
    }

    tbody.innerHTML = ''; // Clear existing content

    // Create rows for each state
    STATES.forEach(state => {
        const row = document.createElement('tr');
        
        // Add state name
        const stateCell = document.createElement('td');
        stateCell.textContent = state;
        row.appendChild(stateCell);

        let total = 0;
        // Add rounds data
        for (let round = 1; round <= 5; round++) {
            const cell = document.createElement('td');
            const roundData = data[state] || {};
            const value = roundData[round] || 0;
            cell.textContent = value.toLocaleString();
            total += value;
            row.appendChild(cell);
        }

        // Add total
        const totalCell = document.createElement('td');
        totalCell.textContent = total.toLocaleString();
        totalCell.classList.add('total-column');
        row.appendChild(totalCell);

        tbody.appendChild(row);
    });

    // Highlight the winner's row
    const winnerName = document.getElementById('winnerName').textContent;
    if (winnerName) {
        const rows = tbody.getElementsByTagName('tr');
        for (let row of rows) {
            if (row.cells[0].textContent === winnerName) {
                row.classList.add('winner-row');
            }
        }
    }
}
