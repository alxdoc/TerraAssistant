import logging
from typing import Dict
from datetime import datetime
from models import db, Command, Task

# Настройка логирования
logger = logging.getLogger(__name__)

class CommandProcessor:
    def __init__(self):
        self.response_templates = {
            'greeting': [
                "Здравствуйте! Я ТЕРРА, ваш голосовой бизнес-ассистент. Чем могу помочь?",
                "Приветствую! Готова помочь вам в решении задач.",
                "Добрый день! Как я могу вам помочь?"
            ],
            'unknown': [
                "Извините, я не совсем поняла. Можете сказать иначе?",
                "Не уверена, что правильно поняла. Попробуйте переформулировать."
            ],
            'error': [
                "Извините, произошла ошибка: {details}",
                "Возникла проблема при выполнении команды: {details}"
            ]
        }

    def process_command(self, command_type: str, entities: Dict) -> str:
        """Обрабатывает команду"""
        try:
            logger.info(f"Начало обработки команды типа: {command_type}")
            logger.debug(f"Сущности команды: {entities}")
            
            # Проверяем валидность типа команды
            if not command_type:
                logger.warning("Получен пустой тип команды")
                return self.response_templates['unknown'][0]
            
            # Обработка различных типов команд
            handlers = {
                'greeting': self.handle_greeting,
                'task_creation': lambda: self.handle_task_creation(entities),
                'document_analysis': lambda: self.handle_document_analysis(entities),
                'search': lambda: self.handle_search(entities)
            }
            
            # Получаем обработчик для данного типа команды
            handler = handlers.get(command_type)
            
            if handler:
                logger.debug(f"Найден обработчик для команды типа: {command_type}")
                response = handler()
                logger.info(f"Команда успешно обработана. Ответ: {response}")
                return response
            else:
                logger.warning(f"Неизвестный тип команды: {command_type}")
                return self.response_templates['unknown'][0]
                
        except Exception as e:
            logger.error(f"Ошибка при обработке команды: {str(e)}", exc_info=True)
            return self.format_error(str(e))

    def handle_greeting(self) -> str:
        """Обработка приветствия"""
        import random
        return random.choice(self.response_templates['greeting'])

    def handle_task_creation(self, entities: Dict) -> str:
        """Создание новой задачи"""
        try:
            description = entities.get('description', 'Новая задача')
            
            task = Task(
                title=description[:200],
                description=description,
                status='pending',
                created_at=datetime.now()
            )
            
            db.session.add(task)
            db.session.commit()
            
            return f"Создана новая задача: {description}"
            
        except Exception as e:
            logger.error(f"Ошибка при создании задачи: {str(e)}")
            return self.format_error("Не удалось создать задачу")

    def handle_document_analysis(self, entities: Dict) -> str:
        """Обработка анализа документа"""
        return "Начат анализ документа. Это может занять некоторое время."

    def handle_search(self, entities: Dict) -> str:
        """Обработка поискового запроса"""
        query = entities.get('description', '')
        if not query:
            return "Не указан поисковый запрос"
        return f"Выполняется поиск по запросу: {query}"

    def format_error(self, details: str) -> str:
        """Форматирование сообщения об ошибке"""
        return self.response_templates['error'][0].format(details=details)

    def save_command(self, command_type: str, result: str) -> None:
        """
        Сохраняет выполненную команду в базу данных
        """
        try:
            command = Command(
                text=result,
                command_type=command_type,
                status='completed',
                result=result
            )
            
            db.session.add(command)
            db.session.commit()
            logger.debug("Команда успешно сохранена в базу данных")
            
        except Exception as e:
            logger.error(f"Ошибка при сохранении команды: {str(e)}", exc_info=True)


# Создаем глобальный экземпляр процессора команд
command_processor = CommandProcessor()

def process_command(command_type: str, entities: Dict) -> str:
    """Глобальная функция для обработки команд"""
    result = command_processor.process_command(command_type, entities)
    command_processor.save_command(command_type, result) #Added command saving
    return result