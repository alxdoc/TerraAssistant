import os
import logging
from flask import Flask, render_template, jsonify, request
from models import db
from utils.command_processor import process_command
from utils.nlp import analyze_text

# Настройка логирования для отладки
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    try:
        # Инициализация Flask приложения
        app = Flask(__name__)
        
        # Конфигурация базы данных
        basedir = os.path.abspath(os.path.dirname(__file__))
        app.config.update(
            SECRET_KEY=os.environ.get("FLASK_SECRET_KEY", "terra_assistant_key"),
            SQLALCHEMY_DATABASE_URI=f"sqlite:///{os.path.join(basedir, 'terra.db')}",
            SQLALCHEMY_TRACK_MODIFICATIONS=False
        )
        
        # Инициализация базы данных
        db.init_app(app)
        logger.info("База данных успешно инициализирована")

        # Маршруты
        @app.route('/')
        def index():
            try:
                logger.debug('Обработка запроса к главной странице')
                return render_template('index.html')
            except Exception as e:
                logger.error(f'Ошибка при обработке главной страницы: {e}')
                return 'Internal Server Error', 500

        @app.route('/process_command', methods=['POST'])
        def handle_command():
            try:
                logger.debug('Получен POST запрос к /process_command')
                text = request.json.get('text', '')
                logger.debug(f'Текст команды: {text}')
                
                # Анализ текста команды
                command_type, entities = analyze_text(text)
                logger.debug(f'Тип команды: {command_type}, сущности: {entities}')
                
                # Обработка команды
                result = process_command(command_type, entities)
                logger.debug(f'Результат обработки: {result}')
                
                return jsonify({
                    'status': 'success',
                    'command_type': command_type,
                    'result': result
                })
            except Exception as e:
                logger.error(f'Ошибка при обработке команды: {e}')
                return jsonify({
                    'status': 'error',
                    'error': str(e)
                }), 500

        # Создание таблиц базы данных
        with app.app_context():
            db.create_all()
            logger.info('База данных инициализирована')

        logger.info('Flask приложение успешно создано')
        return app

    except Exception as e:
        logger.error(f'Ошибка при создании приложения: {e}')
        raise

# Создание экземпляра приложения
app = create_app()
