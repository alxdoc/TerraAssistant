// Главный класс голосового ассистента
class VoiceAssistant {
    constructor() {
        console.log('Initializing voice assistant...');
        this.isListening = false;
        this.hasPermission = false;
        this.mediaRecorder = null;
        this.audioChunks = [];
        
        try {
            // Проверяем поддержку MediaRecorder API
            if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                console.error('MediaRecorder API не поддерживается');
                throw new Error('MediaRecorder API не поддерживается в этом браузере');
            }
            
            console.log('MediaRecorder API поддерживается, инициализация...');
            
            this.initialize();
            
        } catch (error) {
            console.error('Constructor error:', error);
            this.updateStatus('Ошибка инициализации: ' + error.message, 'error');
            this.disableButtons();
        }
    }
            
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

    async setupMediaRecorder() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ 
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true
                }
            });
            
            this.mediaRecorder = new MediaRecorder(stream);
            
            this.mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    this.audioChunks.push(event.data);
                }
            };
            
            this.mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
                this.audioChunks = [];
                
                this.updateStatus('Обработка аудио...', 'processing');
                await this.sendAudioToServer(audioBlob);
            };
            
            this.hasPermission = true;
            this.updateStatus('Готов к работе', 'ready');
            
        } catch (error) {
            console.error('MediaRecorder setup error:', error);
            this.hasPermission = false;
            this.updateStatus('Ошибка доступа к микрофону: ' + error.message, 'error');
            throw error;
        }
    }

    async sendAudioToServer(audioBlob) {
        try {
            const formData = new FormData();
            formData.append('audio', audioBlob, 'recording.webm');
            
            const response = await fetch('/process_audio', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            this.displayResult(result);
            
        } catch (error) {
            console.error('Error sending audio:', error);
            this.updateStatus('Ошибка отправки аудио: ' + error.message, 'error');
            this.displayResult({
                command_type: 'error',
                result: `Ошибка обработки аудио: ${error.message}`
            });
        }
    }

    async start() {
        console.log('Starting recording...');
        const startBtn = document.getElementById('startBtn');
        const stopBtn = document.getElementById('stopBtn');
        
        try {
            this.updateStatus('Запуск записи...', 'processing');
            
            if (!this.hasPermission || !this.mediaRecorder) {
                await this.setupMediaRecorder();
            }
            
            if (this.isListening) {
                await this.stop();
                await new Promise(resolve => setTimeout(resolve, 500));
            }
            
            this.audioChunks = [];
            this.mediaRecorder.start();
            
            startBtn.disabled = true;
            stopBtn.disabled = false;
            startBtn.classList.add('listening');
            
            this.isListening = true;
            this.updateStatus('Запись...', 'listening');
            
        } catch (error) {
            console.error('Error starting recording:', error);
            this.updateStatus('Ошибка запуска: ' + error.message, 'error');
            
            startBtn.disabled = false;
            startBtn.classList.remove('listening');
            stopBtn.disabled = true;
            
            this.displayResult({
                command_type: 'error',
                result: `Ошибка запуска записи: ${error.message}`
            });
        }
    }

    stop() {
        console.log('Stopping recording...');
        if (this.isListening && this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
            try {
                this.mediaRecorder.stop();
                console.log('Recording stopped successfully');
                
                const startBtn = document.getElementById('startBtn');
                const stopBtn = document.getElementById('stopBtn');
                
                if (startBtn && stopBtn) {
                    startBtn.disabled = false;
                    startBtn.classList.remove('listening');
                    stopBtn.disabled = true;
                }
                
                this.isListening = false;
                this.updateStatus('Обработка записи...', 'processing');
            } catch (error) {
                console.error('Error stopping recording:', error);
                this.updateStatus('Ошибка при остановке записи', 'error');
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
            this.displayResult({
                command_type: 'error',
                result: 'Пожалуйста, произнесите команду'
            });
            return;
        }
        
        try {
            this.updateStatus('Обработка команды...', 'processing');
            console.log('Sending request to server with text:', text);
            
            const response = await fetch('/process_command', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text: text })
            });
            
            console.log('Server response status:', response.status);
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error('Server error response:', errorText);
                throw new Error(`Ошибка сервера ${response.status}: ${errorText}`);
            }
            
            const result = await response.json();
            console.log('Server response data:', result);
            
            if (result.error) {
                throw new Error(result.error);
            }
            
            this.displayResult(result);
            this.updateStatus('Команда обработана', 'success');
            setTimeout(() => this.updateStatus('Готов к работе', 'ready'), 2000);
            
        } catch (error) {
            console.error('Error processing voice input:', error);
            const errorMessage = error.message || 'Неизвестная ошибка';
            this.updateStatus('Ошибка: ' + errorMessage, 'error');
            
            this.displayResult({
                command_type: 'error',
                result: `Не удалось обработать команду: ${errorMessage}`
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
