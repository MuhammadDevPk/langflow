// Voice AI Interface - Proper Voice Activity Detection (VAD)
// Always monitors, only records when speech detected

let mediaRecorder;
let audioChunks = [];
let isRecording = false;
let isInCall = false;
let isMonitoring = false;
let silenceTimeout;
let audioContext;
let analyser;
let dataArray;
let stream;

// VAD thresholds - VERY LOW for sensitive microphone
const SILENCE_THRESHOLD = 2;       // Below this = silence
const SPEECH_THRESHOLD = 3;        // Above this = speech starts (user's mic reaches ~5)
const SILENCE_DURATION = 1800;     // 1.8s of silence after speech = end
const MIN_SPEECH_DURATION = 500;   // Minimum 0.5s of speech to send

let speechStartTime = null;
let isAgentSpeaking = false;

const recordButton = document.getElementById('recordButton');
const statusIndicator = document.getElementById('statusIndicator');
const chatLog = document.getElementById('chatLog');
const audioPlayer = document.getElementById('audioPlayer');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    recordButton.addEventListener('click', toggleCall);
    clearWelcomeMessage();

    // Track agent speaking state
    audioPlayer.addEventListener('play', () => {
        isAgentSpeaking = true;
    });
    audioPlayer.addEventListener('ended', () => {
        isAgentSpeaking = false;
    });
    audioPlayer.addEventListener('pause', () => {
        isAgentSpeaking = false;
    });
});

function clearWelcomeMessage() {
    setTimeout(() => {
        const welcome = chatLog.querySelector('.welcome-message');
        if (welcome && chatLog.children.length > 1) {
            welcome.remove();
        }
    }, 1000);
}

async function toggleCall() {
    if (!isInCall) {
        await startCall();
    } else {
        await endCall();
    }
}

async function startCall() {
    try {
        stream = await navigator.mediaDevices.getUserMedia({
            audio: {
                echoCancellation: true,
                noiseSuppression: true,
                autoGainControl: true
            }
        });

        // Setup audio context for VAD
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const source = audioContext.createMediaStreamSource(stream);
        analyser = audioContext.createAnalyser();
        analyser.fftSize = 512;
        analyser.smoothingTimeConstant = 0.3;
        source.connect(analyser);

        const bufferLength = analyser.frequencyBinCount;
        dataArray = new Uint8Array(bufferLength);

        isInCall = true;
        isMonitoring = false; // Don't start monitoring yet
        updateUI('agent-speaking');

        console.log('Call started. Fetching greeting...');

        // Fetch and play greeting
        await playGreeting();

        // After greeting finishes, start monitoring
        isMonitoring = true;
        updateUI('monitoring');
        console.log('Voice monitoring started. Thresholds: Speech=' + SPEECH_THRESHOLD + ', Silence=' + SILENCE_THRESHOLD);
        monitorVoiceActivity();

    } catch (error) {
        console.error('Error accessing microphone:', error);
        alert('Could not access microphone. Please grant permission.');
    }
}

function monitorVoiceActivity() {
    if (!isInCall || !isMonitoring) return;

    analyser.getByteTimeDomainData(dataArray);

    // Calculate volume
    let sum = 0;
    for (let i = 0; i < dataArray.length; i++) {
        const value = Math.abs(dataArray[i] - 128);
        sum += value;
    }
    const volume = sum / dataArray.length;

    // Debug: Update status with volume level
    const statusText = statusIndicator.querySelector('.status-text');
    if (!isRecording && statusText) {
        statusText.textContent = `Monitoring... (Vol: ${Math.round(volume)})`;
    }

    if (volume > SPEECH_THRESHOLD && !isRecording) {
        // Speech detected! Start recording
        console.log('🎤 Speech detected! Volume:', volume);

        // If agent is speaking, interrupt it
        if (isAgentSpeaking) {
            console.log('Interrupting agent...');
            audioPlayer.pause();
            audioPlayer.currentTime = 0;
            isAgentSpeaking = false;
        }

        startRecording();
    } else if (isRecording) {
        // Already recording, check for silence
        if (volume < SILENCE_THRESHOLD) {
            // Silence detected
            if (!silenceTimeout) {
                console.log('🔇 Silence detected, waiting...');
                silenceTimeout = setTimeout(() => {
                    console.log('⏹️ Stopping recording after silence');
                    stopRecording();
                }, SILENCE_DURATION);
            }
        } else {
            // Speech continues, clear timeout
            if (silenceTimeout) {
                clearTimeout(silenceTimeout);
                silenceTimeout = null;
            }
        }
    }

    // Continue monitoring
    requestAnimationFrame(monitorVoiceActivity);
}

function startRecording() {
    if (!stream || isRecording) return;

    mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
    });

    audioChunks = [];
    speechStartTime = Date.now();

    mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
            audioChunks.push(event.data);
        }
    };

    mediaRecorder.onstop = async () => {
        const speechDuration = Date.now() - speechStartTime;

        // Only send if speech was long enough
        if (speechDuration >= MIN_SPEECH_DURATION && audioChunks.length > 0) {
            const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
            await sendAudioToServer(audioBlob);
        } else {
            console.log('Speech too short, discarding...');
            // Resume monitoring immediately
            if (isInCall) {
                updateUI('monitoring');
            }
        }

        audioChunks = [];
        speechStartTime = null;
    };

    mediaRecorder.start();
    isRecording = true;
    updateUI('recording');
}

function stopRecording() {
    if (silenceTimeout) {
        clearTimeout(silenceTimeout);
        silenceTimeout = null;
    }

    if (mediaRecorder && mediaRecorder.state === 'recording') {
        mediaRecorder.stop();
        isRecording = false;
    }
}

async function endCall() {
    isInCall = false;
    isMonitoring = false;
    isRecording = false;

    if (silenceTimeout) {
        clearTimeout(silenceTimeout);
        silenceTimeout = null;
    }

    if (mediaRecorder && mediaRecorder.state === 'recording') {
        mediaRecorder.stop();
    }

    if (audioContext) {
        audioContext.close();
        audioContext = null;
    }

    if (audioPlayer) {
        audioPlayer.pause();
        audioPlayer.currentTime = 0;
        isAgentSpeaking = false;
    }

    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        stream = null;
    }

    updateUI('ready');
}

async function sendAudioToServer(audioBlob) {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.webm');

    updateUI('processing');

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
            updateUI('agent-speaking');
            await playAudioResponse(data.response_audio);
        }

        // Resume monitoring
        if (isInCall) {
            updateUI('monitoring');
        }

    } catch (error) {
        console.error('Error processing audio:', error);
        addMessage('system', `Error: ${error.message}`);

        // Resume monitoring
        if (isInCall) {
            updateUI('monitoring');
        }
    }
}

async function playGreeting() {
    try {
        const response = await fetch('/get_greeting');

        if (!response.ok) {
            throw new Error('Failed to fetch greeting');
        }

        const data = await response.json();

        // Display greeting in chat
        addMessage('agent', data.greeting_text);

        // Play greeting audio
        if (data.greeting_audio) {
            await playAudioResponse(data.greeting_audio);
        }

    } catch (error) {
        console.error('Error playing greeting:', error);
        // Continue anyway - user can still speak
    }
}

function playAudioResponse(audioBase64) {
    return new Promise((resolve, reject) => {
        const audioData = `data:audio/mpeg;base64,${audioBase64}`;
        audioPlayer.src = audioData;
        audioPlayer.onended = () => {
            isAgentSpeaking = false;
            resolve();
        };
        audioPlayer.onerror = reject;
        audioPlayer.play().catch(err => {
            console.error('Error playing audio:', err);
            isAgentSpeaking = false;
            reject(err);
        });
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

    recordButton.classList.remove('monitoring', 'recording', 'in-call');

    switch (state) {
        case 'monitoring':
            recordButton.classList.add('in-call');
            buttonText.textContent = 'End Call';
            statusText.textContent = 'Monitoring...';
            statusIndicator.classList.add('active');
            break;
        case 'recording':
            recordButton.classList.add('in-call', 'recording');
            buttonText.textContent = 'End Call';
            statusText.textContent = 'Recording...';
            statusIndicator.classList.add('active');
            break;
        case 'processing':
            recordButton.classList.add('in-call');
            buttonText.textContent = 'End Call';
            statusText.textContent = 'Processing...';
            statusIndicator.classList.add('active');
            break;
        case 'agent-speaking':
            recordButton.classList.add('in-call');
            buttonText.textContent = 'End Call';
            statusText.textContent = 'Agent speaking...';
            statusIndicator.classList.add('active');
            break;
        case 'ready':
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
