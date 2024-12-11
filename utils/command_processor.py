import logging
import re
from datetime import datetime, timedelta
from typing import Dict

logger = logging.getLogger(__name__)

class CommandProcessor:
    def __init__(self):
        self.context = {}
    
    def process_command(self, command_type: str, entities: Dict) -> str:
        """Process the command based on its type and context"""
        logger.info(f"Processing command of type: {command_type} with entities: {entities}")
        
        try:
            # Приветствие с учетом времени суток
            if command_type == 'greeting':
                hour = datetime.now().hour
                greeting = (
                    "Доброе утро" if 5 <= hour < 12
                    else "Добрый день" if 12 <= hour < 17
                    else "Добрый вечер" if 17 <= hour < 23
                    else "Доброй ночи"
                )
                return f"{greeting}! Я - ваш бизнес-ассистент ТЕРРА. Чем могу помочь?"
            
            elif command_type == 'task_creation':
                return format_task_creation(entities.get('description', ''))
            
            # Обработка бизнес-команд
            business_commands = [
                'marketing', 'client', 'supplier', 'contract',
                'quality', 'risk', 'strategy', 'compliance',
                'innovation', 'document', 'search', 'contact',
                'project', 'analytics', 'employee'
            ]
            
            if command_type in business_commands:
                return format_business_command(command_type, entities.get('description', ''))
            
            return "Извините, я не распознал команду. Пожалуйста, попробуйте переформулировать."
            
        except Exception as e:
            logger.error(f"Error processing command: {str(e)}", exc_info=True)
            return f"Произошла ошибка при обработке команды: {str(e)}"

command_processor = CommandProcessor()

def process_command(command_type: str, entities: Dict) -> str:
    """Global function to process commands"""
    return command_processor.process_command(command_type, entities)

def format_task_creation(description: str) -> str:
    """Format task creation response with parsed details"""
    if not description:
        return "Пожалуйста, укажите описание задачи"

    logger.info(f"Исходный текст задачи: '{description}'")
    
    priority = 'высокий' if 'срочн' in description.lower() else 'обычный'
    logger.info(f"Определен приоритет: {priority}")
    
    cleaners = [
        r't?[еэ]рр?а?[,]?\s*',
        r'создай(?:те)?\s+',
        r'создать\s+',
        r'добавь(?:те)?\s+',
        r'добавить\s+',
        r'постав(?:ь|ите)?\s+',
        r'срочную?\s+',
        r'важную?\s+',
        r'критичную?\s+',
        r'задачу\s*',
        r'поручение\s*',
        r'^[\s,\-–]+',
        r'[\s,\-–]+$'
    ]
    
    for pattern in cleaners:
        old_text = description
        description = re.sub(pattern, '', description, flags=re.IGNORECASE)
        if old_text != description:
            logger.info(f"Применен паттерн очистки: '{pattern}' -> '{description}'")
    
    task_date = None
    date_words = {
        'завтра': timedelta(days=1),
        'послезавтра': timedelta(days=2),
        'через день': timedelta(days=1),
        'через неделю': timedelta(weeks=1),
        'через месяц': timedelta(days=30)
    }
    
    for word, delta in date_words.items():
        if word in description.lower():
            task_date = datetime.now() + delta
            description = description.replace(word, '').strip()
            logger.info(f"Найдена дата по слову '{word}': {task_date}")
            break
    
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
            logger.info(f"Найдено время: {hours}:{minutes:02d}")
    
    description = ' '.join(word for word in description.split() if word)
    description = description.rstrip('.')
    
    response_parts = [
        "✅ Создаю новую задачу:",
        f"\n📝 Описание: {description.capitalize()}"
    ]
    
    if task_date:
        date_format = '%d.%m.%Y в %H:%M' if task_date.hour != 0 or task_date.minute != 0 else '%d.%m.%Y'
        response_parts.append(f"\n📅 {'Дата и время' if 'в' in date_format else 'Дата'}: {task_date.strftime(date_format)}")
    
    response_parts.extend([
        f"\n⚡ Приоритет: {priority.capitalize()}",
        "\n✨ Задача успешно создана и добавлена в систему."
    ])
    
    return ''.join(response_parts)

def format_business_command(command_type: str, description: str) -> str:
    """Format business command response"""
    logger.info(f"Форматирование бизнес-команды типа: {command_type}")
    logger.debug(f"Исходное описание: '{description}'")
    
    if not description:
        logger.warning("Пустое описание команды")
        return f"Пожалуйста, укажите описание для команды типа {command_type}"
    
    responses = {
        'finance': {
            'icon': '💰',
            'action': 'Финансовая операция',
            'category': 'Финансы'
        },
        'marketing': {
            'icon': '📢',
            'action': 'Маркетинговая задача',
            'category': 'Маркетинг'
        },
        'project': {
            'icon': '📊',
            'action': 'Проектная задача',
            'category': 'Управление проектами'
        },
        'client': {
            'icon': '👥',
            'action': 'Работа с клиентом',
            'category': 'Клиенты'
        }
    }
    
    response_info = responses.get(command_type, {
        'icon': '📝',
        'action': 'Выполняю команду',
        'category': command_type.capitalize()
    })
    
    return (
        f"{response_info['icon']} {response_info['action']}:\n"
        f"📝 Описание: {description.capitalize()}\n"
        f"📁 Категория: {response_info['category']}\n"
        "✨ Задача успешно добавлена в систему."
    )