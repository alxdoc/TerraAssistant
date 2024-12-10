class VoiceAssistant {
    constructor() {
        console.log('Initializing voice assistant...');
        
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            console.error('Speech Recognition API not supported');
            this.updateStatus('Ваш браузер не поддерживает распознавание речи', 'error');
            document.getElementById('startBtn').disabled = true;
            document.getElementById('stopBtn').disabled = true;
            return;
        }
        console.log('Speech Recognition API supported');
        
        this.recognition = new SpeechRecognition();
        this.recognition.lang = 'ru-RU';
        this.recognition.continuous = false;
        this.recognition.interimResults = false;
        this.isListening = false;
        this.hasPermission = false;
        
        this.setupRecognition();
        this.initialize();
    }

    async initialize() {
        console.log('Initializing voice assistant...');
        try {
            // Check if the browser supports speech recognition
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (!SpeechRecognition) {
                throw new Error('Speech Recognition API not supported');
            }

            // Initialize recognition
            this.recognition = new SpeechRecognition();
            this.recognition.lang = 'ru-RU';
            this.recognition.continuous = false;
            this.recognition.interimResults = false;

            // Setup event handlers
            this.setupRecognition();

            // Check microphone permission
            await this.checkMicrophonePermission();
            this.updateStatus('Готов к работе', 'ready');
            
            // Enable start button
            document.getElementById('startBtn').disabled = false;
            document.getElementById('stopBtn').disabled = true;
        } catch (error) {
            console.error('Initialization error:', error);
            this.updateStatus('Ошибка инициализации: ' + error.message, 'error');
            document.getElementById('startBtn').disabled = true;
            document.getElementById('stopBtn').disabled = true;
        }
    }

    async checkMicrophonePermission() {
        console.log('Checking microphone permission...');
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            stream.getTracks().forEach(track => track.stop());
            this.hasPermission = true;
            console.log('Microphone permission granted');
            return true;
        } catch (error) {
            console.error('Microphone permission error:', error);
            this.hasPermission = false;
            this.updateStatus('Нет доступа к микрофону', 'error');
            throw error;
        }
    }

    setupRecognition() {
        this.recognition.onstart = () => {
            console.log('Recognition started');
            this.isListening = true;
            this.updateStatus('Слушаю...', 'listening');
            document.getElementById('startBtn').classList.add('listening');
            document.getElementById('stopBtn').disabled = false;
        };

        this.recognition.onend = () => {
            console.log('Recognition ended');
            this.isListening = false;
            document.getElementById('startBtn').classList.remove('listening');
            document.getElementById('stopBtn').disabled = true;
            
            if (!this.hasPermission) {
                this.updateStatus('Нет доступа к микрофону', 'error');
            } else {
                this.updateStatus('Готов к работе', 'ready');
            }
        };

        this.recognition.onresult = (event) => {
            console.log('Got recognition result');
            const text = event.results[event.results.length - 1][0].transcript.trim().toLowerCase();
            console.log('Recognized text:', text);
            this.processVoiceInput(text);
        };

        this.recognition.onerror = (event) => {
            console.error('Recognition error:', event.error);
            this.isListening = false;
            
            if (event.error === 'not-allowed') {
                this.hasPermission = false;
                this.updateStatus('Нет доступа к микрофону', 'error');
            } else {
                this.updateStatus(`Ошибка: ${event.error}`, 'error');
            }
            
            document.getElementById('startBtn').classList.remove('listening');
            document.getElementById('stopBtn').disabled = true;
        };
    }

    async start() {
        console.log('Starting recognition...');
        
        // Disable start button while we check permissions
        const startBtn = document.getElementById('startBtn');
        startBtn.disabled = true;
        
        try {
            // Always check permission before starting
            if (!this.hasPermission) {
                console.log('Requesting microphone permission...');
                await this.checkMicrophonePermission();
            }
            
            if (this.isListening) {
                console.log('Already listening');
                return;
            }
            
            // Start recognition
            await this.recognition.start();
            console.log('Recognition started successfully');
            
            // Update UI
            document.getElementById('stopBtn').disabled = false;
            startBtn.classList.add('listening');
            this.updateStatus('Слушаю...', 'listening');
        } catch (error) {
            console.error('Error starting recognition:', error);
            this.updateStatus('Ошибка запуска распознавания: ' + error.message, 'error');
            this.isListening = false;
            startBtn.disabled = false;
            startBtn.classList.remove('listening');
            document.getElementById('stopBtn').disabled = true;
        }
    }

    stop() {
        console.log('Stopping recognition...');
        if (this.isListening) {
            try {
                this.recognition.stop();
                console.log('Recognition stopped successfully');
            } catch (error) {
                console.error('Error stopping recognition:', error);
            }
        }
    }

    processVoiceInput(text) {
        console.log('Processing voice input:', text);
        if (text.includes('терра')) {
            const command = text.replace('терра', '').trim();
            if (command) {
                this.updateStatus('Обработка команды...', 'processing');
                this.executeCommand(command);
            }
        }
    }

    async executeCommand(command) {
        console.log('Executing command:', command);
        try {
            const response = await fetch('/process_command', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text: command })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            console.log('Command execution result:', result);
            this.displayResult(result);
            this.updateStatus('Готов к работе', 'ready');
        } catch (error) {
            console.error('Error executing command:', error);
            this.updateStatus('Ошибка выполнения команды', 'error');
        }
    }

    updateStatus(status, type = 'info') {
        console.log('Status update:', status, type);
        const statusElement = document.getElementById('status');
        if (statusElement) {
            statusElement.textContent = status;
            statusElement.className = `status-text ${type}`;
        }
    }

    displayResult(result) {
        console.log('Displaying result:', result);
        const resultContainer = document.getElementById('result-container');
        const resultElement = document.createElement('div');
        resultElement.className = 'alert alert-info mt-3';
        resultElement.innerHTML = `
            <h5>Тип команды: ${result.command_type}</h5>
            <p>${result.result}</p>
        `;
        resultContainer.prepend(resultElement);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    console.log('Document loaded, initializing voice assistant...');
    const assistant = new VoiceAssistant();
    
    const startButton = document.getElementById('startBtn');
    const stopButton = document.getElementById('stopBtn');
    
    if (!startButton || !stopButton) {
        console.error('Could not find microphone buttons');
        return;
    }
    
    stopButton.disabled = true;
    
    startButton.addEventListener('click', async () => {
        console.log('Start button clicked');
        startButton.disabled = true;
        try {
            await assistant.start();
        } catch (error) {
            console.error('Error starting recognition:', error);
            startButton.disabled = false;
        }
    });
    
    stopButton.addEventListener('click', () => {
        console.log('Stop button clicked');
        try {
            assistant.stop();
            startButton.disabled = false;
        } catch (error) {
            console.error('Error stopping recognition:', error);
        }
    });
    
    console.log('Voice assistant initialized');
});
