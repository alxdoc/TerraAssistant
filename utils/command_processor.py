import logging
from typing import Dict, Optional, Callable
from models import db, Command, Task

logger = logging.getLogger(__name__)

class CommandProcessor:
    def __init__(self):
        """Initialize command processor with response templates"""
        self.response_templates = {
            'error': [
                "Произошла ошибка: {details}",
                "Не удалось выполнить команду: {details}",
                "Ошибка обработки: {details}"
            ],
            'unknown': [
                "Извините, я не понимаю эту команду",
                "Не удалось распознать команду",
                "Команда не распознана"
            ],
            'greeting': [
                "Здравствуйте! Я ТЕРРА, ваш голосовой бизнес-ассистент. Чем могу помочь?",
                "Приветствую! Готова помочь вам в решении задач.",
                "Добрый день! Как я могу вам помочь?"
            ]
        }

    def process_command(self, command_type: str, entities: Dict) -> str:
        """Process a command of given type with provided entities"""
        try:
            logger.info(f"Processing command of type {command_type} with entities {entities}")
            
            # Маппинг типов команд на обработчики
            handlers = {
                'greeting': self.handle_greeting,
                'task_creation': lambda: self.handle_task_creation(entities),
                'document_analysis': lambda: self.handle_document_analysis(entities),
                'search': lambda: self.handle_search(entities),
                'calendar': lambda: self.handle_calendar(entities),
                'contact': lambda: self.handle_contact(entities),
                'reminder': lambda: self.handle_reminder(entities),
                'unknown': lambda: self.handle_unknown_command(entities)
            }
            
            # Получаем обработчик для данного типа команды
            handler = handlers.get(command_type)
            if not handler:
                logger.warning(f"Unknown command type: {command_type}")
                return self.handle_unknown_command(entities)
            
            # Выполняем обработку
            result = handler()
            logger.info(f"Command processed successfully, result: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error processing command: {str(e)}", exc_info=True)
            return self.format_error(str(e))

    def handle_greeting(self) -> str:
        """Handle greeting command"""
        import random
        return random.choice(self.response_templates['greeting'])

    def handle_unknown_command(self, entities: Dict) -> str:
        """Handle unknown command type"""
        return self.response_templates['unknown'][0]

    def handle_task_creation(self, entities: Dict) -> str:
        """Handle task creation command"""
        description = entities.get('description', '')
        if not description:
            return "Пожалуйста, укажите описание задачи"
        
        try:
            task = Task(
                title="Новая задача",
                description=description,
                status="pending"
            )
            db.session.add(task)
            db.session.commit()
            return f"Создана задача: {description}"
        except Exception as e:
            logger.error(f"Error creating task: {str(e)}", exc_info=True)
            return self.format_error("Не удалось создать задачу")

    def handle_document_analysis(self, entities: Dict) -> str:
        """Handle document analysis command"""
        description = entities.get('description', '')
        if not description:
            return "Пожалуйста, укажите документ для анализа"
        return f"Анализирую документ: {description}"

    def handle_search(self, entities: Dict) -> str:
        """Handle search command"""
        query = entities.get('description', '')
        if not query:
            return "Пожалуйста, укажите поисковый запрос"
        return f"Выполняется поиск по запросу: {query}"

    def handle_calendar(self, entities: Dict) -> str:
        """Handle calendar command"""
        description = entities.get('description', '')
        if not description:
            return "Пожалуйста, укажите детали для календаря"
        return f"Добавлено в календарь: {description}"

    def handle_contact(self, entities: Dict) -> str:
        """Handle contact-related command"""
        description = entities.get('description', '')
        if not description:
            return "Пожалуйста, укажите информацию о контакте"
        return f"Обработка контакта: {description}"

    def handle_reminder(self, entities: Dict) -> str:
        """Handle reminder command"""
        description = entities.get('description', '')
        if not description:
            return "Пожалуйста, укажите текст напоминания"
        return f"Установлено напоминание: {description}"

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
