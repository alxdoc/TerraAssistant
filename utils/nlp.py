import re
from typing import Tuple, Dict

def analyze_text(text: str) -> Tuple[str, Dict]:
    """
    Анализирует текст команды и определяет её тип и сущности
    """
    text = text.lower()
    
    # Базовые шаблоны команд
    patterns = {
        'task_creation': r'(созда|добав|нов[ыа])(ть|я)?\s+(задач|заявк)',
        'document_analysis': r'(проверить|анализ|проверка)\s+(документ|договор)',
        'search': r'(найти|поиск|искать)',
        'report': r'(отчет|статистика|данные)',
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
    """
    entities = {}
    
    if command_type == 'task_creation':
        # Поиск описания задачи
        description_match = re.search(r'задач[уа]\s+(.+)', text)
        if description_match:
            entities['description'] = description_match.group(1)
    
    elif command_type == 'document_analysis':
        # Поиск типа документа
        doc_type_match = re.search(r'(документ|договор|смет[уа])', text)
        if doc_type_match:
            entities['document_type'] = doc_type_match.group(1)
    
    elif command_type == 'search':
        # Поиск критериев поиска
        search_match = re.search(r'(найти|поиск|искать)\s+(.+)', text)
        if search_match:
            entities['search_query'] = search_match.group(2)
    
    return entities
