const CommandTypes = {
    TASK_CREATION: 'task_creation',
    DOCUMENT_ANALYSIS: 'document_analysis',
    SEARCH: 'search',
    REPORT: 'report',
    UNKNOWN: 'unknown'
};

const CommandPatterns = {
    [CommandTypes.TASK_CREATION]: [
        'создать задачу',
        'новая задача',
        'добавить заявку',
        'запланировать',
        'поставить задачу',
        'назначить задание'
    ],
    [CommandTypes.DOCUMENT_ANALYSIS]: [
        'проверить документ',
        'анализ документа',
        'проверка договора',
        'изучить документ',
        'просмотреть контракт',
        'проанализировать соглашение'
    ],
    [CommandTypes.SEARCH]: [
        'найти',
        'поиск',
        'искать',
        'где находится',
        'покажи информацию о',
        '查找' // добавляем поддержку китайского для демонстрации мультиязычности
    ],
    [CommandTypes.REPORT]: [
        'отчет',
        'статистика',
        'показать данные',
        'сводка',
        'итоги',
        'результаты за',
        'сформировать отчет'
    ]
};

// Дополнительные служебные функции для улучшения распознавания
function normalizeText(text) {
    return text.toLowerCase()
        .replace(/ё/g, 'е')
        .replace(/\s+/g, ' ')
        .trim();
}

// Улучшенная функция определения типа команды с поддержкой частичного совпадения
function detectCommandType(text) {
    text = normalizeText(text);
    console.log('Detecting command type for:', text);
    
    // Удаляем ключевое слово "терра" из текста, если оно есть
    text = text.replace(/терра/gi, '').trim();
    console.log('Text after removing keyword:', text);
    
    // Проверяем каждый тип команды
    for (const [type, patterns] of Object.entries(CommandPatterns)) {
        console.log(`Checking patterns for type ${type}:`, patterns);
        for (const pattern of patterns) {
            const normalizedPattern = normalizeText(pattern);
            // Используем более гибкое сравнение
            if (text.includes(normalizedPattern) || 
                normalizedPattern.includes(text) ||
                levenshteinDistance(text, normalizedPattern) <= 2) {
                console.log(`Match found for type ${type} with pattern:`, pattern);
                return type;
            }
        }
    }
    
    // Проверяем на приветствие
    if (text.match(/^(привет|здравствуй|добр[ыое][йе]|хай)/)) {
        return 'greeting';
    }
    
    console.log('No matching command type found, returning unknown');
    return CommandTypes.UNKNOWN;
}

// Функция для вычисления расстояния Левенштейна
function levenshteinDistance(a, b) {
    if (a.length === 0) return b.length;
    if (b.length === 0) return a.length;

    const matrix = [];

    for (let i = 0; i <= b.length; i++) {
        matrix[i] = [i];
    }

    for (let j = 0; j <= a.length; j++) {
        matrix[0][j] = j;
    }

    for (let i = 1; i <= b.length; i++) {
        for (let j = 1; j <= a.length; j++) {
            if (b.charAt(i - 1) === a.charAt(j - 1)) {
                matrix[i][j] = matrix[i - 1][j - 1];
            } else {
                matrix[i][j] = Math.min(
                    matrix[i - 1][j - 1] + 1,
                    matrix[i][j - 1] + 1,
                    matrix[i - 1][j] + 1
                );
            }
        }
    }

    return matrix[b.length][a.length];
}
