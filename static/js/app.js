const socket = io();

socket.on('connect', () => {
    console.log('Successfully connected to the server');
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

const approveButton = document.getElementById('approveButton');
approveButton.addEventListener('click', function() {
    console.log('Approve button clicked!');
    socket.emit('message', 'test');
});

const agreementBox = document.getElementById('agreementBox');
agreementBox.addEventListener('input', () => {  
    socket.emit('text_update', { text: agreementBox.value });
});
