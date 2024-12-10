import re
from typing import Tuple, Dict

def analyze_text(text: str) -> Tuple[str, Dict]:
    """
    Анализирует текст команды и определяет её тип и сущности
    """
    text = text.lower()
    
    # Расширенные шаблоны команд
    patterns = {
        'greeting': r'^(привет|здравствуй|добрый день|доброе утро|добрый вечер|хай)',
        'task_creation': r'(созда|добав|нов[ыа])(ть|й|я)?\s+(задач|заявк|дел)',
        'document_analysis': r'(проверить|анализ|проверка|посмотри|изучи)\s+(документ|договор|файл)',
        'search': r'(найти|поиск|искать|где|покажи)',
        'report': r'(отчет|статистика|данные|информаци)',
        'help': r'(помощь|помоги|что ты умеешь|подскажи)',
    }
    
    # Определение типа команды
    command_type = 'unknown'
    for cmd_type, pattern in patterns.items():
        if re.search(pattern, text):
            command_type = cmd_type
            break
    
    # Извлечение сущностей
    entities = extract_entities(text, command_type)
    
    return command_type, entities

def extract_entities(text: str, command_type: str) -> Dict:
    """
    Извлекает сущности из текста команды в зависимости от её типа
    с расширенной обработкой контекста
    """
    entities = {}
    text = text.lower()
    
    if command_type == 'task_creation':
        # Расширенный поиск описания задачи
        description_patterns = [
            r'задач[уа]\s+(.+)',
            r'создать\s+(.+)',
            r'добавить\s+(.+)',
            r'запланировать\s+(.+)',
            r'назначить\s+(.+)'
        ]
        
        for pattern in description_patterns:
            match = re.search(pattern, text)
            if match:
                description = match.group(1)
                # Удаляем лишние слова-триггеры из описания
                description = re.sub(r'^(задачу|заявку|работу)\s+', '', description)
                entities['description'] = description
                break
                
        # Поиск приоритета
        if any(word in text for word in ['срочно', 'важно', 'критично']):
            entities['priority'] = 'high'
        elif any(word in text for word in ['не срочно', 'потом', 'когда будет время']):
            entities['priority'] = 'low'
        else:
            entities['priority'] = 'normal'
    
    elif command_type == 'document_analysis':
        # Расширенный поиск типа документа
        doc_patterns = {
            'contract': r'(договор|контракт|соглашение)',
            'report': r'(отчет|справк[аи]|выписк[аи])',
            'invoice': r'(счет|счет-фактур[аы]|накладн[ая][яу])',
            'other': r'(документ|файл|бумаг[аи])'
        }
        
        for doc_type, pattern in doc_patterns.items():
            if re.search(pattern, text):
                entities['document_type'] = doc_type
                break
                
        # Поиск дополнительных параметров
        if re.search(r'за\s+(\d{4})\s*год', text):
            entities['year'] = re.search(r'за\s+(\d{4})\s*год', text).group(1)
    
    elif command_type == 'search':
        # Улучшенный поиск критериев
        search_patterns = [
            r'найти\s+(.+)',
            r'поиск\s+(.+)',
            r'искать\s+(.+)',
            r'где\s+(.+)',
            r'информаци[яю]\s+о\s+(.+)'
        ]
        
        for pattern in search_patterns:
            match = re.search(pattern, text)
            if match:
                entities['search_query'] = match.group(1)
                break
                
        # Определение категории поиска
        categories = {
            'person': r'(человек|сотрудник|работник)',
            'document': r'(документ|файл|договор)',
            'task': r'(задач|заявк|работ)'
        }
        
        for category, pattern in categories.items():
            if re.search(pattern, text):
                entities['category'] = category
                break
    
    return entities
