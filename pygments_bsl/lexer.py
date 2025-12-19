from pygments.lexer import RegexLexer, words, bygroups, using
from pygments.token import Token

from functools import lru_cache
import re
import copy

from .generated_data import (
    ENUM_PROPERTY_NAMES,
    GLOBAL_METHOD_NAMES,
    GLOBAL_PROPERTY_NAMES,
    TYPE_NAMES,
)

PREFIX_NO_DOT = r'(?<!\.)'
SUFFIX_WORD = r'\b'
SUFFIX_CALL = r'(?=(\s?[\(]))'
IDENT = r'[A-Za-zА-Яа-яЁё_][\wа-яё0-9_]*'
IDENT_RE = re.compile(r'^' + IDENT + r'$', re.IGNORECASE)

@lru_cache(maxsize=4096)
def _casefold(text):
    return text.casefold()

def _casefold_set(items):
    return {_casefold(item) for item in items}

def _is_call(text, end_pos):
    pos = end_pos
    length = len(text)
    while pos < length and text[pos].isspace():
        pos += 1
    return pos < length and text[pos] == '('

def _call_has_args(text, end_pos):
    pos = end_pos
    length = len(text)
    while pos < length and text[pos].isspace():
        pos += 1
    if pos >= length or text[pos] != '(':
        return False
    pos += 1
    while pos < length and text[pos].isspace():
        pos += 1
    return pos < length and text[pos] != ')'

def _bsl_name_callback(lexer, match):
    name = match.group(0)
    name_cf = _casefold(name)
    is_call = _is_call(match.string, match.end())

    if name_cf in lexer._bsl_exception_names:
        yield match.start(), Token.Name.Exception, name
        return

    if name_cf in lexer._bsl_keyword_as_function and is_call:
        yield match.start(), Token.Name.Builtin, name
        return

    if name_cf in lexer._bsl_call_only_builtins:
        yield match.start(), (Token.Name.Builtin if is_call else Token.Name.Variable), name
        return

    if name_cf in lexer._bsl_keyword_declaration:
        yield match.start(), Token.Keyword.Declaration, name
        return

    if name_cf in lexer._bsl_keyword_constant:
        yield match.start(), Token.Keyword.Constant, name
        return

    if name_cf in lexer._bsl_keyword:
        yield match.start(), Token.Keyword, name
        return

    if name_cf in lexer._bsl_name_builtin:
        yield match.start(), Token.Name.Builtin, name
        return

    if name_cf in lexer._bsl_name_class:
        yield match.start(), Token.Name.Class, name
        return

    yield match.start(), (Token.Name.Function if is_call else Token.Name.Variable), name

def _sdbl_name_callback(lexer, match):
    name = match.group(0)
    name_cf = _casefold(name)
    is_call = _is_call(match.string, match.end())

    if name_cf in lexer._sdbl_function_call and is_call:
        yield match.start(), Token.Name.Builtin, name
        return

    if name_cf in lexer._sdbl_keyword_constant:
        yield match.start(), Token.Keyword.Constant, name
        return

    if name_cf in lexer._sdbl_keyword_declaration:
        yield match.start(), Token.Keyword.Declaration, name
        return

    if name_cf in lexer._sdbl_name_class:
        yield match.start(), Token.Name.Class, name
        return

    yield match.start(), Token.Name.Variable, name

def _sdbl_metadata_callback(lexer, match):
    text = match.group(0)
    parts = text.split('.')
    pos = match.start()
    has_error = False

    root = parts[0]
    root_cf = _casefold(root)
    is_call = _is_call(match.string, match.end())
    has_args = _call_has_args(match.string, match.end())

    root_token = Token.Name.Namespace
    if root_cf == _casefold('РегистрСведений') and len(parts) >= 3 and is_call and has_args:
        root_token = Token.Name.Class

    yield pos, root_token, root
    pos += len(root)

    for idx, segment in enumerate(parts[1:], start=1):
        yield pos, Token.Operator, '.'
        pos += 1

        if IDENT_RE.fullmatch(segment):
            if idx == len(parts) - 1 and is_call:
                seg_token = Token.Name.Function
            elif has_error:
                seg_token = Token.Name.Variable
            else:
                seg_token = Token.Name.Class
            yield pos, seg_token, segment
        else:
            yield pos, Token.Generic.Error, segment
            has_error = True
        pos += len(segment)

def _locale_assignment_callback(lexer, match):
    yield match.start(), Token.Name.Attribute, match.group(1)
    if match.group(2):
        yield match.start(2), Token.String, match.group(2)
    yield match.start(3), Token.Operator, match.group(3)

CALL_ONLY_BUILTINS = {
    'Булево','Boolean','Число','Number','Строка','String','Дата','Date',
}
CONSTANT_NAMES = (
    'Неопределено','Undefined','Истина','True','Ложь','False','NULL'
)

class BslLexer(RegexLexer):
    name = '1C (BSL) Lexer'
    aliases = ['bsl', 'os']
    filenames = ['*.bsl', '*.os']

    flags = re.MULTILINE | re.IGNORECASE | re.VERBOSE

    _KEYWORD_DECLARATION_WORDS = (
        # storage.type.var.bsl
        'Перем','Var',
    )

    _KEYWORD_WORDS = (
        'Процедура','Procedure','Функция','Function',
        'Экспорт', 'Export',
        'КонецПроцедуры','EndProcedure','КонецФункции','EndFunction',
        'Прервать','Break','Продолжить','Continue','Возврат','Return',
        'Если','If','Иначе','Else','ИначеЕсли','ElsIf',
        'Тогда','Then','КонецЕсли','EndIf',
        'Попытка','Try','Исключение','Except',
        'КонецПопытки','EndTry',
        'Пока','While','Для','For','Каждого','Each',
        'Из','In','По','To','Цикл','Do','КонецЦикла', 'EndDo',
        'НЕ','NOT','И','AND','ИЛИ','OR',
        'Новый','New',
        'Выполнить','Execute',
        'Знач', 'Val',
        'Перейти', 'Goto',
        'Асинх', 'Async',
        'Ждать', 'Await',
    )
    
    NAME_CLASS_NAMES = tuple(dict.fromkeys(GLOBAL_PROPERTY_NAMES))

    _NAME_CLASS_WORDS = tuple(
        name for name in NAME_CLASS_NAMES
        if name not in CALL_ONLY_BUILTINS and name not in CONSTANT_NAMES
    )

    _NAME_BUILTIN_WORDS = tuple(
        name for name in dict.fromkeys(GLOBAL_METHOD_NAMES)
        if name not in CALL_ONLY_BUILTINS
    )

    _KEYWORD_CONSTANT_WORDS = CONSTANT_NAMES

    _KEYWORD_EXCEPTION_WORDS = (
        'ВызватьИсключение','Raise',
    )

    # keywords that also used as function-like calls (treat as builtin when followed by '(')
    _KEYWORD_AS_FUNCTION_WORDS = (
        'Новый','New',
    )

    EXECUTE_STRING_CALL = r'(?<!\.)\b(Выполнить|Execute)\b(?=\s*\(\s*"Выполнить)'
    QUERY_STRING_START = r'"(?=[^"]*\b(ВЫБРАТЬ|SELECT)\b)(?![^"]*(?:\r?\n)\#(?:Удаление|КонецУдаления|Delete|EndDelete))'

    TYPE_NAME_PATTERN = r'(?:' + '|'.join(re.escape(n) for n in TYPE_NAMES) + r')'

    OPERATORS = words((
        '=','<=','>=','<>','<','>','+','-','*','/','%','.'
    ))

    METADATA_ROOT = r'(?:' + '|'.join([
        'WebСервисы',
        'WSСсылки',
        'БизнесПроцессы',
        'ГруппыКоманд',
        'Документы',
        'ЖурналыДокументов',
        'Задачи',
        'Интерфейсы',
        'Константы',
        'КритерииОтбора',
        'НумераторыДокументов',
        'Обработки',
        'ОбщиеКартинки',
        'ОбщиеКоманды',
        'ОбщиеМакеты',
        'ОбщиеМодули',
        'ОбщиеФормы',
        'Отчеты',
        'ПакетыXDTO',
        'ПараметрыСеанса',
        'ПараметрыФункциональныхОпций',
        'Перечисления',
        'ПланыВидовРасчета',
        'ПланыВидовХарактеристик',
        'ПланыОбмена',
        'ПланыСчетов',
        'ПодпискиНаСобытия',
        'Последовательности',
        'РегистрыБухгалтерии',
        'РегистрыНакопления',
        'РегистрыРасчета',
        'РегистрыСведений',
        'РегламентныеЗадания',
        'Роли',
        'Справочники',
        'Стили',
        'ФункциональныеОпции',
        'ХранилищаНастроек',
        'ЭлементыСтиля',
        'Языки',
        # preserve existing english alias
        'Catalogs',
    ]) + r')'

    # see https://pygments.org/docs/tokens
    _bsl_keyword_declaration = _casefold_set(_KEYWORD_DECLARATION_WORDS)
    _bsl_keyword = _casefold_set(_KEYWORD_WORDS)
    _bsl_keyword_constant = _casefold_set(_KEYWORD_CONSTANT_WORDS)
    _bsl_exception_names = _casefold_set(_KEYWORD_EXCEPTION_WORDS)
    _bsl_keyword_as_function = _casefold_set(_KEYWORD_AS_FUNCTION_WORDS)
    _bsl_call_only_builtins = _casefold_set(CALL_ONLY_BUILTINS)
    _bsl_name_builtin = _casefold_set(_NAME_BUILTIN_WORDS)
    _bsl_name_class = _casefold_set(_NAME_CLASS_WORDS)
    _bsl_keyword_constant_pattern = words(CONSTANT_NAMES, prefix=PREFIX_NO_DOT, suffix=SUFFIX_WORD)

    tokens = {
        'root': [
            (r'\ufeff', Token.Text),
            (r'\r\n?|\n', Token.Text),
            (r'[^\S\n]+', Token.Text),
            (r'\#\!.*?(?=\n|$)', Token.Comment.Preproc),
            (r'\/\/.*?(?=\n)', Token.Comment.Single),
            (r'\#(Использовать|Use)\b', Token.Comment.Preproc, 'preproc_use'),
            (r'\#(native)\b.*', Token.Comment.Preproc),
            (r'\#(Если|If)\b', Token.Comment.Preproc, 'preproc_if'),
            (r'\#(ИначеЕсли|ElsIf)\b', Token.Comment.Preproc, 'preproc_if'),
            (r'\#(Иначе|Else|КонецЕсли|EndIf|Область|Region|КонецОбласти|EndRegion|Вставка|Insert|КонецВставки|EndInsert|Удаление|Delete|КонецУдаления|EndDelete)\b.*', Token.Comment.Preproc),
            # decorator with quoted name: split into decorator, punctuation and inner name
            (r'(&[\wа-яё_][\wа-яё0-9_]*)\s*(\()\s*"([^"]*)"\s*(\))',
             bygroups(Token.Name.Decorator, Token.Punctuation, Token.Name.Function, Token.Punctuation)),
            # decorator with parameters: split decorator and parse parameters
            (r'(&[\wа-яё_][\wа-яё0-9_]*)\s*(\()', bygroups(Token.Name.Decorator, Token.Punctuation), 'decorator_params'),
            (r'(Новый|New)(\s+)(' + TYPE_NAME_PATTERN + r')\b',
             bygroups(Token.Keyword, Token.Text, Token.Name.Class)),
            (rf'({METADATA_ROOT})(\.)({IDENT})(\.)', bygroups(Token.Name.Namespace, Token.Operator, Token.Name.Class, Token.Operator)),
            (r'[\[\]:(),;]', Token.Punctuation),
            (r'\&.*$', Token.Name.Decorator),
            (r'\b(Процедура|Функция|Procedure|Function)\b(\s+)([\wа-яё_][\wа-яё0-9_]*)\s*(\()',
             bygroups(Token.Keyword, Token.Text, Token.Name.Function, Token.Punctuation), 'params'),
            (OPERATORS, Token.Operator),
            (r'\#.*$', Token.Comment.Preproc),
            # match forbidden-constant calls like Неопределено(....) as a single error token
            (r'\b(?:' + '|'.join(CONSTANT_NAMES) + r')\b\s*\([^\)]*\)', Token.Generic.Error),
            (EXECUTE_STRING_CALL, Token.Name.Builtin),
            (rf'(?<=\.){IDENT}(?=\s*\()', Token.Name.Function),
            (rf'(?<=\.){IDENT}', Token.Name.Variable),
            (rf'{PREFIX_NO_DOT}{IDENT}', _bsl_name_callback),
            (r'\b\d+\.?\d*\b', Token.Literal.Number),
            (QUERY_STRING_START, Token.Literal.String, 'query_string'),
            (r'"(?=(?:[^"]|"")*\b(?:ru|en)\b\s*=)', Token.String, 'string_locale'),
            ('\"', Token.String, 'string'),
            (r'\'.*?\'', Token.Literal.Date),
            (r'~.*?(?=[:;])', Token.Name.Label),
        ],
        'preproc_if': [
            (r'\r\n?|\n', Token.Text, '#pop'),
            (r'\b(Сервер|НаСервере|Клиент|НаКлиенте|ТонкийКлиент|МобильныйКлиент|ВебКлиент|ВнешнееСоединение|ТолстыйКлиентУправляемоеПриложение|ТолстыйКлиентОбычноеПриложение|МобильныйАвтономныйСервер|МобильноеПриложениеКлиент|МобильноеПриложениеСервер|Windows|Linux|MacOS)\b', Token.Keyword.Constant),
            (r'\b(И|Или|НЕ|Then|Тогда|And|Or|Not)\b', Token.Comment.Preproc),
            (r'\#', Token.Comment.Preproc),
            (r'[^\S\n]+', Token.Text),
            (r'[^\s#]+', Token.Comment.Preproc),
        ],
        'preproc_use': [
            (r'\r\n?|\n', Token.Text, '#pop'),
            (r'[^\S\n]+', Token.Text),
            (r'"[^"]*"', Token.Literal.String),
            (r'[^\s#]+', Token.Name.Variable),
        ],
        'string': [
            ('\"(?![\"])', Token.String, '#pop'),
            (r'\r\n?|\n', Token.Text),
            (r'(?<=\n)[^\S\n]+', Token.Text),
            (r'(?<=[^\S\n])\/\/.*?(?=\n)', Token.Comment.Single),
            (r'\#(Удаление|Delete|КонецУдаления|EndDelete)\b.*', Token.Comment.Preproc),
            (r'(?<=^)\/\/.*?(?=\n)', Token.Comment.Single),
            (r'\|', Token.String),
            (r'\"\"', Token.String.Escape),
            (r"\\'", Token.String.Escape),
            (r'%\d', Token.String.Interpol),
            (r'%%', Token.String.Escape),
            (r'%[A-Za-zА-Яа-яЁё_]', Token.Generic.Error),
            (r'(?:\\(?!\')|%(?![%\dA-Za-zА-Яа-яЁё_])|[^\"\|\n%\\])+', Token.String),
        ],
        'string_locale': [
            ('\"(?![\"])', Token.String, '#pop'),
            (r'\r\n?|\n', Token.Text),
            (r'(?<=\n)[^\S\n]+', Token.Text),
            (r'(?<=[^\S\n])\/\/.*?(?=\n)', Token.Comment.Single),
            (r'(?<=^)\/\/.*?(?=\n)', Token.Comment.Single),
            (r'\|', Token.String),
            (r'\"\"', Token.String.Escape),
            (r"\\'", Token.String.Escape),
            (r'%\d', Token.String.Interpol),
            (r'%%', Token.String.Escape),
            (r'%[A-Za-zА-Яа-яЁё_]', Token.Generic.Error),
            (r'(\b(?:ru|en)\b)(\s*)(=)', _locale_assignment_callback),
            (r';', Token.Operator),
            (r'(?:(?!\b(?:ru|en)\b\s*=)(?:\\(?!\')|%(?![%\dA-Za-zА-Яа-яЁё_])|[^\"\|\n%\\;]))+', Token.String),
        ],
        'query_string': [
            (r'""', Token.Literal.String.Escape),
            (r'"', Token.Literal.String, '#pop'),
            # Delay instantiation to avoid forward reference issues and keep formatter options
            (r'[^"]+', using(lambda **kwargs: SdblQueryLexer(**kwargs))),
        ],
        'decorator_params': [
            (r'\)', Token.Punctuation, '#pop'),
            (r'\r\n?|\n', Token.Text),
            (r'[^\S\n]+', Token.Text),
            (r',', Token.Operator),
            (r'=', Token.Operator),
            (r'"[^"]*"', Token.Literal.String),
            (r'(\b[A-Za-zА-Яа-яёЁ_][\wа-яё0-9_]*\b)(\s*)(=)(\s*)(?!Неопределено\b|Undefined\b|Null\b|Истина\b|True\b|Ложь\b|False\b)([A-Za-zА-Яа-яёЁ_][\wа-яё0-9_]*)',
             bygroups(Token.Name.Variable, Token.Text, Token.Operator, Token.Text, Token.Generic.Error)),
            (r'([A-Za-zА-Яа-яёЁ_][\wа-яё0-9_]*)', Token.Name.Variable),
            (r'\b\d+\.?\d*\b', Token.Literal.Number),
            (QUERY_STRING_START, Token.Literal.String, 'query_string'),
            (r'.', Token.Text),
        ],
        'params': [
            (r'\)', Token.Punctuation, '#pop'),
            (r'\r\n?|\n', Token.Text),
            (r'[^\S\n]+', Token.Text),
            (r'\,', Token.Punctuation),
            (r'(&[\wа-яё_][\wа-яё0-9_]*)\s*(\()', bygroups(Token.Name.Decorator, Token.Punctuation), 'decorator_params'),
            (r'\&[^\s,(]+', Token.Name.Decorator),
            (r'\bЗнач\b|\bVal\b', Token.Keyword),
            (_bsl_keyword_constant_pattern, Token.Keyword.Constant),
            (r'(\b[A-Za-zА-Яа-яёЁ_][\wа-яё0-9_]*\b)(\s*)(=)(\s*)(?!Неопределено\b|Undefined\b|Null\b|Истина\b|True\b|Ложь\b|False\b)([A-Za-zА-Яа-яёЁ_][\wа-яё0-9_]*)',
             bygroups(Token.Name.Variable, Token.Text, Token.Operator, Token.Text, Token.Generic.Error)),
            (r'([A-Za-zА-Яа-яёЁ_][\wа-яё0-9_]*)', Token.Name.Variable),
            (r'=', Token.Operator),
            (r'\b\d+\.?\d*\b', Token.Literal.Number),
            (QUERY_STRING_START, Token.Literal.String, 'query_string'),
            (r'.', Token.Text),
        ],
        # String.Regex
    }




class SdblLexer(RegexLexer):
    name = '1C (SDBL) Lexer'
    aliases = ['sdbl']
    filenames = ['*.sdbl']

    flags = re.MULTILINE | re.IGNORECASE | re.VERBOSE

    _KEYWORD_DECLARATION_WORDS = (
        'ДЛЯ ИЗМЕНЕНИЯ','FOR UPDATE',
        'ИТОГИ ПО','TOTALS BY',
        'ИНДЕКСИРОВАТЬ ПО','INDEX BY','ИНДЕКСИРОВАТЬ ПО НАБОРАМ','INDEX BY SETS',
        'СГРУППИРОВАТЬ ПО','GROUP BY',
        'СОЕДИНЕНИЕ ПО','JOIN ON',
        'УПОРЯДОЧИТЬ ПО','ORDER BY',
        'АВТОНОМЕРЗАПИСИ','RECORDAUTONUMBER',
        'АВТОУПОРЯДОЧИВАНИЕ','AUTOORDER',
        'БУЛЕВО','BOOLEAN',
        'В','IN',
        'ВНЕШНЕЕ','OUTER',
        'ВНУТРЕННЕЕ','INNER',
        'ВОЗР','ASC',
        'ВСЕ','ALL',
        'ВЫБОР','CASE',
        'ВЫБРАТЬ','SELECT',
        'ВЫРАЗИТЬ','CAST',
        'ГДЕ','WHERE',
        'ГОД','YEAR',
        'ГРУППИРУЮЩИМ','GROUPING',
        'ДАТА','DATE',
        'ДАТАВРЕМЯ','DATETIME',
        'ДЕКАДА','TENDAYS',
        'ДЕНЬ','DAY',
        'ДЕНЬГОДА','DAYOFYEAR',
        'ДЕНЬНЕДЕЛИ','WEEKDAY',
        'ДЛЯ','FOR',
        'ДОБАВИТЬ','ADD',
        'ДОБАВИТЬКДАТЕ','DATEADD',
        'ЕСТЬ','IS',
        'ЕСТЬNULL','ISNULL',
        'Значение','VALUE',
        'И','AND',
        'ИЕРАРХИИ','HIERARCHY',
        'ИЕРАРХИЯ','HIERARCHY',
        'ИЗ','FROM',
        'ИЗМЕНЕНИЯ','UPDATE',
        'ИЛИ','OR',
        'ИМЕЮЩИЕ','HAVING',
        'ИНАЧЕ','ELSE',
        'ИНДЕКСИРОВАТЬ','INDEX',
        'ИТОГИ','TOTALS',
        'КАК','AS',
        'КВАРТАЛ','QUARTER',
        'КОГДА','WHEN',
        'КОЛИЧЕСТВО','COUNT',
        'КОНЕЦ','END',
        'КОНЕЦПЕРИОДА','ENDOFPERIOD',
        'ЛЕВОЕ','LEFT',
        'МАКСИМУМ','MAX',
        'МЕЖДУ','BETWEEN',
        'МЕСЯЦ','MONTH',
        'МИНИМУМ','MIN',
        'МИНУТА','MINUTE',
        'НАБОРАМ','SETS',
        'НАЧАЛОПЕРИОДА','BEGINOFPERIOD',
        'НЕ','NOT',
        'НЕДЕЛЯ','WEEK',
        'ОБЩИЕ','OVERALL',
        'ОБЪЕДИНИТЬ','UNION',
        'ПЕРВЫЕ','TOP',
        'ПЕРИОДАМИ','PERIODS',
        'ПО','BY','ON','OF',
        'ПОДОБНО','LIKE',
        'ПОДСТРОКА','SUBSTRING',
        'ПОЛНОЕ','FULL',
        'ПОЛУГОДИЕ','HALFYEAR',
        'ПОМЕСТИТЬ','INTO',
        'ПРАВОЕ','RIGHT',
        'ПРЕДСТАВЛЕНИЕ','PRESENTATION',
        'ПРЕДСТАВЛЕНИЕССЫЛКИ','REFPRESENTATION',
        'ПУСТАЯТАБЛИЦА','EMPTYTABLE',
        'РАЗЛИЧНЫЕ','DISTINCT',
        'РАЗНОСТЬДАТ','DATEDIFF',
        'РАЗРЕШЕННЫЕ','ALLOWED',
        'СГРУППИРОВАТЬ','GROUP',
        'СГРУППИРОВАНОПО','GROUPEDBY',
        'СЕКУНДА','SECOND',
        'СЕКУНДА','SECOND',
        'СОЕДИНЕНИЕ','JOIN',
        'СПЕЦСИМВОЛ','ESCAPE',
        'СРЕДНЕЕ','AVG',
        'СТРОКА','STRING',
        'СУММА','SUM',
        'ТИП','TYPE',
        'ТИПЗНАЧЕНИЯ','VALUETYPE',
        'ТОГДА','THEN',
        'ТОЛЬКО','ONLY',
        'УБЫВ','DESC',
        'УНИКАЛЬНО','UNIQUE',
        'УНИКАЛЬНЫЙИДЕНТИФИКАТОР','UUID',
        'УНИЧТОЖИТЬ','DROP',
        'УПОРЯДОЧИТЬ','ORDER',
        'ЧАС','HOUR',
        'ЧИСЛО','NUMBER',
    )
    
    _KEYWORD_CONSTANT_WORDS = (
        # constant.language.sdbl
        'НЕОПРЕДЕЛЕНО','UNDEFINED','Истина','True','Ложь','False','NULL'
    )

    IDENT = r'[A-Za-zА-Яа-яЁё_][\wа-яё0-9_]*'
    METADATA_ROOT = r'(?:РегистрСведений|РегистрНакопления|РегистрБухгалтерии|РегистрРасчета|Документ|ЖурналДокументов|ВнешнийИсточникДанных|Константа|Перечисление|ПланВидовРасчета|ПланВидовХарактеристик|ПланОбмена|ПланСчетов|БизнесПроцесс|БизнесПроцессы|КритерийОтбора|Последовательность|Задача|Справочник|Catalog|ExternalDataSource|Constant|Enum|ChartOfCalculationTypes|ChartOfCharacteristicTypes|ExchangePlan|ChartOfAccounts|BusinessProcess|BusinessProcesses|Document|DocumentJournal|InformationRegister|AccumulationRegister|AccountingRegister|CalculationRegister|Task|FilterCriterion|Sequence)'
    _METADATA_CHAIN = rf'{PREFIX_NO_DOT}{METADATA_ROOT}(?:\.[^\s\.,;\(\)]+)+'

    _FUNCTION_CALL_WORDS = (
        'ГОД','YEAR',
        'ДАТАВРЕМЯ','DATETIME',
        'ВЫРАЗИТЬ','CAST',
        'ДАТА','DATE',
        'ДОБАВИТЬКДАТЕ','DATEADD',
        'РАЗНОСТЬДАТ','DATEDIFF',
        'АВТОНОМЕРЗАПИСИ','RECORDAUTONUMBER',
        'ПОДСТРОКА','SUBSTRING','СТРОКА','STRING',
        'ДлинаСтроки',
        'STRINGLENGTH',
        'СокрЛ','СокрП','СокрЛП',
        'TRIML','TRIMR','TRIMALL',
        'Лев','Прав','СтрНайти','ВРег','НРег','СтрЗаменить',
        'STRFIND','STRREPLACE','UPPER','LOWER',
        'ACOS','ASIN','ATAN','COS','TAN','SIN','EXP','LOG','LOG10','POW','SQRT','ОКР','ЦЕЛ',
        'ROUND','INT',
        'СУММА','SUM','МИНИМУМ','MIN','МАКСИМУМ','MAX','СРЕДНЕЕ','AVG','КОЛИЧЕСТВО','COUNT',
        'ТИП','TYPE','ТИПЗНАЧЕНИЯ','VALUETYPE',
        'НАЧАЛОПЕРИОДА','BEGINOFPERIOD','КОНЕЦПЕРИОДА','ENDOFPERIOD',
        'ДЕНЬ','DAY','ДЕНЬГОДА','DAYOFYEAR','ДЕНЬНЕДЕЛИ','WEEKDAY',
        'МЕСЯЦ','MONTH','КВАРТАЛ','QUARTER','НЕДЕЛЯ','WEEK','ДЕКАДА','TENDAYS',
        'СЕКУНДА','SECOND','МИНУТА','MINUTE','ЧАС','HOUR',
        'ДОБАВИТЬ','ADD','ИНДЕКСИРОВАТЬ ПО НАБОРАМ','INDEX BY SETS',
        'ПРЕДСТАВЛЕНИЕ','PRESENTATION','ПРЕДСТАВЛЕНИЕССЫЛКИ','REFPRESENTATION',
        'ЕСТЬNULL','ISNULL','СГРУППИРОВАНОПО','GROUPEDBY','РАЗМЕРХРАНИМЫХДАННЫХ','УНИКАЛЬНЫЙИДЕНТИФИКАТОР','UUID',
    )

    _NAME_CLASS_WORDS = tuple(dict.fromkeys(GLOBAL_PROPERTY_NAMES + ('РегистрСведений',)))

    OPERATORS = r'(<=|>=|<>|=|<|>|\+|-|\*|\/|\.)'

    _KEYWORD_DECLARATION_PHRASES = tuple(
        word for word in _KEYWORD_DECLARATION_WORDS if ' ' in word
    )
    _KEYWORD_DECLARATION_SINGLE = tuple(
        word for word in _KEYWORD_DECLARATION_WORDS if ' ' not in word
    )
    _FUNCTION_CALL_PHRASES = tuple(
        word for word in _FUNCTION_CALL_WORDS if ' ' in word
    )
    _FUNCTION_CALL_SINGLE = tuple(
        word for word in _FUNCTION_CALL_WORDS if ' ' not in word
    )

    _sdbl_keyword_declaration = _casefold_set(_KEYWORD_DECLARATION_SINGLE)
    _sdbl_keyword_constant = _casefold_set(_KEYWORD_CONSTANT_WORDS)
    _sdbl_function_call = _casefold_set(_FUNCTION_CALL_SINGLE)
    _sdbl_name_class = _casefold_set(_NAME_CLASS_WORDS)

    tokens = {
        'root': [
            (r'\ufeff', Token.Text),
            (r'\r\n?|\n', Token.Text),
            (r'[^\S\n]+', Token.Text),
            (r'\/\/.*?(?=\n)', Token.Comment.Single),
            (r'\|', Token.Generic.Error),
            (r'(&[A-Za-zА-Яа-яЁё_][\wа-яё0-9_]*)', Token.Literal.String.Interpol),
            (r'(\.)([!#][^\s\.,;\(\)]+)', bygroups(Token.Operator, Token.Generic.Error)),
            (OPERATORS, Token.Operator),
            (_METADATA_CHAIN, _sdbl_metadata_callback),
            (r'(КАК)(\s+)(?!(?i:(?:ЧИСЛО|NUMBER|ИЗМЕНЕНИЯ|UPDATE))(?=\s|,|\(|\)|\n|$))([A-Za-zА-Яа-яЁё_][\wа-яё0-9_]*)',
             bygroups(Token.Keyword.Declaration, Token.Text, Token.Name.Variable)),
            (rf'(?<=\.){IDENT}(?=\s*\()', Token.Name.Function),
            (rf'(?<=\.){IDENT}', Token.Name.Variable),
            (r'[\[\]:(),;]', Token.Punctuation),
            (words(_FUNCTION_CALL_PHRASES, prefix=PREFIX_NO_DOT, suffix=SUFFIX_CALL), Token.Name.Builtin),
            (r'(?-i:ССЫЛКА|REFS)\b', Token.Keyword.Declaration),
            (words(_KEYWORD_DECLARATION_PHRASES, prefix=PREFIX_NO_DOT, suffix=SUFFIX_WORD), Token.Keyword.Declaration),
            (rf'{PREFIX_NO_DOT}{IDENT}', _sdbl_name_callback),
            (r'\b\d+\.?\d*\b', Token.Literal.Number),
            ('\"', Token.Literal.String, 'string'),
        ],
        'string': [
            ('\"(?![\"])', Token.Literal.String, '#pop'),
            (r'\r\n?|\n', Token.Text),
            (r'(?<=\n)[^\S\n]+', Token.Text),
            (r'(?<=[^\S\n])\/\/.*?(?=\n)', Token.Comment.Single),
            (r'(?<=^)\/\/.*?(?=\n)', Token.Comment.Single),
            (r'\"\"', Token.Literal.String.Escape),
            (r'\|', Token.Literal.String),
            (r'[^\"\n]+', Token.Literal.String),
        ]
    }


class SdblQueryLexer(SdblLexer):
    name = '1C (SDBL) Embedded Lexer'
    aliases = []

    tokens = copy.deepcopy(SdblLexer.tokens)
    _root_rules = tokens['root']
    for idx, rule in enumerate(_root_rules):
        if len(rule) >= 2 and rule[0] == r'\|' and rule[1] == Token.Generic.Error:
            _root_rules[idx] = (r'\|', Token.Literal.String)
            break
