from pygments.lexer import RegexLexer, words, bygroups, using, default, include
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

def _constraint_name_callback(lexer, match):
    name = match.group(0)
    name_cf = _casefold(name)
    is_call = _is_call(match.string, match.end())

    if name_cf in lexer._acl_function_call and is_call:
        yield match.start(), Token.Name.Builtin, name
        return

    if name_cf in lexer._acl_keyword_constant:
        yield match.start(), Token.Keyword.Constant, name
        return

    if name_cf in lexer._acl_keyword_declaration:
        yield match.start(), Token.Keyword.Declaration, name
        return

    if name_cf in lexer._acl_name_class:
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

def _locale_single_quote_callback(lexer, match):
    yield match.start(), Token.String.Escape, "'"
    if match.group(1):
        content = match.group(1)
        start = match.start(1)
        pos = 0
        for item in re.finditer(r'""|%\d|%%|%[A-Za-zА-Яа-яЁё_]', content):
            if item.start() > pos:
                yield start + pos, Token.String, content[pos:item.start()]
            token = Token.String.Interpol
            if item.group(0) in ('""', '%%'):
                token = Token.String.Escape
            elif re.match(r'%[A-Za-zА-Яа-яЁё_]', item.group(0)):
                token = Token.Generic.Error
            yield start + item.start(), token, item.group(0)
            pos = item.end()
        if pos < len(content):
            yield start + pos, Token.String, content[pos:]
    yield match.start() + len(match.group(0)) - 1, Token.String.Escape, "'"

def _locale_error_pipe_line_callback(lexer, match):
    pipe_match = re.match(r'\n([^\S\n]*)(\|)(.*)', match.group(0))
    if not pipe_match:
        yield match.start(), Token.Generic.Error, match.group(0)
        return
    yield match.start(), Token.Text, '\n'
    if pipe_match.group(1):
        yield match.start() + 1, Token.Text, pipe_match.group(1)
    yield match.start() + 1 + len(pipe_match.group(1)), Token.String, pipe_match.group(2)
    rest = pipe_match.group(3)
    if rest:
        yield match.start() + 1 + len(pipe_match.group(1)) + 1, Token.Generic.Error, rest

def _locale_missing_open_quote_callback(lexer, match):
    yield match.start(1), Token.Generic.Error, match.group(1)
    yield match.start(2), Token.String, match.group(2)

def _locale_missing_semicolon_callback(lexer, match):
    yield match.start(1), Token.Name.Attribute, match.group(1)
    if match.group(2):
        yield match.start(2), Token.String, match.group(2)
    yield match.start(3), Token.Operator, match.group(3)
    if match.group(4):
        yield match.start(4), Token.String, match.group(4)
    yield match.start(4) + len(match.group(4)), Token.String.Escape, "'"
    if match.group(5):
        yield match.start(5), Token.String, match.group(5)
    yield match.start(5) + len(match.group(5)), Token.String.Escape, "'"
    error = f"{match.group(6)}{match.group(7)}"
    if error:
        yield match.start(6), Token.Generic.Error, error

def _locale_extra_quote_callback(lexer, match):
    yield match.start(1), Token.Name.Attribute, match.group(1)
    if match.group(2):
        yield match.start(2), Token.String, match.group(2)
    yield match.start(3), Token.Operator, match.group(3)
    if match.group(4):
        yield match.start(4), Token.String, match.group(4)
    yield match.start(4) + len(match.group(4)), Token.String.Escape, "'"
    if match.group(5):
        yield match.start(5), Token.String, match.group(5)
    yield match.start(5) + len(match.group(5)), Token.String.Escape, "'"
    error = f"{match.group(6)}{match.group(7)}"
    if error:
        yield match.start(6), Token.Generic.Error, error

def _locale_missing_semicolon_pipe_callback(lexer, match):
    yield match.start(1), Token.Name.Attribute, match.group(1)
    if match.group(2):
        yield match.start(2), Token.String, match.group(2)
    yield match.start(3), Token.Operator, match.group(3)
    if match.group(4):
        yield match.start(4), Token.String, match.group(4)
    yield match.start(4) + len(match.group(4)), Token.String.Escape, "'"
    if match.group(5):
        yield match.start(5), Token.String, match.group(5)
    yield match.start(5) + len(match.group(5)), Token.String.Escape, "'"
    error = match.group(6)
    if error:
        pipe_match = re.match(r'\n([^\S\n]*)(\|)(.*)', error)
        if pipe_match:
            yield match.start(6), Token.Text, '\n'
            if pipe_match.group(1):
                yield match.start(6) + 1, Token.Text, pipe_match.group(1)
            yield match.start(6) + 1 + len(pipe_match.group(1)), Token.String, pipe_match.group(2)
            rest = pipe_match.group(3)
            if rest:
                yield match.start(6) + 1 + len(pipe_match.group(1)) + 1, Token.Generic.Error, rest
        else:
            yield match.start(6), Token.Generic.Error, error

def _doc_type_list_with_iz_callback(lexer, match):
    yield match.start(1), Token.Comment.Single, match.group(1)
    yield match.start(2), Token.Punctuation, match.group(2)

    type_list = match.group(3)
    type_list_start = match.start(3)
    for item in re.finditer(
        r'[A-Za-zА-Яа-яЁё_][\wа-яё0-9_]*(?:\.[A-Za-zА-Яа-яЁё_][\wа-яё0-9_]*)*'
        r'|\b[Ии]з\b|,\s*|\s+',
        type_list,
    ):
        value = item.group(0)
        if value.lower() == 'из':
            token = Token.Keyword
        elif value.startswith(',') or value.isspace():
            token = Token.Punctuation
        else:
            token = Token.Name.Class
        yield type_list_start + item.start(), token, value

    yield match.start(4), Token.Punctuation, match.group(4)
    yield match.start(5), Token.Comment.Single, match.group(5)

def _emit_doc_type_list(type_list, type_list_start):
    for item in re.finditer(
        r'[A-Za-zА-Яа-яЁё_][\wа-яё0-9_]*(?:\.[A-Za-zА-Яа-яЁё_][\wа-яё0-9_]*)*'
        r'|,\s*|\s+',
        type_list,
    ):
        value = item.group(0)
        if value.startswith(',') or value.isspace():
            token = Token.Punctuation
        else:
            token = Token.Name.Class
        yield type_list_start + item.start(), token, value

def _doc_type_list_or_desc_callback(lexer, match):
    yield match.start(1), Token.Comment.Single, match.group(1)
    yield match.start(2), Token.Name.Class, match.group(2)
    yield match.start(3), Token.Punctuation, match.group(3)
    rest = match.group(4)
    if (
        '.' not in match.group(2)
        and match.group(2) in lexer._bsl_name_class
        and re.match(
            r'^[A-Za-zА-Яа-яЁё_][\wа-яё0-9_]*(?:\.[A-Za-zА-Яа-яЁё_][\wа-яё0-9_]*)*\s*$',
            rest,
        )
    ):
        yield from _emit_doc_type_list(rest, match.start(4))
    else:
        yield match.start(4), Token.Comment.Single, rest

def _doc_param_name_type_list_eol_callback(lexer, match):
    yield match.start(1), Token.Comment.Single, match.group(1)
    left = match.group(2)
    left_cf = left.casefold()
    if left_cf in lexer._bsl_name_class or left_cf in lexer._bsl_call_only_builtins:
        yield match.start(2), Token.Name.Class, left
        yield match.start(3), Token.Punctuation, match.group(3)
        yield match.start(4), Token.Comment.Single, match.group(4)
        return
    right = match.group(4)
    yield match.start(2), Token.Name.Variable, left
    yield match.start(3), Token.Punctuation, match.group(3)
    yield from _emit_doc_type_list(right, match.start(4))

def _doc_type_list_after_name_callback(lexer, match):
    yield match.start(1), Token.Comment.Single, match.group(1)
    yield match.start(2), Token.Name.Variable, match.group(2)
    yield match.start(3), Token.Punctuation, match.group(3)
    yield from _emit_doc_type_list(match.group(4), match.start(4))
    yield match.start(5), Token.Punctuation, match.group(5)
    yield match.start(6), Token.Comment.Single, match.group(6)

def _doc_type_list_bullet_callback(lexer, match):
    yield match.start(1), Token.Comment.Single, match.group(1)
    yield match.start(2), Token.Punctuation, match.group(2)
    yield from _emit_doc_type_list(match.group(3), match.start(3))
    yield match.start(4), Token.Punctuation, match.group(4)
    yield match.start(5), Token.Comment.Single, match.group(5)

def _doc_type_list_bullet_with_iz_colon_callback(lexer, match):
    yield match.start(1), Token.Comment.Single, match.group(1)
    yield match.start(2), Token.Punctuation, match.group(2)
    yield match.start(3), Token.Name.Variable, match.group(3)
    yield match.start(4), Token.Punctuation, match.group(4)
    type_list = match.group(5)
    type_list_start = match.start(5)
    for item in re.finditer(
        r'[A-Za-zА-Яа-яЁё_][\wа-яё0-9_]*(?:\.[A-Za-zА-Яа-яЁё_][\wа-яё0-9_]*)*'
        r'|\b[Ии]з\b',
        type_list,
    ):
        value = item.group(0)
        token = Token.Keyword if value.lower() == 'из' else Token.Name.Class
        yield type_list_start + item.start(), token, value
    yield match.start(6), Token.Punctuation, match.group(6)

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

    _NAME_BUILTIN_EXTRA = (
        'ДобавитьОбработчик', 'AddHandler',
        'УдалитьОбработчик', 'RemoveHandler',
    )
    _NAME_BUILTIN_WORDS = tuple(
        name for name in dict.fromkeys(GLOBAL_METHOD_NAMES)
        if name not in CALL_ONLY_BUILTINS
    ) + _NAME_BUILTIN_EXTRA

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
    CONSTRAINT_STRING_START = (
        r'"(?=[^"]*\b(?:'
        r'РазрешитьЧтениеИзменение|AllowReadUpdate|'
        r'РазрешитьЧтение|AllowRead|'
        r'РазрешитьИзменениеЕслиРазрешеноЧтение|AllowUpdateIfReadingAllowed|'
        r'ПрисоединитьДополнительныеТаблицы|AttachAdditionalTables|'
        r'ЗначениеРазрешено|ValueAllowed|'
        r'ЧтениеОбъектаРазрешено|ObjectReadingAllowed|'
        r'ИзменениеОбъектаРазрешено|ObjectUpdateAllowed|'
        r'ЧтениеСпискаРазрешено|ListReadingAllowed|'
        r'ИзменениеСпискаРазрешено|ListUpdateAllowed|'
        r'ПравоДоступа|AccessRight|'
        r'РольДоступна|RoleAvailable'
        r')\b)'
        r'(?![^"]*(?:\r?\n)\#(?:Удаление|КонецУдаления|Delete|EndDelete))'
    )
    LOCALE_KEY_PATTERN = r'[a-z]{2,3}'
    _ODD_LOCALE_QUOTES_LOOKAHEAD = (
        r'(?=(?:[^\n\']*\'[^\n\']*\')*[^\n\']*\'[^\n\']*(?=\n|(?<!")"(?!")))'
    )
    _LOCALE_MISSING_SEMICOLON_PATTERN = (
        r'(?:(?<=\n)|^)(\b' + LOCALE_KEY_PATTERN + r'\b)(\s*)(=)(\s*)'
        r'\'([^\n\']*)\'(\s+)(\b' + LOCALE_KEY_PATTERN + r'\b[^\n"]*)'
        r'(?=\n|")'
    )
    _LOCALE_EXTRA_QUOTE_PATTERN = (
        r'(?:(?<=\n)|^)(\b' + LOCALE_KEY_PATTERN + r'\b)(\s*)(=)(\s*)'
        r'\'([^\n\']*)\'(\')([^\n"]*)'
        r'(?=\n|")'
    )
    _LOCALE_MISSING_SEMICOLON_FIRST_PATTERN = (
        r'(\b' + LOCALE_KEY_PATTERN + r'\b)(\s*)(=)(\s*)'
        r'\'([^\n\']*)\'(\s+)(\b' + LOCALE_KEY_PATTERN + r'\b[^\n"]*)'
        r'(?=\n|")'
    )
    _LOCALE_EXTRA_QUOTE_FIRST_PATTERN = (
        r'(\b' + LOCALE_KEY_PATTERN + r'\b)(\s*)(=)(\s*)'
        r'\'([^\n\']*)\'(\')([^\n"]*)'
        r'(?=\n|")'
    )
    _LOCALE_MISSING_SEMICOLON_PIPE_FIRST_PATTERN = (
        r'(\b' + LOCALE_KEY_PATTERN + r'\b)(\s*)(=)(\s*)'
        r'\'([^\n\']*)\'(\n[^\S\n]*\|[^\n"]*)'
    )
    _LOCALE_MISSING_SEMICOLON_PIPE_PATTERN = (
        r'(?<=\n)(\b' + LOCALE_KEY_PATTERN + r'\b)(\s*)(=)(\s*)'
        r'\'([^\n\']*)\'(\n[^\S\n]*\|[^\n"]*)'
    )

    TYPE_NAME_PATTERN = r'(?:' + '|'.join(re.escape(n) for n in TYPE_NAMES) + r')'
    DOC_TYPE_NAMES = tuple(dict.fromkeys(TYPE_NAMES + tuple(CALL_ONLY_BUILTINS) + (
        'Булево','Число','Строка','Дата','Массив','ТаблицаЗначений','Структура','Соответствие',
        'ПланОбменаСсылка','ДанныеФормыСтруктура','КомпоновщикНастроекКомпоновкиДанных',
        'Boolean','Number','String','Date',
    )))
    DOC_TYPE_PATTERN = r'(?:' + '|'.join(re.escape(n) for n in DOC_TYPE_NAMES) + r')'
    DOC_TYPE_LIST_PATTERN = (
        r'[A-Za-zА-Яа-яЁё_][\wа-яё0-9_]*'
        r'(?:\.[A-Za-zА-Яа-яЁё_][\wа-яё0-9_]*)*'
        r'(?:[^\S\n]+[Ии]з[^\S\n]+[A-Za-zА-Яа-яЁё_][\wа-яё0-9_]*'
        r'(?:\.[A-Za-zА-Яа-яЁё_][\wа-яё0-9_]*)*)?'
        r'(?:[^\S\n]*,[^\S\n]*[A-Za-zА-Яа-яЁё_][\wа-яё0-9_]*'
        r'(?:\.[A-Za-zА-Яа-яЁё_][\wа-яё0-9_]*)*'
        r'(?:[^\S\n]+[Ии]з[^\S\n]+[A-Za-zА-Яа-яЁё_][\wа-яё0-9_]*'
        r'(?:\.[A-Za-zА-Яа-яЁё_][\wа-яё0-9_]*)*)?)*'
    )
    DOC_TYPE_LIST_WITH_COMMA_PATTERN = (
        r'[A-Za-zА-Яа-яЁё_][\wа-яё0-9_]*'
        r'(?:\.[A-Za-zА-Яа-яЁё_][\wа-яё0-9_]*)*'
        r'(?:[^\S\n]+[Ии]з[^\S\n]+[A-Za-zА-Яа-яЁё_][\wа-яё0-9_]*'
        r'(?:\.[A-Za-zА-Яа-яЁё_][\wа-яё0-9_]*)*)?'
        r'(?:[^\S\n]*,[^\S\n]*[A-Za-zА-Яа-яЁё_][\wа-яё0-9_]*'
        r'(?:\.[A-Za-zА-Яа-яЁё_][\wа-яё0-9_]*)*'
        r'(?:[^\S\n]+[Ии]з[^\S\n]+[A-Za-zА-Яа-яЁё_][\wа-яё0-9_]*'
        r'(?:\.[A-Za-zА-Яа-яЁё_][\wа-яё0-9_]*)*)?)+'
    )
    DOC_TYPE_LIST_WITH_IZ_PATTERN = (
        r'[A-Za-zА-Яа-яЁё_][\wа-яё0-9_]*'
        r'(?:\.[A-Za-zА-Яа-яЁё_][\wа-яё0-9_]*)*'
        r'[^\S\n]+[Ии]з[^\S\n]+[A-Za-zА-Яа-яЁё_][\wа-яё0-9_]*'
        r'(?:\.[A-Za-zА-Яа-яЁё_][\wа-яё0-9_]*)*'
        r'(?:[^\S\n]*,[^\S\n]*[A-Za-zА-Яа-яЁё_][\wа-яё0-9_]*'
        r'(?:\.[A-Za-zА-Яа-яЁё_][\wа-яё0-9_]*)*'
        r'[^\S\n]+[Ии]з[^\S\n]+[A-Za-zА-Яа-яЁё_][\wа-яё0-9_]*'
        r'(?:\.[A-Za-zА-Яа-яЁё_][\wа-яё0-9_]*)*)*'
    )

    OPERATORS = words((
        '=','<=','>=','<>','<','>','+','-','*','/','%','?','.'
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
        # english metadata roots
        'WebServices',
        'WSReferences',
        'BusinessProcesses',
        'CommandGroups',
        'Documents',
        'DocumentJournals',
        'Tasks',
        'Interfaces',
        'Constants',
        'FilterCriteria',
        'DocumentNumerators',
        'DataProcessors',
        'CommonPictures',
        'CommonCommands',
        'CommonTemplates',
        'CommonModules',
        'CommonForms',
        'Reports',
        'XDTOPackages',
        'SessionParameters',
        'FunctionalOptionsParameters',
        'Enumerations',
        'ChartsOfCalculationTypes',
        'ChartsOfCharacteristicTypes',
        'ExchangePlans',
        'ChartsOfAccounts',
        'EventSubscriptions',
        'Sequences',
        'AccountingRegisters',
        'AccumulationRegisters',
        'CalculationRegisters',
        'InformationRegisters',
        'ScheduledJobs',
        'Roles',
        'Styles',
        'FunctionalOptions',
        'SettingsStorages',
        'StyleItems',
        'Languages',
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
        'preproc_root': [
            (r'\#(Использовать|Use)\b', Token.Comment.Preproc, 'preproc_use'),
            (r'\#(native)\b.*', Token.Comment.Preproc),
            (r'\#(Если|If)\b', Token.Comment.Preproc, 'preproc_if'),
            (r'\#(ИначеЕсли|ElsIf)\b', Token.Comment.Preproc, 'preproc_if'),
            (r'\#(Иначе|Else|КонецЕсли|EndIf|Область|Region|КонецОбласти|EndRegion|Вставка|Insert|КонецВставки|EndInsert|Удаление|Delete|КонецУдаления|EndDelete)\b.*', Token.Comment.Preproc),
        ],
        'string_locale_start': [
            (r'"(?=(?:[^"]|"")*\b' + LOCALE_KEY_PATTERN + r'\b\s*=)', Token.String, 'string_locale_first_line'),
        ],
        'doc_comment': [
            (r'(\/\/\s*)(СМ\.|SEE)(\s+)([A-Za-zА-Яа-яЁё_][\wа-яё0-9_]*(?:\.[A-Za-zА-Яа-яЁё_][\wа-яё0-9_]*)*)(\s*)(\()(.*?)(\))',
             bygroups(Token.Comment.Single, Token.Keyword, Token.Comment.Single, Token.Name.Namespace, Token.Comment.Single, Token.Punctuation, Token.Comment.Single, Token.Punctuation)),
            (r'(\/\/\s*)(СМ\.|SEE)(\s+)([A-Za-zА-Яа-яЁё_][\wа-яё0-9_]*(?:\.[A-Za-zА-Яа-яЁё_][\wа-яё0-9_]*)*)',
             bygroups(Token.Comment.Single, Token.Keyword, Token.Comment.Single, Token.Name.Namespace)),
            (r'(\/\/\s*)(Устарела|Deprecate)([.:])?(.*)',
             bygroups(Token.Comment.Single, Token.Keyword, Token.Punctuation, Token.Comment.Single)),
            (r'(\/\/\s*)(Параметры|Parameters|Возвращаемое\s+значение|Returns|Пример(?:ы)?|Example(?:s)?|Варианты\s+вызова|Call\s+options)(:)',
             bygroups(Token.Comment.Single, Token.Keyword, Token.Punctuation)),
            (r'(\/\/\s*)(' + DOC_TYPE_PATTERN + r')(\s*:)',
             bygroups(Token.Comment.Single, Token.Name.Class, Token.Punctuation)),
            (r'(\/\/\s*)([A-Za-zА-Яа-яЁё_][\wа-яё0-9_]*)(\s+)([Ии]з)(\s+)(см\.)(\s+)([A-Za-zА-Яa-яЁё_][\wа-яё0-9_]*(?:\.[A-Za-zА-Яa-яЁё_][\wа-яё0-9_]*)*)(\s*-\s*)(.*)',
             bygroups(Token.Comment.Single, Token.Name.Class, Token.Punctuation, Token.Keyword, Token.Punctuation, Token.Keyword, Token.Comment.Single, Token.Name.Class, Token.Punctuation, Token.Comment.Single)),
            (r'(\/\/\s*)([A-Za-zА-Яa-яЁё_][\wа-яё0-9_]*)(\s+)([Ии]з)(\s+)(см\.)(\s+)([A-Za-zА-Яa-яЁё_][\wа-яё0-9_]*(?:\.[A-Za-zА-Яa-яЁё_][\wа-яё0-9_]*)*)(?=\s*$)',
             bygroups(Token.Comment.Single, Token.Name.Class, Token.Punctuation, Token.Keyword, Token.Punctuation, Token.Keyword, Token.Comment.Single, Token.Name.Class)),
            (r'(\/\/\s*)([A-Za-zА-Яa-яЁё_][\wа-яё0-9_]*)(\s+)([Ии]з)(\s+)([A-Za-zА-Яa-яЁё_][\wа-яё0-9_]*(?:\.[A-Za-zА-Яa-яЁё_][\wа-яё0-9_]*)*)(\s*-\s*)(.*)',
             bygroups(Token.Comment.Single, Token.Name.Class, Token.Punctuation, Token.Keyword, Token.Punctuation, Token.Name.Class, Token.Punctuation, Token.Comment.Single)),
            (r'(\/\/\s*)([A-Za-zА-Яa-яЁё_][\wа-яё0-9_]*)(\s+)([Ии]з)(\s+)([A-Za-zА-Яa-яЁё_][\wа-яё0-9_]*(?:\.[A-Za-zА-Яa-яЁё_][\wа-яё0-9_]*)*)(?=\s*$)',
             bygroups(Token.Comment.Single, Token.Name.Class, Token.Punctuation, Token.Keyword, Token.Punctuation, Token.Name.Class)),
            (r'(\/\/\s*)([A-Za-zА-Яа-яЁё_][\wа-яё0-9_]*)(\s+(?:-|–)\s+)(см\.)(\s+)([A-Za-zА-Яа-яЁё_][\wа-яё0-9_]*(?:\.[A-Za-zА-Яа-яЁё_][\wа-яё0-9_]*)*)(.*)',
             bygroups(Token.Comment.Single, Token.Name.Variable, Token.Punctuation, Token.Keyword, Token.Comment.Single, Token.Name.Class, Token.Comment.Single)),
            (r'(\/\/\s*)([A-Za-zА-Яа-яЁё_][\wа-яё0-9_]*)(\s+(?:-|–)\s+)(' + DOC_TYPE_LIST_PATTERN + r')([^\S\n]*:[^\S\n]*)(см\.)(\s+)([A-Za-zА-Яа-яЁё_][\wа-яё0-9_]*(?:\.[A-Za-zА-Яа-яЁё_][\wа-яё0-9_]*)*)(.*)',
             bygroups(Token.Comment.Single, Token.Name.Variable, Token.Punctuation, Token.Name.Class, Token.Punctuation, Token.Keyword, Token.Comment.Single, Token.Name.Class, Token.Comment.Single)),
            (r'(\/\/\s*)([A-Za-zА-Яа-яЁё_][\wа-яё0-9_]*)(\s+(?:-|–)\s+)(' + DOC_TYPE_LIST_PATTERN + r')([^\S\n]*:[^\S\n]*)(.*)',
             bygroups(Token.Comment.Single, Token.Name.Variable, Token.Punctuation, Token.Name.Class, Token.Punctuation, Token.Comment.Single)),
            (r'(\/\/\s*)([A-Za-zА-Яа-яЁё_][\wа-яё0-9_]*)(\s+(?:-|–)\s+)(' + DOC_TYPE_LIST_PATTERN + r')(\s+)([Ии]з)(\s+)(см\.)(\s+)([A-Za-zА-Яа-яЁё_][\wа-яё0-9_]*(?:\.[A-Za-zА-Яа-яЁё_][\wа-яё0-9_]*)*)(\s+(?:-|–)\s+)(.*)',
             bygroups(Token.Comment.Single, Token.Name.Variable, Token.Punctuation, Token.Name.Class, Token.Punctuation, Token.Keyword, Token.Punctuation, Token.Keyword, Token.Comment.Single, Token.Name.Class, Token.Punctuation, Token.Comment.Single)),
            (r'(\/\/\s*)([A-Za-zА-Яа-яЁё_][\wа-яё0-9_]*)(\s+(?:-|–)\s+)(' + DOC_TYPE_LIST_PATTERN + r')(\s+)([Ии]з)(\s+)(см\.)(\s+)([A-Za-zА-Яа-яЁё_][\wа-яё0-9_]*(?:\.[A-Za-zА-Яа-яЁё_][\wа-яё0-9_]*)*)(?=\s*$)',
             bygroups(Token.Comment.Single, Token.Name.Variable, Token.Punctuation, Token.Name.Class, Token.Punctuation, Token.Keyword, Token.Punctuation, Token.Keyword, Token.Comment.Single, Token.Name.Class)),
            (r'(\/\/\s*)([A-Za-zА-Яа-яЁё_][\wа-яё0-9_]*)(\s+(?:-|–)\s+)(' + DOC_TYPE_LIST_PATTERN + r')([^\S\n]+)([Ии]з)(?=\s*$)',
             bygroups(Token.Comment.Single, Token.Name.Variable, Token.Punctuation, Token.Name.Class, Token.Punctuation, Token.Keyword)),
            (r'(\/\/\s*)([A-Za-zА-Яа-яЁё_][\wа-яё0-9_]*)(\s+(?:-|–)\s+)(' + DOC_TYPE_LIST_PATTERN + r')([^\S\n]+)([Ии]з)([^\S\n]+)([^-\n]*?)(\s+(?:-|–)\s+)(.*)',
             bygroups(Token.Comment.Single, Token.Name.Variable, Token.Punctuation, Token.Name.Class, Token.Punctuation, Token.Keyword, Token.Punctuation, Token.Name.Class, Token.Punctuation, Token.Comment.Single)),
            (r'(\/\/\s*)([A-Za-zА-Яа-яЁё_][\wа-яё0-9_]*)(\s+(?:-|–)\s+)(' + DOC_TYPE_LIST_PATTERN + r')([^\S\n]+)([Ии]з)([^\S\n]+)([^-\n]*?)(?=\s*$)',
             bygroups(Token.Comment.Single, Token.Name.Variable, Token.Punctuation, Token.Name.Class, Token.Punctuation, Token.Keyword, Token.Punctuation, Token.Name.Class)),
            (r'(\/\/\s*)([A-Za-zА-Яа-яЁё_][\wа-яё0-9_]*)(\s+(?:-|–)\s+)(' + DOC_TYPE_LIST_PATTERN + r')(\s+(?:-|–)\s+)(.*)',
             _doc_type_list_after_name_callback),
            (r'(\/\/\s*)([A-Za-zА-Яа-яЁё_][\wа-яё0-9_]*)(\s+(?:-|–)\s+)(' + DOC_TYPE_PATTERN + r')(?=\s*$)',
             bygroups(Token.Comment.Single, Token.Name.Variable, Token.Punctuation, Token.Name.Class)),
            (r'(\/\/\s*)([A-Za-zА-Яа-яЁё_][\wа-яё0-9_]*)(\s+(?:-|–)\s+)(' + DOC_TYPE_LIST_PATTERN + r')(?=\s*$)',
             _doc_param_name_type_list_eol_callback),
            (r'(\/\/\s*)(' + DOC_TYPE_PATTERN + r')(\s+(?:-|–)\s+)((?-i:[a-zа-яё]).*)',
             bygroups(Token.Comment.Single, Token.Name.Class, Token.Punctuation, Token.Comment.Single)),
            (r'(\/\/\s*)([A-Za-zА-Яа-яЁё_][\wа-яё0-9_]*)(\s+(?:-|–)\s+)((?-i:[a-zа-яё]).*)',
             bygroups(Token.Comment.Single, Token.Name.Variable, Token.Punctuation, Token.Comment.Single)),
            (r'(\/\/\s*)(' + DOC_TYPE_LIST_PATTERN + r')(\s+(?:-|–)\s+)(.*)',
             _doc_type_list_or_desc_callback),
            (r'(\/\/\s*)(' + DOC_TYPE_LIST_WITH_COMMA_PATTERN + r')(\s+(?:-|–)\s+)(.*)',
             bygroups(Token.Comment.Single, Token.Name.Class, Token.Punctuation, Token.Comment.Single)),
            (r'(\/\/\s*)(' + DOC_TYPE_PATTERN + r')(\s+(?:-|–)\s+)(.*)',
             bygroups(Token.Comment.Single, Token.Name.Class, Token.Punctuation, Token.Comment.Single)),
            (r'(\/\/\s*)(\*+\s+)([A-Za-zА-Яа-яЁё_][\wа-яё0-9_]*)(\s+(?:-|–)\s+)(' + DOC_TYPE_LIST_WITH_IZ_PATTERN + r')(\s*:)',
             _doc_type_list_bullet_with_iz_colon_callback),
            (r'(\/\/\s*)(\*+\s+)([A-Za-zА-Яа-яЁё_][\wа-яё0-9_]*)(\s+(?:-|–)\s+)(' + DOC_TYPE_LIST_PATTERN + r')(\s*:)',
             bygroups(Token.Comment.Single, Token.Punctuation, Token.Name.Variable, Token.Punctuation, Token.Name.Class, Token.Punctuation)),
            (r'(\/\/\s*)(\*+\s+)([A-Za-zА-Яа-яЁё_][\wа-яё0-9_]*)(\s+(?:-|–)\s+)(' + DOC_TYPE_LIST_PATTERN + r')([^\S\n]+)([Ии]з)(?=\s*$)',
             bygroups(Token.Comment.Single, Token.Punctuation, Token.Name.Variable, Token.Punctuation, Token.Name.Class, Token.Punctuation, Token.Keyword)),
            (r'(\/\/\s*)(\*+\s+)([A-Za-zА-Яа-яЁё_][\wа-яё0-9_]*)(\s+(?:-|–)\s+)(' + DOC_TYPE_LIST_PATTERN + r')([^\S\n]+)([Ии]з)([^\S\n]+)([^-\n]*?)(\s+(?:-|–)\s+)(.*)',
             bygroups(Token.Comment.Single, Token.Punctuation, Token.Name.Variable, Token.Punctuation, Token.Name.Class, Token.Punctuation, Token.Keyword, Token.Punctuation, Token.Name.Class, Token.Punctuation, Token.Comment.Single)),
            (r'(\/\/\s*)(\*+\s+)([A-Za-zА-Яа-яЁё_][\wа-яё0-9_]*)(\s+(?:-|–)\s+)(см\.)(\s+)([A-Za-zА-Яа-яЁё_][\wа-яё0-9_]*(?:\.[A-Za-zА-Яа-яЁё_][\wа-яё0-9_]*)*)(.*)',
             bygroups(Token.Comment.Single, Token.Punctuation, Token.Name.Variable, Token.Punctuation, Token.Keyword, Token.Comment.Single, Token.Name.Class, Token.Comment.Single)),
            (r'(\/\/\s*)(\*+\s+)([A-Za-zА-Яа-яЁё_][\wа-яё0-9_]*)(\s+(?:-|–)\s+)(' + DOC_TYPE_LIST_PATTERN + r')(\s+(?:-|–)\s+)(.*)',
             bygroups(Token.Comment.Single, Token.Punctuation, Token.Name.Variable, Token.Punctuation, Token.Name.Class, Token.Punctuation, Token.Comment.Single)),
            (r'(\/\/\s*)(\*+\s+)([A-Za-zА-Яа-яЁё_][\wа-яё0-9_]*)(\s+(?:-|–)\s+)(' + DOC_TYPE_LIST_PATTERN + r')(?=\s*$)',
             bygroups(Token.Comment.Single, Token.Punctuation, Token.Name.Variable, Token.Punctuation, Token.Name.Class)),
            (r'(\/\/\s*)(\*{1,2})(\s+)(.*)',
             bygroups(Token.Comment.Single, Token.Punctuation, Token.Comment.Single, Token.Comment.Single)),
            (r'(\/\/\s*)(-\s*)(' + DOC_TYPE_LIST_PATTERN + r')(\s+)([Ии]з)(\s+)(см\.)(\s+)([A-Za-zА-Яa-яЁё_][\wа-яё0-9_]*(?:\.[A-Za-zА-Яa-яЁё_][\wа-яё0-9_]*)*)(\s+(?:-|–)\s+)(.*)',
             bygroups(Token.Comment.Single, Token.Punctuation, Token.Name.Class, Token.Punctuation, Token.Keyword, Token.Punctuation, Token.Keyword, Token.Comment.Single, Token.Name.Class, Token.Punctuation, Token.Comment.Single)),
            (r'(\/\/\s*)(-\s*)(' + DOC_TYPE_LIST_PATTERN + r')(\s+)([Ии]з)(\s+)(см\.)(\s+)([A-Za-zА-Яa-яЁё_][\wа-яё0-9_]*(?:\.[A-Za-zА-Яa-яЁё_][\wа-яё0-9_]*)*)(?=\s*$)',
             bygroups(Token.Comment.Single, Token.Punctuation, Token.Name.Class, Token.Punctuation, Token.Keyword, Token.Punctuation, Token.Keyword, Token.Comment.Single, Token.Name.Class)),
            (r'(\/\/\s*)(-\s*)(' + DOC_TYPE_LIST_WITH_IZ_PATTERN + r')(\s+(?:-|–)\s+)(.*)',
             _doc_type_list_with_iz_callback),
            (r'(\/\/\s*)(-\s*)(' + DOC_TYPE_LIST_PATTERN + r')(\s+(?:-|–)\s+)(.*)',
             _doc_type_list_bullet_callback),
            (r'(\/\/\s*)(-\s*)(' + DOC_TYPE_LIST_PATTERN + r')(?=\s*$)',
             bygroups(Token.Comment.Single, Token.Punctuation, Token.Name.Class)),
            (r'(\/\/\s*)([A-Za-zА-Яа-яЁё_][\wа-яё0-9_]*)(\s+(?:-|–)\s+)(.*)',
             bygroups(Token.Comment.Single, Token.Name.Class, Token.Punctuation, Token.Comment.Single)),
            (r'(\/\/\s*)(TODO:)(.*)',
             bygroups(Token.Comment.Single, Token.Keyword, Token.Comment.Single)),
            (r'(\/\/\s*)(\{\{|\}\})(MRG)(\[[^\]]*\])(.*)',
             bygroups(Token.Comment.Single, Token.Punctuation, Token.Keyword, Token.Punctuation, Token.Comment.Single)),
            (r'\/\/.*?(?=\n|$)', Token.Comment.Single),
        ],
        'root': [
            (r'\ufeff', Token.Text),
            (r'\r\n?|\n', Token.Text),
            (r'[^\S\n]+', Token.Text),
            (r'\|.*?(?=\n|$)', Token.Generic.Error),
            (r'\#\!.*?(?=\n|$)', Token.Comment.Preproc),
            include('doc_comment'),
            include('preproc_root'),
            # decorator with quoted name: split into decorator, punctuation and inner name
            (r'(&[\wа-яё_][\wа-яё0-9_]*)\s*(\()\s*(")([^"]*)(")\s*(\))',
             bygroups(Token.Name.Decorator, Token.Punctuation, Token.String.Single, Token.Name.Function, Token.String.Single, Token.Punctuation)),
            # decorator with parameters: split decorator and parse parameters
            (r'(&[\wа-яё_][\wа-яё0-9_]*)\s*(\()', bygroups(Token.Name.Decorator, Token.Punctuation), 'decorator_params'),
            (r'(Новый|New)(\s*)(\()(\s*)(")(' + TYPE_NAME_PATTERN + r')(")(\s*)(\))',
             bygroups(Token.Name.Builtin, Token.Text, Token.Punctuation, Token.Text, Token.String, Token.Name.Class, Token.String, Token.Text, Token.Punctuation)),
            (r'(Новый|New)(\s+)(' + TYPE_NAME_PATTERN + r')\b',
             bygroups(Token.Keyword, Token.Text, Token.Name.Class)),
            (rf'({METADATA_ROOT})(\.)({IDENT})(\.)', bygroups(Token.Name.Namespace, Token.Operator, Token.Name.Class, Token.Operator)),
            (r'[\[\]:(),;]', Token.Punctuation),
            (r'\&.*$', Token.Name.Decorator),
            (r'\b(Процедура|Функция|Procedure|Function)\b(\s+)([\wа-яё_][\wа-яё0-9_]*)\s*(\()',
             bygroups(Token.Keyword, Token.Text, Token.Name.Function, Token.Punctuation), 'params'),
            (r'=', Token.Operator, 'after_assign'),
            (OPERATORS, Token.Operator),
            (r'\#.*$', Token.Comment.Preproc),
            # match forbidden-constant calls like Неопределено(....) as a single error token
            (r'\b(?:' + '|'.join(CONSTANT_NAMES) + r')\b\s*\([^\)]*\)', Token.Generic.Error),
            (EXECUTE_STRING_CALL, Token.Name.Builtin),
            (rf'(?<=\.){IDENT}(?=\s*\()', Token.Name.Function),
            (rf'(?<=\.){IDENT}', Token.Name.Variable),
            (rf'{PREFIX_NO_DOT}{IDENT}', _bsl_name_callback),
            (r'\b\d+\.?\d*\b', Token.Literal.Number),
            (CONSTRAINT_STRING_START, Token.Literal.String, 'constraint_string'),
            (QUERY_STRING_START, Token.Literal.String, 'query_string'),
            include('string_locale_start'),
            ('\"', Token.String, 'string'),
            (r'\'.*?\'', Token.Literal.Date),
            (r'~.*?(?=[:;])', Token.Name.Label),
        ],
        'preproc_if': [
            (r'\r\n?|\n', Token.Text, '#pop'),
            (r'\b(Сервер|НаСервере|Клиент|НаКлиенте|ТонкийКлиент|МобильныйКлиент|ВебКлиент|ВнешнееСоединение|ТолстыйКлиентУправляемоеПриложение|ТолстыйКлиентОбычноеПриложение|МобильныйАвтономныйСервер|МобильноеПриложениеКлиент|МобильноеПриложениеСервер|Server|AtServer|Client|AtClient|ThinClient|WebClient|ExternalConnection|MobileClient|MobileStandaloneServer|MobileAppClient|MobileAppServer|ThickClientOrdinaryApplication|ThickClientManagedApplication|Windows|Linux|MacOS)\b', Token.Keyword.Constant),
            (r'\b(И|Или|НЕ|Then|Тогда|And|Or|Not)\b', Token.Comment.Preproc),
            (r'\#', Token.Comment.Preproc),
            (r'[()]', Token.Comment.Punctuation),
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
            (r'(?![^\S\n]*\|)[^"\n]+(?=\n(?![^\S\n]*(?:\||//|\#)))', Token.Generic.Error, '#pop'),
            (r'\r\n?|\n', Token.Text),
            (r'(?<=\n)[^\S\n]+', Token.Text),
            (r'(?<=[^\S\n])\/\/.*?(?=\n)', Token.Comment.Single),
            (r'\#(Удаление|Delete|КонецУдаления|EndDelete)\b.*', Token.Comment.Preproc),
            (r'(?<=^)\/\/.*?(?=\n)', Token.Comment.Single),
            (r'(?<=\n)([^\S\n]*)(\|)([^\n"]+)(?=\n(?![^\S\n]*(?:\||//|\#)))',
             bygroups(Token.Text, Token.String, Token.Generic.Error), '#pop'),
            (r'(\|)([^\n"]+)(?=\n(?![^\S\n]*(?:\||//|\#)))',
             bygroups(Token.String, Token.Generic.Error), '#pop'),
            (r'\|', Token.String),
            (r'\"\"', Token.String.Escape),
            (r"\\'", Token.String.Escape),
            (r'%\d', Token.String.Interpol),
            (r'%%', Token.String.Escape),
            (r'%[A-Za-zА-Яа-яЁё_]', Token.Generic.Error),
            (r'(?:\\(?!\')|%(?![%\dA-Za-zА-Яа-яЁё_])|[^\"\|\n%\\])+', Token.String),
        ],
        'string_locale_first_line': [
            ('\"(?![\"])(?=[^\S\n]*(?:\\)|,|;|$))', Token.String, '#pop'),
            ('\"(?![\"])', Token.String, ('#pop', 'string_trailing_error')),
            (_LOCALE_MISSING_SEMICOLON_PIPE_FIRST_PATTERN,
             _locale_missing_semicolon_pipe_callback, 'string_locale_error_pipe_pop'),
            (_LOCALE_MISSING_SEMICOLON_FIRST_PATTERN, _locale_missing_semicolon_callback, 'string_locale_error_missing_semicolon'),
            (_LOCALE_EXTRA_QUOTE_FIRST_PATTERN, _locale_extra_quote_callback, 'string_locale_error_pipe_strict'),
            (r'(?![^\n]*;)[^\n"]+(?=\n[^\S\n]*\|\s*' + LOCALE_KEY_PATTERN + r'\b\s*=)',
             Token.Generic.Error, 'string_locale_error_pipe_pop'),
            (r'(?<=\n)[^\n"]+(?=\n[^\S\n]*\|\s*' + LOCALE_KEY_PATTERN + r'\b\s*=)',
             Token.Generic.Error, 'string_locale_error_pipe_pop'),
            (r'(?=[^\n]*\b' + LOCALE_KEY_PATTERN + r'\b\s*=)' +
             _ODD_LOCALE_QUOTES_LOOKAHEAD +
             r'(?![^\n;]*\n[^\S\n]*\|)([^\n"]+)(")',
             _locale_missing_open_quote_callback, '#pop'),
            (r'(?=[^\n]*\b' + LOCALE_KEY_PATTERN + r'\b\s*=)' +
             _ODD_LOCALE_QUOTES_LOOKAHEAD +
             r'(?![^\n\']*\'[^\n\']*\')' +
             r'(?![^\n;]*\n[^\S\n]*\|)[^\n"]+(?=\n|")',
             Token.Generic.Error, 'string_locale_error'),
            (r'(?![^\n]*;)(?!' + _ODD_LOCALE_QUOTES_LOOKAHEAD + r')[^\n"]+(?=\n)',
             Token.Generic.Error, 'string_locale_error'),
            (r'\r\n?|\n', Token.Text, ('#pop', 'string_locale')),
            (r'(?<=\n)[^\S\n]+', Token.Text),
            (r'(?<=[^\S\n])\/\/.*?(?=\n)', Token.Comment.Single),
            (r'(?<=^)\/\/.*?(?=\n)', Token.Comment.Single),
            (r'[^\S\n]+', Token.String),
            (r"'([^'\n]*)'", _locale_single_quote_callback),
            (r"'", Token.String.Escape, 'string_locale_single_quote'),
            (r'\|', Token.String),
            (r'\"\"', Token.String.Escape),
            (r"\\'", Token.String.Escape),
            (r'%\d', Token.String.Interpol),
            (r'%%', Token.String.Escape),
            (r'%[A-Za-zА-Яа-яЁё_]', Token.Generic.Error),
            (r'(\b' + LOCALE_KEY_PATTERN + r'\b)(\s*)(=)', _locale_assignment_callback),
            (r';', Token.Operator),
            (r'(?:(?!\b' + LOCALE_KEY_PATTERN + r'\b\s*=)(?:\\(?!\')|%(?![%\dA-Za-zА-Яа-яЁё_])|[^\"\|\n%\\;]))+', Token.String),
        ],
        'string_locale': [
            ('\"(?![\"])(?=[^\S\n]*(?:\\)|,|;|$))', Token.String, '#pop'),
            ('\"(?![\"])', Token.String, ('#pop', 'string_trailing_error')),
            (r'\r\n?|\n', Token.Text),
            (_LOCALE_MISSING_SEMICOLON_PIPE_PATTERN,
             _locale_missing_semicolon_pipe_callback, 'string_locale_error_pipe_pop'),
            (r'(?<=\n)' + _LOCALE_MISSING_SEMICOLON_PATTERN, _locale_missing_semicolon_callback, 'string_locale_error_missing_semicolon'),
            (r'(?<=\n)' + _LOCALE_EXTRA_QUOTE_PATTERN, _locale_extra_quote_callback, 'string_locale_error_pipe_strict'),
            (r'(?<=\n)(?![^\n]*;)[^\n"]+(?=\n[^\S\n]*\|\s*' + LOCALE_KEY_PATTERN + r'\b\s*=)',
             Token.Generic.Error, 'string_locale_error_pipe_pop'),
            (r'(?<=\n)(?=[^\n]*\b' + LOCALE_KEY_PATTERN + r'\b\s*=)' +
             _ODD_LOCALE_QUOTES_LOOKAHEAD +
             r'(?![^\n;]*\n[^\S\n]*\|)([^\n"]+)(")',
             _locale_missing_open_quote_callback, '#pop'),
            (r'(?<=\n)(?=[^\n]*\b' + LOCALE_KEY_PATTERN + r'\b\s*=)' +
             _ODD_LOCALE_QUOTES_LOOKAHEAD +
             r'(?![^\n\']*\'[^\n\']*\')' +
             r'(?![^\n;]*\n[^\S\n]*\|)[^\n"]+(?=\n|")',
             Token.Generic.Error, 'string_locale_error'),
            (r'(?<=\n)(?![^\n]*;)(?!' + _ODD_LOCALE_QUOTES_LOOKAHEAD + r')(?![^\n]*\b' +
             LOCALE_KEY_PATTERN + r'\b\s*=)[^\n"]+(?=\n)',
             Token.Generic.Error, 'string_locale_error'),
            (r'(?<=\n)(?![^\n]*;)(?!' + _ODD_LOCALE_QUOTES_LOOKAHEAD + r')(?![^\n]*\b' +
             LOCALE_KEY_PATTERN + r'\b\s*=)[^\n"]+(?=")',
             Token.Generic.Error, 'string_locale_error'),
            (r'(?<=\n)[^\S\n]+', Token.Text),
            (r'(?<=[^\S\n])\/\/.*?(?=\n)', Token.Comment.Single),
            (r'(?<=^)\/\/.*?(?=\n)', Token.Comment.Single),
            (r'[^\S\n]+', Token.String),
            (r"'([^'\n]*)'", _locale_single_quote_callback),
            (r"'", Token.String.Escape, 'string_locale_single_quote'),
            (r'\|', Token.String),
            (r'\"\"', Token.String.Escape),
            (r"\\'", Token.String.Escape),
            (r'%\d', Token.String.Interpol),
            (r'%%', Token.String.Escape),
            (r'%[A-Za-zА-Яа-яЁё_]', Token.Generic.Error),
            (r'(\b' + LOCALE_KEY_PATTERN + r'\b)(\s*)(=)', _locale_assignment_callback),
            (r';', Token.Operator),
            (r'(?:(?!\b' + LOCALE_KEY_PATTERN + r'\b\s*=)(?:\\(?!\')|%(?![%\dA-Za-zА-Яа-яЁё_])|[^\"\|\n%\\;]))+', Token.String),
        ],
        'string_after_assign': [
            ('\"(?![\"])(?=[^\S\n]*(?:;|\\+|,|\\)|$|\\b(?:Тогда|Then|И|ИЛИ|НЕ|Иначе|Else|ИначеЕсли|ElsIf)\\b))',
             Token.String, '#pop'),
            ('\"(?![\"])', Token.String, ('#pop', 'string_trailing_error')),
            (r'(?![^\S\n]*\|)[^"\n]+(?=\n(?![^\S\n]*(?:\||//|\#)))', Token.Generic.Error, '#pop'),
            (r'\r\n?|\n', Token.Text),
            (r'(?<=\n)[^\S\n]+', Token.Text),
            (r'(?<=[^\S\n])\/\/.*?(?=\n)', Token.Comment.Single),
            (r'\#(Удаление|Delete|КонецУдаления|EndDelete)\b.*', Token.Comment.Preproc),
            (r'(?<=^)\/\/.*?(?=\n)', Token.Comment.Single),
            (r'(?<=\n)([^\S\n]*)(\|)([^\n"]+)(?=\n(?![^\S\n]*(?:\||//|\#)))',
             bygroups(Token.Text, Token.String, Token.Generic.Error), '#pop'),
            (r'(\|)([^\n"]+)(?=\n(?![^\S\n]*(?:\||//|\#)))',
             bygroups(Token.String, Token.Generic.Error), '#pop'),
            (r'\|', Token.String),
            (r'\"\"', Token.String.Escape),
            (r"\\'", Token.String.Escape),
            (r'%\d', Token.String.Interpol),
            (r'%%', Token.String.Escape),
            (r'%[A-Za-zА-Яа-яЁё_]', Token.Generic.Error),
            (r'(?:\\(?!\')|%(?![%\dA-Za-zА-Яа-яЁё_])|[^\"\|\n%\\])+', Token.String),
        ],
        'string_trailing_error': [
            (r'[^\n]+', Token.Generic.Error),
            (r'\r\n?|\n', Token.Text, '#pop'),
        ],
        'string_locale_error': [
            (r'\"\"', Token.Generic.Error),
            (r'"', Token.String, '#pop:2'),
            (r'\n[^\S\n]*\|[^\n"]*', _locale_error_pipe_line_callback),
            (r'\r\n?|\n', Token.Generic.Error),
            (r'[^\"\n]+', Token.Generic.Error),
        ],
        'string_locale_error_missing_semicolon': [
            (r'\"\"', Token.Generic.Error),
            (r'"', Token.String, '#pop:2'),
            (r'\r\n?|\n', Token.Generic.Error),
            (r'[^\"\n]+', Token.Generic.Error),
        ],
        'string_locale_error_pipe_pop': [
            (r'\n[^\S\n]*\|[^\n"]*', _locale_error_pipe_line_callback, '#pop'),
            (r'\"\"', Token.Generic.Error),
            (r'"', Token.String, '#pop:2'),
            (r'\r\n?|\n', Token.Generic.Error),
            (r'[^\"\n]+', Token.Generic.Error),
        ],
        'string_locale_error_pipe_strict': [
            (r'\n[^\S\n]*\|[^\n"]*', _locale_error_pipe_line_callback),
            (r'\"\"', Token.Generic.Error),
            (r'"', Token.Generic.Error, '#pop:2'),
            (r'\r\n?|\n', Token.Generic.Error),
            (r'[^\"\n]+', Token.Generic.Error),
        ],
        'string_locale_single_quote': [
            (r"'", Token.String.Escape, '#pop'),
            (r'\r\n?|\n', Token.Text),
            (r'(?<=\n)[^\S\n]+', Token.Text),
            (r'\|', Token.String),
            (r'\"\"', Token.String.Escape),
            (r'%\d', Token.String.Interpol),
            (r'%%', Token.String.Escape),
            (r'%[A-Za-zА-Яа-яЁё_]', Token.Generic.Error),
            (r"[^'\"\|\n%]+", Token.String),
            (r'.', Token.String),
        ],
        'after_assign': [
            (r'\r\n?|\n', Token.Text, '#pop'),
            (r'[^\S\n]+', Token.Text),
            (QUERY_STRING_START, Token.Literal.String, ('#pop', 'query_string')),
            (r'"(?=(?:[^"]|"")*\b' + LOCALE_KEY_PATTERN + r'\b\s*=)', Token.String, ('#pop', 'string_locale_first_line')),
            (r'"', Token.String, ('#pop', 'string_after_assign')),
            default('#pop'),
        ],
        'query_string': [
            (r'[^\S\n]+', Token.Text),
            (r'(\|)(//(?:[^"\n]|\"\")*(?=\n|"))',
             bygroups(Token.Literal.String, Token.Comment.Single)),
            (r'//[^\n]*', Token.Comment.Single),
            (r'""', Token.Literal.String.Escape),
            (r'"', Token.Literal.String, '#pop'),
            # Delay instantiation to avoid forward reference issues and keep formatter options
            (r'\n', Token.Text),
            (r'(?:[^"/\n]|/(?!/))+', using(lambda **kwargs: SdblQueryLexer(**kwargs))),
        ],
        'constraint_string': [
            (r'[^\S\n]+', Token.Text),
            (r'(\|)(//(?:[^"\n]|\"\")*(?=\n|"))',
             bygroups(Token.Literal.String, Token.Comment.Single)),
            (r'//[^\n]*', Token.Comment.Single),
            (r'""', Token.Literal.String.Escape),
            (r'"', Token.Literal.String, '#pop'),
            (r'\n', Token.Text),
            (r'(?:[^"/\n]|/(?!/))+', using(lambda **kwargs: ConstraintLogicLexer(**kwargs))),
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
            (CONSTRAINT_STRING_START, Token.Literal.String, 'constraint_string'),
            (QUERY_STRING_START, Token.Literal.String, 'query_string'),
            (r'.', Token.Text),
        ],
        'params': [
            (r'\)', Token.Punctuation, '#pop'),
            (r'\r\n?|\n', Token.Text),
            (r'[^\S\n]+', Token.Text),
            (r'\/\/.*?(?=\n|$)', Token.Comment.Single),
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
            (CONSTRAINT_STRING_START, Token.Literal.String, 'constraint_string'),
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

    _OPERATOR_WORDS = (
        'И','ИЛИ','НЕ',
        'ПОДОБНО','В','ИЕРАРХИИ','МЕЖДУ','ЕСТЬ',
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
    _OPERATOR_WORD_SINGLE = tuple(
        word for word in _OPERATOR_WORDS if ' ' not in word
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
            (r'\/\/.*?(?=\n|$)', Token.Comment.Single),
            (r'\|', Token.Generic.Error),
            (r'(&[A-Za-zА-Яа-яЁё_][\wа-яё0-9_]*)', Token.Literal.String.Interpol),
            (r'(\#[A-Za-zА-Яа-яЁё_][\wа-яё0-9_]*)', Token.Generic.Error),
            (r'(\.)([!#][^\s\.,;\(\)]+)', bygroups(Token.Operator, Token.Generic.Error)),
            (OPERATORS, Token.Operator),
            (words(_OPERATOR_WORD_SINGLE, prefix=PREFIX_NO_DOT, suffix=SUFFIX_WORD), Token.Operator.Word),
            (_METADATA_CHAIN, _sdbl_metadata_callback),
            (r'(КАК)(\s+)(?!(?i:(?:ЧИСЛО|NUMBER|ИЗМЕНЕНИЯ|UPDATE))(?=\s|,|\(|\)|\n|$))([A-Za-zА-Яа-яЁё_][\wа-яё0-9_]*)',
             bygroups(Token.Keyword.Declaration, Token.Text, Token.Name.Variable)),
            (r'(ВЫРАЗИТЬ)(\s*)(\()', bygroups(Token.Name.Builtin, Token.Text, Token.Punctuation), 'cast_params'),
            (rf'(?<=\.){IDENT}(?=\s*\()', Token.Name.Function),
            (rf'(?<=\.){IDENT}', Token.Name.Variable),
            (r'[\[\]:(),;]', Token.Punctuation),
            (words(_FUNCTION_CALL_PHRASES, prefix=PREFIX_NO_DOT, suffix=SUFFIX_CALL), Token.Name.Builtin),
            (words(_KEYWORD_DECLARATION_PHRASES, prefix=PREFIX_NO_DOT, suffix=SUFFIX_WORD), Token.Keyword.Declaration),
            (rf'{PREFIX_NO_DOT}{IDENT}', _sdbl_name_callback),
            (r'\b\d+\.?\d*\b', Token.Literal.Number),
            ('\"', Token.Literal.String, 'string'),
        ],
        'cast_params': [
            (r'\)', Token.Punctuation, '#pop'),
            (r'\(', Token.Punctuation, '#push'),
            (r'\r\n?|\n', Token.Text),
            (r'[^\S\n]+', Token.Text),
            (r'\/\/.*?(?=\n)', Token.Comment.Single),
            (r'(&[A-Za-zА-Яа-яЁё_][\wа-яё0-9_]*)', Token.Literal.String.Interpol),
            (r'(\#[A-Za-zА-Яа-яЁё_][\wа-яё0-9_]*)', Token.Generic.Error),
            (r'(\.)([!#][^\s\.,;\(\)]+)', bygroups(Token.Operator, Token.Generic.Error)),
            (OPERATORS, Token.Operator),
            (words(_OPERATOR_WORD_SINGLE, prefix=PREFIX_NO_DOT, suffix=SUFFIX_WORD), Token.Operator.Word),
            (_METADATA_CHAIN, _sdbl_metadata_callback),
            (r'(КАК)(\s+)([A-Za-zА-Яа-яЁё_][\wа-яё0-9_]*)',
             bygroups(Token.Keyword.Declaration, Token.Text, Token.Name.Class)),
            (rf'(?<=\.){IDENT}(?=\s*\()', Token.Name.Function),
            (rf'(?<=\.){IDENT}', Token.Name.Variable),
            (r'[\[\]:(),;]', Token.Punctuation),
            (words(_FUNCTION_CALL_PHRASES, prefix=PREFIX_NO_DOT, suffix=SUFFIX_CALL), Token.Name.Builtin),
            (r'(?-i:ССЫЛКА|REFS)\b', Token.Operator.Word),
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


class ConstraintLogicLexer(RegexLexer):
    name = '1C (Access Rights Logic) Lexer'
    aliases = []
    filenames = []

    flags = re.MULTILINE | re.IGNORECASE | re.VERBOSE

    _KEYWORD_DECLARATION_WORDS = (
        'ПрисоединитьДополнительныеТаблицы','AttachAdditionalTables',
        'ЭтотСписок','ThisList',
        'РазрешитьЧтениеИзменение','AllowReadUpdate',
        'РазрешитьЧтение','AllowRead',
        'РазрешитьИзменениеЕслиРазрешеноЧтение','AllowUpdateIfReadingAllowed',
        'ГДЕ','WHERE',
        'ЛЕВОЕ','LEFT',
        'СОЕДИНЕНИЕ','JOIN',
        'ПО','ON',
        'КАК','AS',
        'ВЫБОР','CASE',
        'КОГДА','WHEN',
        'ТОГДА','THEN',
        'ИНАЧЕ','ELSE',
        'КОНЕЦ','END',
        'ТОЛЬКО','ONLY',
        'КРОМЕ','EXCEPT',
    )

    _OPERATOR_WORDS = (
        'И','ИЛИ','НЕ',
        'В','ЕСТЬ',
    )

    _KEYWORD_CONSTANT_WORDS = (
        'НЕОПРЕДЕЛЕНО','UNDEFINED','Истина','True','Ложь','False','NULL','Null',
        'ПустаяСсылка','Отключено','Disabled',
    )

    _FUNCTION_CALL_WORDS = (
        'ЗначениеРазрешено','ValueAllowed',
        'ЧтениеОбъектаРазрешено','ObjectReadingAllowed',
        'ИзменениеОбъектаРазрешено','ObjectUpdateAllowed',
        'ЧтениеСпискаРазрешено','ListReadingAllowed',
        'ИзменениеСпискаРазрешено','ListUpdateAllowed',
        'ЭтоАвторизованныйПользователь','IsAuthorizedUser',
        'ПравоДоступа','AccessRight',
        'РольДоступна','RoleAvailable',
        'ДляВсехСтрок','ForAllRows',
        'ДляОднойИзСтрок','ForAtLeastOneRow',
        'ТипЗначения','ValueType',
        'Тип','Type',
        'Значение','Value',
    )

    IDENT = r'[A-Za-zА-Яа-яЁё_][\wа-яё0-9_]*'
    METADATA_ROOT = SdblLexer.METADATA_ROOT
    _METADATA_CHAIN = rf'{PREFIX_NO_DOT}{METADATA_ROOT}(?:\.[^\s\.,;\(\)]+)+'

    OPERATORS = r'(<=|>=|<>|=|<|>|\+|-|\*|\/|\.)'

    _KEYWORD_DECLARATION_PHRASES = tuple(
        word for word in _KEYWORD_DECLARATION_WORDS if ' ' in word
    )
    _KEYWORD_DECLARATION_SINGLE = tuple(
        word for word in _KEYWORD_DECLARATION_WORDS if ' ' not in word
    )
    _OPERATOR_WORD_SINGLE = tuple(
        word for word in _OPERATOR_WORDS if ' ' not in word
    )
    _FUNCTION_CALL_PHRASES = tuple(
        word for word in _FUNCTION_CALL_WORDS if ' ' in word
    )
    _FUNCTION_CALL_SINGLE = tuple(
        word for word in _FUNCTION_CALL_WORDS if ' ' not in word
    )

    _acl_keyword_declaration = _casefold_set(_KEYWORD_DECLARATION_SINGLE)
    _acl_keyword_constant = _casefold_set(_KEYWORD_CONSTANT_WORDS)
    _acl_function_call = _casefold_set(_FUNCTION_CALL_SINGLE)
    _acl_name_class = _casefold_set(SdblLexer._NAME_CLASS_WORDS)

    tokens = {
        'root': [
            (r'\ufeff', Token.Text),
            (r'\r\n?|\n', Token.Text),
            (r'[^\S\n]+', Token.Text),
            (r'\/\/.*?(?=\n|$)', Token.Comment.Single),
            (r'\|', Token.Literal.String),
            (OPERATORS, Token.Operator),
            (words(_OPERATOR_WORD_SINGLE, prefix=PREFIX_NO_DOT, suffix=SUFFIX_WORD), Token.Operator.Word),
            (_METADATA_CHAIN, _sdbl_metadata_callback),
            (rf'(?<=\.){IDENT}(?=\s*\()', Token.Name.Function),
            (rf'(?<=\.){IDENT}', Token.Name.Variable),
            (r'[\[\]:(),;]', Token.Punctuation),
            (rf'{PREFIX_NO_DOT}{IDENT}', _constraint_name_callback),
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
