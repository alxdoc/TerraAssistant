from flask import Flask, render_template, jsonify, request
import logging
import os
import openai
import tempfile

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Настройка OpenAI API
openai.api_key = os.environ.get('OPENAI_API_KEY')

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dev-key-1234'
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Ограничение размера файла: 16MB
    
    @app.route('/')
    def index():
        """Render the main page"""
        return render_template('index.html')
    
    @app.route('/process_audio', methods=['POST'])
    def process_audio():
        """Process audio file using Whisper API"""
        try:
            if 'audio' not in request.files:
                return jsonify({
                    'status': 'error',
                    'command_type': 'error',
                    'result': 'Аудио файл не найден'
                }), 400
            
            audio_file = request.files['audio']
            
            # Сохраняем временный файл
            with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as tmp_file:
                audio_file.save(tmp_file.name)
                tmp_file_path = tmp_file.name
            
            try:
                # Отправляем файл в Whisper API
                with open(tmp_file_path, 'rb') as audio:
                    logger.info("Sending audio to Whisper API")
                    transcript = openai.Audio.transcribe(
                        file=audio,
                        model="whisper-1",
                        language="ru"
                    )
                
                # Получаем распознанный текст
                text = transcript.text.lower().strip()
                logger.info(f"Whisper API response: {text}")
                
                # Обрабатываем команду
                if 'терра' in text or 'terra' in text:
                    return jsonify({
                        'status': 'success',
                        'command_type': 'greeting',
                        'result': 'Здравствуйте! Я ТЕРРА, ваш голосовой ассистент. Чем могу помочь?'
                    })
                else:
                    return jsonify({
                        'status': 'success',
                        'command_type': 'echo',
                        'result': f'Для активации скажите "ТЕРРА" и вашу команду'
                    })
                
            finally:
                # Удаляем временный файл
                os.unlink(tmp_file_path)
            
        except Exception as e:
            logger.error(f"Error processing audio: {str(e)}")
            return jsonify({
                'status': 'error',
                'command_type': 'error',
                'result': 'Произошла ошибка при обработке аудио'
            }), 500
    
    return app