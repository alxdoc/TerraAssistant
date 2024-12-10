class VoiceAssistant {
    constructor() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            console.error('Speech Recognition API not supported');
            this.updateStatus('Ваш браузер не поддерживает распознавание речи');
            document.getElementById('startBtn').disabled = true;
            document.getElementById('stopBtn').disabled = true;
            return;
        }
        console.log('Speech Recognition API supported');
        
        this.recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        this.recognition.lang = 'ru-RU';
        this.recognition.continuous = true;
        this.recognition.interimResults = false;
        this.isListening = false;
        this.hasPermission = false;
        this.setupRecognition();
        this.checkMicrophonePermission();
    }

    async checkMicrophonePermission() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            stream.getTracks().forEach(track => track.stop());
            this.hasPermission = true;
            this.updateStatus('Готов к работе');
        } catch (error) {
            console.error('Ошибка доступа к микрофону:', error);
            this.hasPermission = false;
            this.updateStatus('Нет доступа к микрофону');
        }
    }

    setupRecognition() {
        this.recognition.onstart = () => {
            this.updateStatus('Слушаю...');
            this.isListening = true;
            document.getElementById('startBtn').classList.add('listening');
        };

        this.recognition.onend = () => {
            document.getElementById('startBtn').classList.remove('listening');
            if (this.isListening && this.hasPermission) {
                setTimeout(() => {
                    try {
                        this.recognition.start();
                    } catch (error) {
                        console.error('Ошибка перезапуска распознавания:', error);
                        this.isListening = false;
                        this.updateStatus('Ошибка распознавания');
                    }
                }, 100);
            }
        };

        this.recognition.onresult = (event) => {
            const text = event.results[event.results.length - 1][0].transcript.trim().toLowerCase();
            this.processVoiceInput(text);
        };

        this.recognition.onerror = (event) => {
            console.error('Ошибка распознавания речи:', event.error);
            if (event.error === 'not-allowed') {
                this.hasPermission = false;
                this.isListening = false;
                this.updateStatus('Нет доступа к микрофону');
            } else {
                this.updateStatus(`Ошибка: ${event.error}`);
            }
        };

    async start() {
        console.log('Starting voice recognition...');
        console.log('Current state:', { hasPermission: this.hasPermission, isListening: this.isListening });
        
        if (!this.hasPermission) {
            console.log('Requesting microphone permission...');
            await this.checkMicrophonePermission();
        }
        
        if (this.hasPermission && !this.isListening) {
            try {
                console.log('Starting recognition service...');
                await this.recognition.start();
                this.updateStatus('Слушаю...');
            } catch (error) {
                console.error('Ошибка запуска распознавания:', error);
                this.updateStatus('Ошибка запуска. Попробуйте перезагрузить страницу');
                this.isListening = false;
            }
        } else if (!this.hasPermission) {
            console.log('No microphone permission');
            this.updateStatus('Пожалуйста, разрешите доступ к микрофону');
        } else {
            console.log('Recognition already active');
        }
    }

    stop() {
        this.isListening = false;
        try {
            this.recognition.stop();
            this.updateStatus('Ожидание');
            document.getElementById('startBtn').classList.remove('listening');
        } catch (error) {
            console.error('Ошибка остановки распознавания:', error);
        }
    }

    processVoiceInput(text) {
        if (text.includes('терра')) {
            const command = text.replace('терра', '').trim();
            if (command) {
                this.updateStatus('Обработка команды...');
                this.executeCommand(command);
            }
        }
    }

    async executeCommand(command) {
        try {
            const response = await fetch('/process_command', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text: command })
            });
            
            const result = await response.json();
            this.displayResult(result);
        } catch (error) {
            console.error('Error executing command:', error);
            this.updateStatus('Ошибка выполнения команды');
        }
    }

    updateStatus(status) {
        const statusElement = document.getElementById('status');
        statusElement.textContent = status;
    }

    displayResult(result) {
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
    console.log('Initializing Voice Assistant...');
    const assistant = new VoiceAssistant();
    
    const startButton = document.getElementById('startBtn');
    const stopButton = document.getElementById('stopBtn');
    
    if (!startButton || !stopButton) {
        console.error('Could not find microphone buttons');
        return;
    }
    
    startButton.addEventListener('click', async () => {
        console.log('Start button clicked');
        try {
            await assistant.start();
        } catch (error) {
            console.error('Error starting recognition:', error);
        }
    });
    
    stopButton.addEventListener('click', () => {
        console.log('Stop button clicked');
        try {
            assistant.stop();
        } catch (error) {
            console.error('Error stopping recognition:', error);
        }
    });
    
    console.log('Voice Assistant initialized');
});
