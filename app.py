import os
import logging
from flask import Flask, render_template, jsonify, request
from models import db
from utils.command_processor import process_command
from utils.nlp import analyze_text

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or "terra_assistant_key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///terra.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
db.init_app(app)

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

with app.app_context():
    db.create_all()
