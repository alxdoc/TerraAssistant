// Главный класс голосового ассистента
class VoiceAssistant {
    constructor() {
        console.log('Initializing voice assistant...');
        this.isListening = false;
        this.hasPermission = false;
        this.mediaRecorder = null;
        this.audioChunks = [];
        
        this.initialize();
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
            
            if (stream.getAudioTracks().length === 0) {
                throw new Error('Не удалось получить аудио трек');
            }
            
            // Останавливаем тестовый стрим
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
            
            // Проверяем поддерживаемые MIME типы
            const mimeType = this.getSupportedMimeType();
            console.log('Using MIME type:', mimeType);
            
            this.mediaRecorder = new MediaRecorder(stream, {
                mimeType: mimeType
            });
            
            this.mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    this.audioChunks.push(event.data);
                }
            };
            
            this.mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(this.audioChunks, { type: mimeType });
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

    getSupportedMimeType() {
        const types = [
            'audio/webm',
            'audio/webm;codecs=opus',
            'audio/ogg;codecs=opus',
            'audio/wav',
            'audio/mp4'
        ];
        
        for (const type of types) {
            if (MediaRecorder.isTypeSupported(type)) {
                return type;
            }
        }
        
        throw new Error('Не найден поддерживаемый формат аудио');
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
    
    startBtn.addEventListener('click', async () => {
        console.log('Start button clicked');
        try {
            await assistant.start();
        } catch (error) {
            console.error('Error starting recording:', error);
            assistant.updateStatus('Ошибка запуска: ' + error.message, 'error');
        }
    });
    
    stopBtn.addEventListener('click', () => {
        console.log('Stop button clicked');
        assistant.stop();
    });
    
    stopBtn.disabled = true;
});
