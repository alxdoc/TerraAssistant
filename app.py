from flask import Flask, render_template, jsonify, request
import logging

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dev-key-1234'
    
    @app.route('/')
    def index():
        """Render the main page"""
        return render_template('index.html')
    
    @app.route('/process_command', methods=['POST'])
    def process_command():
        """Process voice commands"""
        try:
            data = request.get_json()
            if not data or 'text' not in data:
                return jsonify({'error': 'No text provided'}), 400
            
            text = data['text'].lower()
            logger.info(f"Received command: {text}")
            
            # Базовая обработка команды
            if 'терра' in text or 'terra' in text:
                return jsonify({
                    'status': 'success',
                    'command_type': 'greeting',
                    'result': 'Здравствуйте! Я ТЕРРА, ваш голосовой ассистент. Чем могу помочь?'
                })
            else:
                return jsonify({
                    'status': 'success',
                    'command_type': 'echo',
                    'result': f'Для активации скажите "ТЕРРА" и вашу команду'
                })
            
        except Exception as e:
            logger.error(f"Error processing command: {str(e)}")
            return jsonify({
                'status': 'error',
                'command_type': 'error',
                'result': 'Произошла ошибка при обработке команды'
            }), 500
    
    return app