import logging
import re
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

class DialogContext:
    def __init__(self):
        self.context_history = []
        self.current_topic = None
        self.confidence_threshold = 0.6
        self.max_context_length = 5
        
        # Шаблоны команд для распознавания
        self.command_patterns = {
            'greeting': [
                'привет', 'здравствуй', 'добр', 'хай', 'hello'
            ],
            'task_creation': [
                'создать задачу', 'новая задача', 'добавить задачу',
                'запланировать', 'поставить задачу'
            ],
            'finance': [
                'финансы', 'бюджет', 'расходы', 'доходы', 'платеж',
                'счет', 'транзакция'
            ],
            'project': [
                'проект', 'создать проект', 'статус проекта',
                'обновить проект', 'завершить проект'
            ]
        }

        # Регистрация извлекателей сущностей для разных типов команд
        self.entity_extractors = {
            'task_creation': self._extract_task_details,
            'project': self._extract_project_details,
        }

    def update_context(self, command_type: str, entities: Dict) -> None:
        """Обновляет историю контекста"""
        context = {
            'command_type': command_type,
            'entities': entities,
            'timestamp': datetime.now()
        }
        self.context_history.append(context)
        
        # Ограничиваем размер истории контекста
        if len(self.context_history) > self.max_context_length:
            self.context_history.pop(0)

    def _clean_text(self, text: str) -> str:
        """Очищает и нормализует входной текст"""
        text = text.lower()
        text = text.replace('терра', '').replace('terra', '')
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def _calculate_command_confidence(self, text: str, patterns: List[str]) -> float:
        """Вычисляет уверенность в распознавании команды"""
        max_confidence = 0.0
        for pattern in patterns:
            if pattern in text:
                confidence = len(pattern) / len(text)
                max_confidence = max(max_confidence, confidence)
        return max_confidence

    def analyze_text(self, text: str) -> Tuple[str, Dict]:
        """Анализирует текст и возвращает тип команды и извлеченные сущности"""
        try:
            cleaned_text = self._clean_text(text)
            if not cleaned_text:
                return 'unknown', {}

            command_type = 'unknown'
            entities: Dict = {}
            confidence_scores = {}
            
            # Проверяем связь с предыдущим контекстом
            if self.context_history and self.current_topic:
                context_confidence = self._calculate_context_relevance(cleaned_text)
                if context_confidence > 0.5:  # Порог связанности контекста
                    entities['related_to'] = self.current_topic

            # Распознаем основной тип команды
            max_confidence = 0
            for intent, patterns in self.command_patterns.items():
                confidence = self._calculate_command_confidence(cleaned_text, patterns)
                confidence_scores[intent] = confidence
                if confidence > max_confidence:
                    max_confidence = confidence
                    if confidence > self.confidence_threshold:
                        command_type = intent

            # Извлекаем сущности на основе типа команды
            if command_type in self.entity_extractors:
                extracted_entities = self.entity_extractors[command_type](cleaned_text)
                entities.update(extracted_entities)
                
                # Дополнительное извлечение временных и числовых параметров
                time_entities = self._extract_time_entities(cleaned_text)
                numeric_entities = self._extract_numeric_entities(cleaned_text)
                entities.update(time_entities)
                entities.update(numeric_entities)
                
            elif command_type == 'greeting':
                entities['greeting'] = True
                hour = datetime.now().hour
                entities['time_of_day'] = (
                    'morning' if 5 <= hour < 12
                    else 'afternoon' if 12 <= hour < 17
                    else 'evening' if 17 <= hour < 23
                    else 'night'
                )

            # Обновляем контекст с новой информацией
            self.current_topic = command_type
            self.update_context(command_type, entities)
            
            logger.info(f"Recognized command type: {command_type}, Entities: {entities}")
            logger.debug(f"Confidence scores: {confidence_scores}")
            
            return command_type, entities

        except Exception as e:
            logger.error(f"Error analyzing text: {str(e)}", exc_info=True)
            return 'unknown', {'error': str(e)}

    def _calculate_context_relevance(self, text: str) -> float:
        """Вычисляет релевантность текста текущему контексту."""
        if not self.context_history:
            return 0.0
            
        last_context = self.context_history[-1]
        if 'entities' not in last_context:
            return 0.0
            
        # Проверяем связь с предыдущими сущностями
        relevant_words = set()
        for entity_value in last_context['entities'].values():
            if isinstance(entity_value, str):
                relevant_words.update(entity_value.lower().split())
            elif isinstance(entity_value, (list, tuple)):
                for item in entity_value:
                    if isinstance(item, str):
                        relevant_words.update(item.lower().split())
                        
        text_words = set(text.lower().split())
        common_words = relevant_words.intersection(text_words)
        
        if not relevant_words:
            return 0.0
            
        return len(common_words) / len(relevant_words)

    def _extract_time_entities(self, text: str) -> Dict:
        """Извлекает временные параметры из текста."""
        entities = {}
        
        # Поиск времени в формате ЧЧ:ММ
        time_patterns = [
            r'в (\d{1,2})[:\.](\d{2})',
            r'на (\d{1,2})[:\.](\d{2})',
            r'в (\d{1,2}) (\d{2})',
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, text)
            if match:
                hours, minutes = map(int, match.groups())
                if 0 <= hours <= 23 and 0 <= minutes <= 59:
                    entities['time'] = f"{hours:02d}:{minutes:02d}"
                    break
        
        # Поиск дат
        date_markers = {
            'сегодня': 0,
            'завтра': 1,
            'послезавтра': 2,
            'через неделю': 7,
            'через месяц': 30
        }
        
        for marker, days in date_markers.items():
            if marker in text:
                target_date = datetime.now() + timedelta(days=days)
                entities['date'] = target_date.strftime('%Y-%m-%d')
                break
                
        return entities

    def _extract_numeric_entities(self, text: str) -> Dict:
        """Извлекает числовые параметры из текста."""
        entities = {}
        
        # Поиск числовых значений с единицами измерения
        numeric_patterns = [
            (r'(\d+)\s*(рубл[яейь]|руб)', 'amount'),
            (r'(\d+)\s*(час[ао]в|час)', 'duration_hours'),
            (r'(\d+)\s*(минут[аы]?|мин)', 'duration_minutes'),
            (r'(\d+)\s*(шт[а-я]*|единиц[а-я]*)', 'quantity')
        ]
        
        for pattern, entity_name in numeric_patterns:
            match = re.search(pattern, text)
            if match:
                entities[entity_name] = int(match.group(1))
                
        return entities

    def _extract_task_details(self, text: str) -> Dict:
        """Извлекает детали задачи из текста."""
        entities = {}
        
        # Поиск описания задачи
        description_patterns = [
            r'задач[ау]?\s+(.+?)(?:\s+на\s+|$)',
            r'создать\s+(.+?)(?:\s+на\s+|$)',
            r'запланировать\s+(.+?)(?:\s+на\s+|$)'
        ]
        
        for pattern in description_patterns:
            match = re.search(pattern, text)
            if match:
                entities['description'] = match.group(1).strip()
                break
                
        # Определение приоритета
        if any(word in text.lower() for word in ['срочн', 'важн', 'критичн']):
            entities['priority'] = 'high'
        else:
            entities['priority'] = 'normal'
            
        return entities

    def _extract_project_details(self, text: str) -> Dict:
        """Извлекает детали проекта из текста."""
        entities = {}
        
        # Поиск названия проекта
        name_patterns = [
            r'проект[а]?\s+[""]?([^""]+)[""]?',
            r'создать проект\s+[""]?([^""]+)[""]?',
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, text)
            if match:
                entities['project_name'] = match.group(1).strip()
                break
                
        # Определение статуса проекта
        status_keywords = {
            'начать': 'new',
            'запустить': 'started',
            'завершить': 'completed',
            'закрыть': 'closed'
        }
        
        for keyword, status in status_keywords.items():
            if keyword in text.lower():
                entities['status'] = status
                break
                
        return entities
