const inputBar = document.querySelector('.input-bar');
const sendButton = document.querySelector('.send-button');
const chatMessages = document.querySelector('.chat-messages');

function addMessage(content, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', sender === 'bot' ? 'bot-message' : 'user-message');
    messageDiv.textContent = content;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

sendButton.addEventListener('click', async () => {
    const userMessage = inputBar.value.trim();

    if (userMessage !== '') {
        addMessage(userMessage, 'user');
        inputBar.value = '';

        try {
            const response = await fetch('/chatbot', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: userMessage }),
            });

            if (response.ok) {
                const data = await response.json();
                addMessage(data.reply, 'bot');
            } else {
                addMessage('Error al conectar con el servidor.', 'bot');
            }
        } catch (error) {
            console.error(error);
            addMessage('No se pudo conectar con el servidor.', 'bot');
        }
    }
});

