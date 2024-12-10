import logging
from flask import render_template, jsonify, request
from utils.command_processor import process_command
from utils.nlp import analyze_text, DialogContext

# Настройка логирования
logger = logging.getLogger(__name__)

def register_routes(app):
    """Register all application routes"""
    # Создание глобального контекста диалога
    app.dialog_context = DialogContext()

    @app.route('/')
    def index():
        """Главная страница"""
        try:
            return render_template('index.html')
        except Exception as e:
            logger.error(f'Ошибка при рендеринге главной страницы: {e}')
            return "Ошибка загрузки страницы", 500

    @app.route('/process_command', methods=['POST'])
    def handle_command():
        """Обработка голосовой команды"""
        try:
            data = request.get_json()
            if not data or 'text' not in data:
                return jsonify({
                    'status': 'error',
                    'error': 'Текст команды не может быть пустым'
                }), 400
            
            text = data['text']
            logger.debug(f"Получена команда: {text}")
            
            # Анализ текста команды с учетом контекста
            command_type, entities = analyze_text(text, app.dialog_context)
            logger.debug(f"Определен тип команды: {command_type}, сущности: {entities}")
            
            # Обработка команды
            result = process_command(command_type, entities)
            logger.debug(f"Результат обработки команды: {result}")
            
            return jsonify({
                'status': 'success',
                'command_type': command_type,
                'result': result
            })
            
        except Exception as e:
            logger.error(f'Ошибка при обработке команды: {str(e)}', exc_info=True)
            return jsonify({
                'status': 'error',
                'error': str(e)
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

    logger.info('Routes registered successfully')
