import os
import sys
import logging
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from models import db, Command, Task
from utils.command_processor import process_command
from utils.nlp import analyze_text

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Создание и настройка приложения
app = Flask(__name__)

# Конфигурация CORS
CORS(app)

# Конфигурация базы данных
basedir = os.path.abspath(os.path.dirname(__file__))
instance_path = os.path.join(basedir, 'instance')

# Создаем директорию для базы данных, если её нет
try:
    Path(instance_path).mkdir(parents=True, exist_ok=True)
    logger.info(f'Директория для базы данных создана: {instance_path}')
except Exception as e:
    logger.error(f'Не удалось создать директорию для базы данных: {str(e)}')
    sys.exit(1)

app.config.update(
    SECRET_KEY=os.environ.get("FLASK_SECRET_KEY", "terra_assistant_key"),
    SQLALCHEMY_DATABASE_URI=f"sqlite:///{os.path.join(instance_path, 'terra.db')}",
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

@app.route('/process_command', methods=['POST', 'OPTIONS'])
def handle_command():
    """Обработка голосовой команды"""
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        if not request.is_json:
            return jsonify({
                'status': 'error',
                'error': 'Content-Type должен быть application/json'
            }), 400
            
        text = request.json.get('text', '')
        logger.info(f'Получена команда: {text}')
        
        # Анализ текста команды
        command_type, entities = analyze_text(text)
        logger.info(f'Определен тип команды: {command_type}')
        
        # Обработка команды
        result = process_command(command_type, entities)
        
        return jsonify({
            'status': 'success',
            'command_type': command_type,
            'result': result,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f'Ошибка при обработке команды: {str(e)}', exc_info=True)
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
    try:
        logger.info('Запуск приложения...')
        if not init_db():
            logger.error('Не удалось инициализировать базу данных')
            exit(1)
            
        logger.info('Запуск Flask сервера на порту 5000...')
        app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
    except Exception as e:
        logger.error(f'Критическая ошибка при запуске приложения: {str(e)}', exc_info=True)
        exit(1)
