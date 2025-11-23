// Voice AI Interface - Frontend JavaScript
// Handles audio recording and API communication

let mediaRecorder;
let audioChunks = [];
let isRecording = false;

const recordButton = document.getElementById('recordButton');
const statusIndicator = document.getElementById('statusIndicator');
const chatLog = document.getElementById('chatLog');
const audioPlayer = document.getElementById('audioPlayer');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    recordButton.addEventListener('click', toggleRecording);
    clearWelcomeMessage();
});

function clearWelcomeMessage() {
    // Clear welcome message after first interaction
    setTimeout(() => {
        const welcome = chatLog.querySelector('.welcome-message');
        if (welcome && chatLog.children.length > 1) {
            welcome.remove();
        }
    }, 1000);
}

async function toggleRecording() {
    if (!isRecording) {
        await startRecording();
    } else {
        await stopRecording();
    }
}

async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

        mediaRecorder = new MediaRecorder(stream, {
            mimeType: 'audio/webm;codecs=opus'
        });

        audioChunks = [];

        mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                audioChunks.push(event.data);
            }
        };

        mediaRecorder.onstop = async () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
            await sendAudioToServer(audioBlob);

            // Stop all tracks
            stream.getTracks().forEach(track => track.stop());
        };

        mediaRecorder.start();
        isRecording = true;
        updateUI('recording');

    } catch (error) {
        console.error('Error accessing microphone:', error);
        alert('Could not access microphone. Please grant permission.');
    }
}

async function stopRecording() {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
        isRecording = false;
        updateUI('processing');
    }
}

async function sendAudioToServer(audioBlob) {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.webm');

    try {
        const response = await fetch('/process_audio', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Server error');
        }

        const data = await response.json();

        // Display transcript
        addMessage('user', data.transcript);

        // Display agent response
        addMessage('agent', data.response_text);

        // Play audio response
        if (data.response_audio) {
            playAudioResponse(data.response_audio);
        }

        updateUI('ready');

    } catch (error) {
        console.error('Error processing audio:', error);
        addMessage('system', `Error: ${error.message}`);
        updateUI('ready');
    }
}

function playAudioResponse(audioBase64) {
    const audioData = `data:audio/mpeg;base64,${audioBase64}`;
    audioPlayer.src = audioData;
    audioPlayer.play().catch(err => {
        console.error('Error playing audio:', err);
    });
}

function addMessage(sender, text) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;

    const icon = sender === 'user' ? '👤' : sender === 'agent' ? '🤖' : '⚠️';
    const label = sender === 'user' ? 'You' : sender === 'agent' ? 'Agent' : 'System';

    messageDiv.innerHTML = `
        <div class="message-header">
            <span class="message-icon">${icon}</span>
            <span class="message-sender">${label}</span>
            <span class="message-time">${new Date().toLocaleTimeString()}</span>
        </div>
        <div class="message-text">${escapeHtml(text)}</div>
    `;

    chatLog.appendChild(messageDiv);
    chatLog.scrollTop = chatLog.scrollHeight;
}

function updateUI(state) {
    const statusText = statusIndicator.querySelector('.status-text');
    const buttonText = recordButton.querySelector('.text');

    switch (state) {
        case 'recording':
            recordButton.classList.add('recording');
            buttonText.textContent = 'Recording...';
            statusText.textContent = 'Listening';
            statusIndicator.classList.add('active');
            break;
        case 'processing':
            recordButton.classList.remove('recording');
            recordButton.disabled = true;
            buttonText.textContent = 'Processing...';
            statusText.textContent = 'Processing';
            break;
        case 'ready':
            recordButton.classList.remove('recording');
            recordButton.disabled = false;
            buttonText.textContent = 'Click to Speak';
            statusText.textContent = 'Ready';
            statusIndicator.classList.remove('active');
            break;
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
