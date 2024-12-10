import os
import sys
import logging
from pathlib import Path
from datetime import datetime
import traceback

# Настройка логирования до импорта Flask
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

try:
    from flask import Flask, render_template, jsonify, request
    from flask_cors import CORS
    from models import db, Command, Task
    from utils.command_processor import process_command
    from utils.nlp import analyze_text, DialogContext
    
    # Инициализация глобального контекста диалога
    dialog_context = DialogContext()
    logger.info('Все необходимые модули успешно импортированы')
except Exception as e:
    logger.error('Ошибка при импорте модулей:', exc_info=True)
    sys.exit(1)

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
        logger.debug('Получен новый запрос на обработку команды')
        if not request.is_json:
            logger.warning('Получен запрос с неверным Content-Type')
            return jsonify({
                'status': 'error',
                'error': 'Content-Type должен быть application/json'
            }), 400
            
        text = request.json.get('text', '')
        logger.info(f'Получена команда: {text}')
        
        if not text:
            logger.warning('Получена пустая команда')
            return jsonify({
                'status': 'error',
                'error': 'Текст команды не может быть пустым'
            }), 400
            
        try:
            # Анализ текста команды
            command_type, entities = analyze_text(text)
            logger.info(f'Определен тип команды: {command_type}, сущности: {entities}')
            
            # Обработка команды
            result = process_command(command_type, entities)
            logger.info(f'Результат обработки команды: {result}')
            
            response = {
                'status': 'success',
                'command_type': command_type,
                'result': result,
                'timestamp': datetime.now().isoformat()
            }
            
            logger.debug(f'Отправка ответа: {response}')
            return jsonify(response)
            
        except Exception as command_error:
            logger.error('Ошибка при обработке команды:', exc_info=True)
            logger.error('Stacktrace: %s', traceback.format_exc())
            return jsonify({
                'status': 'error',
                'error': str(command_error),
                'details': traceback.format_exc()
            }), 500
            
    except Exception as e:
        logger.error('Критическая ошибка:', exc_info=True)
        logger.error('Stacktrace: %s', traceback.format_exc())
        return jsonify({
            'status': 'error',
            'error': str(e),
            'details': traceback.format_exc()
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
        
        # Проверяем доступность директории для базы данных
        if not os.path.exists(instance_path):
            try:
                os.makedirs(instance_path)
                logger.info(f'Создана директория для базы данных: {instance_path}')
            except Exception as e:
                logger.error(f'Не удалось создать директорию для базы данных: {str(e)}')
                raise
        
        # Инициализируем базу данных
        if not init_db():
            logger.error('Не удалось инициализировать базу данных')
            sys.exit(1)
        
        logger.info('База данных успешно инициализирована')
        logger.info('Запуск Flask сервера на порту 5000...')
        
        # Запускаем сервер
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            use_reloader=False,
            use_debugger=True,
            threaded=True
        )
    except Exception as e:
        logger.error(f'Критическая ошибка при запуске приложения:', exc_info=True)
        logger.error('Stacktrace: %s', traceback.format_exc())
        sys.exit(1)
