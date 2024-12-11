import os
import logging
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
        app = Flask(__name__, 
                   static_folder='static',
                   template_folder='templates')
        
        # Конфигурация приложения
        app.config.update(
            SECRET_KEY=os.environ.get('SECRET_KEY', 'dev-key-1234'),
            SQLALCHEMY_DATABASE_URI=f'sqlite:///{os.path.join(os.getcwd(), "instance", "terra.db")}',
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            TEMPLATES_AUTO_RELOAD=True
        )
        
        # Инициализация CORS
        CORS(app)
        
        # Создаем директорию instance если её нет
        os.makedirs(os.path.join(os.getcwd(), 'instance'), exist_ok=True)
        
        # Инициализация базы данных
        init_db(app)
        
        # Инициализация контекста диалога
        app.dialog_context = DialogContext()
        
        @app.route('/')
        def index():
            """Главная страница"""
            try:
                return render_template('index.html')
            except Exception as e:
                logger.error(f'Error rendering index page: {str(e)}', exc_info=True)
                return "Internal Server Error", 500

        @app.route('/process_command', methods=['POST'])
        def handle_command():
            """Обработка голосовой команды"""
            try:
                if not request.is_json:
                    return jsonify({
                        'status': 'error',
                        'command_type': 'error',
                        'error': 'Требуется JSON запрос'
                    }), 400

                data = request.get_json()
                text = data.get('text', '').strip()
                
                if not text:
                    return jsonify({
                        'status': 'error',
                        'command_type': 'error',
                        'error': 'Пожалуйста, произнесите команду'
                    }), 400

                logger.info(f"Processing command: '{text}'")
                command_type, entities = analyze_text(text, app.dialog_context)
                result = process_command(command_type, entities)

                if not result:
                    return jsonify({
                        'status': 'error',
                        'command_type': command_type,
                        'error': 'Не удалось выполнить команду'
                    }), 500

                try:
                    command = Command(
                        text=text,
                        command_type=command_type,
                        status='completed',
                        result=result
                    )
                    db.session.add(command)
                    db.session.commit()
                except Exception as db_error:
                    logger.error(f"Database error: {str(db_error)}", exc_info=True)
                    db.session.rollback()

                return jsonify({
                    'status': 'success',
                    'command_type': command_type,
                    'result': result
                })

            except Exception as e:
                logger.error(f"Command processing error: {str(e)}", exc_info=True)
                return jsonify({
                    'status': 'error',
                    'command_type': 'error',
                    'error': str(e)
                }), 500

        @app.errorhandler(404)
        def not_found_error(error):
            return jsonify({'error': 'Not found'}), 404

        @app.errorhandler(500)
        def internal_error(error):
            db.session.rollback()
            return jsonify({'error': 'Internal server error'}), 500

        return app

    except Exception as e:
        logger.error(f"Application creation failed: {str(e)}", exc_info=True)
        raise
