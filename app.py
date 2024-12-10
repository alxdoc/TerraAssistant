import os
import logging
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
CORS(app)

# Конфигурация базы данных
basedir = os.path.abspath(os.path.dirname(__file__))
app.config.update(
    SECRET_KEY=os.environ.get("FLASK_SECRET_KEY", "terra_assistant_key"),
    SQLALCHEMY_DATABASE_URI=f"sqlite:///{os.path.join(basedir, 'terra.db')}",
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    TEMPLATES_AUTO_RELOAD=True
)

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

if __name__ == '__main__':
    try:
        logger.info('Запуск приложения...')
        init_db()
        logger.info('Запуск Flask сервера на порту 5000...')
        app.run(host='0.0.0.0', port=5000, debug=True)
    except Exception as e:
        logger.error(f'Критическая ошибка при запуске приложения: {e}', exc_info=True)
        raise
