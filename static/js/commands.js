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
        'добавить заявку'
    ],
    [CommandTypes.DOCUMENT_ANALYSIS]: [
        'проверить документ',
        'анализ документа',
        'проверка договора'
    ],
    [CommandTypes.SEARCH]: [
        'найти',
        'поиск',
        'искать'
    ],
    [CommandTypes.REPORT]: [
        'отчет',
        'статистика',
        'показать данные'
    ]
};

function detectCommandType(text) {
    text = text.toLowerCase();
    
    for (const [type, patterns] of Object.entries(CommandPatterns)) {
        if (patterns.some(pattern => text.includes(pattern))) {
            return type;
        }
    }
    
    return CommandTypes.UNKNOWN;
}
