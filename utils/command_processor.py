import logging
from typing import Dict
from models import Command, db

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class CommandProcessor:
    def __init__(self):
        self.response_templates = {
            'greeting': [
                "Здравствуйте! Чем могу помочь?",
                "Приветствую! Готов помочь вам.",
                "Добрый день! Как я могу быть полезен?"
            ],
            'unknown': [
                "Извините, я не понял команду. Пожалуйста, повторите.",
                "Не могу распознать команду. Попробуйте сформулировать иначе.",
            ],
            'error': [
                "Произошла ошибка: {details}",
                "Не удалось выполнить команду: {details}"
            ]
        }

    def process_command(self, command_type: str, entities: Dict) -> str:
        """Process command based on its type"""
        try:
            logger.debug(f"Processing command type: {command_type} with entities: {entities}")
            
            # Словарь обработчиков команд
            handlers = {
                'greeting': lambda: self.handle_greeting(entities),
                'task_creation': lambda: self.handle_task_creation(entities),
                'document_analysis': lambda: self.handle_document_analysis(entities),
                'search': lambda: self.handle_search(entities),
                'calendar': lambda: self.handle_calendar(entities),
                'contact': lambda: self.handle_contact(entities),
                'reminder': lambda: self.handle_reminder(entities),
                'finance': lambda: self.handle_finance(entities),
                'project': lambda: self.handle_project(entities),
                'sales': lambda: self.handle_sales(entities),
                'inventory': lambda: self.handle_inventory(entities),
                'analytics': lambda: self.handle_analytics(entities),
                'employee': lambda: self.handle_employee(entities),
                'meeting': lambda: self.handle_meeting(entities),
                'unknown': lambda: self.handle_unknown_command(entities)
            }
            
            # Получаем и выполняем обработчик команды
            handler = handlers.get(command_type, handlers['unknown'])
            result = handler()
            logger.info(f"Command processed successfully: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error processing command: {str(e)}", exc_info=True)
            return self.format_error(str(e))

    def handle_greeting(self, entities: Dict) -> str:
        """Handle greeting command"""
        import random
        return random.choice(self.response_templates['greeting'])

    def handle_unknown_command(self, entities: Dict) -> str:
        """Handle unknown command"""
        import random
        return random.choice(self.response_templates['unknown'])

    def handle_task_creation(self, entities: Dict) -> str:
        """Handle task creation command"""
        description = entities.get('description', '')
        if not description:
            return "Пожалуйста, укажите описание задачи"
        logger.info(f"Creating task: {description}")
        return f"Создана задача: {description}"

    def handle_document_analysis(self, entities: Dict) -> str:
        """Handle document analysis command"""
        description = entities.get('description', '')
        if not description:
            return "Пожалуйста, укажите документ для анализа"
        logger.info(f"Analyzing document: {description}")
        return f"Анализ документа: {description}"

    def handle_search(self, entities: Dict) -> str:
        """Handle search command"""
        description = entities.get('description', '')
        if not description:
            return "Пожалуйста, укажите, что нужно найти"
        logger.info(f"Searching for: {description}")
        return f"Поиск: {description}"

    def handle_calendar(self, entities: Dict) -> str:
        """Handle calendar command"""
        description = entities.get('description', '')
        if not description:
            return "Пожалуйста, уточните действие с календарем"
        logger.info(f"Calendar operation: {description}")
        return f"Работа с календарем: {description}"

    def handle_contact(self, entities: Dict) -> str:
        """Handle contact command"""
        description = entities.get('description', '')
        if not description:
            return "Пожалуйста, уточните действие с контактом"
        logger.info(f"Contact operation: {description}")
        return f"Обработка контакта: {description}"

    def handle_reminder(self, entities: Dict) -> str:
        """Handle reminder command"""
        description = entities.get('description', '')
        if not description:
            return "Пожалуйста, укажите текст напоминания"
        logger.info(f"Setting reminder: {description}")
        return f"Установлено напоминание: {description}"

    def handle_finance(self, entities: Dict) -> str:
        """Handle finance-related commands"""
        description = entities.get('description', '')
        if not description:
            return "Пожалуйста, уточните финансовую операцию"
        logger.info(f"Обработка финансовой операции: {description}")
        return f"Обработка финансовой операции: {description}"

    def handle_project(self, entities: Dict) -> str:
        """Handle project management commands"""
        description = entities.get('description', '')
        if not description:
            return "Пожалуйста, уточните действие с проектом"
        logger.info(f"Управление проектом: {description}")
        return f"Обработка проекта: {description}"

    def handle_sales(self, entities: Dict) -> str:
        """Handle sales-related commands"""
        description = entities.get('description', '')
        if not description:
            return "Пожалуйста, уточните информацию о продаже"
        logger.info(f"Обработка продажи: {description}")
        return f"Обработка продажи: {description}"

    def handle_inventory(self, entities: Dict) -> str:
        """Handle inventory management commands"""
        description = entities.get('description', '')
        if not description:
            return "Пожалуйста, уточните операцию со складом"
        logger.info(f"Управление складом: {description}")
        return f"Обработка складской операции: {description}"

    def handle_analytics(self, entities: Dict) -> str:
        """Handle analytics and reporting commands"""
        description = entities.get('description', '')
        if not description:
            return "Пожалуйста, уточните тип аналитики"
        logger.info(f"Анализ данных: {description}")
        return f"Подготовка аналитики: {description}"

    def handle_employee(self, entities: Dict) -> str:
        """Handle employee management commands"""
        description = entities.get('description', '')
        if not description:
            return "Пожалуйста, уточните действие с данными сотрудника"
        logger.info(f"Управление персоналом: {description}")
        return f"Обработка данных сотрудника: {description}"

    def handle_meeting(self, entities: Dict) -> str:
        """Handle meeting organization commands"""
        description = entities.get('description', '')
        if not description:
            return "Пожалуйста, уточните детали встречи"
        logger.info(f"Организация встречи: {description}")
        return f"Планирование встречи: {description}"

    def format_error(self, details: str) -> str:
        """Format error message"""
        return self.response_templates['error'][0].format(details=details)

    def save_command(self, command_type: str, result: str) -> None:
        """Save executed command to database"""
        try:
            command = Command(
                text=result,
                command_type=command_type,
                status='completed',
                result=result
            )
            db.session.add(command)
            db.session.commit()
            logger.debug("Command successfully saved to database")
        except Exception as e:
            logger.error(f"Error saving command: {str(e)}", exc_info=True)

# Create global command processor instance
command_processor = CommandProcessor()

def process_command(command_type: str, entities: Dict) -> str:
    """Global function for processing commands"""
    result = command_processor.process_command(command_type, entities)
    command_processor.save_command(command_type, result)
    return result
