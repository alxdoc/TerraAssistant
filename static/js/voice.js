class VoiceAssistant {
    constructor() {
        console.log('Initializing voice assistant...');
        this.isListening = false;
        this.hasPermission = false;
        
        try {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (!SpeechRecognition) {
                throw new Error('Speech Recognition API not supported');
            }
            console.log('Speech Recognition API supported');
            
            this.recognition = new SpeechRecognition();
            this.recognition.lang = 'ru-RU';
            this.recognition.continuous = false;
            this.recognition.interimResults = false;
            
            this.setupRecognition();
            this.initialize();
        } catch (error) {
            console.error('Constructor error:', error);
            this.updateStatus('Ошибка инициализации: ' + error.message, 'error');
            this.disableButtons();
        }
    }

    disableButtons() {
        if (document.getElementById('startBtn')) {
            document.getElementById('startBtn').disabled = true;
        }
        if (document.getElementById('stopBtn')) {
            document.getElementById('stopBtn').disabled = true;
        }
    }

    async initialize() {
        console.log('Initializing voice assistant...');
        try {
            await this.checkMicrophonePermission();
            this.updateStatus('Готов к работе', 'ready');
            
            document.getElementById('startBtn').disabled = false;
            document.getElementById('stopBtn').disabled = true;
        } catch (error) {
            console.error('Initialization error:', error);
            this.updateStatus('Ошибка инициализации: ' + error.message, 'error');
            this.disableButtons();
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
        const startBtn = document.getElementById('startBtn');
        startBtn.disabled = true;
        document.getElementById('status').textContent = 'Инициализация...';
        
        try {
            if (!this.hasPermission) {
                console.log('Requesting microphone permission...');
                await this.checkMicrophonePermission();
            }
            
            if (this.isListening) {
                console.log('Already listening');
                return;
            }
            
            await this.recognition.start();
            console.log('Recognition started successfully');
            
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
        if (this.isListening && this.recognition) {
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
        if (!text) {
            console.log('Empty text received');
            return;
        }
        
        if (text.toLowerCase().includes('терра')) {
            const command = text.toLowerCase().replace('терра', '').trim();
            if (command) {
                console.log('Valid command detected:', command);
                this.updateStatus('Обработка команды...', 'processing');
                this.executeCommand(command);
            } else {
                console.log('Empty command after keyword');
                this.updateStatus('Команда не распознана', 'error');
                this.displayResult({
                    command_type: 'error',
                    result: 'Пожалуйста, произнесите команду после слова "ТЕРРА"'
                });
            }
        } else {
            console.log('Keyword "терра" not found in:', text);
            this.updateStatus('Ожидание команды', 'ready');
        }
    }

    async executeCommand(command) {
        console.log('Executing command:', command);
        try {
            this.updateStatus('Отправка команды...', 'processing');
            console.log('Sending request to server...');
            
            const response = await fetch('/process_command', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text: command })
            });
            
            console.log('Server response status:', response.status);
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error('Server error response:', errorText);
                throw new Error(`Ошибка сервера: ${response.status}`);
            }
            
            const result = await response.json();
            console.log('Command execution result:', result);
            
            if (result.status === 'error') {
                throw new Error(result.error || 'Неизвестная ошибка');
            }
            
            this.displayResult(result);
            this.updateStatus('Готов к работе', 'ready');
        } catch (error) {
            console.error('Error executing command:', error);
            this.updateStatus(`Ошибка: ${error.message}`, 'error');
            
            // Показываем ошибку пользователю
            this.displayResult({
                command_type: 'error',
                result: `Произошла ошибка: ${error.message}`
            });
        }
    }

    updateStatus(status, type = 'info') {
        console.log('Status update:', status, type);
        const statusElement = document.getElementById('status');
        const statusIndicator = document.querySelector('.status-indicator');
        
        if (statusElement && statusIndicator) {
            // Обновляем текст статуса с анимацией
            statusElement.style.opacity = '0';
            setTimeout(() => {
                statusElement.textContent = status;
                statusElement.className = `status-text ${type}`;
                statusElement.style.opacity = '1';
            }, 150);

            // Обновляем класс индикатора
            statusIndicator.className = 'status-indicator';
            if (type === 'listening') {
                statusIndicator.classList.add('listening');
            }
        }
    }

    displayResult(result) {
        console.log('Displaying result:', result);
        try {
            const resultContainer = document.getElementById('result-container');
            if (!resultContainer) {
                console.error('Result container not found');
                return;
            }

            // Создаем новый элемент результата
            const resultElement = document.createElement('div');
            
            // Определяем тип оповещения и иконку
            const alertType = result.status === 'error' ? 'alert-danger' : 'alert-info';
            const icon = result.status === 'error' ? 
                '<i class="fas fa-exclamation-circle"></i>' : 
                '<i class="fas fa-check-circle"></i>';
            
            // Форматируем тип команды для отображения
            const commandTypeDisplay = {
                'task_creation': 'Создание задачи',
                'document_analysis': 'Анализ документа',
                'search': 'Поиск',
                'report': 'Отчёт',
                'unknown': 'Неизвестная команда',
                'error': 'Ошибка'
            }[result.command_type] || result.command_type;

            // Создаем содержимое элемента
            resultElement.innerHTML = `
                <div class="d-flex align-items-start">
                    ${icon}
                    <div class="flex-grow-1">
                        <h5>${commandTypeDisplay}</h5>
                        <p>${result.result || 'Нет результата'}</p>
                        <small class="text-muted">${new Date().toLocaleTimeString()}</small>
                    </div>
                </div>
            `;

            // Устанавливаем классы для элемента
            resultElement.className = `alert ${alertType}`;
            
            // Добавляем элемент в начало контейнера
            if (resultContainer.firstChild) {
                resultContainer.insertBefore(resultElement, resultContainer.firstChild);
            } else {
                resultContainer.appendChild(resultElement);
            }

            // Запускаем анимацию появления
            // Важно: добавляем класс show в следующем кадре анимации
            requestAnimationFrame(() => {
                resultElement.classList.add('show');
            });

            // Удаляем старые результаты
            const maxResults = 5; // Ограничиваем количество отображаемых результатов
            const children = Array.from(resultContainer.children);
            if (children.length > maxResults) {
                children.slice(maxResults).forEach(oldResult => {
                    // Запускаем анимацию исчезновения
                    oldResult.classList.remove('show');
                    // Удаляем элемент после завершения анимации
                    oldResult.addEventListener('transitionend', function handler() {
                        oldResult.removeEventListener('transitionend', handler);
                        if (oldResult.parentNode === resultContainer) {
                            resultContainer.removeChild(oldResult);
                        }
                    });
                });
            }
        } catch (error) {
            console.error('Error displaying result:', error);
            this.updateStatus('Ошибка отображения результата', 'error');
        }
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
        try {
            await assistant.start();
        } catch (error) {
            console.error('Error in click handler:', error);
        }
    });
    
    stopButton.addEventListener('click', () => {
        console.log('Stop button clicked');
        try {
            assistant.stop();
        } catch (error) {
            console.error('Error in stop handler:', error);
        }
    });
});