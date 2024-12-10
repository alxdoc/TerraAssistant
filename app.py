import os
import logging
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from models import db, Command, Task
from utils.command_processor import process_command
from utils.nlp import analyze_text, DialogContext

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Инициализация глобального контекста диалога
dialog_context = DialogContext()

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Создание и настройка приложения
app = Flask(__name__)

# Конфигурация CORS
CORS(app)

# Конфигурация базы данных
app.config.update(
    SECRET_KEY="terra_assistant_key",
    SQLALCHEMY_DATABASE_URI="sqlite:///terra.db",
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    TEMPLATES_AUTO_RELOAD=True,
    CORS_HEADERS='Content-Type')

# Инициализация базы данных
db.init_app(app)

def init_db():
    """Инициализация базы данных"""
    try:
        logger.debug('Начало инициализации базы данных...')
        if not os.path.exists(instance_path):
            logger.error(f'Директория {instance_path} не существует')
            return False
            
        with app.app_context():
            logger.debug('Проверка соединения с базой данных...')
            db.engine.connect()
            logger.debug('Соединение с базой данных успешно')
            
            logger.debug('Создание всех таблиц...')
            db.create_all()
            logger.info('База данных успешно инициализирована')
            return True
    except Exception as e:
        logger.error(f'Ошибка при инициализации базы данных: {str(e)}', exc_info=True)
        return False

@app.route('/')
def index():
    """Главная страница"""
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f'Ошибка при рендеринге главной страницы: {e}')
        return "Ошибка загрузки страницы", 500

@app.route('/process_command', methods=['POST'])
def handle_command():
    """Обработка голосовой команды"""
    try:
        text = request.json.get('text', '')
        if not text:
            return jsonify({
                'status': 'error',
                'error': 'Текст команды не может быть пустым'
            }), 400
            
        # Анализ текста команды с учетом контекста
        command_type, entities = analyze_text(text, dialog_context)
        
        # Обработка команды
        result = process_command(command_type, entities)
        
        return jsonify({
            'status': 'success',
            'command_type': command_type,
            'result': result,
            'timestamp': datetime.now().isoformat()
        })
            
    except Exception as e:
        logger.error(f'Ошибка при обработке команды: {str(e)}')
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.errorhandler(Exception)
def handle_error(error):
    logger.error(f'Необработанная ошибка: {str(error)}', exc_info=True)
    return jsonify({
        'status': 'error',
        'message': 'Внутренняя ошибка сервера',
        'error': str(error)
    }), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
