import logging
import sys
import os
from flask import Flask
from flask_cors import CORS
from models import init_db

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    """Create and configure the Flask application"""
    try:
        # Создание приложения
        app = Flask(__name__)
        CORS(app)

        # Настройка логирования для Flask
        app.logger.setLevel(logging.DEBUG)

        # Создаем директорию для базы данных
        instance_path = os.path.join(os.getcwd(), 'instance')
        os.makedirs(instance_path, exist_ok=True)

        # Конфигурация
        app.config.update(
            SECRET_KEY=os.environ.get('SECRET_KEY', 'terra_assistant_key'),
            SQLALCHEMY_DATABASE_URI=f'sqlite:///{os.path.join(instance_path, "terra.db")}',
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            TEMPLATES_AUTO_RELOAD=True,
            CORS_HEADERS='Content-Type'
        )

        # Инициализация базы данных
        with app.app_context():
            init_db(app)
            logger.info("Database initialized successfully")

        # Регистрация маршрутов
        from app import register_routes
        register_routes(app)
        logger.info("Routes registered successfully")

        return app

    except Exception as e:
        logger.error(f"Failed to create application: {str(e)}", exc_info=True)
        raise

def main():
    try:
        app = create_app()
        logger.info("Starting the Flask server...")
        app.run(host='0.0.0.0', port=5000, debug=True)
    except Exception as e:
        logger.error(f"Failed to start the server: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
