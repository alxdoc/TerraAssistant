// Типы команд
const CommandTypes = {
    TASK_CREATION: 'task_creation',
    MARKETING: 'marketing',
    CLIENT: 'client',
    SUPPLIER: 'supplier',
    CONTRACT: 'contract',
    QUALITY: 'quality',
    RISK: 'risk',
    STRATEGY: 'strategy',
    COMPLIANCE: 'compliance',
    INNOVATION: 'innovation',
    DOCUMENT: 'document_analysis',
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

// Шаблоны команд для распознавания
const CommandPatterns = {
    [CommandTypes.TASK_CREATION]: [
        'создать задачу',
        'новая задача',
        'добавить заявку',
        'запланировать',
        'поставить задачу',
        'назначить задание'
    ],
    [CommandTypes.MARKETING]: [
        'маркетинг',
        'рекламная кампания',
        'продвижение',
        'анализ рынка',
        'целевая аудитория',
        'маркетинговый план',
        'бренд',
        'социальные сети'
    ],
    [CommandTypes.CLIENT]: [
        'клиентская база',
        'клиенты',
        'работа с клиентами',
        'обслуживание клиентов',
        'лояльность клиентов',
        'обратная связь',
        'клиентский опыт'
    ],
    [CommandTypes.SUPPLIER]: [
        'поставщики',
        'управление поставками',
        'закупки',
        'оценка поставщиков',
        'договор поставки',
        'логистика',
        'цепочка поставок'
    ],
    [CommandTypes.CONTRACT]: [
        'договор',
        'контракт',
        'соглашение',
        'условия договора',
        'подписание договора',
        'расторжение договора',
        'дополнительное соглашение'
    ],
    [CommandTypes.QUALITY]: [
        'качество',
        'контроль качества',
        'управление качеством',
        'стандарты качества',
        'улучшение качества',
        'оценка качества',
        'система качества'
    ],
    [CommandTypes.RISK]: [
        'риски',
        'управление рисками',
        'оценка рисков',
        'минимизация рисков',
        'анализ рисков',
        'риск-менеджмент',
        'страхование рисков'
    ],
    [CommandTypes.STRATEGY]: [
        'стратегия',
        'стратегическое планирование',
        'развитие бизнеса',
        'долгосрочные цели',
        'бизнес-план',
        'конкурентная стратегия',
        'стратегические инициативы'
    ],
    [CommandTypes.COMPLIANCE]: [
        'соответствие',
        'нормативы',
        'регуляторные требования',
        'compliance',
        'аудит соответствия',
        'правовые требования',
        'стандарты compliance'
    ],
    [CommandTypes.INNOVATION]: [
        'инновации',
        'инновационные проекты',
        'технологическое развитие',
        'цифровая трансформация',
        'новые технологии',
        'модернизация',
        'оптимизация процессов'
    ],
    [CommandTypes.DOCUMENT]: [
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
        'покажи информацию',
        'найди данные',
        'поищи'
    ],
    [CommandTypes.CALENDAR]: [
        'календарь',
        'расписание',
        'встреча',
        'запланировать встречу',
        'добавить в календарь'
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
        'транзакция',
        'оплата',
        'выставить счет'
    ],
    [CommandTypes.PROJECT]: [
        'проект',
        'создать проект',
        'статус проекта',
        'обновить проект',
        'завершить проект',
        'команда проекта',
        'план проекта'
    ],
    [CommandTypes.SALES]: [
        'продажи',
        'новая сделка',
        'клиент',
        'заказ',
        'оформить продажу',
        'воронка продаж',
        'выставить счет',
        'статус сделки',
        'потенциальный клиент'
    ],
    [CommandTypes.INVENTORY]: [
        'склад',
        'товары',
        'остатки',
        'проверить наличие',
        'заказать товар',
        'инвентаризация',
        'поставка',
        'приход товара',
        'отгрузка'
    ],
    [CommandTypes.ANALYTICS]: [
        'аналитика',
        'анализ данных',
        'тренды',
        'прогноз',
        'показатели',
        'метрики',
        'эффективность',
        'отчет по продажам',
        'статистика',
        'динамика продаж'
    ],
    [CommandTypes.EMPLOYEE]: [
        'сотрудник',
        'персонал',
        'штат',
        'отпуск',
        'график работы',
        'зарплата',
        'оценка работы',
        'повышение',
        'обучение',
        'компетенции'
    ],
    [CommandTypes.MEETING]: [
        'совещание',
        'организовать встречу',
        'запланировать звонок',
        'конференция',
        'презентация',
        'брифинг',
        'переговоры'
    ],
    [CommandTypes.GREETING]: [
        'привет',
        'здравствуй',
        'добрый день',
        'доброе утро',
        'добрый вечер',
        'приветствую'
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
            return CommandTypes.GREETING;
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
