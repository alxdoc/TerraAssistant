import logging
import re
from datetime import datetime, timedelta
from typing import Dict

logger = logging.getLogger(__name__)

def format_task_creation(description: str) -> str:
    """Format task creation response with parsed details"""
    if not description:
        return "Пожалуйста, укажите описание задачи"
    
    logger.info(f"Начало обработки задачи. Исходный текст: '{description}'")
    
    # Проверяем наличие слов, указывающих на высокий приоритет
    original_text = description.lower()
    priority_words = ['срочн', 'срочная', 'срочную', 'важн', 'важная', 'важную', 'критичн']
    
    # Определяем приоритет
    priority = 'обычный'
    for word in priority_words:
        if word in original_text:
            priority = 'высокий'
            logger.info(f"Установлен высокий приоритет из-за слова '{word}'")
            break
    
    # Очищаем текст от служебных слов
    cleaners = [
        (r'терра\s*[,]?\s*', ''),
        (r'создай\s+', ''),
        (r'создать\s+', ''),
        (r'добавь\s+', ''),
        (r'добавить\s+', ''),
        (r'срочную?\s+', ''),
        (r'важную?\s+', ''),
        (r'критичную?\s+', ''),
        (r'задачу\s+', ''),
        (r'^[\s,\-–]+', ''),
        (r'[\s,\-–]+$', '')
    ]
    
    # Применяем очистку
    for pattern, replacement in cleaners:
        old_text = description
        description = re.sub(pattern, replacement, description, flags=re.IGNORECASE)
        if old_text != description:
            logger.info(f"Очистка текста: '{old_text}' -> '{description}'")
    
    # Обрабатываем дату и время
    task_date = None
    
    # Проверяем относительные даты
    date_words = {
        'завтра': timedelta(days=1),
        'послезавтра': timedelta(days=2),
        'через день': timedelta(days=1),
        'через неделю': timedelta(weeks=1),
        'через месяц': timedelta(days=30)
    }
    
    # Ищем дату
    for word, delta in date_words.items():
        if word in description.lower():
            task_date = datetime.now() + delta
            description = description.replace(word, '').strip()
            logger.info(f"Установлена дата: {task_date} (слово: {word})")
            break
    
    # Ищем время
    time_match = re.search(r'в\s+(\d{1,2})(?:[:.:](\d{2}))?\s*(?:час[оа]в?|час|ч)?', description)
    if time_match:
        hours = int(time_match.group(1))
        minutes = int(time_match.group(2)) if time_match.group(2) else 0
        
        if 0 <= hours <= 23 and 0 <= minutes <= 59:
            if task_date:
                task_date = task_date.replace(hour=hours, minute=minutes)
            else:
                task_date = datetime.now().replace(hour=hours, minute=minutes)
                if task_date < datetime.now():
                    task_date += timedelta(days=1)
            
            description = re.sub(r'в\s+\d{1,2}(?:[:.:]?\d{2})?\s*(?:час[оа]в?|час|ч)?\s*', '', description)
            logger.info(f"Установлено время: {hours}:{minutes:02d}")
    
    # Финальная очистка описания
    description = re.sub(r'\s+', ' ', description).strip()
    logger.info(f"Финальное описание: '{description}'")
    
    # Формируем ответ
    response_parts = [
        "✅ Создаю новую задачу:\n",
        f"📝 Описание: {description.capitalize()}"
    ]
    
    if task_date:
        date_format = '%d.%m.%Y в %H:%M' if task_date.hour != 0 or task_date.minute != 0 else '%d.%m.%Y'
        response_parts.append(f"📅 {'Дата и время' if 'в' in date_format else 'Дата'}: {task_date.strftime(date_format)}")
    
    response_parts.extend([
        f"⚡ Приоритет: {priority.capitalize()}",
        "✨ Задача успешно создана и добавлена в систему."
    ])
    
    return '\n'.join(response_parts)

class CommandProcessor:
    def __init__(self):
        self.context = {}
    
    def process_command(self, command_type: str, entities: Dict) -> str:
        """Process the command based on its type"""
        logger.info(f"Processing command of type: {command_type} with entities: {entities}")
        
        if command_type == 'greeting':
            return "Здравствуйте! Я - ваш бизнес-ассистент ТЕРРА. Чем могу помочь?"
        
        if command_type == 'task_creation':
            return format_task_creation(entities.get('description', ''))
        
        return "Извините, я не распознал команду. Пожалуйста, попробуйте переформулировать."

# Create a singleton instance
command_processor = CommandProcessor()

def process_command(command_type: str, entities: Dict) -> str:
    """Global function to process commands"""
    return command_processor.process_command(command_type, entities)