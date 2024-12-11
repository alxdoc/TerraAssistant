import logging
import os
from dotenv import load_dotenv

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Загружаем переменные окружения из .env файла
load_dotenv()

# Проверяем наличие переменных окружения
required_env_vars = ['OPENAI_API_KEY']
missing_vars = [var for var in required_env_vars if not os.getenv(var)]

if missing_vars:
    logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
    raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

# Проверяем наличие переменных окружения
if not os.getenv('OPENAI_API_KEY'):
    logger.error("OPENAI_API_KEY не найден в переменных окружения")
    raise ValueError("OPENAI_API_KEY обязателен для работы приложения")

try:
    from app import create_app
    logger.info("Импорт create_app успешен")
except Exception as e:
    logger.error(f"Ошибка при импорте create_app: {str(e)}", exc_info=True)
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
