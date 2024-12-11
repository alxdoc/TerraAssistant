let mediaRecorder;
let audioChunks = [];
let isRecording = false;

document.addEventListener('DOMContentLoaded', () => {
    const startBtn = document.getElementById('startBtn');
    const stopBtn = document.getElementById('stopBtn');
    const status = document.getElementById('status');
    const resultContainer = document.getElementById('result-container');

    // Инициализация кнопок
    stopBtn.disabled = true;

    startBtn.addEventListener('click', startRecording);
    stopBtn.addEventListener('click', stopRecording);

    async function startRecording() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            
            mediaRecorder.ondataavailable = (event) => {
                audioChunks.push(event.data);
            };

            mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                await sendAudioToServer(audioBlob);
                audioChunks = [];
            };

            mediaRecorder.start();
            isRecording = true;
            
            // Обновляем UI
            startBtn.disabled = true;
            stopBtn.disabled = false;
            status.textContent = 'Запись...';
            status.style.color = 'var(--bs-danger)';
            
        } catch (err) {
            console.error('Ошибка при начале записи:', err);
            status.textContent = 'Ошибка доступа к микрофону';
        }
    }

    function stopRecording() {
        if (mediaRecorder && isRecording) {
            mediaRecorder.stop();
            isRecording = false;
            
            // Останавливаем все треки
            mediaRecorder.stream.getTracks().forEach(track => track.stop());
            
            // Обновляем UI
            startBtn.disabled = false;
            stopBtn.disabled = true;
            status.textContent = 'Обработка...';
            status.style.color = 'var(--bs-warning)';
        }
    }

    async function sendAudioToServer(audioBlob) {
        try {
            const formData = new FormData();
            formData.append('audio', audioBlob);

            const response = await fetch('/process_audio', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();
            
            // Обновляем UI в зависимости от результата
            status.textContent = 'Готово';
            status.style.color = 'var(--bs-success)';
            
            // Создаем и добавляем новый результат
            const resultElement = document.createElement('div');
            resultElement.className = 'result-item mb-3 p-3 border rounded';
            
            if (result.status === 'success') {
                resultElement.innerHTML = `
                    <div class="command-type text-muted small">Тип команды: ${result.command_type}</div>
                    <div class="command-result">${result.result}</div>
                `;
            } else {
                resultElement.innerHTML = `
                    <div class="text-danger">${result.result}</div>
                `;
            }
            
            resultContainer.insertBefore(resultElement, resultContainer.firstChild);
            
        } catch (err) {
            console.error('Ошибка при отправке аудио:', err);
            status.textContent = 'Ошибка при обработке';
            status.style.color = 'var(--bs-danger)';
            
            const errorElement = document.createElement('div');
            errorElement.className = 'result-item mb-3 p-3 border rounded';
            errorElement.innerHTML = `
                <div class="text-danger">Произошла ошибка при обработке аудио</div>
            `;
            resultContainer.insertBefore(errorElement, resultContainer.firstChild);
        }
    }
});
