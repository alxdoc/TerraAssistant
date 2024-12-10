from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import logging

logger = logging.getLogger(__name__)
db = SQLAlchemy()

def init_db(app):
    """Initialize the database with the application"""
    try:
        logger.info("Initializing database...")
        db.init_app(app)
        
        # Создаем все таблицы в контексте приложения
        with app.app_context():
            db.create_all()
            logger.info("Database tables created successfully")
            
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}", exc_info=True)
        raise

class Command(db.Model):
    """Model for storing voice commands and their results"""
    __tablename__ = 'commands'
    
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500), nullable=False)
    command_type = db.Column(db.String(50))
    status = db.Column(db.String(20))
    result = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Command {self.id}: {self.command_type}>'

class Task(db.Model):
    """Model for storing tasks created by voice commands"""
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')
    category = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Task {self.id}: {self.title}>'
