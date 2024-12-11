const CommandTypes = {
    TASK_CREATION: 'task_creation',
    DOCUMENT_ANALYSIS: 'document_analysis',
    SEARCH: 'search',
    CALENDAR: 'calendar',
    CONTACT: 'contact',
    REMINDER: 'reminder',
    FINANCE: 'finance',
    PROJECT: 'project',
    SALES: 'sales',
    INVENTORY: 'inventory',
    ANALYTICS: 'analytics',
    EMPLOYEE: 'employee',
    MEETING: 'meeting',
    GREETING: 'greeting',
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
        'найди информацию',
        'поищи'
    ],
    [CommandTypes.REPORT]: [
        'отчет',
        'статистика',
        'показать данные',
        'сводка',
        'итоги',
        'результаты за',
        'сформировать отчет'
    ],
    [CommandTypes.CALENDAR]: [
        'календарь',
        'расписание',
        'встреча',
        'запланировать встречу',
        'добавить в календарь',
        'показать расписание'
    ],
    [CommandTypes.CONTACT]: [
        'контакт',
        'добавить контакт',
        'найти контакт',
        'информация о человеке',
        'данные сотрудника',
        'телефон'
    ],
    [CommandTypes.REMINDER]: [
        'напомнить',
        'установить напоминание',
        'поставить будильник',
        'не забыть',
        'запомнить'
    ],
    [CommandTypes.FINANCE]: [
        'финансы',
        'баланс',
        'бюджет',
        'расходы',
        'доходы',
        'платеж',
        'счет',
        'транзакция'
    ],
    [CommandTypes.PROJECT]: [
        'проект',
        'создать проект',
        'статус проекта',
        'обновить проект',
        'завершить проект',
        'команда проекта'
    ],
    [CommandTypes.SALES]: [
        'продажи',
        'новая сделка',
        'клиент',
        'заказ',
        'оформить продажу',
        'воронка продаж',
        'выставить счет'
    ],
    [CommandTypes.INVENTORY]: [
        'склад',
        'товары',
        'остатки',
        'проверить наличие',
        'заказать товар',
        'инвентаризация'
    ],
    [CommandTypes.ANALYTICS]: [
        'аналитика',
        'анализ данных',
        'тренды',
        'прогноз',
        'показатели',
        'метрики',
        'эффективность'
    ],
    [CommandTypes.EMPLOYEE]: [
        'сотрудник',
        'персонал',
        'штат',
        'отпуск',
        'график работы',
        'зарплата',
        'оценка работы'
    ],
    [CommandTypes.MEETING]: [
        'совещание',
        'организовать встречу',
        'запланировать звонок',
        'конференция',
        'презентация',
        'брифинг'
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
    text = text.replace(/терра|terra/gi, '').trim();
    console.log('Text after removing keyword:', text);
    
    // Проверяем на приветствие перед основной обработкой
    const greetings = ['привет', 'здравствуй', 'добр', 'хай', 'hello'];
    for (const greeting of greetings) {
        if (text.toLowerCase().startsWith(greeting)) {
            console.log('Greeting detected:', text);
            return 'greeting';
        }
    }
    
    // Проверяем каждый тип команды
    for (const [type, patterns] of Object.entries(CommandPatterns)) {
        console.log(`Checking patterns for type ${type}:`, patterns);
        for (const pattern of patterns) {
            // Используем улучшенное сравнение строк
            if (compareStrings(text, pattern)) {
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

// Улучшенная функция для сравнения строк с поддержкой русского языка
function compareStrings(str1, str2) {
    // Нормализуем строки
    str1 = str1.toLowerCase()
        .replace(/ё/g, 'е')
        .replace(/[^а-яa-z0-9\s]/g, '')
        .trim();
    str2 = str2.toLowerCase()
        .replace(/ё/g, 'е')
        .replace(/[^а-яa-z0-9\s]/g, '')
        .trim();

    // Если строки короткие, используем точное сравнение
    if (str1.length < 4 || str2.length < 4) {
        return str1 === str2;
    }

    // Для длинных строк используем расстояние Левенштейна
    const maxDistance = Math.floor(Math.max(str1.length, str2.length) * 0.3); // 30% tolerance
    return levenshteinDistance(str1, str2) <= maxDistance;
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
