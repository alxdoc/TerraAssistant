import logging
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict

import logging
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict

try:
    import nltk
    from nltk.tokenize import word_tokenize
    from nltk.corpus import stopwords
    from nltk.stem import WordNetLemmatizer
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    
    # Предварительная загрузка необходимых моделей NLTK для русского языка
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)
    nltk.download('omw-1.4', quiet=True)  # Open Multilingual Wordnet
    nltk.download('universal_tagset', quiet=True)
    
    # Проверяем доступность русского языка
    if 'russian' not in stopwords.fileids():
        raise ImportError("Russian language resources not found in NLTK")
        
except Exception as e:
    logging.error(f"Ошибка при импорте библиотек NLP: {str(e)}")
    logging.error("Убедитесь, что установлены все необходимые компоненты NLTK для русского языка")
    raise

# Настройка логирования
logger = logging.getLogger(__name__)

# Инициализация NLTK и загрузка необходимых компонентов
def initialize_nltk():
    """Инициализация и проверка наличия всех необходимых компонентов NLTK"""
    components = [
        ('punkt', 'tokenizers/punkt'),
        ('stopwords', 'corpora/stopwords'),
        ('averaged_perceptron_tagger', 'taggers/averaged_perceptron_tagger'),
        ('universal_tagset', 'taggers/universal_tagset')
    ]
    
    for component, path in components:
        try:
            nltk.data.find(path)
            logger.info(f'Компонент NLTK {component} уже установлен')
        except LookupError:
            logger.info(f'Загрузка компонента NLTK {component}')
            nltk.download(component, quiet=True)

# Выполняем инициализацию
initialize_nltk()

# Загружаем стоп-слова для русского языка
try:
    stop_words_ru = set(stopwords.words('russian'))
    logger.info('Русские стоп-слова успешно загружены')
except Exception as e:
    logger.error(f'Ошибка при загрузке русских стоп-слов: {str(e)}')
    stop_words_ru = set()

class DialogContext:
    def __init__(self):
        """Инициализация контекста диалога"""
        self.current_topic = None
        self.last_entities = {}
        self.conversation_history = []
        self.last_update = datetime.now()
        self.intent_confidence = defaultdict(float)
        self.context_memory = {}
        self.follow_up_questions = []
        self.expected_response_type = None
        self.dialog_state = 'initial'
        
        # Инициализация NLP компонентов
        try:
            # Загружаем стоп-слова для русского языка
            self.stop_words = set(stopwords.words('russian'))
            logger.info(f"Загружено {len(self.stop_words)} стоп-слов для русского языка")
            
            # Настраиваем векторизатор для работы с русским языком
            self.vectorizer = TfidfVectorizer(
                ngram_range=(1, 2),
                stop_words=None,  # Будем фильтровать стоп-слова вручную
                token_pattern=r'(?u)\b\w+\b',  # Паттерн для русских слов
                analyzer='word',
                max_features=5000
            )
            
            # Инициализируем хранилище векторов намерений
            self.intent_vectors = {}
            
            # Словарь для хранения лемм русских слов
            self.lemma_cache = {}
            
            # Инициализация базы знаний намерений
            self.initialize_intent_vectors()
            
            logger.info("NLP компоненты успешно инициализированы")
        except Exception as e:
            logger.error(f"Ошибка при инициализации NLP компонентов: {str(e)}")
            raise

    def initialize_intent_vectors(self):
        """Инициализация векторов для определения намерений"""
        intent_examples = {
            'task_creation': [
                'создать задачу', 'новая задача', 'добавить заявку',
                'запланировать', 'поставить задачу', 'назначить задание',
                'нужно сделать', 'запиши задачу', 'добавь в список дел'
            ],
            'document_analysis': [
                'проверить документ', 'анализ документа', 'проверка договора',
                'изучить документ', 'просмотреть контракт', 'проанализировать соглашение',
                'оценить документ', 'проверь договор'
            ],
            'search': [
                'найти', 'поиск', 'искать', 'где находится',
                'покажи информацию о', 'найди данные', 'поищи',
                'помоги найти', 'есть ли информация о'
            ],
            'report': [
                'отчет', 'статистика', 'показать данные', 'сводка',
                'итоги', 'результаты за', 'сформировать отчет',
                'дай статистику', 'покажи итоги'
            ],
            'greeting': [
                'привет', 'здравствуй', 'добрый день', 'доброе утро',
                'добрый вечер', 'приветствую'
            ],
            'help': [
                'помощь', 'что ты умеешь', 'какие команды', 'инструкция',
                'как пользоваться', 'подскажи возможности'
            ]
        }
        
        # Подготовка и векторизация примеров
        all_examples = []
        for examples in intent_examples.values():
            processed_examples = [self.preprocess_text(ex) for ex in examples]
            all_examples.extend(processed_examples)
            
        self.vectorizer.fit(all_examples)
        
        # Создаем векторы для каждого намерения
        for intent, examples in intent_examples.items():
            processed_examples = [self.preprocess_text(ex) for ex in examples]
            vectors = self.vectorizer.transform(processed_examples)
            self.intent_vectors[intent] = vectors.mean(axis=0)

    def preprocess_text(self, text: str) -> str:
        """Предобработка текста с поддержкой русского языка"""
        # Приведение к нижнему регистру
        text = text.lower()
        
        # Базовая токенизация для русского языка
        tokens = re.findall(r'\b\w+\b', text)
        
        # Удаление стоп-слов и пустых токенов
        tokens = [token for token in tokens 
                 if token not in self.stop_words 
                 and token.strip() 
                 and len(token) > 1]
        
        # Простая стемминг/лемматизация для русского языка
        # Удаляем наиболее распространенные окончания
        processed_tokens = []
        for token in tokens:
            # Простые правила для русских окончаний
            if len(token) > 4:
                if token.endswith(('ть', 'тся')):
                    token = token[:-2]
                elif token.endswith(('ый', 'ая', 'ое', 'ые', 'ими', 'ого')):
                    token = token[:-2]
                elif token.endswith(('ешь', 'ет', 'ем', 'ете', 'ут', 'ют')):
                    token = token[:-2]
            processed_tokens.append(token)
        
        return ' '.join(processed_tokens)

    def detect_intent(self, text: str) -> Tuple[str, float]:
        """Определяет намерение с помощью TF-IDF и косинусного сходства"""
        processed_text = self.preprocess_text(text)
        text_vector = self.vectorizer.transform([processed_text])
        
        max_similarity = -1
        detected_intent = 'unknown'
        
        for intent, intent_vector in self.intent_vectors.items():
            similarity = cosine_similarity(text_vector, intent_vector)[0][0]
            if similarity > max_similarity:
                max_similarity = similarity
                detected_intent = intent
        
        # Если уверенность низкая, проверяем контекст
        if max_similarity < 0.3:
            if self.current_topic and len(self.conversation_history) > 0:
                return self.current_topic, 0.4
            return 'unknown', max_similarity
            
        return detected_intent, max_similarity

    def update(self, text: str, intent: str, entities: Dict[str, any]) -> None:
        """Обновляет контекст диалога с учетом новой информации"""
        timestamp = datetime.now()
        
        # Обработка текста
        processed_text = self.preprocess_text(text)
        
        # Сохраняем историю диалога
        self.conversation_history.append({
            'text': text,
            'processed_text': processed_text,
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
            self.follow_up_questions.extend(
                self.generate_follow_up_questions(missing_required_info)
            )
        else:
            self.dialog_state = 'complete'
        
        # Обновляем тему разговора и контекстную память
        if intent != 'unknown':
            self.current_topic = intent
            self.update_context_memory(intent, entities)

    def check_missing_required_info(self, intent: str, entities: Dict[str, any]) -> List[str]:
        """Проверяет наличие всей необходимой информации"""
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
        """Генерирует уточняющие вопросы"""
        questions = {
            'description': 'Пожалуйста, опишите задачу подробнее',
            'document_type': 'Какой тип документа вы хотите проанализировать?',
            'search_query': 'Что именно вы хотите найти?',
            'report_type': 'Какой тип отчета вам нужен?',
            'time_period': 'За какой период времени нужен отчет?'
        }
        return [questions[info] for info in missing_info if info in questions]

    def update_context_memory(self, intent: str, entities: Dict[str, any]) -> None:
        """Обновляет контекстную память"""
        important_entities = [
            'description', 'document_type', 'search_query', 
            'report_type', 'time_period'
        ]
        
        for entity, value in entities.items():
            if entity in important_entities:
                self.context_memory[entity] = {
                    'value': value,
                    'timestamp': datetime.now(),
                    'intent': intent
                }

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
    """Анализ текста с учетом контекста диалога"""
    text = text.lower().strip()
    logger.debug(f"Анализ текста: {text}")
    
    # Используем глобальный контекст, если не передан локальный
    if context is None:
        context = dialog_context
    
    # Определяем намерение
    intent, confidence = context.detect_intent(text)
    logger.debug(f"Определено намерение: {intent} с уверенностью {confidence}")
    
    # Извлекаем сущности
    entities = extract_entities(text, intent, context)
    logger.debug(f"Извлечены сущности: {entities}")
    
    # Обновляем контекст
    context.update(text, intent, entities)
    
    return intent, entities

def extract_entities(text: str, intent: str, context: DialogContext) -> Dict[str, any]:
    """Извлекает сущности из текста с учетом контекста"""
    entities = {}
    
    # Получаем предыдущий контекст
    prev_context = context.get_context()
    prev_entities = prev_context['entities']
    
    # Извлекаем базовые сущности
    entities.update(extract_basic_entities(text))
    
    # Добавляем специфичные для намерения сущности
    if intent == 'task_creation':
        task_entities = extract_task_entities(text, prev_entities)
        if task_entities:
            entities.update(task_entities)
    elif intent == 'document_analysis':
        doc_entities = extract_document_entities(text, prev_entities)
        if doc_entities:
            entities.update(doc_entities)
    elif intent == 'search':
        search_entities = extract_search_entities(text)
        if search_entities:
            entities.update(search_entities)
    elif intent == 'report':
        report_entities = extract_report_entities(text, prev_entities)
        if report_entities:
            entities.update(report_entities)
    
    return entities

def extract_basic_entities(text: str) -> Dict[str, any]:
    """Извлекает базовые сущности (даты, числа, etc.)"""
    entities = {}
    
    # Извлечение дат
    date_patterns = {
        'today': r'сегодня|текущ[иа][йя]|сейчас',
        'tomorrow': r'завтра|следующ[иа][йя]',
        'next_week': r'следующ[ая][яй]\s+недел[яи]|через\s+неделю',
        'specific_date': r'(\d{1,2})[.-](\d{1,2})[.-](\d{4})'
    }
    
    for date_type, pattern in date_patterns.items():
        if re.search(pattern, text):
            entities['date_reference'] = date_type
            if date_type == 'specific_date':
                match = re.search(pattern, text)
                if match:
                    entities['date'] = {
                        'day': int(match.group(1)),
                        'month': int(match.group(2)),
                        'year': int(match.group(3))
                    }
    
    # Извлечение чисел
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
    
    return entities

def extract_task_entities(text: str, prev_entities: Dict[str, any]) -> Dict[str, any]:
    """Извлекает сущности для создания задачи"""
    entities = {}
    
    # Извлечение описания задачи
    description_patterns = [
        r'задач[уа]\s+(.+?)(?=\s+на|$)',
        r'создать\s+(.+?)(?=\s+на|$)',
        r'добавить\s+(.+?)(?=\s+на|$)',
        r'нужно\s+(.+?)(?=\s+на|$)',
        r'надо\s+(.+?)(?=\s+на|$)'
    ]
    
    for pattern in description_patterns:
        match = re.search(pattern, text)
        if match:
            entities['description'] = match.group(1).strip()
            break
    
    # Если описание не найдено, но есть в контексте
    if 'description' not in entities and 'description' in prev_entities:
        entities['description'] = prev_entities['description']
    
    # Определение приоритета
    priority_patterns = {
        'high': r'срочн|важн|критичн|немедленн',
        'low': r'не\s+срочн|потом|когда\s+будет\s+время|низк',
        'normal': r'обычн|стандартн|средн'
    }
    
    for priority, pattern in priority_patterns.items():
        if re.search(pattern, text):
            entities['priority'] = priority
            break
    
    return entities

def extract_document_entities(text: str, prev_entities: Dict[str, any]) -> Dict[str, any]:
    """Извлекает сущности для анализа документов"""
    entities = {}
    
    doc_type_patterns = {
        'contract': r'договор|контракт|соглашение',
        'report': r'отчет|справк[аи]|выписк[аи]',
        'letter': r'письм[ао]|обращени[ея]|заявлени[ея]',
        'technical': r'инструкци[яи]|описание|документаци[яи]'
    }
    
    for doc_type, pattern in doc_type_patterns.items():
        if re.search(pattern, text):
            entities['document_type'] = doc_type
            break
    
    # Если тип документа не найден, но есть в контексте
    if 'document_type' not in entities and 'document_type' in prev_entities:
        entities['document_type'] = prev_entities['document_type']
    
    return entities

def extract_search_entities(text: str) -> Dict[str, any]:
    """Извлекает сущности для поиска"""
    entities = {}
    
    # Извлечение поискового запроса
    search_patterns = [
        r'найти\s+(.+?)(?=\s+в|$)',
        r'поиск\s+(.+?)(?=\s+в|$)',
        r'где\s+(.+?)(?=\s+в|$)',
        r'ищу\s+(.+?)(?=\s+в|$)',
        r'покажи\s+(.+?)(?=\s+в|$)'
    ]
    
    for pattern in search_patterns:
        match = re.search(pattern, text)
        if match:
            entities['search_query'] = match.group(1).strip()
            break
    
    return entities

def extract_report_entities(text: str, prev_entities: Dict[str, any]) -> Dict[str, any]:
    """Извлекает сущности для отчетов"""
    entities = {}
    
    # Определение типа отчета
    report_type_patterns = {
        'sales': r'продаж|выручк[аи]|доход',
        'activity': r'активност[ьи]|действи[яй]|работ[аы]',
        'analytics': r'аналитик[аи]|статистик[аи]|показател[ьи]',
        'performance': r'производительност[ьи]|эффективност[ьи]'
    }
    
    for report_type, pattern in report_type_patterns.items():
        if re.search(pattern, text):
            entities['report_type'] = report_type
            break
    
    # Если тип отчета не найден, но есть в контексте
    if 'report_type' not in entities and 'report_type' in prev_entities:
        entities['report_type'] = prev_entities['report_type']
    
    # Определение периода
    period_patterns = {
        'day': r'день|сутки|сегодня',
        'week': r'недел[яю]|7 дней',
        'month': r'месяц|30 дней',
        'quarter': r'квартал|3 месяца',
        'year': r'год|12 месяцев'
    }
    
    for period, pattern in period_patterns.items():
        if re.search(pattern, text):
            entities['time_period'] = period
            break
    
    # Если период не найден, но есть в контексте
    if 'time_period' not in entities and 'time_period' in prev_entities:
        entities['time_period'] = prev_entities['time_period']
    
    return entities
