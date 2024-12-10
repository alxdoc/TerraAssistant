// Главный класс голосового ассистента
class VoiceAssistant {
    constructor() {
        console.log('Initializing voice assistant...');
        this.isListening = false;
        this.hasPermission = false;
        
        try {
            // Проверяем поддержку Web Speech API
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (!SpeechRecognition) {
                console.error('Speech Recognition API не поддерживается');
                throw new Error('Speech Recognition API не поддерживается в этом браузере');
            }
            
            console.log('Speech Recognition API поддерживается, инициализация...');
            
            // Создаем экземпляр распознавания речи
            this.recognition = new SpeechRecognition();
            
            if (!this.recognition) {
                throw new Error('Не удалось создать экземпляр распознавания речи');
            }
            
            console.log('Recognition instance created successfully');
            
            // Настраиваем параметры
            this.recognition.lang = 'ru-RU';
            this.recognition.continuous = false;
            this.recognition.interimResults = false;
            this.recognition.maxAlternatives = 1;
            
            // Логируем конфигурацию
            console.log('Recognition configured with params:', {
                lang: this.recognition.lang,
                continuous: this.recognition.continuous,
                interimResults: this.recognition.interimResults,
                maxAlternatives: this.recognition.maxAlternatives
            });
            
            this.setupRecognition();
            
        } catch (error) {
            console.error('Constructor error:', error);
            this.updateStatus('Ошибка инициализации: ' + error.message, 'error');
            this.disableButtons();
        }
    }

    async initialize() {
        console.log('Initializing voice assistant...');
        try {
            const hasPermission = await this.checkMicrophonePermission();
            console.log('Microphone permission status:', hasPermission);
            
            if (hasPermission) {
                this.updateStatus('Готов к работе', 'ready');
                document.getElementById('startBtn').disabled = false;
                document.getElementById('stopBtn').disabled = true;
            } else {
                throw new Error('Нет разрешения на использование микрофона');
            }
        } catch (error) {
            console.error('Initialization error:', error);
            this.updateStatus('Ошибка инициализации: ' + error.message, 'error');
            this.disableButtons();
            
            this.displayResult({
                command_type: 'error',
                result: `Ошибка инициализации: ${error.message}. Пожалуйста, разрешите доступ к микрофону и перезагрузите страницу.`
            });
        }
    }

    async checkMicrophonePermission() {
        console.log('Checking microphone permission...');
        try {
            if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                throw new Error('API микрофона не поддерживается в этом браузере');
            }

            const stream = await navigator.mediaDevices.getUserMedia({ 
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true
                }
            });
            
            // Проверяем состояние треков
            const audioTracks = stream.getAudioTracks();
            if (audioTracks.length === 0) {
                throw new Error('Не удалось получить аудио трек');
            }
            
            // Останавливаем треки после проверки
            stream.getTracks().forEach(track => {
                track.stop();
                console.log('Track stopped:', track.kind);
            });
            
            this.hasPermission = true;
            console.log('Microphone permission granted and verified');
            return true;
        } catch (error) {
            console.error('Microphone permission error:', error);
            this.hasPermission = false;
            this.updateStatus('Нет доступа к микрофону: ' + error.message, 'error');
            
            this.displayResult({
                command_type: 'error',
                result: `Ошибка доступа к микрофону: ${error.message}. Пожалуйста, разрешите доступ к микрофону в настройках браузера.`
            });
            throw error;
        }
    }

    setupRecognition() {
        this.recognition.onstart = () => {
            console.log('Recognition started');
            this.isListening = true;
            this.updateStatus('Слушаю...', 'listening');
            
            const startBtn = document.getElementById('startBtn');
            const stopBtn = document.getElementById('stopBtn');
            
            if (startBtn && stopBtn) {
                startBtn.classList.add('listening');
                stopBtn.disabled = false;
            }
        };

        this.recognition.onend = () => {
            console.log('Recognition ended');
            this.isListening = false;
            
            const startBtn = document.getElementById('startBtn');
            const stopBtn = document.getElementById('stopBtn');
            
            if (startBtn && stopBtn) {
                startBtn.classList.remove('listening');
                startBtn.disabled = false;
                stopBtn.disabled = true;
            }
            
            if (!this.hasPermission) {
                this.updateStatus('Нет доступа к микрофону', 'error');
            } else {
                this.updateStatus('Готов к работе', 'ready');
            }
        };

        this.recognition.onresult = (event) => {
            try {
                console.log('Got recognition result:', event);
                
                if (event.results && event.results.length > 0) {
                    const result = event.results[event.results.length - 1];
                    
                    if (result.isFinal) {
                        const text = result[0].transcript.trim();
                        console.log('Recognized final text:', text);
                        
                        this.updateStatus('Текст распознан: ' + text, 'processing');
                        
                        if (text) {
                            // Показываем пользователю что текст распознан
                            this.displayResult({
                                command_type: 'info',
                                result: `Распознанный текст: ${text}`
                            });
                            
                            // Проверяем наличие ключевого слова
                            const terraRegex = /терра|terra/i;
                            if (terraRegex.test(text)) {
                                const command = text.replace(terraRegex, '').trim();
                                if (command) {
                                    this.processVoiceInput(text);
                                } else {
                                    this.updateStatus('Ожидание команды после слова "ТЕРРА"', 'ready');
                                }
                            } else {
                                this.updateStatus('Ожидание команды со словом "ТЕРРА"', 'ready');
                            }
                        }
                    }
                }
            } catch (error) {
                console.error('Error processing recognition result:', error);
                this.updateStatus('Ошибка обработки распознанной речи', 'error');
            }
        };

        this.recognition.onerror = (event) => {
            console.error('Recognition error:', event.error);
            this.isListening = false;
            
            let errorMessage = 'Ошибка распознавания речи';
            
            switch(event.error) {
                case 'not-allowed':
                    this.hasPermission = false;
                    errorMessage = 'Нет доступа к микрофону';
                    break;
                case 'no-speech':
                    errorMessage = 'Речь не обнаружена';
                    break;
                case 'network':
                    errorMessage = 'Проблема с сетью';
                    break;
                default:
                    errorMessage = `Ошибка: ${event.error}`;
            }
            
            this.updateStatus(errorMessage, 'error');
            
            const startBtn = document.getElementById('startBtn');
            if (startBtn) {
                startBtn.classList.remove('listening');
            }
            
            const stopBtn = document.getElementById('stopBtn');
            if (stopBtn) {
                stopBtn.disabled = true;
            }
        };
    }

    async start() {
        console.log('Starting recognition...');
        const startBtn = document.getElementById('startBtn');
        const stopBtn = document.getElementById('stopBtn');
        
        try {
            this.updateStatus('Запуск распознавания...', 'processing');
            
            if (!this.hasPermission) {
                await this.checkMicrophonePermission();
            }
            
            if (this.isListening) {
                await this.stop();
                await new Promise(resolve => setTimeout(resolve, 500));
            }
            
            await this.recognition.start();
            
            startBtn.disabled = true;
            stopBtn.disabled = false;
            startBtn.classList.add('listening');
            
            this.isListening = true;
            this.updateStatus('Слушаю...', 'listening');
            
        } catch (error) {
            console.error('Error starting recognition:', error);
            this.updateStatus('Ошибка запуска: ' + error.message, 'error');
            
            startBtn.disabled = false;
            startBtn.classList.remove('listening');
            stopBtn.disabled = true;
            
            this.displayResult({
                command_type: 'error',
                result: `Ошибка запуска распознавания: ${error.message}`
            });
        }
    }

    stop() {
        console.log('Stopping recognition...');
        if (this.isListening && this.recognition) {
            try {
                this.recognition.stop();
                console.log('Recognition stopped successfully');
                
                const startBtn = document.getElementById('startBtn');
                const stopBtn = document.getElementById('stopBtn');
                
                if (startBtn && stopBtn) {
                    startBtn.disabled = false;
                    startBtn.classList.remove('listening');
                    stopBtn.disabled = true;
                }
                
                this.isListening = false;
                this.updateStatus('Готов к работе', 'ready');
            } catch (error) {
                console.error('Error stopping recognition:', error);
                this.updateStatus('Ошибка при остановке распознавания', 'error');
            }
        }
    }

    disableButtons() {
        const startBtn = document.getElementById('startBtn');
        const stopBtn = document.getElementById('stopBtn');
        
        if (startBtn) startBtn.disabled = true;
        if (stopBtn) stopBtn.disabled = true;
    }

    updateStatus(status, type = 'info') {
        console.log('Status update:', status, type);
        const statusElement = document.getElementById('status');
        const statusIndicator = document.querySelector('.status-indicator');
        
        if (statusElement && statusIndicator) {
            statusElement.textContent = status;
            statusElement.className = `status-text ${type}`;
            
            statusIndicator.className = 'status-indicator';
            if (type === 'listening') {
                statusIndicator.classList.add('listening');
            }
        }
    }

    displayResult(result) {
        console.log('Displaying result:', result);
        const resultContainer = document.getElementById('result-container');
        if (!resultContainer) return;

        const resultElement = document.createElement('div');
        const isError = result.command_type === 'error' || result.error;
        
        const alertType = isError ? 'alert-danger' : 'alert-info';
        const icon = isError ? 
            '<i class="fas fa-exclamation-circle"></i>' : 
            '<i class="fas fa-check-circle"></i>';
        
        const resultText = isError ? 
            (result.error || 'Произошла ошибка при выполнении команды') :
            (result.result || 'Нет результата');

        resultElement.innerHTML = `
            <div class="alert ${alertType}">
                <div class="d-flex align-items-start">
                    ${icon}
                    <div class="flex-grow-1 ms-3">
                        <p>${resultText}</p>
                        <small class="text-muted">${new Date().toLocaleTimeString()}</small>
                    </div>
                </div>
            </div>
        `;
        
        if (resultContainer.firstChild) {
            resultContainer.insertBefore(resultElement.firstElementChild, resultContainer.firstChild);
        } else {
            resultContainer.appendChild(resultElement.firstElementChild);
        }

        // Ограничиваем количество отображаемых результатов
        const maxResults = 5;
        while (resultContainer.children.length > maxResults) {
            resultContainer.removeChild(resultContainer.lastChild);
        }
    }

    async processVoiceInput(text) {
        console.log('Processing voice input:', text);
        if (!text) {
            console.log('Empty text received');
            this.updateStatus('Пустой текст', 'error');
            return;
        }
        
        try {
            const response = await fetch('/process_command', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text: text })
            });
            
            if (!response.ok) {
                throw new Error(`Ошибка сервера: ${response.status}`);
            }
            
            const result = await response.json();
            console.log('Server response:', result);
            
            this.displayResult(result);
            this.updateStatus('Готов к работе', 'ready');
            
        } catch (error) {
            console.error('Error processing voice input:', error);
            this.updateStatus('Ошибка обработки команды: ' + error.message, 'error');
            
            this.displayResult({
                command_type: 'error',
                result: `Ошибка: ${error.message}`
            });
        }
    }
}

// Инициализация после загрузки страницы
document.addEventListener('DOMContentLoaded', () => {
    console.log('Document loaded, initializing voice assistant...');
    const assistant = new VoiceAssistant();
    
    const startBtn = document.getElementById('startBtn');
    const stopBtn = document.getElementById('stopBtn');
    
    if (!startBtn || !stopBtn) {
        console.error('Could not find microphone buttons');
        return;
    }
    
    // Добавляем обработчики событий для кнопок
    startBtn.addEventListener('click', async () => {
        console.log('Start button clicked');
        try {
            await assistant.start();
        } catch (error) {
            console.error('Error starting recognition:', error);
            assistant.updateStatus('Ошибка запуска: ' + error.message, 'error');
        }
    });
    
    stopBtn.addEventListener('click', () => {
        console.log('Stop button clicked');
        assistant.stop();
    });
    
    // Изначально деактивируем кнопку остановки
    stopBtn.disabled = true;
    
    // Инициализируем ассистента
    assistant.initialize();
});
