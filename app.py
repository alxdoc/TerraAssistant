import os
import logging
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from models import db, Command, Task  # Добавляем импорт моделей
from utils.command_processor import process_command
from utils.nlp import analyze_text

# Настройка логирования для отладки
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

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
        logger.info('Начало инициализации базы данных...')
        with app.app_context():
            # Проверяем существование таблиц
            logger.debug('Проверка существующих таблиц...')
            inspector = db.inspect(db.engine)
            existing_tables = inspector.get_table_names()
            logger.debug(f'Существующие таблицы: {existing_tables}')
            
            # Создаем таблицы
            logger.debug('Создание таблиц...')
            db.create_all()
            
            # Проверяем созданные таблицы
            new_tables = inspector.get_table_names()
            logger.debug(f'Таблицы после создания: {new_tables}')
            
            logger.info('База данных успешно инициализирована')
    except Exception as e:
        logger.error(f'Ошибка при инициализации базы данных: {e}', exc_info=True)
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
        logger.info('Начало обработки голосовой команды')
        
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
        try:
            result = process_command(command_type, entities)
            logger.debug(f'Результат обработки: {result}')
            
            response = jsonify({
                'status': 'success',
                'command_type': command_type,
                'result': result,
                'timestamp': datetime.now().isoformat()
            })
            return response
        except Exception as e:
            logger.error(f'Ошибка при обработке команды: {str(e)}')
            return jsonify({
                'status': 'error',
                'error': 'Ошибка при обработке команды: ' + str(e)
            }), 500
        
    except Exception as e:
        logger.error(f'Ошибка при обработке команды: {e}', exc_info=True)
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

# Примечание: init_db() будет вызываться из main.py

if __name__ == '__main__':
    logger.info("Запуск Flask сервера...")
    app.run(host='0.0.0.0', port=5000, debug=True)
