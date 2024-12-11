import logging
import os
import tempfile
from flask import Flask, render_template, jsonify, request
from openai import OpenAI
from flask_cors import CORS
from utils.nlp import DialogContext
from utils.command_processor import process_command
from models import init_db

# Настройка логирования для внешних библиотек
logging.getLogger('werkzeug').setLevel(logging.INFO)
logging.getLogger('sqlalchemy').setLevel(logging.WARNING)

# Настройка логирования для внешних библиотек
logging.getLogger('werkzeug').setLevel(logging.INFO)
logging.getLogger('sqlalchemy').setLevel(logging.WARNING)

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Настройка OpenAI API
client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    try:
        # Конфигурация приложения
        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-1234')
        app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Ограничение размера файла: 16MB
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/terra.db'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        # Инициализация CORS
        CORS(app)
        
        # Инициализация базы данных
        init_db(app)
        
        # Создаем глобальный объект для хранения контекста диалога
        app.dialog_context = DialogContext()
        
        logger.info("Application initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing application: {str(e)}")
        raise

    @app.route('/')
    def index():
        """Render the main page"""
        return render_template('index.html')
    
    @app.route('/process_audio', methods=['POST'])
    def process_audio():
        """Process audio file using Whisper API"""
        tmp_file_path = None
        try:
            logger.debug("Processing audio request")
            
            if 'audio' not in request.files:
                logger.warning("No audio file in request")
                return jsonify({
                    'status': 'error',
                    'command_type': 'error',
                    'result': 'Аудио файл не найден'
                }), 400
            
            audio_file = request.files['audio']
            if not audio_file.filename:
                logger.warning("Empty audio filename")
                return jsonify({
                    'status': 'error',
                    'command_type': 'error',
                    'result': 'Пустой аудио файл'
                }), 400
            
            # Сохраняем временный файл
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as tmp_file:
                    logger.debug(f"Saving temporary file: {tmp_file.name}")
                    audio_file.save(tmp_file.name)
                    tmp_file_path = tmp_file.name
            except Exception as e:
                logger.error(f"Error saving temporary file: {str(e)}")
                return jsonify({
                    'status': 'error',
                    'command_type': 'error',
                    'result': 'Ошибка при сохранении аудио файла'
                }), 500
            
            try:
                # Отправляем файл в Whisper API
                with open(tmp_file_path, 'rb') as audio:
                    logger.info("Sending audio to Whisper API")
                    transcript = client.audio.transcriptions.create(
                        file=audio,
                        model="whisper-1",
                        language="ru"
                    )
                
                # Получаем распознанный текст
                text = transcript.text.lower().strip()
                logger.info(f"Whisper API response: {text}")
                
                # Анализируем текст и получаем тип команды
                command_type, entities = app.dialog_context.analyze_text(text)
                logger.info(f"Распознан тип команды: {command_type}, сущности: {entities}")
                
                # Обрабатываем команду через процессор команд
                result = process_command(command_type, entities)
                logger.info(f"Результат обработки команды: {result}")
                
                return jsonify({
                    'status': 'success',
                    'command_type': command_type,
                    'result': result
                })
                
            except Exception as e:
                logger.error(f"Error processing audio with Whisper API: {str(e)}")
                return jsonify({
                    'status': 'error',
                    'command_type': 'error',
                    'result': 'Ошибка при распознавании речи'
                }), 500
            
        except Exception as e:
            logger.error(f"Unexpected error processing audio: {str(e)}")
            return jsonify({
                'status': 'error',
                'command_type': 'error',
                'result': 'Произошла неожиданная ошибка при обработке аудио'
            }), 500
            
        finally:
            # Удаляем временный файл
            if tmp_file_path and os.path.exists(tmp_file_path):
                try:
                    os.unlink(tmp_file_path)
                    logger.debug(f"Temporary file removed: {tmp_file_path}")
                except Exception as e:
                    logger.error(f"Error removing temporary file: {str(e)}")
    
    return app
