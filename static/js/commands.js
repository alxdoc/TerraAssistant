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

// Улучшенная функция определения типа команды
function detectCommandType(text) {
    text = normalizeText(text);
    
    // Проверяем каждый тип команды
    for (const [type, patterns] of Object.entries(CommandPatterns)) {
        if (patterns.some(pattern => text.includes(normalizeText(pattern)))) {
            return type;
        }
    }
    
    return CommandTypes.UNKNOWN;
}
