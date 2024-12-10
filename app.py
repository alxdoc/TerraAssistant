import os
import logging
from flask import Flask, render_template, jsonify, request
from models import db
from utils.command_processor import process_command
from utils.nlp import analyze_text

# Настройка логирования для отладки
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Инициализация Flask приложения
app = Flask(__name__)

# Конфигурация базы данных
basedir = os.path.abspath(os.path.dirname(__file__))
app.config.update(
    SECRET_KEY=os.environ.get("FLASK_SECRET_KEY", "terra_assistant_key"),
    SQLALCHEMY_DATABASE_URI=f"sqlite:///{os.path.join(basedir, 'terra.db')}",
    SQLALCHEMY_TRACK_MODIFICATIONS=False
)

# Инициализация базы данных
db.init_app(app)

# Логирование успешной инициализации
logger.info('Flask application initialized successfully')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_command', methods=['POST'])
def handle_command():
    text = request.json.get('text', '')
    
    # Analyze the command text
    command_type, entities = analyze_text(text)
    
    # Process the command and get results
    result = process_command(command_type, entities)
    
    return jsonify({
        'status': 'success',
        'command_type': command_type,
        'result': result
    })

# Создание таблиц базы данных
with app.app_context():
    db.create_all()
