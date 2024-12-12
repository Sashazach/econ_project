const socket = io();

socket.on('message', (message) => {
  const messagesDiv = document.getElementById('messages');
  messagesDiv.innerHTML += `<p>${message}</p>`;
});

const sendMessageButton = document.getElementById('sendMessage');
sendMessageButton.addEventListener('click', () => {
  const messageInput = document.getElementById('messageInput');
  const message = messageInput.value;
  socket.emit('message', message);
  messageInput.value = '';
});