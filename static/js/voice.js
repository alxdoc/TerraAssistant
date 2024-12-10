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
            
            // Добавляем таймаут для автоматической остановки
            setTimeout(() => {
                if (this.isListening) {
                    console.log('Auto-stopping recognition after timeout');
                    this.stop();
                    // Автоматически перезапускаем прослушивание
                    setTimeout(() => {
                        if (!this.isListening) {
                            console.log('Auto-restarting recognition');
                            this.start();
                        }
                    }, 1000);
                }
            }, 30000); // 30 секунд на распознавание
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
                // Проверяем, не было ли ошибок при распознавании
                if (!document.querySelector('.status-text.error')) {
                    this.updateStatus('Готов к работе', 'ready');
                }
                
                // Автоматически перезапускаем распознавание после короткой задержки при ошибках
                setTimeout(() => {
                    if (startBtn && !startBtn.disabled && document.querySelector('.status-text.error')) {
                        this.initialize();
                    }
                }, 2000);
            }
        };

        this.recognition.onresult = (event) => {
            try {
                console.log('Got recognition result:', event);
                if (event.results && event.results.length > 0) {
                    const result = event.results[event.results.length - 1];
                    if (result.isFinal) {
                        const text = result[0].transcript.trim();
                        console.log('Recognized text:', text);
                        
                        if (text) {
                            console.log('Processing voice input:', text);
                            
                            // Проверяем наличие ключевого слова в любом регистре
                            const terraRegex = /терра|terra/i;
                            if (terraRegex.test(text)) {
                                // Извлекаем команду, убирая ключевое слово
                                const command = text.replace(terraRegex, '').trim();
                                console.log('Extracted command:', command);
                                
                                if (command) {
                                    this.processVoiceInput(text);
                                    // Автоматически продолжаем слушать
                                    setTimeout(() => {
                                        if (!this.isListening) {
                                            console.log('Restarting recognition after command');
                                            this.start();
                                        }
                                    }, 1000);
                                } else {
                                    console.log('Empty command after keyword');
                                    this.updateStatus('Ожидание команды после слова "ТЕРРА"', 'ready');
                                }
                            } else {
                                console.log('Keyword not found in:', text);
                                this.updateStatus('Ожидание команды со словом "ТЕРРА"', 'ready');
                            }
                        } else {
                            console.log('Empty recognition result');
                            this.updateStatus('Не удалось распознать речь', 'error');
                        }
                    }
                }
            } catch (error) {
                console.error('Error processing recognition result:', error);
                this.updateStatus('Ошибка обработки распознанной речи', 'error');
                
                // Восстанавливаем состояние и пробуем перезапустить
                this.isListening = false;
                document.getElementById('startBtn').disabled = false;
                document.getElementById('stopBtn').disabled = true;
                
                setTimeout(() => {
                    if (!this.isListening) {
                        console.log('Attempting to restart after error');
                        this.start();
                    }
                }, 2000);
            }
        };

        this.recognition.onerror = (event) => {
            console.error('Recognition error:', event.error, event);
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
            document.getElementById('startBtn').classList.remove('listening');
            document.getElementById('stopBtn').disabled = true;
        };
    }

    async start() {
        console.log('Starting recognition...');
        const startBtn = document.getElementById('startBtn');
        const stopBtn = document.getElementById('stopBtn');
        
        try {
            startBtn.disabled = true;
            this.updateStatus('Инициализация...', 'processing');
            
            if (!this.hasPermission) {
                console.log('Requesting microphone permission...');
                await this.checkMicrophonePermission();
            }
            
            if (this.isListening) {
                console.log('Already listening, stopping current session...');
                await this.stop();
                await new Promise(resolve => setTimeout(resolve, 500)); // Небольшая пауза
            }
            
            console.log('Starting new recognition session...');
            this.recognition.start();
            console.log('Recognition started successfully');
            
            this.isListening = true;
            stopBtn.disabled = false;
            startBtn.classList.add('listening');
            this.updateStatus('Слушаю...', 'listening');
            
        } catch (error) {
            console.error('Error starting recognition:', error);
            this.updateStatus('Ошибка запуска распознавания: ' + error.message, 'error');
            this.isListening = false;
            startBtn.disabled = false;
            startBtn.classList.remove('listening');
            stopBtn.disabled = true;
            
            // Пробуем перезапустить через небольшую паузу при определенных ошибках
            if (error.name === 'NotAllowedError' || error.name === 'NotFoundError') {
                setTimeout(() => this.initialize(), 2000);
            }
        }
    }

    stop() {
        console.log('Stopping recognition...');
        if (this.isListening && this.recognition) {
            try {
                this.recognition.stop();
                console.log('Recognition stopped successfully');
                
                // Восстанавливаем состояние кнопок
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

    processVoiceInput(text) {
        console.log('Processing voice input:', text);
        if (!text) {
            console.log('Empty text received');
            return;
        }
        
        // Нормализуем текст для более надежного распознавания
        const normalizedText = text.toLowerCase().trim();
        console.log('Normalized text:', normalizedText);
        
        // Проверяем наличие ключевого слова в любой форме
        if (normalizedText.includes('терра') || normalizedText.includes('terra')) {
            // Извлекаем команду, убирая все варианты ключевого слова
            let command = normalizedText
                .replace(/терра|terra/gi, '')
                .trim();
                
            console.log('Extracted command:', command);
            
            if (command) {
                console.log('Valid command detected:', command);
                const commandType = detectCommandType(command);
                console.log('Detected command type:', commandType);
                
                this.updateStatus('Обработка команды...', 'processing');
                this.executeCommand(command, commandType)
                    .then(() => {
                        // После успешной обработки команды автоматически возобновляем прослушивание
                        setTimeout(() => {
                            if (!this.isListening) {
                                console.log('Auto-restarting listening after command processing');
                                this.start();
                            }
                        }, 1000);
                    })
                    .catch(error => {
                        console.error('Command execution error:', error);
                        this.updateStatus('Ошибка при выполнении команды', 'error');
                        // Также пробуем перезапустить прослушивание после ошибки
                        setTimeout(() => {
                            if (!this.isListening) {
                                this.start();
                            }
                        }, 2000);
                    });
            } else {
                console.log('Empty command after keyword');
                this.updateStatus('Команда не распознана', 'error');
                this.displayResult({
                    command_type: 'error',
                    result: 'Пожалуйста, произнесите команду после слова "ТЕРРА"'
                });
                // Перезапускаем прослушивание после ошибки
                setTimeout(() => {
                    if (!this.isListening) {
                        this.start();
                    }
                }, 2000);
            }
        } else {
            console.log('Keyword not found in:', normalizedText);
            this.updateStatus('Ожидание команды со словом "ТЕРРА"', 'ready');
            // Продолжаем слушать, если ключевое слово не найдено
            if (!this.isListening) {
                setTimeout(() => this.start(), 1000);
            }
        }
    }

    async executeCommand(command, commandType) {
        console.log('Executing command:', command);
        console.log('Command type:', commandType);
        try {
            this.updateStatus('Отправка команды...', 'processing');
            console.log('Sending request to server...');
            
            const response = await fetch('/process_command', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    text: command,
                    command_type: commandType
                })
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
            
            // Определяем статус результата
            const isError = result.status === 'error' || result.error;
            
            // Определяем тип оповещения и иконку
            const alertType = isError ? 'alert-danger' : 'alert-info';
            const icon = isError ? 
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
            }[result.command_type] || 'Команда';

            // Определяем текст результата
            let resultText = isError ? 
                (result.error || 'Произошла ошибка при выполнении команды') :
                (result.result || 'Нет результата');

            // Создаем содержимое элемента
            resultElement.innerHTML = `
                <div class="d-flex align-items-start">
                    ${icon}
                    <div class="flex-grow-1">
                        <h5>${commandTypeDisplay}</h5>
                        <p>${resultText}</p>
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