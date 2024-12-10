import logging
import os
from app import create_app
from models import init_db

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    try:
        logger.info("Starting application initialization...")
        
        # Создание и настройка приложения
        app = create_app()
        logger.debug("Application instance created")
        
        # Создание директории для базы данных
        instance_path = os.path.join(os.getcwd(), 'instance')
        os.makedirs(instance_path, exist_ok=True)
        logger.debug(f"Instance directory created at: {instance_path}")
        
        # Конфигурация базы данных и приложения
        database_uri = f'sqlite:///{os.path.join(instance_path, "terra.db")}'
        logger.debug(f"Database URI: {database_uri}")
        
        app.config.update(
            SECRET_KEY=os.environ.get('SECRET_KEY', 'terra_assistant_key'),
            SQLALCHEMY_DATABASE_URI=database_uri,
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            TEMPLATES_AUTO_RELOAD=True,
            CORS_HEADERS='Content-Type'
        )
        logger.debug("Application configuration updated")
        
        # Инициализация базы данных
        with app.app_context():
            init_db(app)
            logger.info("Database initialized successfully")
        
        logger.info("Starting the Flask server on port 5000...")
        app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
    except Exception as e:
        logger.error(f"Failed to start the server: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main()
