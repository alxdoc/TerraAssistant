import logging
import re
from datetime import datetime
from typing import List, Dict, Tuple, Optional, Any
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DialogContext:
    def __init__(self):
        self.current_topic: Optional[str] = None
        self.context_history: List[Dict] = []
        self.confidence_threshold = 0.7
        self.command_patterns = {
            'task_creation': [
                'создать задачу', 'создай задачу', 'новая задача',
                'добавить задачу', 'поставить задачу', 'назначить задачу'
            ],
            'finance': [
                'финансы', 'доход', 'расход', 'баланс', 'бюджет',
                'платеж', 'счет', 'оплата', 'транзакция'
            ],
            'project': [
                'проект', 'создать проект', 'статус проекта',
                'обновить проект', 'завершить проект'
            ],
            'marketing': [
                'маркетинг', 'реклама', 'продвижение', 'анализ рынка',
                'целевая аудитория', 'маркетинговый план'
            ],
            'client': [
                'клиент', 'клиентская база', 'работа с клиентами',
                'обслуживание клиентов', 'лояльность клиентов'
            ],
            'greeting': [
                'привет', 'здравствуй', 'добрый день', 'доброе утро',
                'добрый вечер', 'приветствую'
            ]
        }
        self.entity_extractors = {  # Add entity extractors for more robust entity recognition.
            'task_creation': self._extract_task_details,
            'project': self._extract_project_details,
            # Add more entity extractors as needed...
        }


    def _clean_text(self, text: str) -> str:
        """Cleans text from unnecessary symbols and normalizes it."""
        text = re.sub(r't?[еэ]рр?а?[,]?\s*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\s+', ' ', text)
        text = text.strip('.,!?;:')
        return text.strip()

    def _calculate_command_confidence(self, text: str, patterns: List[str]) -> float:
        """Calculates the confidence in command recognition."""
        max_confidence = 0.0
        text = text.lower()
        for pattern in patterns:
            if pattern.lower() in text:
                max_confidence = 1.0
                break  # Exact match, no need to check further
            pattern_words = set(pattern.lower().split())
            text_words = set(text.split())
            common_words = pattern_words.intersection(text_words)
            if common_words:
                confidence = len(common_words) / max(len(pattern_words), len(text_words))
                max_confidence = max(max_confidence, confidence)
        return max_confidence

    def _update_context_history(self, context: Dict[str, Any]) -> None:
        """Updates the context history."""
        self.context_history.append(context)
        if len(self.context_history) > 10:
            self.context_history.pop(0)

    def update_context(self, command_type: str, entities: Dict) -> None:
        """Updates the current dialog context."""
        logger.debug(f"Updating context: {command_type}, Entities: {entities}")
        context = {
            'timestamp': datetime.now().isoformat(),
            'command_type': command_type,
            'entities': entities,
        }
        self._update_context_history(context)


    def analyze_text(self, text: str) -> Tuple[str, Dict]:
        """Analyzes text and returns intent and entities, considering context."""
        try:
            logger.debug(f"Analyzing text: {text}")
            cleaned_text = self._clean_text(text.lower().strip())
            command_type = 'unknown'
            entities: Dict = {}
            confidence_scores = {}

            for intent, patterns in self.command_patterns.items():
                confidence = self._calculate_command_confidence(cleaned_text, patterns)
                confidence_scores[intent] = confidence
                if confidence > self.confidence_threshold:
                    command_type = intent
                    break

            #Extract Entities based on command type
            if command_type in self.entity_extractors:
                extracted_entities = self.entity_extractors[command_type](cleaned_text)
                entities.update(extracted_entities)
            elif command_type == 'greeting':
                entities['greeting'] = True


            self.update_context(command_type, entities)
            logger.info(f"Recognized command type: {command_type}, Entities: {entities}")
            return command_type, entities

        except Exception as e:
            logger.error(f"Error analyzing text: {str(e)}", exc_info=True)
            return 'unknown', {'error': str(e)}

    def _extract_task_details(self, text: str) -> Dict:
        #Example - improve this to extract actual task details.
        match = re.search(r'задача (.*)', text)
        task_description = match.group(1) if match else "No description found"
        return {'task_description': task_description}

    def _extract_project_details(self, text:str) -> Dict:
        #Example - improve this to extract actual project details.
        match = re.search(r'проект (.*)', text)
        project_name = match.group(1) if match else "No project name found"
        return {'project_name': project_name}