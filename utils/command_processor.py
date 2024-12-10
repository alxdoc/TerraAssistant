import logging
from typing import Dict
from datetime import datetime
from models import db, Command, Task

# Настройка логирования
logger = logging.getLogger(__name__)

def process_command(command_type: str, entities: Dict) -> str:
    """
    Обрабатывает команду определенного типа и возвращает результат
    """
    try:
        if command_type == 'task_creation':
            result = create_task(entities)
        elif command_type == 'document_analysis':
            result = analyze_document(entities)
        elif command_type == 'search':
            result = perform_search(entities)
        elif command_type == 'report':
            result = generate_report()
        else:
            result = "Команда не распознана"
            
        if not result:
            result = "Команда выполнена, но результат пуст"
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Ошибка при обработке команды {command_type}: {str(e)}")
        result = f"Произошла ошибка при выполнении команды: {str(e)}"
    
    # Сохраняем команду в базу данных
    save_command(command_type, result)
    
    return result

def create_task(entities: Dict) -> str:
    """
    Создает новую задачу
    """
    description = entities.get('description', 'Новая задача')
    
    task = Task(
        title=description[:200],
        description=description,
        category='voice_created'
    )
    
    db.session.add(task)
    db.session.commit()
    
    return f"Создана новая задача: {description}"

def analyze_document(entities: Dict) -> str:
    """
    Имитирует анализ документа
    """
    doc_type = entities.get('document_type', 'документ')
    return f"Начат анализ документа типа '{doc_type}'. Это может занять некоторое время."

def perform_search(entities: Dict) -> str:
    """
    Выполняет поиск по заданному запросу
    """
    query = entities.get('search_query', '')
    if not query:
        return "Не указан поисковый запрос"
    
    # Здесь может быть реальная логика поиска
    return f"Выполняется поиск по запросу: {query}"

def generate_report() -> str:
    """
    Генерирует простой отчет о задачах
    """
    tasks = Task.query.all()
    total_tasks = len(tasks)
    pending_tasks = len([t for t in tasks if t.status == 'pending'])
    
    return f"Всего задач: {total_tasks}, Ожидающих: {pending_tasks}"

def save_command(command_type: str, result: str) -> None:
    """
    Сохраняет выполненную команду в базу данных
    """
    command = Command(
        text=result,
        command_type=command_type,
        status='completed',
        result=result
    )
    
    db.session.add(command)
    db.session.commit()
