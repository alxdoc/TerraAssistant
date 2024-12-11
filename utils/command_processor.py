import logging
import re
from datetime import datetime, timedelta
from typing import Dict

logger = logging.getLogger(__name__)

def format_task_creation(description: str) -> str:
    """Format task creation response with parsed details"""
    if not description:
        return "Пожалуйста, укажите описание задачи"

    # Логируем исходный текст
    logger.info(f"Исходный текст задачи: '{description}'")
    
    # Проверяем приоритет по наличию слова "срочн"
    priority = 'высокий' if 'срочн' in description.lower() else 'обычный'
    logger.info(f"Определен приоритет: {priority}")
    
    # Шаг 2: Очищаем текст от служебных слов
    cleaners = [
        r't?[еэ]рр?а?[,]?\s*',  # Улучшенное распознавание вариаций "тера/терра"
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
    
    # Очищаем текст
    for pattern in cleaners:
        old_text = description
        description = re.sub(pattern, '', description, flags=re.IGNORECASE)
        if old_text != description:
            logger.info(f"Применен паттерн очистки: '{pattern}' -> '{description}'")
    
    # Шаг 3: Обработка даты и времени
    task_date = None
    
    # Поиск даты
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
    
    # Поиск времени
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
    
    # Шаг 4: Финальная очистка описания
    description = ' '.join(word for word in description.split() if word)
    # Удаляем точку в конце, если она есть
    description = description.rstrip('.')
    logger.info(f"Финальное описание: '{description}'")
    
    # Шаг 5: Формируем ответ
    response_parts = [
        "✅ Создаю новую задачу:",
        f"\n📝 Описание: {description.capitalize()}",
    ]
    
    if task_date:
        date_format = '%d.%m.%Y в %H:%M' if task_date.hour != 0 or task_date.minute != 0 else '%d.%m.%Y'
        response_parts.append(f"\n📅 {'Дата и время' if 'в' in date_format else 'Дата'}: {task_date.strftime(date_format)}")
    
    response_parts.extend([
        f"\n⚡ Приоритет: {priority.capitalize()}",
        "\n✨ Задача успешно создана и добавлена в систему."
    ])
    
    return ''.join(response_parts)

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
            
        # Обработка бизнес-команд
        business_commands = [
            'marketing', 'client', 'supplier', 'contract',
            'quality', 'risk', 'strategy', 'compliance',
            'innovation', 'document', 'search', 'contact',
            'project', 'analytics', 'employee'  # Добавляем новые типы команд
        ]
        
        if command_type in business_commands:
            return format_business_command(command_type, entities.get('description', ''))
        
        return "Извините, я не распознал команду. Пожалуйста, попробуйте переформулировать."

# Create a singleton instance
command_processor = CommandProcessor()

def format_business_command(command_type: str, description: str) -> str:
    """Format business command response with extended functionality"""
    logger.info(f"Форматирование бизнес-команды типа: {command_type}")
    logger.debug(f"Исходное описание: '{description}'")
    
    if not description:
        logger.warning("Пустое описание команды")
        return f"Пожалуйста, укажите описание для команды типа {command_type}"
    
    # Очищаем описание от служебных слов
    cleaners = [
        r't?[еэ]рр?а?[,]?\s*',
        r'создай(?:те)?\s+',
        r'создать\s+',
        r'нов(?:ый|ую|ое)\s+',
        r'показать\s+',
        r'покажи\s+',
        r'подготовить\s+',
        r'запусти(?:ть)?\s+',
        r'начать\s+',
        r'установить\s+',
        r'назначить\s+',
        r'добавить\s+',
        r'^[\s,\-–]+',
        r'[\s,\-–]+$'
    ]
    
    for pattern in cleaners:
        old_desc = description
        description = re.sub(pattern, '', description, flags=re.IGNORECASE)
        if old_desc != description:
            logger.debug(f"Применен паттерн '{pattern}': '{old_desc}' -> '{description}'")
    
    # Форматируем ответ в зависимости от типа команды
    # Извлекаем специальные параметры из описания
    params = {}
    
    # Ищем сроки
    deadline_match = re.search(r'до\s+(\d{1,2})[.\-](\d{1,2})(?:[.\-](\d{4})|)', description)
    if deadline_match:
        day, month = deadline_match.group(1), deadline_match.group(2)
        year = deadline_match.group(3) if deadline_match.group(3) else str(datetime.now().year)
        params['deadline'] = f"{day}.{month}.{year}"
        description = re.sub(r'до\s+\d{1,2}[.\-]\d{1,2}(?:[.\-]\d{4}|)\s*', '', description)
    
    # Ищем приоритет и статус
    priority_words = {
        'срочно': 'высокий',
        'срочный': 'высокий',
        'важно': 'высокий',
        'критично': 'критический',
        'критический': 'критический',
        'низкий': 'низкий',
        'обычный': 'средний'
    }
    
    status_words = {
        'в работе': 'in_progress',
        'выполняется': 'in_progress',
        'завершен': 'completed',
        'завершён': 'completed',
        'готов': 'completed',
        'отложен': 'on_hold',
        'приостановлен': 'on_hold',
        'отменен': 'cancelled',
        'отменён': 'cancelled'
    }
    for word, priority in priority_words.items():
        if word in description.lower():
            params['priority'] = priority
            description = re.sub(rf'\s*{word}\s*', '', description, flags=re.IGNORECASE)
            
    # Ищем статус
    for word, status in status_words.items():
        if word in description.lower():
            params['status'] = status
            description = re.sub(rf'\s*{word}\s*', '', description, flags=re.IGNORECASE)
            
    # Ищем команду проекта
    team_match = re.search(r'команда:?\s*([^,.]+)', description, re.IGNORECASE)
    if team_match:
        params['team'] = team_match.group(1).strip()
        description = re.sub(r'команда:?\s*[^,.]+[,.]?\s*', '', description, flags=re.IGNORECASE)
        
    # Ищем этап проекта
    stage_match = re.search(r'этап:?\s*([^,.]+)', description, re.IGNORECASE)
    if stage_match:
        params['stage'] = stage_match.group(1).strip()
        description = re.sub(r'этап:?\s*[^,.]+[,.]?\s*', '', description, flags=re.IGNORECASE)
    
    responses = {
        'marketing': {
            'icon': '📢',
            'action': 'Создаю маркетинговую задачу',
            'category': 'Маркетинг',
            'extra_info': lambda p: f"\n🎯 Приоритет: {p.get('priority', 'обычный').capitalize()}" if 'priority' in p else ''
        },
        'employee': {
            'icon': '👤',
            'action': 'Обрабатываю запрос по персоналу',
            'category': 'Управление персоналом',
            'extra_info': lambda p: f"\n📅 Срок: {p.get('deadline', 'Не указан')}" if 'deadline' in p else ''
        },
        'project': {
            'icon': '📊',
            'action': 'Работаю с проектом',
            'category': 'Управление проектами',
            'extra_info': lambda p: '\n'.join(filter(None, [
                f"📅 Срок: {p.get('deadline', 'Не указан')}" if 'deadline' in p else '',
                f"🎯 Приоритет: {p.get('priority', 'обычный').capitalize()}" if 'priority' in p else '',
                f"📊 Статус: {p.get('status', 'новый').replace('_', ' ').capitalize()}" if 'status' in p else '',
                f"👥 Команда: {p.get('team', 'Не назначена')}" if 'team' in p else '',
                f"📍 Этап: {p.get('stage', 'Начальный')}" if 'stage' in p else ''
            ]))
        },
        'analytics': {
            'icon': '📈',
            'action': 'Формирую аналитический отчет',
            'category': 'Бизнес-аналитика',
            'extra_info': lambda p: f"\n⚡ Приоритет: {p.get('priority', 'обычный').capitalize()}" if 'priority' in p else ''
        },
        'client': {
            'icon': '👥',
            'action': 'Создаю запись клиента',
            'category': 'Клиенты'
        },
        'supplier': {
            'icon': '🏭',
            'action': 'Создаю запись поставщика',
            'category': 'Поставщики'
        },
        'contract': {
            'icon': '📋',
            'action': 'Создаю договор',
            'category': 'Договоры'
        },
        'quality': {
            'icon': '✨',
            'action': 'Создаю задачу контроля качества',
            'category': 'Качество'
        },
        'risk': {
            'icon': '⚠️',
            'action': 'Создаю запись о риске',
            'category': 'Риски'
        },
        'strategy': {
            'icon': '🎯',
            'action': 'Создаю стратегическую задачу',
            'category': 'Стратегия'
        }
    }
    
    response_info = responses.get(command_type, {
        'icon': '📝',
        'action': 'Обрабатываю команду',
        'category': command_type.capitalize()
    })
    
    response_parts = [
        f"{response_info['icon']} {response_info['action']}:",
        f"\n📝 Описание: {description.capitalize()}",
        f"\n📁 Категория: {response_info['category']}"
    ]
    
    # Добавляем дополнительную информацию, если она есть
    if 'extra_info' in response_info:
        extra = response_info['extra_info'](params)
        if extra:
            response_parts.append(extra)
    
    response_parts.append("\n✨ Запись успешно создана и добавлена в систему.")
    
    return ''.join(response_parts)

def process_command(command_type: str, entities: Dict) -> str:
    """Global function to process commands"""
    return command_processor.process_command(command_type, entities)
