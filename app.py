import logging
import os
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from models import init_db, Command, db
from utils.command_processor import process_command
from utils.nlp import analyze_text, DialogContext

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def create_app():
    """Create and configure the Flask application"""
    try:
        logger.info("Starting Flask application creation...")
        
        # Создаем приложение Flask
        app = Flask(__name__)
        logger.debug("Flask application instance created")
        
        # Конфигурация приложения
        app.config.update(
            SECRET_KEY='dev-key-1234',
            SQLALCHEMY_DATABASE_URI=f'sqlite:///{os.path.join(app.instance_path, "terra.db")}',
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            TEMPLATES_AUTO_RELOAD=True
        )
        
        # Инициализация CORS
        CORS(app)
        
        # Создаем директорию instance если её нет
        os.makedirs(app.instance_path, exist_ok=True)
        
        # Инициализация базы данных
        init_db(app)
        
        # Инициализация контекста диалога
        app.dialog_context = DialogContext()
        
        logger.info("Application initialized successfully")

        @app.route('/')
        def index():
            """Главная страница"""
            try:
                logger.debug("Запрос главной страницы")
                return render_template('index.html')
            except Exception as e:
                logger.error(f'Ошибка при рендеринге главной страницы: {e}', exc_info=True)
                return "Ошибка загрузки страницы", 500

        @app.route('/process_command', methods=['POST'])
        def handle_command():
            """Обработка голосовой команды"""
            if not request.is_json:
                return jsonify({
                    'status': 'error',
                    'command_type': 'error',
                    'error': 'Ожидается JSON'
                }), 400

            data = request.get_json()
            if not data:
                return jsonify({
                    'status': 'error',
                    'command_type': 'error',
                    'error': 'Данные не могут быть пустыми'
                }), 400

            text = data.get('text', '').strip()
            if not text:
                return jsonify({
                    'status': 'error',
                    'command_type': 'error',
                    'error': 'Команда не может быть пустой'
                }), 400

            logger.info(f"Обработка команды: '{text}'")
            
            try:
                # Анализ команды
                command_type, entities = analyze_text(text, app.dialog_context)
                logger.info(f"Тип команды: {command_type}, сущности: {entities}")

                # Обработка команды
                result = process_command(command_type, entities)
                if not result:
                    return jsonify({
                        'status': 'error',
                        'command_type': command_type,
                        'error': 'Не удалось обработать команду'
                    }), 500

                # Сохранение результата в БД
                try:
                    command = Command(
                        text=text,
                        command_type=command_type,
                        status='completed',
                        result=result
                    )
                    db.session.add(command)
                    db.session.commit()
                    logger.info(f"Command saved to database: {command}")
                except Exception as db_error:
                    logger.error(f"Error saving to database: {db_error}")
                    db.session.rollback()

                return jsonify({
                    'status': 'success',
                    'command_type': command_type,
                    'result': result
                })

            except Exception as e:
                error_msg = str(e)
                logger.error(f"Ошибка при обработке команды: {error_msg}", exc_info=True)
                return jsonify({
                    'status': 'error',
                    'command_type': 'error',
                    'error': f'Ошибка: {error_msg}'
                }), 500

        @app.before_request
        def log_request_info():
            """Логирование информации о каждом запросе"""
            logger.debug('Headers: %s', request.headers)
            logger.debug('Body: %s', request.get_data())
            logger.debug('Path: %s', request.path)

        @app.after_request
        def after_request(response):
            """Добавляем необходимые заголовки для CORS"""
            logger.debug('Response Status: %s', response.status)
            logger.debug('Response Headers: %s', response.headers)
            return response

        @app.errorhandler(Exception)
        def handle_error(error):
            """Глобальный обработчик ошибок"""
            logger.error(f'Необработанная ошибка: {str(error)}', exc_info=True)
            return jsonify({
                'status': 'error',
                'message': 'Внутренняя ошибка сервера',
                'error': str(error)
            }), 500

        return app
        
    except Exception as e:
        logger.error(f"Failed to create application: {str(e)}", exc_info=True)
        raise
