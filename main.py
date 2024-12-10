import logging
from app import app, init_db

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        # Инициализация базы данных
        init_db()
        
        # Запуск сервера
        logger.info("Запуск Flask сервера на порту 5000...")
        app.run(host="0.0.0.0", port=5000, debug=True)
    except Exception as e:
        logger.error(f"Ошибка при запуске сервера: {e}", exc_info=True)
        raise
