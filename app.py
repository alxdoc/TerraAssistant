import os
import logging
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from models import db
from utils.command_processor import process_command
from utils.nlp import analyze_text

# Настройка логирования для отладки
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Создание и настройка приложения
app = Flask(__name__)
logger.info("Инициализация Flask приложения...")

# Конфигурация CORS
CORS(app, resources={r"/*": {"origins": "*"}})
logger.info("CORS настроен для всех маршрутов")

# Конфигурация базы данных
basedir = os.path.abspath(os.path.dirname(__file__))
app.config.update(
    SECRET_KEY=os.environ.get("FLASK_SECRET_KEY", "terra_assistant_key"),
    SQLALCHEMY_DATABASE_URI=f"sqlite:///{os.path.join(basedir, 'terra.db')}",
    SQLALCHEMY_TRACK_MODIFICATIONS=False
)
logger.info("Конфигурация базы данных завершена")

# Инициализация базы данных
db.init_app(app)

def init_db():
    """Инициализация базы данных"""
    try:
        with app.app_context():
            db.create_all()
            logger.info('База данных успешно инициализирована')
    except Exception as e:
        logger.error(f'Ошибка при инициализации базы данных: {e}')
        raise

@app.route('/')
def index():
    """Главная страница"""
    try:
        logger.debug('Обработка запроса к главной странице')
        return render_template('index.html')
    except Exception as e:
        logger.error(f'Ошибка при обработке главной страницы: {e}')
        return 'Internal Server Error', 500

@app.route('/process_command', methods=['POST', 'OPTIONS'])
def handle_command():
    """Обработка голосовой команды"""
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        logger.debug('Получен POST запрос к /process_command')
        logger.debug(f'Заголовки запроса: {dict(request.headers)}')
        logger.debug(f'Тело запроса: {request.get_data(as_text=True)}')
        
        if not request.is_json:
            logger.error('Получен не JSON запрос')
            return jsonify({
                'status': 'error',
                'error': 'Content-Type должен быть application/json'
            }), 400
            
        text = request.json.get('text', '')
        logger.debug(f'Текст команды: {text}')
        
        # Анализ текста команды
        command_type, entities = analyze_text(text)
        logger.debug(f'Тип команды: {command_type}, сущности: {entities}')
        
        # Обработка команды
        result = process_command(command_type, entities)
        logger.debug(f'Результат обработки: {result}')
        
        response = jsonify({
            'status': 'success',
            'command_type': command_type,
            'result': result
        })
        return response
        
    except Exception as e:
        logger.error(f'Ошибка при обработке команды: {e}', exc_info=True)
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

# Инициализация базы данных при создании приложения
init_db()

if __name__ == '__main__':
    logger.info("Запуск Flask сервера...")
    app.run(host='0.0.0.0', port=5000, debug=True)
