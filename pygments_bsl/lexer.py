from pygments.lexer import RegexLexer, words, bygroups, using
from pygments.token import Token

import re
import copy

from .generated_data import (
    ENUM_PROPERTY_NAMES,
    GLOBAL_METHOD_NAMES,
    GLOBAL_PROPERTY_NAMES,
    TYPE_NAMES,
)

CALL_ONLY_BUILTINS = {
    'Булево','Boolean','Число','Number','Строка','String','Дата','Date',
}
CONSTANT_NAMES = (
    # constant.language.bsl
    'Неопределено','Undefined','Истина','True','Ложь','False','NULL'
)

class BslLexer(RegexLexer):
    name = '1C (BSL) Lexer'
    aliases = ['bsl', 'os']
    filenames = ['*.bsl', '*.os']

    flags = re.MULTILINE | re.IGNORECASE | re.VERBOSE

    KEYWORD_DECLARATION = words((
        # storage.type.var.bsl
        'Перем','Var',
    ), prefix='(?<!\.)', suffix=r'\b')    

    KEYWORD = words((
        # storage.type.bsl
        'Процедура','Procedure','Функция','Function',
        # storage.modifier.bsl
        'Экспорт', 'Export',
        # storage.type.bsl
        'КонецПроцедуры','EndProcedure','КонецФункции','EndFunction',
        # keyword.control.bsl
        'Прервать','Break','Продолжить','Continue','Возврат','Return',
        # keyword.control.conditional.bsl
        'Если','If','Иначе','Else','ИначеЕсли','ElsIf',
        'Тогда','Then','КонецЕсли','EndIf',
        # keyword.control.exception.bsl
        'Попытка','Try','Исключение','Except',
        'КонецПопытки','EndTry',
        # keyword.control.repeat.bsl
        'Пока','While','Для','For','Каждого','Each',
        'Из','In','По','To','Цикл','Do','КонецЦикла', 'EndDo',
        # keyword.operator.logical.bsl
        'НЕ','NOT','И','AND','ИЛИ','OR',
        # support.function.bsl
        'Новый','New',
        'Выполнить','Execute',
        # storage.modifier.bsl
        'Знач', 'Val',
        # 
        'Перейти', 'Goto',
        'Асинх', 'Async',
        'Ждать', 'Await',
    ), prefix='(?<!\.)', suffix=r'\b')
    
    NAME_CLASS_NAMES = tuple(dict.fromkeys(GLOBAL_PROPERTY_NAMES))

    NAME_CLASS = words(
        tuple(name for name in dict.fromkeys(NAME_CLASS_NAMES)
              if name not in CALL_ONLY_BUILTINS and name not in CONSTANT_NAMES),
        prefix='(?<!\.)',
        suffix=r'\b'
    )

    NAME_BUILTIN = words(
        tuple(name for name in dict.fromkeys(GLOBAL_METHOD_NAMES) if name not in CALL_ONLY_BUILTINS),
        prefix='(?<!\.)',
        suffix=r'\b'
    )

    NAME_BUILTIN_CALL = words(
        tuple(CALL_ONLY_BUILTINS),
        prefix='(?<!\.)',
        suffix=r'(?=(\s?[\(]))'
    )

    KEYWORD_CONSTANT = words(CONSTANT_NAMES, prefix='(?<!\.)', suffix=r'\b')

    KEYWORD_EXCEPTION = words((
        'ВызватьИсключение','Raise',
    ), prefix='(?<!\.)', suffix=r'\b')

    KEYWORD_EXCEPTION_CALL = words((
        'ВызватьИсключение','Raise',
    ), prefix='(?<!\.)', suffix=r'(?=(\s?[\(]))')

    # keywords that also used as function-like calls (treat as builtin when followed by '(')
    KEYWORD_AS_FUNCTION = words((
        'Новый','New',
    ), prefix='(?<!\.)', suffix=r'(?=(\s?[\(]))')

    # treat execute as builtin only when executing nested call string
    EXECUTE_CALL = r'(?<!\.)\b(Выполнить|Execute)\b(?=\s*\(\s*\"Выполнить)'

    TYPE_NAME_PATTERN = r'(?:' + '|'.join(re.escape(n) for n in TYPE_NAMES) + r')'
    GLOBAL_METHOD_PATTERN = r'(?<!\.)\b(?:' + '|'.join(re.escape(n) for n in GLOBAL_METHOD_NAMES) + r')\b(?=(\s?[\(]))'

    OPERATORS = words((
        '=','<=','>=','<>','<','>','+','-','*','/','%','.'
    ))

    # see https://pygments.org/docs/tokens
    tokens = {
        'root': [
            (r'\n', Token.Text),
            (r'[^\S\n]+', Token.Text),
            (r'\/\/.*?(?=\n)', Token.Comment.Single),
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
            (r'[\[\]:(),;]', Token.Punctuation),
            (r'\&.*$', Token.Name.Decorator),
            (r'\b(Процедура|Функция|Procedure|Function)\b(\s+)([\wа-яё_][\wа-яё0-9_]*)\s*(\()',
             bygroups(Token.Keyword, Token.Text, Token.Name.Function, Token.Punctuation), 'params'),
            (OPERATORS, Token.Operator),
            (r'\#.*$', Token.Comment.Preproc),
            # match forbidden-constant calls like Неопределено(....) as a single error token
            (r'\b(?:' + '|'.join(CONSTANT_NAMES) + r')\b\s*\([^\)]*\)', Token.Generic.Error),
            (NAME_BUILTIN_CALL, Token.Name.Builtin),
            (GLOBAL_METHOD_PATTERN, Token.Name.Builtin),
            (NAME_BUILTIN, Token.Name.Builtin),
            (KEYWORD_DECLARATION, Token.Keyword.Declaration),
            (KEYWORD_EXCEPTION_CALL, Token.Name.Exception),
            (KEYWORD_AS_FUNCTION, Token.Name.Builtin),
            (EXECUTE_CALL, Token.Name.Builtin),
            (KEYWORD_EXCEPTION, Token.Name.Exception),
            (KEYWORD, Token.Keyword),
            (KEYWORD_CONSTANT, Token.Keyword.Constant),
            (NAME_CLASS, Token.Name.Class),
            (r'[\wа-яё_][\wа-яё0-9_]*(?=(\s?[\(]))', Token.Name.Function),
            (r'\b\d+\.?\d*\b', Token.Literal.Number),
            (r'[\wа-яё_][\wа-яё0-9_]*', Token.Name.Variable),
            (r'"(?=[^"]*\b(ВЫБРАТЬ|SELECT)\b)', Token.Literal.String, 'query_string'),
            ('\"', Token.String, 'string'),
            (r'\'.*?\'', Token.Literal.Date),
            (r'~.*?(?=[:;])', Token.Name.Label),
        ],
        'preproc_if': [
            (r'\n', Token.Text, '#pop'),
            (r'\b(Сервер|НаСервере|Клиент|НаКлиенте|ТонкийКлиент|МобильныйКлиент|ВебКлиент|ВнешнееСоединение|ТолстыйКлиентУправляемоеПриложение|ТолстыйКлиентОбычноеПриложение|МобильныйАвтономныйСервер|МобильноеПриложениеКлиент|МобильноеПриложениеСервер)\b', Token.Keyword.Constant),
            (r'\b(И|Или|НЕ|Then|Тогда|And|Or|Not)\b', Token.Comment.Preproc),
            (r'\#', Token.Comment.Preproc),
            (r'[^\S\n]+', Token.Text),
            (r'[^\s#]+', Token.Comment.Preproc),
        ],
        'string': [
            ('\"(?![\"])', Token.String, '#pop'),
            (r'\n', Token.Text),
            (r'(?<=\n)[^\S\n]+', Token.Text),
            (r'(?<=[^\S\n])\/\/.*?(?=\n)', Token.Comment.Single),
            (r'(?<=^)\/\/.*?(?=\n)', Token.Comment.Single),
            (r'\|', Token.String),
            (r'\"\"', Token.String.Escape),
            (r'%%', Token.String.Escape),
            (r'%\d', Token.String.Interpol),
            (r'%', Token.Literal.String),
            (r'[^\"\|\n%]+', Token.String),
        ],
        'query_string': [
            (r'""', Token.Literal.String.Escape),
            (r'"', Token.Literal.String, '#pop'),
            # Delay instantiation to avoid forward reference issues and keep formatter options
            (r'[^"]+', using(lambda **kwargs: SdblQueryLexer(**kwargs))),
        ],
        'decorator_params': [
            (r'\)', Token.Punctuation, '#pop'),
            (r'\n', Token.Text),
            (r'[^\S\n]+', Token.Text),
            (r',', Token.Operator),
            (r'=', Token.Operator),
            (r'"[^"]*"', Token.Literal.String),
            (r'(\b[A-Za-zА-Яа-яёЁ_][\wа-яё0-9_]*\b)(\s*)(=)(\s*)(?!Неопределено\b|Undefined\b|Null\b|Истина\b|True\b|Ложь\b|False\b)([A-Za-zА-Яа-яёЁ_][\wа-яё0-9_]*)',
             bygroups(Token.Name.Variable, Token.Text, Token.Operator, Token.Text, Token.Generic.Error)),
            (r'([A-Za-zА-Яа-яёЁ_][\wа-яё0-9_]*)', Token.Name.Variable),
            (r'\b\d+\.?\d*\b', Token.Literal.Number),
            (r'"(?=[^"]*\b(ВЫБРАТЬ|SELECT)\b)', Token.Literal.String, 'query_string'),
            (r'.', Token.Text),
        ],
        'params': [
            (r'\)', Token.Punctuation, '#pop'),
            (r'\n', Token.Text),
            (r'[^\S\n]+', Token.Text),
            (r'\,', Token.Punctuation),
            (r'(&[\wа-яё_][\wа-яё0-9_]*)\s*(\()', bygroups(Token.Name.Decorator, Token.Punctuation), 'decorator_params'),
            (r'\&[^\s,(]+', Token.Name.Decorator),
            (r'\bЗнач\b|\bVal\b', Token.Keyword),
            (KEYWORD_CONSTANT, Token.Keyword.Constant),
            (r'(\b[A-Za-zА-Яа-яёЁ_][\wа-яё0-9_]*\b)(\s*)(=)(\s*)(?!Неопределено\b|Undefined\b|Null\b|Истина\b|True\b|Ложь\b|False\b)([A-Za-zА-Яа-яёЁ_][\wа-яё0-9_]*)',
             bygroups(Token.Name.Variable, Token.Text, Token.Operator, Token.Text, Token.Generic.Error)),
            (r'([A-Za-zА-Яа-яёЁ_][\wа-яё0-9_]*)', Token.Name.Variable),
            (r'=', Token.Operator),
            (r'\b\d+\.?\d*\b', Token.Literal.Number),
            (r'"(?=[^"]*\b(ВЫБРАТЬ|SELECT)\b)', Token.Literal.String, 'query_string'),
            (r'.', Token.Text),
        ],
        # String.Regex
    }




class SdblLexer(RegexLexer):
    name = '1C (SDBL) Lexer'
    aliases = ['sdbl']
    filenames = ['*.sdbl']

    flags = re.MULTILINE | re.IGNORECASE | re.VERBOSE

    KEYWORD_DECLARATION = words((
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
        'ПО','BY','ON',
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
        'ССЫЛКА','REFS',
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
    ), prefix='(?<!\.)', suffix=r'\b')
    
    KEYWORD_CONSTANT = words((
        # constant.language.sdbl
        'НЕОПРЕДЕЛЕНО','UNDEFINED','Истина','True','Ложь','False','NULL'
    ), prefix='(?<!\.)', suffix=r'\b')

    FUNCTION_CALL = words((
        'ГОД','YEAR',
        'ДАТАВРЕМЯ','DATETIME',
        'ВЫРАЗИТЬ','CAST',
        'ДАТА','DATE',
        'ДОБАВИТЬКДАТЕ','DATEADD',
        'РАЗНОСТЬДАТ','DATEDIFF',
        'АВТОНОМЕРЗАПИСИ','RECORDAUTONUMBER',
        'ПОДСТРОКА','SUBSTRING','СТРОКА','STRING',
        'ДлинаСтроки',
        'СокрЛ','СокрП','СокрЛП',
        'Лев','Прав','СтрНайти','ВРег','НРег','СтрЗаменить',
        'ACOS','ASIN','ATAN','COS','TAN','SIN','EXP','LOG','LOG10','POW','SQRT','ОКР','ЦЕЛ',
        'СУММА','SUM','МИНИМУМ','MIN','МАКСИМУМ','MAX','СРЕДНЕЕ','AVG','КОЛИЧЕСТВО','COUNT',
        'ТИП','TYPE','ТИПЗНАЧЕНИЯ','VALUETYPE',
        'НАЧАЛОПЕРИОДА','BEGINOFPERIOD','КОНЕЦПЕРИОДА','ENDOFPERIOD',
        'ДЕНЬ','DAY','ДЕНЬГОДА','DAYOFYEAR','ДЕНЬНЕДЕЛИ','WEEKDAY',
        'МЕСЯЦ','MONTH','КВАРТАЛ','QUARTER','НЕДЕЛЯ','WEEK','ДЕКАДА','TENDAYS',
        'СЕКУНДА','SECOND','МИНУТА','MINUTE','ЧАС','HOUR',
        'ДОБАВИТЬ','ADD','ИНДЕКСИРОВАТЬ ПО НАБОРАМ','INDEX BY SETS',
        'ПРЕДСТАВЛЕНИЕ','PRESENTATION','ПРЕДСТАВЛЕНИЕССЫЛКИ','REFPRESENTATION',
        'ЕСТЬNULL','ISNULL','СГРУППИРОВАНОПО','GROUPEDBY','РАЗМЕРХРАНИМЫХДАННЫХ','УНИКАЛЬНЫЙИДЕНТИФИКАТОР','UUID',
    ), prefix='(?<!\.)', suffix=r'(?=(\s?[\(]))')

    OPERATORS = r'(<=|>=|<>|=|<|>|\+|-|\*|\/|\.)'

    tokens = {
        'root': [
            (r'\n', Token.Text),
            (r'[^\S\n]+', Token.Text),
            (r'\/\/.*?(?=\n)', Token.Comment.Single),
            (r'\|', Token.Generic.Error),
            (r'(&[A-Za-zА-Яа-яЁё_][\wа-яё0-9_]*)', Token.Name.Constant),
            (OPERATORS, Token.Operator),
            (r'(?<=\bКАК\s)Ссылка\b', Token.Name.Variable),
            (r'(?<=\.)[A-Za-zА-Яа-яЁё_][\wа-яё0-9_]*', Token.Name.Variable),
            (r'[\[\]:(),;]', Token.Punctuation),
            (FUNCTION_CALL, Token.Name.Builtin),
            (KEYWORD_DECLARATION, Token.Keyword.Declaration),
            (KEYWORD_CONSTANT, Token.Keyword.Constant),
            (r'\b\d+\.?\d*\b', Token.Literal.Number),
            (r'[\wа-яё_][\wа-яё0-9_]*', Token.Name.Variable),
            ('\"', Token.Literal.String, 'string'),
        ],
        'string': [
            ('\"(?![\"])', Token.Literal.String, '#pop'),
            (r'\n', Token.Text),
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
