import logging
import os
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from models import db, Command
from utils.command_processor import process_command
from utils.nlp import analyze_text, DialogContext

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    """Create and configure the Flask application"""
    try:
        logger.info("Starting application creation...")
        app = Flask(__name__, static_folder='static', template_folder='templates')
        logger.debug("Flask app instance created")
        
        # Базовая конфигурация
        app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-1234')
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/terra.db'
        logger.debug("Basic configuration set")
        
        # Инициализация CORS
        CORS(app)
        logger.debug("CORS initialized")
        
        # Инициализация базы данных
        db.init_app(app)
        with app.app_context():
            db.create_all()
            logger.info("Database initialized")
        
        # Создание глобального контекста диалога
        app.dialog_context = DialogContext()
        logger.debug("Dialog context created")
        
        # Настройка логирования для Flask
        if not app.debug:
            file_handler = logging.FileHandler('app.log')
            file_handler.setLevel(logging.WARNING)
            app.logger.addHandler(file_handler)
            logger.debug("File logging handler added")

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
            try:
                logger.info("Получен POST запрос на /process_command")
                
                # Проверка наличия данных и формата
                if not request.is_json:
                    logger.warning("Получен не JSON запрос")
                    return jsonify({
                        'status': 'error',
                        'command_type': 'error',
                        'error': 'Ожидается JSON'
                    }), 400

                data = request.get_json()
                logger.info(f"Полученные данные: {data}")

                if not data:
                    logger.warning("Получены пустые данные")
                    return jsonify({
                        'status': 'error',
                        'command_type': 'error',
                        'error': 'Данные не могут быть пустыми'
                    }), 400

                if 'text' not in data:
                    logger.warning("Отсутствует поле 'text' в данных")
                    return jsonify({
                        'status': 'error',
                        'command_type': 'error',
                        'error': 'Отсутствует текст команды'
                    }), 400
                
                text = str(data['text']).strip()
                logger.info(f"Получена команда: '{text}'")
                
                if not text:
                    logger.warning("Получен пустой текст команды")
                    return jsonify({
                        'status': 'error',
                        'command_type': 'error',
                        'error': 'Команда не может быть пустой'
                    }), 400

                # Анализ текста команды с учетом контекста
                try:
                    command_type, entities = analyze_text(text, app.dialog_context)
                    logger.info(f"Определен тип команды: {command_type}, сущности: {entities}")
                except Exception as analyze_error:
                    logger.error(f"Ошибка при анализе текста: {str(analyze_error)}", exc_info=True)
                    return jsonify({
                        'status': 'error',
                        'command_type': 'error',
                        'error': 'Ошибка при анализе команды'
                    }), 500
                
                # Обработка команды
                try:
                    result = process_command(command_type, entities)
                    logger.info(f"Результат обработки команды: {result}")
                    
                    if not result:
                        logger.warning("Получен пустой результат обработки команды")
                        return jsonify({
                            'status': 'error',
                            'command_type': command_type,
                            'error': 'Не удалось обработать команду'
                        }), 500
                except Exception as process_error:
                    logger.error(f"Ошибка при обработке команды: {str(process_error)}", exc_info=True)
                    return jsonify({
                        'status': 'error',
                        'command_type': command_type,
                        'error': 'Ошибка при обработке команды'
                    }), 500

                # Сохраняем команду в базу данных
                try:
                    command = Command(
                        text=text,
                        command_type=command_type,
                        status='completed',
                        result=result
                    )
                    db.session.add(command)
                    db.session.commit()
                    logger.debug("Команда успешно сохранена в БД")
                except Exception as db_error:
                    logger.error(f"Ошибка при сохранении команды в БД: {db_error}", exc_info=True)
                    # Продолжаем выполнение, так как сохранение в БД не критично для работы
                
                return jsonify({
                    'status': 'success',
                    'command_type': command_type,
                    'result': result
                })
                
            except Exception as e:
                logger.error(f'Ошибка при обработке команды: {str(e)}', exc_info=True)
                return jsonify({
                    'status': 'error',
                    'error': f'Ошибка обработки команды: {str(e)}'
                }), 500

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
