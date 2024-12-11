from flask import Flask
import logging
import os

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Проверяем наличие переменных окружения
if not os.environ.get('OPENAI_API_KEY'):
    logger.error("OPENAI_API_KEY не найден в переменных окружения")
    raise ValueError("OPENAI_API_KEY обязателен для работы приложения")

try:
    from app import create_app
    logger.info("Импорт create_app успешен")
except Exception as e:
    logger.error(f"Ошибка при импорте create_app: {str(e)}")
    raise

if __name__ == "__main__":
    try:
        logger.info("Инициализация приложения...")
        app = create_app()
        logger.info("Приложение создано успешно")
        
        app.run(host='0.0.0.0', port=5000, debug=True)
    except Exception as e:
        logger.error(f"Ошибка запуска сервера: {str(e)}", exc_info=True)
        raise
