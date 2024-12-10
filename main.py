import logging
import os
import logging
import os
from app import create_app

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    try:
        logger.info("Starting application initialization...")
        
        # Создаем директорию для базы данных
        instance_path = os.path.join(os.getcwd(), 'instance')
        os.makedirs(instance_path, exist_ok=True)
        
        # Создаем и настраиваем приложение
        app = create_app()
        
        # Запускаем сервер с явными настройками для Replit
        logger.info("Starting the Flask server on port 5000...")
        app.run(
            host='0.0.0.0',  # Разрешаем внешние подключения
            port=5000,       # Используем порт 5000
            debug=True,      # Включаем режим отладки
            use_reloader=True  # Включаем автоперезагрузку
        )
        
    except Exception as e:
        logger.error(f"Failed to start the server: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main()
