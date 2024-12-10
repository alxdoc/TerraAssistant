import logging
import random
from typing import Dict, Optional, Union
from datetime import datetime
from models import db, Command, Task
from utils.nlp import DialogContext

# Настройка логирования
logger = logging.getLogger(__name__)

class CommandProcessor:
    def __init__(self):
        self.dialog_context = DialogContext()
        self.response_templates = {
            'greeting': [
                "Здравствуйте! Я ТЕРРА, ваш голосовой бизнес-ассистент. Чем могу помочь?",
                "Приветствую! Готова помочь вам в решении задач.",
                "Добрый день! Как я могу вам помочь?"
            ],
            'help': [
                """Я могу помочь вам со следующими задачами:
- Создание и управление задачами
- Анализ документов и данных
- Поиск информации
- Формирование отчётов
Просто опишите, что вам нужно сделать."""
            ],
            'clarification': [
                "Позвольте уточнить: {details}",
                "Правильно ли я понимаю, что {details}?",
                "Можете пояснить, что именно вы имеете в виду?"
            ],
            'error': [
                "Извините, произошла ошибка: {details}",
                "Возникла проблема при выполнении команды: {details}"
            ],
            'unknown': [
                "Извините, я не совсем поняла. Можете сказать иначе?",
                "Не уверена, что правильно поняла. Попробуйте переформулировать."
            ]
        }

    def process_command(self, intent: str, entities: Dict) -> str:
        """
        Обрабатывает команду с учетом контекста диалога
        """
        try:
            logger.debug(f"Обработка команды: {intent} с сущностями: {entities}")
            
            # Получаем контекст диалога
            context = self.dialog_context.get_context()
            logger.debug(f"Текущий контекст: {context}")
            
            # Обработка команды в зависимости от намерения
            if intent == 'greeting':
                result = self.handle_greeting(entities)
            elif intent == 'help':
                result = self.handle_help(entities)
            elif intent == 'task_creation':
                result = self.handle_task_creation(entities, context)
            elif intent == 'clarification':
                result = self.handle_clarification(entities, context)
            elif intent == 'confirmation':
                result = self.handle_confirmation(entities, context)
            elif intent == 'negation':
                result = self.handle_negation(entities, context)
            else:
                result = self.handle_unknown_intent(intent, entities)
            
            # Сохраняем команду
            self.save_command(intent, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Ошибка при обработке команды: {str(e)}", exc_info=True)
            return self.format_response('error', {'details': str(e)})

    def handle_greeting(self, entities: Dict) -> str:
        """Обработка приветствия"""
        import random
        return random.choice(self.response_templates['greeting'])

    def handle_help(self, entities: Dict) -> str:
        """Обработка запроса помощи"""
        return self.response_templates['help'][0]

    def handle_task_creation(self, entities: Dict, context: Dict) -> str:
        """
        Обработка создания задачи с учетом контекста
        """
        try:
            # Проверяем наличие необходимых данных
            description = entities.get('description')
            if not description:
                if context['topic'] == 'task_creation' and 'description' in context['entities']:
                    description = context['entities']['description']
                else:
                    return "Пожалуйста, опишите задачу, которую нужно создать"

            # Создаем задачу
            task = Task(
                title=description[:200],
                description=description,
                category='voice_created',
                status=entities.get('status', 'pending'),
                created_at=datetime.now()
            )
            
            db.session.add(task)
            db.session.commit()
            
            return f"Создана новая задача: {description}"
            
        except Exception as e:
            logger.error(f"Ошибка при создании задачи: {str(e)}", exc_info=True)
            return self.format_response('error', {'details': 'Не удалось создать задачу'})

    def handle_clarification(self, entities: Dict, context: Dict) -> str:
        """
        Обработка запроса на уточнение
        """
        topic = entities.get('clarification_topic')
        if not topic and context['topic']:
            return self.format_response('clarification', 
                {'details': f"вы хотите узнать подробнее о {context['topic']}?"})
        elif topic:
            return f"Расскажите, что именно вас интересует по теме '{topic}'?"
        else:
            return "Что именно вы хотели бы уточнить?"

    def handle_confirmation(self, entities: Dict, context: Dict) -> str:
        """
        Обработка подтверждения
        """
        previous_intent = entities.get('previous_intent')
        if previous_intent == 'task_creation':
            return self.handle_task_creation(context['entities'], context)
        return "Хорошо, что бы вы хотели сделать дальше?"

    def handle_negation(self, entities: Dict, context: Dict) -> str:
        """
        Обработка отрицания
        """
        return "Пожалуйста, поясните, что именно нужно изменить?"

    def handle_unknown_intent(self, intent: str, entities: Dict) -> str:
        """
        Обработка неизвестного намерения
        """
        logger.warning(f"Получено неизвестное намерение: {intent}")
        return random.choice(self.response_templates['unknown'])

    def format_response(self, template_key: str, params: Optional[Dict] = None) -> str:
        """
        Форматирует ответ по шаблону
        """
        templates = self.response_templates.get(template_key, self.response_templates['unknown'])
        template = random.choice(templates)
        
        if params:
            return template.format(**params)
        return template

    def save_command(self, intent: str, result: str) -> None:
        """
        Сохраняет выполненную команду в базу данных
        """
        try:
            command = Command(
                text=result,
                command_type=intent,
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

def process_command(intent: str, entities: Dict) -> str:
    """
    Глобальная функция для обработки команд
    """
    return command_processor.process_command(intent, entities)

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
