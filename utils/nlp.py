import logging
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict

# Настройка логирования
logger = logging.getLogger(__name__)

class DialogContext:
    def __init__(self):
        """Инициализация контекста диалога"""
        self.current_topic = None  # Текущая тема разговора
        self.last_entities = {}  # Последние извлеченные сущности
        self.conversation_history = []  # История диалога
        self.last_update = datetime.now()
        self.intent_confidence = defaultdict(float)
        self.context_memory = {}  # Для хранения контекстной информации
        self.follow_up_questions = []  # Для хранения уточняющих вопросов
        self.expected_response_type = None  # Ожидаемый тип ответа
        self.dialog_state = 'initial'  # Состояние диалога

    def update(self, text: str, intent: str, entities: Dict[str, any]) -> None:
        """
        Обновляет контекст диалога с учетом новой информации
        """
        timestamp = datetime.now()
        
        # Сохраняем историю диалога
        self.conversation_history.append({
            'text': text,
            'intent': intent,
            'entities': entities,
            'timestamp': timestamp,
            'dialog_state': self.dialog_state
        })
        
        # Обновляем контекстную информацию
        self.last_entities.update(entities)
        self.last_update = timestamp
        
        # Анализируем необходимость уточняющих вопросов
        missing_required_info = self.check_missing_required_info(intent, entities)
        if missing_required_info:
            self.dialog_state = 'clarification_needed'
            self.follow_up_questions.extend(self.generate_follow_up_questions(missing_required_info))
        else:
            self.dialog_state = 'complete'
        
        # Обновляем тему разговора и контекстную память
        if intent != 'unknown':
            self.current_topic = intent
            # Сохраняем важную информацию в контекстной памяти
            self.update_context_memory(intent, entities)

    def check_missing_required_info(self, intent: str, entities: Dict[str, any]) -> List[str]:
        """
        Проверяет наличие всей необходимой информации для выполнения намерения
        """
        required_info = {
            'task_creation': ['description'],
            'document_analysis': ['document_type'],
            'search': ['search_query'],
            'report': ['report_type', 'time_period']
        }
        
        if intent not in required_info:
            return []
            
        return [field for field in required_info[intent] 
                if field not in entities and field not in self.last_entities]

    def generate_follow_up_questions(self, missing_info: List[str]) -> List[str]:
        """
        Генерирует уточняющие вопросы на основе отсутствующей информации
        """
        questions = {
            'description': 'Пожалуйста, опишите задачу подробнее',
            'document_type': 'Какой тип документа вы хотите проанализировать?',
            'search_query': 'Что именно вы хотите найти?',
            'report_type': 'Какой тип отчета вам нужен?',
            'time_period': 'За какой период времени нужен отчет?'
        }
        return [questions[info] for info in missing_info if info in questions]

    def update_context_memory(self, intent: str, entities: Dict[str, any]) -> None:
        """
        Обновляет контекстную память, сохраняя важную информацию
        """
        # Сохраняем только важные сущности
        important_entities = ['description', 'document_type', 'search_query', 
                            'report_type', 'time_period']
        
        for entity, value in entities.items():
            if entity in important_entities:
                self.context_memory[entity] = {
                    'value': value,
                    'timestamp': datetime.now(),
                    'intent': intent
                }

    def is_expired(self, timeout_minutes: int = 5) -> bool:
        """Проверяет, не истек ли срок действия контекста"""
        return datetime.now() - self.last_update > timedelta(minutes=timeout_minutes)

    def get_context(self) -> Dict[str, any]:
        """Возвращает текущий контекст диалога"""
        return {
            'topic': self.current_topic,
            'entities': self.last_entities,
            'history': self.conversation_history[-3:] if self.conversation_history else [],
            'state': self.dialog_state,
            'follow_up_questions': self.follow_up_questions
        }

# Глобальный контекст диалога
dialog_context = DialogContext()

def analyze_text(text: str, context: Optional[DialogContext] = None) -> Tuple[str, Dict[str, any]]:
    """
    Расширенный анализ текста с учетом контекста диалога и семантики
    """
    text = text.lower().strip()
    logger.debug(f"Анализ текста: {text}")
    
    # Используем глобальный контекст, если не передан локальный
    if context is None:
        context = dialog_context
        
    logger.debug(f"Текущий контекст: {context.get_context()}")
    
    # Если есть ожидаемый тип ответа, обрабатываем его
    if context.expected_response_type:
        entities = extract_entities(text, context.current_topic, context)
        if entities:
            logger.debug(f"Получен ответ на уточняющий вопрос: {entities}")
            return context.current_topic, entities
    
    # Расширенные шаблоны намерений с семантическими группами
    intents = {
        'greeting': {
            'patterns': [
                r'^(привет|здравствуй|добр[ыое][йе]|хай)',
                r'как[ие]?\s+дела',
                r'доброго\s+времени'
            ],
            'responses': [
                "Здравствуйте! Чем могу помочь?",
                "Приветствую! Готова помочь вам в решении задач.",
                "Добрый день! Как я могу вам помочь?"
            ]
        },
        'task_creation': {
            'patterns': [
                r'(созда|добав|нов[ыа])(ть|й|я)?\s+(задач|заявк|дел)',
                r'(записать|внести|добавить)\s+в\s+список',
                r'(напомни|записать)\s+про'
            ]
        },
        'clarification': {
            'patterns': [
                r'(что|как|почему|зачем|когда)',
                r'(не\s+понимаю|объясни|уточни)',
                r'(можешь|можно)\s+подробнее'
            ]
        },
        'confirmation': {
            'patterns': [
                r'(да|конечно|правильно|верно|точно)',
                r'(согласен|подтверждаю|именно)',
                r'(хорошо|ок|ладно)'
            ]
        },
        'negation': {
            'patterns': [
                r'(нет|неверно|неправильно|ошибка)',
                r'(не\s+согласен|не\s+то)',
                r'(отмени|отменить|вернуть)'
            ]
        }
    }
    
    # Определяем намерение с учетом контекста
    intent, confidence = detect_intent(text, intents, context)
    logger.debug(f"Определено намерение: {intent} с уверенностью {confidence}")
    
    # Извлекаем сущности с учетом контекста
    entities = extract_entities(text, intent, context)
    logger.debug(f"Извлечены сущности: {entities}")
    
    # Обновляем контекст диалога
    context.update(text, intent, entities)
    
    return intent, entities

def detect_intent(text: str, intents: Dict[str, Dict], context: DialogContext) -> Tuple[str, float]:
    """
    Определяет намерение пользователя с учетом контекста диалога
    """
    max_confidence = 0.0
    detected_intent = 'unknown'
    
    # Проверяем соответствие текста шаблонам
    for intent, data in intents.items():
        for pattern in data['patterns']:
            if re.search(pattern, text):
                confidence = calculate_confidence(text, pattern)
                if confidence > max_confidence:
                    max_confidence = confidence
                    detected_intent = intent
    
    # Учитываем контекст предыдущего диалога
    if detected_intent == 'unknown' and context.current_topic:
        if text.strip() in ['да', 'конечно', 'верно']:
            return 'confirmation', 0.8
        elif text.strip() in ['нет', 'неверно', 'отмена']:
            return 'negation', 0.8
    
    return detected_intent, max_confidence

def calculate_confidence(text: str, pattern: str) -> float:
    """
    Рассчитывает уверенность в соответствии текста шаблону
    """
    match = re.search(pattern, text)
    if not match:
        return 0.0
    
    # Длина совпадения относительно длины текста
    match_length = match.end() - match.start()
    text_length = len(text)
    
    # Базовая уверенность на основе длины совпадения
    confidence = match_length / text_length
    
    # Корректируем уверенность на основе позиции совпадения
    if match.start() == 0:
        confidence *= 1.2  # Повышаем уверенность если совпадение в начале
        
    return min(confidence, 1.0)

def extract_entities(text: str, intent: str, context: DialogContext) -> Dict[str, any]:
    """
    Извлекает сущности из текста с учетом контекста диалога
    """
    entities = {}
    text = text.lower()
    
    # Используем контекст предыдущего диалога
    prev_context = context.get_context()
    prev_entities = prev_context['entities']
    
    # Обработка дат и времени
    date_patterns = {
        'today': r'сегодня|текущ[иа][йя]|сейчас',
        'tomorrow': r'завтра|следующ[иа][йя]',
        'next_week': r'следующ[ая][яй]\s+недел[яи]|через\s+неделю',
        'specific_date': r'(\d{1,2})[.-](\d{1,2})[.-](\d{4})',
        'relative_date': r'через\s+(\d+)\s+(день|дня|дней|недел[юйи]|месяц[ае]?в?)'
    }
    
    for date_type, pattern in date_patterns.items():
        if re.search(pattern, text):
            entities['date_reference'] = date_type
            if date_type == 'specific_date':
                match = re.search(pattern, text)
                if match:  # Добавляем проверку на None
                    entities['date'] = {
                        'day': match.group(1),
                        'month': match.group(2),
                        'year': match.group(3)
                    }
    
    # Обработка в зависимости от намерения
    if intent == 'task_creation':
        # Извлечение описания задачи
        description_patterns = [
            r'задач[уа]\s+(.+?)(?=\s+на|$)',
            r'создать\s+(.+?)(?=\s+на|$)',
            r'добавить\s+(.+?)(?=\s+на|$)',
            r'записать\s+(.+?)(?=\s+на|$)',
            r'напомни\s+(.+?)(?=\s+на|$)'
        ]
        
        for pattern in description_patterns:
            match = re.search(pattern, text)
            if match:
                description = match.group(1).strip()
                description = re.sub(r'^(задачу|заявку|работу)\s+', '', description)
                entities['description'] = description
                break
        
        # Если описание не найдено, но есть в контексте
        if 'description' not in entities and 'description' in prev_entities:
            entities['description'] = prev_entities['description']
        
        # Определение приоритета
        priority_patterns = {
            'high': r'срочн|важн|критичн|перво[й]?\s*очередн',
            'low': r'не\s+срочн|потом|когда\s+будет\s+время|низк[ий]\s+приоритет',
            'normal': r'обычн|стандартн|средн'
        }
        
        for priority, pattern in priority_patterns.items():
            if re.search(pattern, text):
                entities['priority'] = priority
                break
        
        # Определение статуса
        status_patterns = {
            'new': r'нов|создать|добавить',
            'in_progress': r'начат|выполня|в\s+работ|процесс',
            'completed': r'завершен|готов|сделан|выполнен'
        }
        
        for status, pattern in status_patterns.items():
            if re.search(pattern, text):
                entities['status'] = status
                break
    
    elif intent == 'clarification':
        # Извлекаем тему уточнения
        clarification_patterns = [
            r'что\s+значит\s+(.+)',
            r'поясни\s+про\s+(.+)',
            r'расскажи\s+подробнее\s+о\s+(.+)'
        ]
        
        for pattern in clarification_patterns:
            match = re.search(pattern, text)
            if match:
                entities['clarification_topic'] = match.group(1)
                break
    
    elif intent == 'confirmation' or intent == 'negation':
        # Сохраняем предыдущий контекст
        entities.update(prev_entities)
        entities['previous_intent'] = prev_context['topic']
    
    # Извлечение числовых значений
    number_patterns = {
        'amount': r'(\d+)\s*(шт|штук|единиц|раз)',
        'duration': r'(\d+)\s*(минут|час[ао]в|дн[яей])',
        'money': r'(\d+)\s*(руб|₽)'
    }
    
    for num_type, pattern in number_patterns.items():
        match = re.search(pattern, text)
        if match:
            entities[num_type] = {
                'value': int(match.group(1)),
                'unit': match.group(2)
            }
    
    logger.debug(f"Извлеченные сущности: {entities}")
    return entities
