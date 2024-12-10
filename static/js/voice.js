class VoiceAssistant {
    constructor() {
        this.recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        this.recognition.lang = 'ru-RU';
        this.recognition.continuous = true;
        this.recognition.interimResults = false;
        this.isListening = false;
        this.setupRecognition();
    }

    setupRecognition() {
        this.recognition.onstart = () => {
            this.updateStatus('Слушаю...');
            this.isListening = true;
        };

        this.recognition.onend = () => {
            if (this.isListening) {
                this.recognition.start();
            }
        };

        this.recognition.onresult = (event) => {
            const text = event.results[event.results.length - 1][0].transcript.trim().toLowerCase();
            this.processVoiceInput(text);
        };

        this.recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            this.updateStatus('Ошибка распознавания');
        };
    }

    start() {
        if (!this.isListening) {
            this.recognition.start();
        }
    }

    stop() {
        this.isListening = false;
        this.recognition.stop();
        this.updateStatus('Ожидание');
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
    const assistant = new VoiceAssistant();
    
    document.getElementById('startBtn').addEventListener('click', () => {
        assistant.start();
    });
    
    document.getElementById('stopBtn').addEventListener('click', () => {
        assistant.stop();
    });
});
