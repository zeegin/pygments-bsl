import os
import re
from unittest import TestCase

from pygments import lexers
from pygments.token import Token

# from pygments_bsl import lexer as lexer_mod
from pygments_bsl.lexer import BslLexer, SdblLexer

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
SPACE_RE = re.compile(r'^[ \n\r\uFEFF]+$')


def filter_tokens(tokens):
    """Drop whitespace/empty tokens for easier assertions."""
    return [
        tok for tok in tokens
        if not (tok[0] is Token.Text and SPACE_RE.match(tok[1])) and tok[1] != ''
    ]


class LexerTestCase(TestCase):
    lexer_name = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        if cls.lexer_name is None:
            raise ValueError("lexer_name must be set on test class")
        cls.lexer = lexers.get_lexer_by_name(cls.lexer_name)

    def lex_filtered(self, source):
        return filter_tokens(self.lexer.get_tokens(source))

    def assertTokens(self, source, expected):
        self.assertEqual(self.lex_filtered(source), expected)

    def assertTokensPrefix(self, source, expected_prefix):
        filtered = self.lex_filtered(source)
        self.assertEqual(filtered[:len(expected_prefix)], expected_prefix)
        return filtered


class BslLexerTestCase(LexerTestCase):

    lexer_name = 'bsl'

    maxDiff = None # if characters too more at assertEqual

    def test_guess_lexer_for_filename(self):
        with open(os.path.join(CURRENT_DIR, 'examplefiles', 'bsl', 'samples.bsl'), 'r', encoding='utf-8') as fh:
            text_bsl = fh.read()
            guessed_lexer = lexers.guess_lexer_for_filename('samples.bsl', text_bsl)
            self.assertEqual(guessed_lexer.name, BslLexer.name)

        with open(os.path.join(CURRENT_DIR, 'examplefiles', 'bsl', 'samples.os'), 'r', encoding='utf-8') as fh:
            text_os = fh.read()
            guessed_lexer = lexers.guess_lexer_for_filename('samples.os', text_os)
            self.assertEqual(guessed_lexer.name, BslLexer.name)

    def test_get_lexer_by_name(self):
        lexer = lexers.get_lexer_by_name('bsl')
        self.assertEqual(lexer.name, BslLexer.name)

        lexer = lexers.get_lexer_by_name('os')
        self.assertEqual(lexer.name, BslLexer.name)

    def test_lexing_region(self):
        self.assertTokens(
            '''
            #Область ИмяОбласти
            // это комментарий
            #КонецОбласти
            ''',
            [
                (Token.Comment.Preproc, '#Область ИмяОбласти'),
                (Token.Comment.Single, '// это комментарий'),
                (Token.Comment.Preproc, '#КонецОбласти'),
            ],
        )

    def test_lexing_preproc_if_chain(self):
        self.assertTokens(
            '''
#Если Сервер Тогда
#ИначеЕсли Клиент Тогда
#Иначе
#КонецЕсли
            ''',
            [
                (Token.Comment.Preproc, '#Если'),
                (Token.Keyword.Constant, 'Сервер'),
                (Token.Comment.Preproc, 'Тогда'),
                (Token.Comment.Preproc, '#ИначеЕсли'),
                (Token.Keyword.Constant, 'Клиент'),
                (Token.Comment.Preproc, 'Тогда'),
                (Token.Comment.Preproc, '#Иначе'),
                (Token.Comment.Preproc, '#КонецЕсли'),
            ],
        )

    def test_lexing_preproc_if_complex_expression(self):
        self.assertTokens(
            '''
#Если Сервер Или ТолстыйКлиентОбычноеПриложение И НЕ ВнешнееСоединение Тогда
#КонецЕсли
            ''',
            [
                (Token.Comment.Preproc, '#Если'),
                (Token.Keyword.Constant, 'Сервер'),
                (Token.Comment.Preproc, 'Или'),
                (Token.Keyword.Constant, 'ТолстыйКлиентОбычноеПриложение'),
                (Token.Comment.Preproc, 'И'),
                (Token.Comment.Preproc, 'НЕ'),
                (Token.Keyword.Constant, 'ВнешнееСоединение'),
                (Token.Comment.Preproc, 'Тогда'),
                (Token.Comment.Preproc, '#КонецЕсли'),
            ],
        )

    def test_lexing_preproc_if_nested(self):
        self.assertTokens(
            '''
#Если (Клиент Или (НЕ Клиент)) И НЕ Клиент Тогда
#ИначеЕсли ((((Не (ВебКлиент))) И ((НЕ МобильныйКлиент)))) Тогда
#КонецЕсли
            ''',
            [
                (Token.Comment.Preproc, '#Если'),
                (Token.Comment.Punctuation, '('),
                (Token.Keyword.Constant, 'Клиент'),
                (Token.Comment.Preproc, 'Или'),
                (Token.Comment.Punctuation, '('),
                (Token.Comment.Preproc, 'НЕ'),
                (Token.Keyword.Constant, 'Клиент'),
                (Token.Comment.Punctuation, ')'),
                (Token.Comment.Punctuation, ')'),
                (Token.Comment.Preproc, 'И'),
                (Token.Comment.Preproc, 'НЕ'),
                (Token.Keyword.Constant, 'Клиент'),
                (Token.Comment.Preproc, 'Тогда'),
                (Token.Comment.Preproc, '#ИначеЕсли'),
                (Token.Comment.Punctuation, '('),
                (Token.Comment.Punctuation, '('),
                (Token.Comment.Punctuation, '('),
                (Token.Comment.Punctuation, '('),
                (Token.Comment.Preproc, 'Не'),
                (Token.Comment.Punctuation, '('),
                (Token.Keyword.Constant, 'ВебКлиент'),
                (Token.Comment.Punctuation, ')'),
                (Token.Comment.Punctuation, ')'),
                (Token.Comment.Punctuation, ')'),
                (Token.Comment.Preproc, 'И'),
                (Token.Comment.Punctuation, '('),
                (Token.Comment.Punctuation, '('),
                (Token.Comment.Preproc, 'НЕ'),
                (Token.Keyword.Constant, 'МобильныйКлиент'),
                (Token.Comment.Punctuation, ')'),
                (Token.Comment.Punctuation, ')'),
                (Token.Comment.Punctuation, ')'),
                (Token.Comment.Punctuation, ')'),
                (Token.Comment.Preproc, 'Тогда'),
                (Token.Comment.Preproc, '#КонецЕсли'),
            ],
        )

    def test_lexing_preproc_if_platforms(self):
        self.assertTokens(
            '''
#Если MacOS Или Linux Тогда
#КонецЕсли
            ''',
            [
                (Token.Comment.Preproc, '#Если'),
                (Token.Keyword.Constant, 'MacOS'),
                (Token.Comment.Preproc, 'Или'),
                (Token.Keyword.Constant, 'Linux'),
                (Token.Comment.Preproc, 'Тогда'),
                (Token.Comment.Preproc, '#КонецЕсли'),
            ],
        )

    def test_lexing_shebang(self):
        self.assertTokens(
            '#! /usr/bin/bsl',
            [
                (Token.Comment.Preproc, '#! /usr/bin/bsl'),
            ],
        )

    def test_lexing_preproc_native(self):
        self.assertTokens(
            '#native',
            [
                (Token.Comment.Preproc, '#native'),
            ],
        )

    def test_lexing_preproc_unknown_symbol(self):
        self.assertTokens(
            '''
#Если Нечто Тогда
#КонецЕсли
            ''',
            [
                (Token.Comment.Preproc, '#Если'),
                (Token.Comment.Preproc, 'Нечто'),
                (Token.Comment.Preproc, 'Тогда'),
                (Token.Comment.Preproc, '#КонецЕсли'),
            ],
        )

    def test_multiline_string_with_preproc_delete(self):
        self.assertTokens(
            '''
"выбрать
#Удаление
|часть строки
#КонецУдаления
|конец строки"
            ''',
            [
                (Token.String, '"'),
                (Token.String, 'выбрать'),
                (Token.Comment.Preproc, '#Удаление'),
                (Token.Literal.String, '|'),
                (Token.Literal.String, 'часть строки'),
                (Token.Comment.Preproc, '#КонецУдаления'),
                (Token.Literal.String, '|'),
                (Token.String, 'конец строки'),
                (Token.String, '"'),
            ],
        )

    def test_lexing_preproc_insert_and_delete_blocks(self):
        self.assertTokens(
            '''
#Вставка
Процедура ДобавитьКод() КонецПроцедуры
#КонецВставки
#Удаление
Функция Устаревшая() КонецФункции
#КонецУдаления
            ''',
            [
                (Token.Comment.Preproc, '#Вставка'),
                (Token.Keyword, 'Процедура'),
                (Token.Name.Function, 'ДобавитьКод'),
                (Token.Punctuation, '('),
                (Token.Punctuation, ')'),
                (Token.Keyword, 'КонецПроцедуры'),
                (Token.Comment.Preproc, '#КонецВставки'),
                (Token.Comment.Preproc, '#Удаление'),
                (Token.Keyword, 'Функция'),
                (Token.Name.Function, 'Устаревшая'),
                (Token.Punctuation, '('),
                (Token.Punctuation, ')'),
                (Token.Keyword, 'КонецФункции'),
                (Token.Comment.Preproc, '#КонецУдаления'),
            ],
        )

    def test_variable_declarations(self):
        cases = [
            (
                'Перем А Экспорт;',
                [
                    (Token.Keyword.Declaration, 'Перем'),
                    (Token.Name.Variable, 'А'),
                    (Token.Keyword, 'Экспорт'),
                    (Token.Punctuation, ';'),
                ],
            ),
            (
                'Перем А, Б;',
                [
                    (Token.Keyword.Declaration, 'Перем'),
                    (Token.Name.Variable, 'А'),
                    (Token.Punctuation, ','),
                    (Token.Name.Variable, 'Б'),
                    (Token.Punctuation, ';'),
                ],
            ),
            (
                'Перем А Экспорт, Б;',
                [
                    (Token.Keyword.Declaration, 'Перем'),
                    (Token.Name.Variable, 'А'),
                    (Token.Keyword, 'Экспорт'),
                    (Token.Punctuation, ','),
                    (Token.Name.Variable, 'Б'),
                    (Token.Punctuation, ';'),
                ],
            ),
            (
                'Перем А, Б Экспорт;',
                [
                    (Token.Keyword.Declaration, 'Перем'),
                    (Token.Name.Variable, 'А'),
                    (Token.Punctuation, ','),
                    (Token.Name.Variable, 'Б'),
                    (Token.Keyword, 'Экспорт'),
                    (Token.Punctuation, ';'),
                ],
            ),
            (
                'Перем А Экспорт, Б Экспорт;',
                [
                    (Token.Keyword.Declaration, 'Перем'),
                    (Token.Name.Variable, 'А'),
                    (Token.Keyword, 'Экспорт'),
                    (Token.Punctuation, ','),
                    (Token.Name.Variable, 'Б'),
                    (Token.Keyword, 'Экспорт'),
                    (Token.Punctuation, ';'),
                ],
            ),
        ]

        for source, expected in cases:
            with self.subTest(source=source):
                self.assertTokens(source, expected)

    def test_lexing_inline_comment(self):
        self.assertTokens(
            '''
            Перем ДиалогРаботыСКаталогом;     // Диалог работы с каталогом
            ''',
            [
                (Token.Keyword.Declaration, 'Перем'),
                (Token.Name.Variable, 'ДиалогРаботыСКаталогом'),
                (Token.Punctuation, ';'),
                (Token.Comment.Single, '// Диалог работы с каталогом'),
            ],
        )

    def test_comment_markers(self):
        self.assertTokens(
            '''
            // TODO: проверить границы
            // {{MRG[ <-> ]
            // }}MRG[ <-> ]
            ''',
            [
                (Token.Comment.Single, '// '),
                (Token.Keyword, 'TODO:'),
                (Token.Comment.Single, ' проверить границы'),
                (Token.Comment.Single, '// '),
                (Token.Punctuation, '{{'),
                (Token.Keyword, 'MRG'),
                (Token.Punctuation, '[ <-> ]'),
                (Token.Comment.Single, '// '),
                (Token.Punctuation, '}}'),
                (Token.Keyword, 'MRG'),
                (Token.Punctuation, '[ <-> ]'),
            ],
        )

    def test_lexing_preprocessor(self):
        self.assertTokens(
            '''
            #Если Сервер Тогда
            // это комментарий
            #КонецЕсли
            ''',
            [
                (Token.Comment.Preproc, '#Если'),
                (Token.Keyword.Constant, 'Сервер'),
                (Token.Comment.Preproc, 'Тогда'),
                (Token.Comment.Single, '// это комментарий'),
                (Token.Comment.Preproc, '#КонецЕсли'),
            ],
        )

    def test_lexing_doc_comments(self):
        self.assertTokens(
            '''
// Параметры:
//   Форма - ФормаКлиентскогоПриложения - форма, из которой вызвана процедура
//   Отказ - Булево - признак отказа
//      ДополнительнаяРегистрация - ТаблицаЗначений
//                                - Массив - строки или структуры, описывающие отбор.
//     НастройкиДополненияВыгрузки - см. ИнтерактивноеИзменениеВыгрузки
//     ИмяРеквизитаДополнения      - Строка - имя реквизита формы для создания или заполнения.
//     ДополнениеВыгрузки - Структура
//                        - ДанныеФормыКоллекция - описание параметров выгрузки:
//       * УзелИнформационнойБазы - ПланОбменаСсылка - узел плана обмена.
//     ДополнениеВыгрузки - Структура
//                        - ДанныеФормыСтруктура - описание параметров выгрузки:
//       * КомпоновщикОтбораВсехДокументов - КомпоновщикНастроекКомпоновкиДанных
//       * АдресКомпоновщикаВсехДокументов - Строка
//       * АдресХранилищаФормы - Строка
// Возвращаемое значение:
//   Булево - описание
//     Массив из Число - с номерами используемых вариантов:
//               0 - без отбора, 1 - отбор всех документов, 2 - подробный, 3 - сценарий узла.
// Пример:
//   * Первый пункт
//   ** Вложенный пункт
            ''',
            [
                (Token.Comment.Single, '// '),
                (Token.Keyword, 'Параметры'),
                (Token.Punctuation, ':'),
                (Token.Comment.Single, '//   '),
                (Token.Name.Variable, 'Форма'),
                (Token.Punctuation, ' - '),
                (Token.Name.Class, 'ФормаКлиентскогоПриложения'),
                (Token.Punctuation, ' - '),
                (Token.Comment.Single, 'форма, из которой вызвана процедура'),
                (Token.Comment.Single, '//   '),
                (Token.Name.Variable, 'Отказ'),
                (Token.Punctuation, ' - '),
                (Token.Name.Class, 'Булево'),
                (Token.Punctuation, ' - '),
                (Token.Comment.Single, 'признак отказа'),
                (Token.Comment.Single, '//      '),
                (Token.Name.Variable, 'ДополнительнаяРегистрация'),
                (Token.Punctuation, ' - '),
                (Token.Name.Class, 'ТаблицаЗначений'),
                (Token.Comment.Single, '//                                '),
                (Token.Punctuation, '- '),
                (Token.Name.Class, 'Массив'),
                (Token.Punctuation, ' - '),
                (Token.Comment.Single, 'строки или структуры, описывающие отбор.'),
                (Token.Comment.Single, '//     '),
                (Token.Name.Variable, 'НастройкиДополненияВыгрузки'),
                (Token.Punctuation, ' - '),
                (Token.Keyword, 'см.'),
                (Token.Comment.Single, ' '),
                (Token.Name.Class, 'ИнтерактивноеИзменениеВыгрузки'),
                (Token.Comment.Single, '//     '),
                (Token.Name.Variable, 'ИмяРеквизитаДополнения'),
                (Token.Punctuation, '      - '),
                (Token.Name.Class, 'Строка'),
                (Token.Punctuation, ' - '),
                (Token.Comment.Single, 'имя реквизита формы для создания или заполнения.'),
                (Token.Comment.Single, '//     '),
                (Token.Name.Variable, 'ДополнениеВыгрузки'),
                (Token.Punctuation, ' - '),
                (Token.Name.Class, 'Структура'),
                (Token.Comment.Single, '//                        '),
                (Token.Punctuation, '- '),
                (Token.Name.Class, 'ДанныеФормыКоллекция'),
                (Token.Punctuation, ' - '),
                (Token.Comment.Single, 'описание параметров выгрузки:'),
                (Token.Comment.Single, '//       '),
                (Token.Punctuation, '* '),
                (Token.Name.Variable, 'УзелИнформационнойБазы'),
                (Token.Punctuation, ' - '),
                (Token.Name.Class, 'ПланОбменаСсылка'),
                (Token.Punctuation, ' - '),
                (Token.Comment.Single, 'узел плана обмена.'),
                (Token.Comment.Single, '//     '),
                (Token.Name.Variable, 'ДополнениеВыгрузки'),
                (Token.Punctuation, ' - '),
                (Token.Name.Class, 'Структура'),
                (Token.Comment.Single, '//                        '),
                (Token.Punctuation, '- '),
                (Token.Name.Class, 'ДанныеФормыСтруктура'),
                (Token.Punctuation, ' - '),
                (Token.Comment.Single, 'описание параметров выгрузки:'),
                (Token.Comment.Single, '//       '),
                (Token.Punctuation, '* '),
                (Token.Name.Variable, 'КомпоновщикОтбораВсехДокументов'),
                (Token.Punctuation, ' - '),
                (Token.Name.Class, 'КомпоновщикНастроекКомпоновкиДанных'),
                (Token.Comment.Single, '//       '),
                (Token.Punctuation, '* '),
                (Token.Name.Variable, 'АдресКомпоновщикаВсехДокументов'),
                (Token.Punctuation, ' - '),
                (Token.Name.Class, 'Строка'),
                (Token.Comment.Single, '//       '),
                (Token.Punctuation, '* '),
                (Token.Name.Variable, 'АдресХранилищаФормы'),
                (Token.Punctuation, ' - '),
                (Token.Name.Class, 'Строка'),
                (Token.Comment.Single, '// '),
                (Token.Keyword, 'Возвращаемое значение'),
                (Token.Punctuation, ':'),
                (Token.Comment.Single, '//   '),
                (Token.Name.Class, 'Булево'),
                (Token.Punctuation, ' - '),
                (Token.Comment.Single, 'описание'),
                (Token.Comment.Single, '//     '),
                (Token.Name.Class, 'Массив'),
                (Token.Punctuation, ' '),
                (Token.Keyword, 'из'),
                (Token.Punctuation, ' '),
                (Token.Name.Class, 'Число'),
                (Token.Punctuation, ' - '),
                (Token.Comment.Single, 'с номерами используемых вариантов:'),
                (Token.Comment.Single, '//               0 - без отбора, 1 - отбор всех документов, 2 - подробный, 3 - сценарий узла.'),
                (Token.Comment.Single, '// '),
                (Token.Keyword, 'Пример'),
                (Token.Punctuation, ':'),
                (Token.Comment.Single, '//   '),
                (Token.Punctuation, '*'),
                (Token.Comment.Single, ' '),
                (Token.Comment.Single, 'Первый пункт'),
                (Token.Comment.Single, '//   '),
                (Token.Punctuation, '**'),
                (Token.Comment.Single, ' '),
                (Token.Comment.Single, 'Вложенный пункт'),
            ],
        )

    def test_doc_comment_structure_type(self):
        self.assertTokens(
            '''
// Возвращаемое значение:
//  Структура:
//     * Дата - Дата
            ''',
            [
                (Token.Comment.Single, '// '),
                (Token.Keyword, 'Возвращаемое значение'),
                (Token.Punctuation, ':'),
                (Token.Comment.Single, '//  '),
                (Token.Name.Class, 'Структура'),
                (Token.Punctuation, ':'),
                (Token.Comment.Single, '//     '),
                (Token.Punctuation, '* '),
                (Token.Name.Variable, 'Дата'),
                (Token.Punctuation, ' - '),
                (Token.Name.Class, 'Дата'),
            ],
        )

    def test_doc_comment_return_fixed_structure_type(self):
        self.assertTokens(
            '''
// Возвращаемое значение:
//   ФиксированнаяСтруктура:
//     * Отправитель
            ''',
            [
                (Token.Comment.Single, '// '),
                (Token.Keyword, 'Возвращаемое значение'),
                (Token.Punctuation, ':'),
                (Token.Comment.Single, '//   '),
                (Token.Name.Class, 'ФиксированнаяСтруктура'),
                (Token.Punctuation, ':'),
                (Token.Comment.Single, '//     '),
                (Token.Punctuation, '*'),
                (Token.Comment.Single, ' '),
                (Token.Comment.Single, 'Отправитель'),
            ],
        )

    def test_doc_comment_structure_bullet_type(self):
        self.assertTokens(
            '''
// Параметры:
//  СведенияОбОбновлении - Структура:
//     * КодАдресногоОбъекта - Структура:
            ''',
            [
                (Token.Comment.Single, '// '),
                (Token.Keyword, 'Параметры'),
                (Token.Punctuation, ':'),
                (Token.Comment.Single, '//  '),
                (Token.Name.Variable, 'СведенияОбОбновлении'),
                (Token.Punctuation, ' - '),
                (Token.Name.Class, 'Структура'),
                (Token.Punctuation, ':'),
                (Token.Comment.Single, '//     '),
                (Token.Punctuation, '* '),
                (Token.Name.Variable, 'КодАдресногоОбъекта'),
                (Token.Punctuation, ' - '),
                (Token.Name.Class, 'Структура'),
                (Token.Punctuation, ':'),
            ],
        )

    def test_lexing_doc_comment_sections_and_links(self):
        self.assertTokens(
            '''
// Parameters:
// Returns:
//     Массив из Число
// Example:
// Call options:
// Устарела.
// Deprecate:
// СМ. ОбщийМодуль.Метод()
// SEE CommonModule.Method(Парам1, Значение)
            ''',
            [
                (Token.Comment.Single, '// '),
                (Token.Keyword, 'Parameters'),
                (Token.Punctuation, ':'),
                (Token.Comment.Single, '// '),
                (Token.Keyword, 'Returns'),
                (Token.Punctuation, ':'),
                (Token.Comment.Single, '//     '),
                (Token.Name.Class, 'Массив'),
                (Token.Punctuation, ' '),
                (Token.Keyword, 'из'),
                (Token.Punctuation, ' '),
                (Token.Name.Class, 'Число'),
                (Token.Comment.Single, '// '),
                (Token.Keyword, 'Example'),
                (Token.Punctuation, ':'),
                (Token.Comment.Single, '// '),
                (Token.Keyword, 'Call options'),
                (Token.Punctuation, ':'),
                (Token.Comment.Single, '// '),
                (Token.Keyword, 'Устарела'),
                (Token.Punctuation, '.'),
                (Token.Comment.Single, '// '),
                (Token.Keyword, 'Deprecate'),
                (Token.Punctuation, ':'),
                (Token.Comment.Single, '// '),
                (Token.Keyword, 'СМ.'),
                (Token.Comment.Single, ' '),
                (Token.Name.Namespace, 'ОбщийМодуль.Метод'),
                (Token.Punctuation, '('),
                (Token.Punctuation, ')'),
                (Token.Comment.Single, '// '),
                (Token.Keyword, 'SEE'),
                (Token.Comment.Single, ' '),
                (Token.Name.Namespace, 'CommonModule.Method'),
                (Token.Punctuation, '('),
                (Token.Comment.Single, 'Парам1, Значение'),
                (Token.Punctuation, ')'),
            ],
        )

    def test_lexing_doc_comment_deprecate_with_description(self):
        self.assertTokens(
            '''
// Устарела. Описание что делать
// 
            ''',
            [
                (Token.Comment.Single, '// '),
                (Token.Keyword, 'Устарела'),
                (Token.Punctuation, '.'),
                (Token.Comment.Single, ' Описание что делать'),
                (Token.Comment.Single, '// '),
            ],
        )

    def test_lexing_doc_comment_bullets_unbounded(self):
        self.assertTokens(
            '''
// Возвращаемое значение:
//   Структура - настройки типового варианта:
//     * Использование - Булево - признак разрешения использования варианта.
//     ** Порядок - Число - порядок размещения варианта.
//     *** Заголовок - Строка - позволяет переопределить название.
//     **** Пояснение - Строка - позволяет переопределить текст.
//     ***** Отбор - см. ОписаниеДополнительнойРегистрацииВариантаВыгрузки
            ''',
            [
                (Token.Comment.Single, '// '),
                (Token.Keyword, 'Возвращаемое значение'),
                (Token.Punctuation, ':'),
                (Token.Comment.Single, '//   '),
                (Token.Name.Class, 'Структура'),
                (Token.Punctuation, ' - '),
                (Token.Comment.Single, 'настройки типового варианта:'),
                (Token.Comment.Single, '//     '),
                (Token.Punctuation, '* '),
                (Token.Name.Variable, 'Использование'),
                (Token.Punctuation, ' - '),
                (Token.Name.Class, 'Булево'),
                (Token.Punctuation, ' - '),
                (Token.Comment.Single, 'признак разрешения использования варианта.'),
                (Token.Comment.Single, '//     '),
                (Token.Punctuation, '** '),
                (Token.Name.Variable, 'Порядок'),
                (Token.Punctuation, ' - '),
                (Token.Name.Class, 'Число'),
                (Token.Punctuation, ' - '),
                (Token.Comment.Single, 'порядок размещения варианта.'),
                (Token.Comment.Single, '//     '),
                (Token.Punctuation, '*** '),
                (Token.Name.Variable, 'Заголовок'),
                (Token.Punctuation, ' - '),
                (Token.Name.Class, 'Строка'),
                (Token.Punctuation, ' - '),
                (Token.Comment.Single, 'позволяет переопределить название.'),
                (Token.Comment.Single, '//     '),
                (Token.Punctuation, '**** '),
                (Token.Name.Variable, 'Пояснение'),
                (Token.Punctuation, ' - '),
                (Token.Name.Class, 'Строка'),
                (Token.Punctuation, ' - '),
                (Token.Comment.Single, 'позволяет переопределить текст.'),
                (Token.Comment.Single, '//     '),
                (Token.Punctuation, '***** '),
                (Token.Name.Variable, 'Отбор'),
                (Token.Punctuation, ' - '),
                (Token.Keyword, 'см.'),
                (Token.Comment.Single, ' '),
                (Token.Name.Class, 'ОписаниеДополнительнойРегистрацииВариантаВыгрузки'),
            ],
        )

    def test_lexing_doc_comment_param_array_type(self):
        self.assertTokens(
            '''
// Параметры:
//   ЗапросыРазрешений - Массив из УникальныйИдентификатор - коллекция запросов разрешений.
//   Объект - КонстантаМенеджерЗначения - менеджер значения объекта данных.
            ''',
            [
                (Token.Comment.Single, '// '),
                (Token.Keyword, 'Параметры'),
                (Token.Punctuation, ':'),
                (Token.Comment.Single, '//   '),
                (Token.Name.Variable, 'ЗапросыРазрешений'),
                (Token.Punctuation, ' - '),
                (Token.Name.Class, 'Массив'),
                (Token.Punctuation, ' '),
                (Token.Keyword, 'из'),
                (Token.Punctuation, ' '),
                (Token.Name.Class, 'УникальныйИдентификатор'),
                (Token.Punctuation, ' - '),
                (Token.Comment.Single, 'коллекция запросов разрешений.'),
                (Token.Comment.Single, '//   '),
                (Token.Name.Variable, 'Объект'),
                (Token.Punctuation, ' - '),
                (Token.Name.Class, 'КонстантаМенеджерЗначения'),
                (Token.Punctuation, ' - '),
                (Token.Comment.Single, 'менеджер значения объекта данных.'),
            ],
        )

    def test_lexing_doc_comment_param_array_type_multiline(self):
        self.assertTokens(
            '''
//      * Свойство - Массив из
//  ПеречислениеСсылка.Переч1 - Описание
            ''',
            [
                (Token.Comment.Single, '//      '),
                (Token.Punctuation, '* '),
                (Token.Name.Variable, 'Свойство'),
                (Token.Punctuation, ' - '),
                (Token.Name.Class, 'Массив'),
                (Token.Punctuation, ' '),
                (Token.Keyword, 'из'),
                (Token.Comment.Single, '//  '),
                (Token.Name.Class, 'ПеречислениеСсылка.Переч1'),
                (Token.Punctuation, ' - '),
                (Token.Comment.Single, 'Описание'),
            ],
        )

    def test_lexing_doc_comment_bullet_mapping_type(self):
        self.assertTokens(
            '''
//      * Свойство - Соответствие из КлючИЗначение:
            ''',
            [
                (Token.Comment.Single, '//      '),
                (Token.Punctuation, '* '),
                (Token.Name.Variable, 'Свойство'),
                (Token.Punctuation, ' - '),
                (Token.Name.Class, 'Соответствие'),
                (Token.Keyword, 'из'),
                (Token.Name.Class, 'КлючИЗначение'),
                (Token.Punctuation, ':'),
            ],
        )

    def test_lexing_doc_comment_hyphen_without_spaces_is_plain(self):
        self.assertTokens(
            '''
// Процедура-обработчик команды "Рассчитать"
// Обычная строка
            ''',
            [
                (Token.Comment.Single, '// Процедура-обработчик команды "Рассчитать"'),
                (Token.Comment.Single, '// Обычная строка'),
            ],
        )

    def test_lexing_doc_comment_param_type_with_dots(self):
        self.assertTokens(
            '''
// Параметры:
//  Адреса - Строка - строка, содержащая электронные адреса
//  ЗадачаИсполнителя - ЗадачаСсылка.ЗадачаИсполнителя – проверяемая задача
//  ЗадачаИсполнителя - ЗадачаСсылка.ЗадачаИсполнителя
            ''',
            [
                (Token.Comment.Single, '// '),
                (Token.Keyword, 'Параметры'),
                (Token.Punctuation, ':'),
                (Token.Comment.Single, '//  '),
                (Token.Name.Variable, 'Адреса'),
                (Token.Punctuation, ' - '),
                (Token.Name.Class, 'Строка'),
                (Token.Punctuation, ' - '),
                (Token.Comment.Single, 'строка, содержащая электронные адреса'),
                (Token.Comment.Single, '//  '),
                (Token.Name.Variable, 'ЗадачаИсполнителя'),
                (Token.Punctuation, ' - '),
                (Token.Name.Class, 'ЗадачаСсылка.ЗадачаИсполнителя'),
                (Token.Punctuation, ' – '),
                (Token.Comment.Single, 'проверяемая задача'),
                (Token.Comment.Single, '//  '),
                (Token.Name.Variable, 'ЗадачаИсполнителя'),
                (Token.Punctuation, ' - '),
                (Token.Name.Class, 'ЗадачаСсылка.ЗадачаИсполнителя'),
            ],
        )

    def test_lexing_doc_comment_param_type_with_dots_no_desc(self):
        self.assertTokens(
            '''
//  ЗадачаИсполнителя - ЗадачаСсылка.ЗадачаИсполнителя
            ''',
            [
                (Token.Comment.Single, '//  '),
                (Token.Name.Variable, 'ЗадачаИсполнителя'),
                (Token.Punctuation, ' - '),
                (Token.Name.Class, 'ЗадачаСсылка.ЗадачаИсполнителя'),
            ],
        )

    def test_lexing_doc_comment_param_type_list(self):
        self.assertTokens(
            '''
// КоллекцияСтрок – ТаблицаЗначений, Массив, СписокЗначений – коллекция для сравнения.
// ФормируемыйОтчет – ОбъектМетаданныхОтчет
// ПрисоединенныйФайлОбъект - ОпределяемыйТип.ПрисоединенныйФайлОбъект - элемент справочника файлов.
            ''',
            [
                (Token.Comment.Single, '// '),
                (Token.Name.Variable, 'КоллекцияСтрок'),
                (Token.Punctuation, ' – '),
                (Token.Name.Class, 'ТаблицаЗначений'),
                (Token.Punctuation, ', '),
                (Token.Name.Class, 'Массив'),
                (Token.Punctuation, ', '),
                (Token.Name.Class, 'СписокЗначений'),
                (Token.Punctuation, ' – '),
                (Token.Comment.Single, 'коллекция для сравнения.'),
                (Token.Comment.Single, '// '),
                (Token.Name.Variable, 'ФормируемыйОтчет'),
                (Token.Punctuation, ' – '),
                (Token.Name.Class, 'ОбъектМетаданныхОтчет'),
                (Token.Comment.Single, '// '),
                (Token.Name.Variable, 'ПрисоединенныйФайлОбъект'),
                (Token.Punctuation, ' - '),
                (Token.Name.Class, 'ОпределяемыйТип.ПрисоединенныйФайлОбъект'),
                (Token.Punctuation, ' - '),
                (Token.Comment.Single, 'элемент справочника файлов.'),
            ],
        )

    def test_lexing_doc_comment_param_type_with_colon_see(self):
        self.assertTokens(
            '''
// СведенияОРегионе – СтрокаТаблицыЗначений: см. РегистрыСведений.АдресныеОбъекты.КлассификаторСубъектовРФ
            ''',
            [
                (Token.Comment.Single, '// '),
                (Token.Name.Variable, 'СведенияОРегионе'),
                (Token.Punctuation, ' – '),
                (Token.Name.Class, 'СтрокаТаблицыЗначений'),
                (Token.Punctuation, ': '),
                (Token.Keyword, 'см.'),
                (Token.Comment.Single, ' '),
                (Token.Name.Class, 'РегистрыСведений.АдресныеОбъекты.КлассификаторСубъектовРФ'),
            ],
        )

    def test_lexing_doc_comment_param_type_and_desc_colon(self):
        self.assertTokens(
            '''
// КоллекцияСтрок - КоллекцияЗначений – коллекция для сравнения;
// ФормируемыйОтчет - ОбъектМетаданных: Отчет
// ПрисоединенныйФайлОбъект - элемент справочника файлов.
            ''',
            [
                (Token.Comment.Single, '// '),
                (Token.Name.Variable, 'КоллекцияСтрок'),
                (Token.Punctuation, ' - '),
                (Token.Name.Class, 'КоллекцияЗначений'),
                (Token.Punctuation, ' – '),
                (Token.Comment.Single, 'коллекция для сравнения;'),
                (Token.Comment.Single, '// '),
                (Token.Name.Variable, 'ФормируемыйОтчет'),
                (Token.Punctuation, ' - '),
                (Token.Name.Class, 'ОбъектМетаданных'),
                (Token.Punctuation, ': '),
                (Token.Comment.Single, 'Отчет'),
                (Token.Comment.Single, '// '),
                (Token.Name.Variable, 'ПрисоединенныйФайлОбъект'),
                (Token.Punctuation, ' - '),
                (Token.Comment.Single, 'элемент справочника файлов.'),
            ],
        )

    def test_lexing_doc_comment_sm_and_iz_consistency(self):
        self.assertTokens(
            '''
//  КонтактнаяИнформация - см. Документ.ЗаказПокупателя
// РеквизитыКомпонент - Массив из см. ВнешниеКомпоненты.РеквизитыКомпоненты
// - Массив Из Строка, ФиксированныйМассив Из Строка - имена реквизитов.
            ''',
            [
                (Token.Comment.Single, '//  '),
                (Token.Name.Variable, 'КонтактнаяИнформация'),
                (Token.Punctuation, ' - '),
                (Token.Keyword, 'см.'),
                (Token.Comment.Single, ' '),
                (Token.Name.Class, 'Документ.ЗаказПокупателя'),
                (Token.Comment.Single, '// '),
                (Token.Name.Variable, 'РеквизитыКомпонент'),
                (Token.Punctuation, ' - '),
                (Token.Name.Class, 'Массив'),
                (Token.Punctuation, ' '),
                (Token.Keyword, 'из'),
                (Token.Punctuation, ' '),
                (Token.Keyword, 'см.'),
                (Token.Comment.Single, ' '),
                (Token.Name.Class, 'ВнешниеКомпоненты.РеквизитыКомпоненты'),
                (Token.Comment.Single, '// '),
                (Token.Punctuation, '- '),
                (Token.Name.Class, 'Массив'),
                (Token.Punctuation, ' '),
                (Token.Keyword, 'Из'),
                (Token.Punctuation, ' '),
                (Token.Name.Class, 'Строка'),
                (Token.Punctuation, ', '),
                (Token.Name.Class, 'ФиксированныйМассив'),
                (Token.Punctuation, ' '),
                (Token.Keyword, 'Из'),
                (Token.Punctuation, ' '),
                (Token.Name.Class, 'Строка'),
                (Token.Punctuation, ' - '),
                (Token.Comment.Single, 'имена реквизитов.'),
            ],
        )

    def test_lexing_comments_around_procedure(self):
        self.assertTokens(
            '''
//  комментарий до
Процедура ИмяПроцедуры(
// комментарий после
            ''',
            [
                (Token.Comment.Single, '//  комментарий до'),
                (Token.Keyword, 'Процедура'),
                (Token.Name.Function, 'ИмяПроцедуры'),
                (Token.Punctuation, '('),
                (Token.Comment.Single, '// комментарий после'),
            ],
        )

    def test_lexing_doc_comment_param_multiline_types(self):
        self.assertTokens(
            '''
// Параметры:
//   Реквизиты - Строка - имена реквизитов, перечисленные через запятую.
//                        Например, "Код, Наименование, Родитель".
//             - Структура, ФиксированнаяСтруктура - в качестве ключа передается
//                        псевдоним поля для возвращаемой структуры с результатом,
//                        а в качестве значения (опционально) фактическое имя поля в таблице.
//                        Если значение не определено, то имя поля берется из ключа.
//             - Массив Из Строка, ФиксированныйМассив Из Строка - имена реквизитов.
            ''',
            [
                (Token.Comment.Single, '// '),
                (Token.Keyword, 'Параметры'),
                (Token.Punctuation, ':'),
                (Token.Comment.Single, '//   '),
                (Token.Name.Variable, 'Реквизиты'),
                (Token.Punctuation, ' - '),
                (Token.Name.Class, 'Строка'),
                (Token.Punctuation, ' - '),
                (Token.Comment.Single, 'имена реквизитов, перечисленные через запятую.'),
                (Token.Comment.Single, '//                        Например, "Код, Наименование, Родитель".'),
                (Token.Comment.Single, '//             '),
                (Token.Punctuation, '- '),
                (Token.Name.Class, 'Структура'),
                (Token.Punctuation, ', '),
                (Token.Name.Class, 'ФиксированнаяСтруктура'),
                (Token.Punctuation, ' - '),
                (Token.Comment.Single, 'в качестве ключа передается'),
                (Token.Comment.Single, '//                        псевдоним поля для возвращаемой структуры с результатом,'),
                (Token.Comment.Single, '//                        а в качестве значения (опционально) фактическое имя поля в таблице.'),
                (Token.Comment.Single, '//                        Если значение не определено, то имя поля берется из ключа.'),
                (Token.Comment.Single, '//             '),
                (Token.Punctuation, '- '),
                (Token.Name.Class, 'Массив'),
                (Token.Punctuation, ' '),
                (Token.Keyword, 'Из'),
                (Token.Punctuation, ' '),
                (Token.Name.Class, 'Строка'),
                (Token.Punctuation, ', '),
                (Token.Name.Class, 'ФиксированныйМассив'),
                (Token.Punctuation, ' '),
                (Token.Keyword, 'Из'),
                (Token.Punctuation, ' '),
                (Token.Name.Class, 'Строка'),
                (Token.Punctuation, ' - '),
                (Token.Comment.Single, 'имена реквизитов.'),
            ],
        )

    def test_lexing_doc_comment_return_type_list(self):
        self.assertTokens(
            '''
// Возвращаемое значение:
//  - СправочникСсылка.Пользователи
//  - СправочникСсылка.ВнешниеПользователи
            ''',
            [
                (Token.Comment.Single, '// '),
                (Token.Keyword, 'Возвращаемое значение'),
                (Token.Punctuation, ':'),
                (Token.Comment.Single, '//  '),
                (Token.Punctuation, '- '),
                (Token.Name.Class, 'СправочникСсылка.Пользователи'),
                (Token.Comment.Single, '//  '),
                (Token.Punctuation, '- '),
                (Token.Name.Class, 'СправочникСсылка.ВнешниеПользователи'),
            ],
        )

    def test_lexing_bom(self):
        self.assertTokens(
            '\ufeffПроцедура Тест()',
            [
                (Token.Keyword, 'Процедура'),
                (Token.Name.Function, 'Тест'),
                (Token.Punctuation, '('),
                (Token.Punctuation, ')'),
            ],
        )

    def test_lexing_ternary_operator(self):
        self.assertTokens(
            'Результат = ?(Условие, ЕслиИстина, ЕслиЛожь);',
            [
                (Token.Name.Variable, 'Результат'),
                (Token.Operator, '='),
                (Token.Operator, '?'),
                (Token.Punctuation, '('),
                (Token.Name.Variable, 'Условие'),
                (Token.Punctuation, ','),
                (Token.Name.Variable, 'ЕслиИстина'),
                (Token.Punctuation, ','),
                (Token.Name.Variable, 'ЕслиЛожь'),
                (Token.Punctuation, ')'),
                (Token.Punctuation, ';'),
            ],
        )

    def test_lexing_remove_handler(self):
        self.assertTokens(
            'УдалитьОбработчик Накладная.ПриЗаписи, Обработка.ПриЗаписиДокумента;',
            [
                (Token.Name.Builtin, 'УдалитьОбработчик'),
                (Token.Name.Variable, 'Накладная'),
                (Token.Operator, '.'),
                (Token.Name.Variable, 'ПриЗаписи'),
                (Token.Punctuation, ','),
                (Token.Name.Variable, 'Обработка'),
                (Token.Operator, '.'),
                (Token.Name.Variable, 'ПриЗаписиДокумента'),
                (Token.Punctuation, ';'),
            ],
        )

    def test_lexing_add_handler_with_metadata(self):
        self.assertTokens(
            '''
Обработка = Обработки.КонтрольДокумента.Создать();
Накладная = Документы.Накладная.СоздатьДокумент();
ДобавитьОбработчик Накладная.ПриЗаписи, Обработка.ПриЗаписиДокумента;
            ''',
            [
                (Token.Name.Variable, 'Обработка'),
                (Token.Operator, '='),
                (Token.Name.Namespace, 'Обработки'),
                (Token.Operator, '.'),
                (Token.Name.Class, 'КонтрольДокумента'),
                (Token.Operator, '.'),
                (Token.Name.Function, 'Создать'),
                (Token.Punctuation, '('),
                (Token.Punctuation, ')'),
                (Token.Punctuation, ';'),
                (Token.Name.Variable, 'Накладная'),
                (Token.Operator, '='),
                (Token.Name.Namespace, 'Документы'),
                (Token.Operator, '.'),
                (Token.Name.Class, 'Накладная'),
                (Token.Operator, '.'),
                (Token.Name.Function, 'СоздатьДокумент'),
                (Token.Punctuation, '('),
                (Token.Punctuation, ')'),
                (Token.Punctuation, ';'),
                (Token.Name.Builtin, 'ДобавитьОбработчик'),
                (Token.Name.Variable, 'Накладная'),
                (Token.Operator, '.'),
                (Token.Name.Variable, 'ПриЗаписи'),
                (Token.Punctuation, ','),
                (Token.Name.Variable, 'Обработка'),
                (Token.Operator, '.'),
                (Token.Name.Variable, 'ПриЗаписиДокумента'),
                (Token.Punctuation, ';'),
            ],
        )

    def test_lexing_preproc_use(self):
        cases = [
            ('#Использовать lib', [(Token.Comment.Preproc, '#Использовать'), (Token.Name.Variable, 'lib')]),
            ('#Использовать "lib"', [(Token.Comment.Preproc, '#Использовать'), (Token.Literal.String, '"lib"')]),
            ('#Использовать lib-name', [(Token.Comment.Preproc, '#Использовать'), (Token.Name.Variable, 'lib-name')]),
            ('#Использовать 1lib', [(Token.Comment.Preproc, '#Использовать'), (Token.Name.Variable, '1lib')]),
        ]

        for source, expected in cases:
            with self.subTest(source=source):
                self.assertTokens(source, expected)

    def test_preproc_region_comment(self):
        self.assertTokens(
            '#КонецОбласти // Концевой комментарий',
            [
                (Token.Comment.Preproc, '#КонецОбласти // Концевой комментарий'),
            ],
        )

    def test_string_tail_and_escapes(self):
        lexer = lexers.get_lexer_by_name('bsl')
        tokens = lexer.get_tokens('''
        А = " \n | А """" + А \n  |";
        ''')

        self.assertEqual(
            filter_tokens(tokens),
            [
                (Token.Name.Variable, 'А'),
                (Token.Operator, '='),
                (Token.String, '"'),
                (Token.String, ' '),
                (Token.Literal.String, '|'),
                (Token.Literal.String, ' А '),
                (Token.String.Escape, '""'),
                (Token.String.Escape, '""'),
                (Token.String, ' + А '),
                (Token.Literal.String, '|'),
                (Token.String, '"'),
                (Token.Punctuation, ';'),
            ],
        )

    def test_lexing_keywords_after_dot(self):
        lexer = lexers.get_lexer_by_name('bsl')
        tokens = lexer.get_tokens('Поле.Процедура; Поле.Функция;')

        self.assertEqual(
            filter_tokens(tokens),
            [
                (Token.Name.Variable, 'Поле'),
                (Token.Operator, '.'),
                (Token.Name.Variable, 'Процедура'),
                (Token.Punctuation, ';'),
                (Token.Name.Variable, 'Поле'),
                (Token.Operator, '.'),
                (Token.Name.Variable, 'Функция'),
                (Token.Punctuation, ';'),
            ],
        )

    def test_lexing_label_keywords(self):
        lexer = lexers.get_lexer_by_name('bsl')
        tokens = lexer.get_tokens('~Если: ~КонецЕсли;')

        self.assertEqual(
            filter_tokens(tokens),
            [
                (Token.Name.Label, '~Если'),
                (Token.Punctuation, ':'),
                (Token.Name.Label, '~КонецЕсли'),
                (Token.Punctuation, ';'),
            ],
        )
    
    def test_lexing_annotation(self):
        lexer = lexers.get_lexer_by_name('bsl')
        tokens = lexer.get_tokens(
            '''
            &НаСервере;
            '''
        )

        self.assertEqual(
            filter_tokens(tokens),
            [
                (Token.Name.Decorator, '&НаСервере;'),
            ],
        )

    def test_decorator_split_name_inside(self):
        lexer = lexers.get_lexer_by_name('bsl')
        tokens = lexer.get_tokens('&Перед("НазваниеМетода");')

        self.assertEqual(
            filter_tokens(tokens),
            [
                (Token.Name.Decorator, '&Перед'),
                (Token.Punctuation, '('),
                (Token.String.Single, '"'),
                (Token.Name.Function, 'НазваниеМетода'),
                (Token.String.Single, '"'),
                (Token.Punctuation, ')'),
                (Token.Punctuation, ';'),
            ],
        )

    def test_decorator_with_params_any(self):
        lexer = lexers.get_lexer_by_name('bsl')
        tokens = lexer.get_tokens(
            '''
            &НаЧемУгодно(ДажеСПараметром = "Да", СПараметромБезЗначения, "Значение без параметра")
            '''
        )

        self.assertEqual(
            filter_tokens(tokens),
            [
                (Token.Name.Decorator, '&НаЧемУгодно'),
                (Token.Punctuation, '('),
                (Token.Name.Variable, 'ДажеСПараметром'),
                (Token.Operator, '='),
                (Token.Literal.String, '"Да"'),
                (Token.Operator, ','),
                (Token.Name.Variable, 'СПараметромБезЗначения'),
                (Token.Operator, ','),
                (Token.Literal.String, '"Значение без параметра"'),
                (Token.Punctuation, ')'),
            ],
        )

    def test_params_with_annotations(self):
        lexer = lexers.get_lexer_by_name('bsl')
        tokens = lexer.get_tokens(
            '''
Процедура САннотированнымиПараметрами(

        &АннотацияДляПараметра
        Знач Парам1,
    &АннотацияДляПараметра
    &АннотацияДляПараметра1
    &АннотацияДляПараметра2(СПараметрами = 3, 4, 5)
    Знач Парам2,
    Парам3,
    Парам4 = Неопределено
) Экспорт
            '''
        )

        self.assertEqual(
            filter_tokens(tokens),
            [
                (Token.Keyword, 'Процедура'),
                (Token.Name.Function, 'САннотированнымиПараметрами'),
                (Token.Punctuation, '('),
                (Token.Name.Decorator, '&АннотацияДляПараметра'),
                (Token.Keyword, 'Знач'),
                (Token.Name.Variable, 'Парам1'),
                (Token.Punctuation, ','),
                (Token.Name.Decorator, '&АннотацияДляПараметра'),
                (Token.Name.Decorator, '&АннотацияДляПараметра1'),
                (Token.Name.Decorator, '&АннотацияДляПараметра2'),
                (Token.Punctuation, '('),
                (Token.Name.Variable, 'СПараметрами'),
                (Token.Operator, '='),
                (Token.Literal.Number, '3'),
                (Token.Operator, ','),
                (Token.Literal.Number, '4'),
                (Token.Operator, ','),
                (Token.Literal.Number, '5'),
                (Token.Punctuation, ')'),
                (Token.Keyword, 'Знач'),
                (Token.Name.Variable, 'Парам2'),
                (Token.Punctuation, ','),
                (Token.Name.Variable, 'Парам3'),
                (Token.Punctuation, ','),
                (Token.Name.Variable, 'Парам4'),
                (Token.Operator, '='),
                (Token.Keyword.Constant, 'Неопределено'),
                (Token.Punctuation, ')'),
                (Token.Keyword, 'Экспорт'),
            ],
        )

    def test_lexing_procedure_declaration(self):
        lexer = lexers.get_lexer_by_name('bsl')
        tokens = lexer.get_tokens(
            '''
            Процедура НевстроеннаяПроцедура()
                Возврат;
            КонецПроцедуры
            '''
        )

        self.assertEqual(
            filter_tokens(tokens),
            [
                (Token.Keyword, 'Процедура'),
                (Token.Name.Function, 'НевстроеннаяПроцедура'),
                (Token.Punctuation, '('),
                (Token.Punctuation, ')'),
                (Token.Keyword, 'Возврат'),
                (Token.Punctuation, ';'),
                (Token.Keyword, 'КонецПроцедуры'),
            ],
        )

    def test_lexing_procedure_declaration_with_annotation(self):
        lexer = lexers.get_lexer_by_name('bsl')
        tokens = lexer.get_tokens(
            '''
            &Перед("ПередЗаписью")
            Процедура Расш1_ПередЗаписью()

            КонецПроцедуры
            '''
        )

        self.assertEqual(
            filter_tokens(tokens),
            [
                (Token.Name.Decorator, '&Перед'),
                (Token.Punctuation, '('),
                (Token.String.Single, '"'),
                (Token.Name.Function, 'ПередЗаписью'),
                (Token.String.Single, '"'),
                (Token.Punctuation, ')'),
                (Token.Keyword, 'Процедура'),
                (Token.Name.Function, 'Расш1_ПередЗаписью'),
                (Token.Punctuation, '('),
                (Token.Punctuation, ')'),
                (Token.Keyword, 'КонецПроцедуры'),
            ],
        )

    def test_method_description_example8_excerpt(self):
        source = '''
// Параметры:
//   Входной - Структура - настройки (дополнительные свойства) отчета, хранящиеся в данных формы:
Процедура ПриСозданииНаСервере(Форма, Отказ, СтандартнаяОбработка) Экспорт
    // Обработка события.
КонецПроцедуры
        '''

        filtered = self.lex_filtered(source)

        expected_prefix = [
            (Token.Comment.Single, '// '),
            (Token.Keyword, 'Параметры'),
            (Token.Punctuation, ':'),
            (Token.Comment.Single, '//   '),
            (Token.Name.Variable, 'Входной'),
            (Token.Punctuation, ' - '),
            (Token.Name.Class, 'Структура'),
            (Token.Punctuation, ' - '),
            (Token.Comment.Single, 'настройки (дополнительные свойства) отчета, хранящиеся в данных формы:'),
            (Token.Keyword, 'Процедура'),
            (Token.Name.Function, 'ПриСозданииНаСервере'),
            (Token.Punctuation, '('),
            (Token.Name.Variable, 'Форма'),
            (Token.Punctuation, ','),
            (Token.Name.Variable, 'Отказ'),
            (Token.Punctuation, ','),
            (Token.Name.Variable, 'СтандартнаяОбработка'),
            (Token.Punctuation, ')'),
            (Token.Keyword, 'Экспорт'),
            (Token.Comment.Single, '// Обработка события.'),
            (Token.Keyword, 'КонецПроцедуры'),
        ]

        self.assertEqual(filtered[:len(expected_prefix)], expected_prefix)

    def test_method_description_example2_comments(self):
        source = '''
// Инициализирует структуру параметров для взаимодействия с файловой системой.
//
// Параметры:
//  РежимДиалога - РежимДиалогаВыбораФайла - режим работы конструируемого диалога выбора файлов.
//
// Возвращаемое значение:
//   см. ФайловаяСистемаКлиент.ПараметрыЗагрузкиФайла
        '''
        self.assertEqual(
            self.lex_filtered(source),
            [
                (Token.Comment.Single, '// Инициализирует структуру параметров для взаимодействия с файловой системой.'),
                (Token.Comment.Single, '//'),
                (Token.Comment.Single, '// '),
                (Token.Keyword, 'Параметры'),
                (Token.Punctuation, ':'),
                (Token.Comment.Single, '//  '),
                (Token.Name.Variable, 'РежимДиалога'),
                (Token.Punctuation, ' - '),
                (Token.Name.Class, 'РежимДиалогаВыбораФайла'),
                (Token.Punctuation, ' - '),
                (Token.Comment.Single, 'режим работы конструируемого диалога выбора файлов.'),
                (Token.Comment.Single, '//'),
                (Token.Comment.Single, '// '),
                (Token.Keyword, 'Возвращаемое значение'),
                (Token.Punctuation, ':'),
                (Token.Comment.Single, '//   '),
                (Token.Keyword, 'см.'),
                (Token.Comment.Single, ' '),
                (Token.Name.Namespace, 'ФайловаяСистемаКлиент.ПараметрыЗагрузкиФайла'),
            ],
        )

    def test_method_description_example3_param_block(self):
        source = '''
// В возвращаемом значении очищаются ссылки на несуществующий объект в базе данных, а именно
// - возвращаемая ссылка заменяется на указанное значение по умолчанию;
// - из данных типа Массив ссылки удаляются;
// - у данных типа Структура и Соответствие ключ не меняется, а значение устанавливается Неопределено;
// - анализ значений в данных типа Массив, Структура, Соответствие выполняется рекурсивно.
        '''
        self.assertEqual(
            self.lex_filtered(source),
            [
                (Token.Comment.Single, '// В возвращаемом значении очищаются ссылки на несуществующий объект в базе данных, а именно'),
                (Token.Comment.Single, '// - возвращаемая ссылка заменяется на указанное значение по умолчанию;'),
                (Token.Comment.Single, '// - из данных типа Массив ссылки удаляются;'),
                (Token.Comment.Single, '// - у данных типа Структура и Соответствие ключ не меняется, а значение устанавливается Неопределено;'),
                (Token.Comment.Single, '// - анализ значений в данных типа Массив, Структура, Соответствие выполняется рекурсивно.'),
            ],
        )

    def test_lexing_procedure_declaration_with_param(self):
        lexer = lexers.get_lexer_by_name('bsl')
        tokens = lexer.get_tokens(
            '''
            Процедура ИмяПроцедуры(
                    Знач ПараметрСКонстантой,
                    ОбычныйПараметр,
                    ПараметрСНекорректнымЗначением = Нелегальщина,
                    ПараметрСНекорректнымЗначением =НелегальщинаБезПробела,
                    ПараметрСДефолтнымЧисловымЗначением = 0
                ) Экспорт
            '''
        )

        self.assertEqual(
            filter_tokens(tokens),
            [
                (Token.Keyword, 'Процедура'),
                (Token.Name.Function, 'ИмяПроцедуры'),
                (Token.Punctuation, '('),
                (Token.Keyword, 'Знач'),
                (Token.Name.Variable, 'ПараметрСКонстантой'),
                (Token.Punctuation, ','),
                (Token.Name.Variable, 'ОбычныйПараметр'),
                (Token.Punctuation, ','),
                (Token.Name.Variable, 'ПараметрСНекорректнымЗначением'),
                (Token.Operator, '='),
                (Token.Generic.Error, 'Нелегальщина'),
                (Token.Punctuation, ','),
                (Token.Name.Variable, 'ПараметрСНекорректнымЗначением'),
                (Token.Operator, '='),
                (Token.Generic.Error, 'НелегальщинаБезПробела'),
                (Token.Punctuation, ','),
                (Token.Name.Variable, 'ПараметрСДефолтнымЧисловымЗначением'),
                (Token.Operator, '='),
                (Token.Literal.Number, '0'),
                (Token.Punctuation, ')'),
                (Token.Keyword, 'Экспорт'),
            ],
        )

    def test_lexing_text_with_quoted(self):
        lexer = lexers.get_lexer_by_name('bsl')
        tokens = lexer.get_tokens(
            '''
            Б = "текст с экраннированной "" кавычкой" + "и конкатенаций""";
            '''
        )

        self.assertEqual(
            filter_tokens(tokens),
            [
                (Token.Name.Variable, 'Б'),
                (Token.Operator, '='),
                (Token.String, '"'),
                (Token.String, 'текст с экраннированной '),
                (Token.String.Escape, '""'),
                (Token.String, ' кавычкой'),
                (Token.String, '"'),
                (Token.Operator, '+'),
                (Token.String, '"'),
                (Token.String, 'и конкатенаций'),
                (Token.String.Escape, '""'),
                (Token.String, '"'),
                (Token.Punctuation, ';'),
            ],
        )

    def test_lexing_text_multiline(self):
        lexer = lexers.get_lexer_by_name('bsl')
        tokens = lexer.get_tokens(
            '''
    В = "многострочная
// комментарий начинающийся с начала строки
    |строка
    //|это комментарий
    |// а это нет
    |";
            '''
        )

        self.assertEqual(
            filter_tokens(tokens),
            [
                (Token.Name.Variable, 'В'),
                (Token.Operator, '='),
                (Token.Literal.String, '"'),
                (Token.Literal.String, 'многострочная'),
                (Token.Comment.Single, '// комментарий начинающийся с начала строки'),
                (Token.Literal.String, '|'),
                (Token.Literal.String, 'строка'),
                (Token.Comment.Single, '//|это комментарий'),
                (Token.Literal.String, '|'),
                (Token.Literal.String, '// а это нет'),
                (Token.Literal.String, '|'),
                (Token.Literal.String, '"'),
                (Token.Punctuation, ';'),
            ],
        )

    def test_lexing_text_interpol(self):
        lexer = lexers.get_lexer_by_name('bsl')
        tokens = lexer.get_tokens(
            '''
    СтрШаблон("Товар: %1, %2 не найден!", Номенклатура, Характеристика);
    СтрШаблон("Скидка составила %1%%", 10);
            '''
        )

        self.assertEqual(
            filter_tokens(tokens),
            [
                (Token.Name.Builtin, 'СтрШаблон'),
                (Token.Punctuation, '('),
                (Token.Literal.String, '"'),
                (Token.Literal.String, 'Товар: '),
                (Token.Literal.String.Interpol, '%1'),
                (Token.Literal.String, ', '),
                (Token.Literal.String.Interpol, '%2'),
                (Token.Literal.String, ' не найден!'),
                (Token.Literal.String, '"'),
                (Token.Punctuation, ','),
                (Token.Name.Variable, 'Номенклатура'),
                (Token.Punctuation, ','),
                (Token.Name.Variable, 'Характеристика'),
                (Token.Punctuation, ')'),
                (Token.Punctuation, ';'),
                (Token.Name.Builtin, 'СтрШаблон'),
                (Token.Punctuation, '('),
                (Token.Literal.String, '"'),
                (Token.Literal.String, 'Скидка составила '),
                (Token.Literal.String.Interpol, '%1'),
                (Token.Literal.String.Escape, '%%'),
                (Token.Literal.String, '"'),
                (Token.Punctuation, ','),
                (Token.Literal.Number, '10'),
                (Token.Punctuation, ')'),
                (Token.Punctuation, ';')
            ],
        )

    def test_lexing_text_interpol_fake(self):
        lexer = lexers.get_lexer_by_name('bsl')
        tokens = lexer.get_tokens(
            '''
    Строка = "Кефир 15% жирности";
            '''
        )

        self.assertEqual(
            filter_tokens(tokens),
            [
                (Token.Name.Variable, 'Строка'),
                (Token.Operator, '='),
                (Token.Literal.String, '"'),
                (Token.Literal.String, 'Кефир 15% жирности'),
                (Token.Literal.String, '"'),
                (Token.Punctuation, ';')
            ],
        )

    def test_lexing_text_interpol_edge_cases(self):
        cases = [
            (
                'ПростоСтрока = "Без интерполяции %% параметра.";',
                [
                    (Token.Name.Variable, 'ПростоСтрока'),
                    (Token.Operator, '='),
                    (Token.Literal.String, '"'),
                    (Token.Literal.String, 'Без интерполяции '),
                    (Token.Literal.String.Escape, '%%'),
                    (Token.Literal.String, ' параметра.'),
                    (Token.Literal.String, '"'),
                    (Token.Punctuation, ';'),
                ],
            ),
            (
                "СтрШаблон(НСтр(\"ru = \'Проверка %1 внутри НСтр\'\"));",
                [
                    (Token.Name.Builtin, 'СтрШаблон'),
                    (Token.Punctuation, '('),
                    (Token.Name.Builtin, 'НСтр'),
                    (Token.Punctuation, '('),
                    (Token.Literal.String, '"'),
                    (Token.Name.Attribute, 'ru'),
                    (Token.Literal.String, ' '),
                    (Token.Operator, '='),
                    (Token.Literal.String, ' '),
                    (Token.Literal.String.Escape, "\'"),
                    (Token.Literal.String, "Проверка "),
                    (Token.Literal.String.Interpol, '%1'),
                    (Token.Literal.String, " внутри НСтр"),
                    (Token.Literal.String.Escape, "\'"),
                    (Token.Literal.String, '"'),
                    (Token.Punctuation, ')'),
                    (Token.Punctuation, ')'),
                    (Token.Punctuation, ';'),
                ],
            ),
            (
                'СтрШаблон("Проверка без интерполяции % параметра.");',
                [
                    (Token.Name.Builtin, 'СтрШаблон'),
                    (Token.Punctuation, '('),
                    (Token.Literal.String, '"'),
                    (Token.Literal.String, 'Проверка без интерполяции % параметра.'),
                    (Token.Literal.String, '"'),
                    (Token.Punctuation, ')'),
                    (Token.Punctuation, ';'),
                ],
            ),
            (
                'СтрШаблон("Проверка с некорректной интерполяцией %A параметра.");',
                [
                    (Token.Name.Builtin, 'СтрШаблон'),
                    (Token.Punctuation, '('),
                    (Token.Literal.String, '"'),
                    (Token.Literal.String, 'Проверка с некорректной интерполяцией '),
                    (Token.Generic.Error, '%A'),
                    (Token.Literal.String, ' параметра.'),
                    (Token.Literal.String, '"'),
                    (Token.Punctuation, ')'),
                    (Token.Punctuation, ';'),
                ],
            ),
        ]

        for source, expected in cases:
            with self.subTest(source=source):
                self.assertTokens(source, expected)

    def test_lexing_nstr_with_single_quotes(self):
        lexer = lexers.get_lexer_by_name('bsl')
        tokens = lexer.get_tokens(
            '''
            НСтр("ru = 'Проверка'");
            '''
        )

        self.assertEqual(
            filter_tokens(tokens),
            [
                (Token.Name.Builtin, 'НСтр'),
                (Token.Punctuation, '('),
                (Token.Literal.String, '"'),
                (Token.Name.Attribute, 'ru'),
                (Token.Literal.String, ' '),
                (Token.Operator, '='),
                (Token.Literal.String, ' '),
                (Token.Literal.String.Escape, "\'"),
                (Token.Literal.String, "Проверка"),
                (Token.Literal.String.Escape, "\'"),
                (Token.Literal.String, '"'),
                (Token.Punctuation, ')'),
                (Token.Punctuation, ';'),
            ],
        )

    def test_lexing_nstr_locale_keys_with_space_after_semicolon(self):
        lexer = lexers.get_lexer_by_name('bsl')
        tokens = lexer.get_tokens(
            '''
            НСтр("ru = 'Русский'; en = 'English'");
            '''
        )

        self.assertEqual(
            filter_tokens(tokens),
            [
                (Token.Name.Builtin, 'НСтр'),
                (Token.Punctuation, '('),
                (Token.Literal.String, '"'),
                (Token.Name.Attribute, 'ru'),
                (Token.Literal.String, ' '),
                (Token.Operator, '='),
                (Token.Literal.String, ' '),
                (Token.Literal.String.Escape, "\'"),
                (Token.Literal.String, "Русский"),
                (Token.Literal.String.Escape, "\'"),
                (Token.Operator, ';'),
                (Token.Literal.String, ' '),
                (Token.Name.Attribute, 'en'),
                (Token.Literal.String, ' '),
                (Token.Operator, '='),
                (Token.Literal.String, ' '),
                (Token.Literal.String.Escape, "\'"),
                (Token.Literal.String, "English"),
                (Token.Literal.String.Escape, "\'"),
                (Token.Literal.String, '"'),
                (Token.Punctuation, ')'),
                (Token.Punctuation, ';'),
            ],
        )


    def test_lexing_nstr_locale_missing_semicolon_same_line(self):
        lexer = lexers.get_lexer_by_name('bsl')
        tokens = lexer.get_tokens(
            '''
            НСтр("ru = 'Русский' en = 'English'");
            '''
        )

        self.assertEqual(
            filter_tokens(tokens),
            [
                (Token.Name.Builtin, 'НСтр'),
                (Token.Punctuation, '('),
                (Token.Literal.String, '"'),
                (Token.Name.Attribute, 'ru'),
                (Token.Literal.String, ' '),
                (Token.Operator, '='),
                (Token.Literal.String, ' '),
                (Token.Literal.String.Escape, "\'"),
                (Token.Literal.String, "Русский"),
                (Token.Literal.String.Escape, "\'"),
                (Token.Generic.Error, " en = 'English'"),
                (Token.Literal.String, '"'),
                (Token.Punctuation, ')'),
                (Token.Punctuation, ';'),
            ],
        )

    def test_lexing_nstr_locale_missing_closing_single_quote(self):
        lexer = lexers.get_lexer_by_name('bsl')
        tokens = lexer.get_tokens(
            '''
            НСтр("ru = 'Русский;
                 |en = 'English'"
            );
            '''
        )

        self.assertEqual(
            filter_tokens(tokens),
            [
                (Token.Name.Builtin, 'НСтр'),
                (Token.Punctuation, '('),
                (Token.Literal.String, '"'),
                (Token.Generic.Error, "ru = 'Русский;"),
                (Token.Literal.String, '|'),
                (Token.Generic.Error, "en = 'English'"),
                (Token.Literal.String, '"'),
                (Token.Punctuation, ')'),
                (Token.Punctuation, ';'),
            ],
        )

    def test_lexing_nstr_locale_multiline_with_semicolons(self):
        self.assertTokens(
            '''
            НСтр("ru = 'Русский';
                 |en = 'English';"
            );
            ''',
            [
                (Token.Name.Builtin, 'НСтр'),
                (Token.Punctuation, '('),
                (Token.Literal.String, '"'),
                (Token.Name.Attribute, 'ru'),
                (Token.Literal.String, ' '),
                (Token.Operator, '='),
                (Token.Literal.String, ' '),
                (Token.Literal.String.Escape, "\'"),
                (Token.Literal.String, "Русский"),
                (Token.Literal.String.Escape, "\'"),
                (Token.Operator, ';'),
                (Token.Literal.String, '|'),
                (Token.Name.Attribute, 'en'),
                (Token.Literal.String, ' '),
                (Token.Operator, '='),
                (Token.Literal.String, ' '),
                (Token.Literal.String.Escape, "\'"),
                (Token.Literal.String, "English"),
                (Token.Literal.String.Escape, "\'"),
                (Token.Operator, ';'),
                (Token.Literal.String, '"'),
                (Token.Punctuation, ')'),
                (Token.Punctuation, ';'),
            ],
        )

    def test_lexing_nstr_locale_keys_missing_open_quote(self):
        lexer = lexers.get_lexer_by_name('bsl')
        tokens = lexer.get_tokens(
            '''
            НСтр("ru = Русский' en = 'English';");
            '''
        )

        self.assertEqual(
            filter_tokens(tokens),
            [
                (Token.Name.Builtin, 'НСтр'),
                (Token.Punctuation, '('),
                (Token.Literal.String, '"'),
                (Token.Generic.Error, "ru = Русский' en = 'English';"),
                (Token.Literal.String, '"'),
                (Token.Punctuation, ')'),
                (Token.Punctuation, ';'),
            ],
        )

    def test_lexing_nstr_locale_missing_quote_after_key(self):
        self.assertTokens(
            '''
            НСтр("ru = Русский'" en = 'English';");
            ''',
            [
                (Token.Name.Builtin, 'НСтр'),
                (Token.Punctuation, '('),
                (Token.Literal.String, '"'),
                (Token.Generic.Error, "ru = Русский'"),
                (Token.Literal.String, '"'),
                (Token.Name.Variable, 'en'),
                (Token.Operator, '='),
                (Token.Literal.Date, "'English'"),
                (Token.Punctuation, ';'),
                (Token.Literal.String, '"'),
                (Token.Generic.Error, ');'),
            ],
        )

    def test_lexing_nstr_locale_multiline_many_locales(self):
        self.assertTokens(
            '''
            НСтр("ru = 'Русский';
                 |en = 'English';
                 |de = 'Deutsch';
                 |fr = 'Français';
                 |es = 'Español'"
            );
            ''',
            [
                (Token.Name.Builtin, 'НСтр'),
                (Token.Punctuation, '('),
                (Token.Literal.String, '"'),
                (Token.Name.Attribute, 'ru'),
                (Token.Literal.String, ' '),
                (Token.Operator, '='),
                (Token.Literal.String, ' '),
                (Token.Literal.String.Escape, "\'"),
                (Token.Literal.String, "Русский"),
                (Token.Literal.String.Escape, "\'"),
                (Token.Operator, ';'),
                (Token.Literal.String, '|'),
                (Token.Name.Attribute, 'en'),
                (Token.Literal.String, ' '),
                (Token.Operator, '='),
                (Token.Literal.String, ' '),
                (Token.Literal.String.Escape, "\'"),
                (Token.Literal.String, "English"),
                (Token.Literal.String.Escape, "\'"),
                (Token.Operator, ';'),
                (Token.Literal.String, '|'),
                (Token.Name.Attribute, 'de'),
                (Token.Literal.String, ' '),
                (Token.Operator, '='),
                (Token.Literal.String, ' '),
                (Token.Literal.String.Escape, "\'"),
                (Token.Literal.String, "Deutsch"),
                (Token.Literal.String.Escape, "\'"),
                (Token.Operator, ';'),
                (Token.Literal.String, '|'),
                (Token.Name.Attribute, 'fr'),
                (Token.Literal.String, ' '),
                (Token.Operator, '='),
                (Token.Literal.String, ' '),
                (Token.Literal.String.Escape, "\'"),
                (Token.Literal.String, "Français"),
                (Token.Literal.String.Escape, "\'"),
                (Token.Operator, ';'),
                (Token.Literal.String, '|'),
                (Token.Name.Attribute, 'es'),
                (Token.Literal.String, ' '),
                (Token.Operator, '='),
                (Token.Literal.String, ' '),
                (Token.Literal.String.Escape, "\'"),
                (Token.Literal.String, "Español"),
                (Token.Literal.String.Escape, "\'"),
                (Token.Literal.String, '"'),
                (Token.Punctuation, ')'),
                (Token.Punctuation, ';'),
            ],
        )

    def test_lexing_nstr_locale_multiline_interpolated(self):
        self.assertTokens(
            '''
            НСтр("ru = 'Все и сразу %1 %% литров ""молока""';");
            ''',
            [
                (Token.Name.Builtin, 'НСтр'),
                (Token.Punctuation, '('),
                (Token.Literal.String, '"'),
                (Token.Name.Attribute, 'ru'),
                (Token.Literal.String, ' '),
                (Token.Operator, '='),
                (Token.Literal.String, ' '),
                (Token.Literal.String.Escape, "\'"),
                (Token.Literal.String, "Все и сразу "),
                (Token.Literal.String.Interpol, '%1'),
                (Token.Literal.String, ' '),
                (Token.Literal.String.Escape, '%%'),
                (Token.Literal.String, ' литров '),
                (Token.Literal.String.Escape, '""'),
                (Token.Literal.String, 'молока'),
                (Token.Literal.String.Escape, '""'),
                (Token.Literal.String.Escape, "\'"),
                (Token.Operator, ';'),
                (Token.Literal.String, '"'),
                (Token.Punctuation, ')'),
                (Token.Punctuation, ';'),
            ],
        )

    def test_lexing_nstr_locale_missing_quote_before_next(self):
        lexer = lexers.get_lexer_by_name('bsl')
        tokens = lexer.get_tokens(
            '''
            НСтр("ru = 'Русский'" en = 'English';");
            Ключ = Истина;
            '''
        )

        self.assertEqual(
            filter_tokens(tokens),
            [
                (Token.Name.Builtin, 'НСтр'),
                (Token.Punctuation, '('),
                (Token.Literal.String, '"'),
                (Token.Name.Attribute, 'ru'),
                (Token.Literal.String, ' '),
                (Token.Operator, '='),
                (Token.Literal.String, ' '),
                (Token.Literal.String.Escape, "\'"),
                (Token.Literal.String, "Русский"),
                (Token.Literal.String.Escape, "\'"),
                (Token.Literal.String, '"'),
                (Token.Generic.Error, " en = 'English';\");"),
                (Token.Name.Variable, 'Ключ'),
                (Token.Operator, '='),
                (Token.Keyword.Constant, 'Истина'),
                (Token.Punctuation, ';')
            ],
        )

    def test_lexing_nstr_locale_extra_single_quote(self):
        lexer = lexers.get_lexer_by_name('bsl')
        tokens = lexer.get_tokens(
            '''
            НСтр("ru = 'Русский'';
                 |en = 'English';"
            );
            '''
        )

        self.assertEqual(
            filter_tokens(tokens),
            [
                (Token.Name.Builtin, 'НСтр'),
                (Token.Punctuation, '('),
                (Token.Literal.String, '"'),
                (Token.Name.Attribute, 'ru'),
                (Token.Literal.String, ' '),
                (Token.Operator, '='),
                (Token.Literal.String, ' '),
                (Token.Literal.String.Escape, "\'"),
                (Token.Literal.String, "Русский"),
                (Token.Literal.String.Escape, "\'"),
                (Token.Generic.Error, "';"),
                (Token.Literal.String, '|'),
                (Token.Generic.Error, "en = 'English';"),
                (Token.Generic.Error, '"'),
                (Token.Punctuation, ')'),
                (Token.Punctuation, ';'),
            ],
        )

    def test_lexing_nstr_multiline_value_with_pipe(self):
        lexer = lexers.get_lexer_by_name('bsl')
        tokens = lexer.get_tokens(
            '''
            СтрокаСообщения = НСтр("ru = 'Составной тип данных для значений по умолчанию не поддерживается.
                    |Реквизит ""%1"".'");
            '''
        )

        self.assertEqual(
            filter_tokens(tokens),
            [
                (Token.Name.Variable, 'СтрокаСообщения'),
                (Token.Operator, '='),
                (Token.Name.Builtin, 'НСтр'),
                (Token.Punctuation, '('),
                (Token.Literal.String, '"'),
                (Token.Name.Attribute, 'ru'),
                (Token.Literal.String, ' '),
                (Token.Operator, '='),
                (Token.Literal.String, ' '),
                (Token.Literal.String.Escape, "\'"),
                (Token.Literal.String, "Составной тип данных для значений по умолчанию не поддерживается."),
                (Token.Literal.String, '|'),
                (Token.Literal.String, 'Реквизит '),
                (Token.Literal.String.Escape, '""'),
                (Token.Literal.String.Interpol, '%1'),
                (Token.Literal.String.Escape, '""'),
                (Token.Literal.String, "."),
                (Token.Literal.String.Escape, "\'"),
                (Token.Literal.String, '"'),
                (Token.Punctuation, ')'),
                (Token.Punctuation, ';'),
            ],
        )

    def test_pipe_outside_string_is_error(self):
        lexer = lexers.get_lexer_by_name('bsl')
        tokens = lexer.get_tokens(
            '''
Строка =
    "Пример";
    |Проблемы";
            '''
        )

        self.assertEqual(
            filter_tokens(tokens),
            [
                (Token.Name.Variable, 'Строка'),
                (Token.Operator, '='),
                (Token.Literal.String, '"'),
                (Token.Literal.String, 'Пример'),
                (Token.Literal.String, '"'),
                (Token.Punctuation, ';'),
                (Token.Generic.Error, '|Проблемы";'),
            ],
        )

    def test_pipe_outside_string_after_multiline_string(self):
        lexer = lexers.get_lexer_by_name('bsl')
        tokens = lexer.get_tokens(
            '''
Строка =
    "Пример"
    |Проблемы";
            '''
        )

        self.assertEqual(
            filter_tokens(tokens),
            [
                (Token.Name.Variable, 'Строка'),
                (Token.Operator, '='),
                (Token.Literal.String, '"'),
                (Token.Literal.String, 'Пример'),
                (Token.Literal.String, '"'),
                (Token.Generic.Error, '|Проблемы";'),
            ],
        )

    def test_lexing_nstr_multiline_without_semicolon_is_error(self):
        lexer = lexers.get_lexer_by_name('bsl')
        tokens = lexer.get_tokens(
            '''
            НСтр("ru = 'Русский'
                 |en = 'English'"
            );
            '''
        )

        self.assertEqual(
            filter_tokens(tokens),
            [
                (Token.Name.Builtin, 'НСтр'),
                (Token.Punctuation, '('),
                (Token.Literal.String, '"'),
                (Token.Name.Attribute, 'ru'),
                (Token.Literal.String, ' '),
                (Token.Operator, '='),
                (Token.Literal.String, ' '),
                (Token.Literal.String.Escape, "\'"),
                (Token.Literal.String, "Русский"),
                (Token.Literal.String.Escape, "\'"),
                (Token.Literal.String, "|"),
                (Token.Generic.Error, "en = 'English'"),
                (Token.Literal.String, '"'),
                (Token.Punctuation, ')'),
                (Token.Punctuation, ';'),
            ],
        )

    def test_lexing_text_with_keyword(self):
        lexer = lexers.get_lexer_by_name('bsl')
        tokens = lexer.get_tokens(
            '''
            СтрокаСоСловомВыбрать = "Some selected text";
            '''
        )

        self.assertEqual(
            filter_tokens(tokens),
            [
                (Token.Name.Variable, 'СтрокаСоСловомВыбрать'),
                (Token.Operator, '='),
                (Token.Literal.String, '"'),
                (Token.Literal.String, 'Some selected text'),
                (Token.Literal.String, '"'),
                (Token.Punctuation, ';'),
            ],
        )

    def test_lexing_unterminated_string_before_code(self):
        self.assertTokens(
            '''
            Строка =
                "Пример
            Ключ = Истина;
            ''',
            [
                (Token.Name.Variable, 'Строка'),
                (Token.Operator, '='),
                (Token.Literal.String, '"'),
                (Token.Generic.Error, 'Пример'),
                (Token.Name.Variable, 'Ключ'),
                (Token.Operator, '='),
                (Token.Keyword.Constant, 'Истина'),
                (Token.Punctuation, ';')
            ],
        )

    def test_lexing_unterminated_multiline_string_with_pipe_before_code(self):
        self.assertTokens(
            '''
            Строка =
                "Пример
                |Не закрытая вторая строка
            Ключ = Истина;
            ''',
            [
                (Token.Name.Variable, 'Строка'),
                (Token.Operator, '='),
                (Token.Literal.String, '"'),
                (Token.Literal.String, 'Пример'),
                (Token.Literal.String, '|'),
                (Token.Generic.Error, 'Не закрытая вторая строка'),
                (Token.Name.Variable, 'Ключ'),
                (Token.Operator, '='),
                (Token.Keyword.Constant, 'Истина'),
                (Token.Punctuation, ';'),
            ],
        )

    def test_string_followed_by_identifier(self):
        lexer = lexers.get_lexer_by_name('bsl')
        tokens = lexer.get_tokens('Строка = "Пример" нелегальщина')

        self.assertEqual(
            filter_tokens(tokens),
            [
                (Token.Name.Variable, 'Строка'),
                (Token.Operator, '='),
                (Token.Literal.String, '"'),
                (Token.Literal.String, 'Пример'),
                (Token.Literal.String, '"'),
                (Token.Generic.Error, ' нелегальщина'),
            ],
        )

    def test_query_inside_string_uses_sdbl(self):
        lexer = lexers.get_lexer_by_name('bsl')
        tokens = lexer.get_tokens(
            '''
Запрос = Новый Запрос(
    "ВЫБРАТЬ
    |   ТаблицаНомераСчетов.НомерСчета КАК НомерСчета,
    |   ТаблицаНомераСчетов.Владелец КАК Владелец
    |ПОМЕСТИТЬ ТаблицаНомераСчетов
    |ИЗ
    |   &ТаблицаНомераСчетов КАК ТаблицаНомераСчетов
    |ИНДЕКСИРОВАТЬ ПО
    |   Владелец
    |"
);
            '''
        )

        filtered = filter_tokens(tokens)
        self.assertIn((Token.Keyword.Declaration, 'ВЫБРАТЬ'), filtered)
        self.assertIn((Token.Keyword.Declaration, 'ПОМЕСТИТЬ'), filtered)
        self.assertIn((Token.Keyword.Declaration, 'ИНДЕКСИРОВАТЬ ПО'), filtered)
        self.assertIn((Token.Name.Variable, 'ТаблицаНомераСчетов'), filtered)
        self.assertIn((Token.Literal.String, '|'), filtered)
        self.assertIn((Token.Literal.String, '"'), filtered)  # closing quote kept as string token

    def test_lexing_number(self):
        lexer = lexers.get_lexer_by_name('bsl')
        tokens = lexer.get_tokens(
            '''
            Число = 0.0 * 100;
            '''
        )

        self.assertEqual(
            filter_tokens(tokens),
            [
                (Token.Name.Variable, 'Число'),
                (Token.Operator, '='),
                (Token.Literal.Number, '0.0'),
                (Token.Operator, '*'),
                (Token.Literal.Number, '100'),
                (Token.Punctuation, ';'),
            ],
        )


    def test_lexing_date_literals(self):
        cases = [
            (
                "Дата = '00010101000000';",
                [
                    (Token.Name.Variable, 'Дата'),
                    (Token.Operator, '='),
                    (Token.Literal.Date, "'00010101000000'"),
                    (Token.Punctuation, ';'),
                ],
            ),
            (
                "КороткаяДата = '00010101';",
                [
                    (Token.Name.Variable, 'КороткаяДата'),
                    (Token.Operator, '='),
                    (Token.Literal.Date, "'00010101'"),
                    (Token.Punctuation, ';'),
                ],
            ),
            (
                "ДатаСРазделителями = '0001-01-01T00:00:00';",
                [
                    (Token.Name.Variable, 'ДатаСРазделителями'),
                    (Token.Operator, '='),
                    (Token.Literal.Date, "'0001-01-01T00:00:00'"),
                    (Token.Punctuation, ';'),
                ],
            ),
            (
                "КороткаяДатаСРазделителями = '0001/01/01';",
                [
                    (Token.Name.Variable, 'КороткаяДатаСРазделителями'),
                    (Token.Operator, '='),
                    (Token.Literal.Date, "'0001/01/01'"),
                    (Token.Punctuation, ';'),
                ],
            ),
        ]

        for source, expected in cases:
            with self.subTest(source=source):
                self.assertTokens(source, expected)


    def test_lexing_date_in_string(self):
        lexer = lexers.get_lexer_by_name('bsl')
        tokens = lexer.get_tokens(
            '''
            СтрокаСДатойВнутри = "Литерал типа Дата: '00010101'";
            '''
        )

        self.assertEqual(
            filter_tokens(tokens),
            [
                (Token.Name.Variable, 'СтрокаСДатойВнутри'),
                (Token.Operator, '='),
                (Token.Literal.String, '"'),
                (Token.Literal.String, "Литерал типа Дата: '00010101'"),
                (Token.Literal.String, '"'),
                (Token.Punctuation, ';'),
            ],
        )

    def test_lexing_if_else(self):
        lexer = lexers.get_lexer_by_name('bsl')
        tokens = lexer.get_tokens(
            '''
            Если А = 0 И НЕ Число <= 0 Тогда
                ОбычныйПараметр = Истина;
            Иначе
                ОбычныйПараметр = Ложь
            КонецЕсли;
            '''
        )

        self.assertEqual(
            filter_tokens(tokens),
            [
                (Token.Keyword, 'Если'),
                (Token.Name.Variable, 'А'),
                (Token.Operator, '='),
                (Token.Literal.Number, '0'),
                (Token.Keyword, 'И'),
                (Token.Keyword, 'НЕ'),
                (Token.Name.Variable, 'Число'),
                (Token.Operator, '<='),
                (Token.Literal.Number, '0'),
                (Token.Keyword, 'Тогда'),
                (Token.Name.Variable, 'ОбычныйПараметр'),
                (Token.Operator, '='),
                (Token.Keyword.Constant, 'Истина'),
                (Token.Punctuation, ';'),
                (Token.Keyword, 'Иначе'),
                (Token.Name.Variable, 'ОбычныйПараметр'),
                (Token.Operator, '='),
                (Token.Keyword.Constant, 'Ложь'),
                (Token.Keyword, 'КонецЕсли'),
                (Token.Punctuation, ';'),
            ],
        )

    def test_lexing_if_else_english(self):
        lexer = lexers.get_lexer_by_name('bsl')
        tokens = lexer.get_tokens(
            '''
            If True Then
                Value = 0;
            ElsIf TypeOf(Parameter) Then
                Value = NULL
            EndIf;
            '''
        )

        self.assertEqual(
            filter_tokens(tokens),
            [
                (Token.Keyword, 'If'),
                (Token.Keyword.Constant, 'True'),
                (Token.Keyword, 'Then'),
                (Token.Name.Variable, 'Value'),
                (Token.Operator, '='),
                (Token.Literal.Number, '0'),
                (Token.Punctuation, ';'),
                (Token.Keyword, 'ElsIf'),
                (Token.Name.Builtin, 'TypeOf'),
                (Token.Punctuation, '('),
                (Token.Name.Variable, 'Parameter'),
                (Token.Punctuation, ')'),
                (Token.Keyword, 'Then'),
                (Token.Name.Variable, 'Value'),
                (Token.Operator, '='),
                (Token.Keyword.Constant, 'NULL'),
                (Token.Keyword, 'EndIf'),
                (Token.Punctuation, ';'),
            ],
        )

    def test_lexing_while_do(self):
        lexer = lexers.get_lexer_by_name('bsl')
        tokens = lexer.get_tokens(
            '''
            Пока ЗначениеЗаполнено(Б) Цикл
                Прервать;
            КонецЦикла;
            '''
        )

        self.assertEqual(
            filter_tokens(tokens),
            [
                (Token.Keyword, 'Пока'),
                (Token.Name.Builtin, 'ЗначениеЗаполнено'),
                (Token.Punctuation, '('),
                (Token.Name.Variable, 'Б'),
                (Token.Punctuation, ')'),
                (Token.Keyword, 'Цикл'),
                (Token.Keyword, 'Прервать'),
                (Token.Punctuation, ';'),
                (Token.Keyword, 'КонецЦикла'),
                (Token.Punctuation, ';'),
            ],
        )

    def test_lexing_call_function(self):
        lexer = lexers.get_lexer_by_name('bsl')
        tokens = lexer.get_tokens(
            '''
            НевстроеннаяПроцедура();
            НевстроеннаяПроцедураСПробелом ();
            '''
        )

        self.assertEqual(
            filter_tokens(tokens),
            [
                (Token.Name.Function, 'НевстроеннаяПроцедура'),
                (Token.Punctuation, '('),
                (Token.Punctuation, ')'),
                (Token.Punctuation, ';'),
                (Token.Name.Function, 'НевстроеннаяПроцедураСПробелом'),
                (Token.Punctuation, '('),
                (Token.Punctuation, ')'),
                (Token.Punctuation, ';'),
            ],
        )

    def test_lexing_call_builtin_function(self):
        cases = [
            'СтрДлина();',
            'СтрДлина ();',
        ]
        expected = [
            (Token.Name.Builtin, 'СтрДлина'),
            (Token.Punctuation, '('),
            (Token.Punctuation, ')'),
            (Token.Punctuation, ';'),
        ]

        for source in cases:
            with self.subTest(source=source):
                self.assertTokens(source, expected)

    def test_call_only_builtins_priority(self):
        cases = [
            (
                'Булево(); Дата();',
                [
                    (Token.Name.Builtin, 'Булево'),
                    (Token.Punctuation, '('),
                    (Token.Punctuation, ')'),
                    (Token.Punctuation, ';'),
                    (Token.Name.Builtin, 'Дата'),
                    (Token.Punctuation, '('),
                    (Token.Punctuation, ')'),
                    (Token.Punctuation, ';'),
                ],
            ),
            (
                'Объект.Булево;\nОбъект.Дата;',
                [
                    (Token.Name.Variable, 'Объект'),
                    (Token.Operator, '.'),
                    (Token.Name.Variable, 'Булево'),
                    (Token.Punctuation, ';'),
                    (Token.Name.Variable, 'Объект'),
                    (Token.Operator, '.'),
                    (Token.Name.Variable, 'Дата'),
                    (Token.Punctuation, ';'),
                ],
            ),
        ]

        for source, expected in cases:
            with self.subTest(source=source):
                self.assertTokens(source, expected)

    def test_lexing_call_new(self):
        lexer = lexers.get_lexer_by_name('bsl')
        tokens = lexer.get_tokens(
            '''
            НовыйОбъект = Новый ТаблицаЗначений;
            '''
        )

        self.assertEqual(
            filter_tokens(tokens),
            [
                (Token.Name.Variable, 'НовыйОбъект'),
                (Token.Operator, '='),
                (Token.Keyword, 'Новый'),
                (Token.Name.Class, 'ТаблицаЗначений'),
                (Token.Punctuation, ';'),
            ],
        )

    def test_lexing_call_new_function(self):
        lexer = lexers.get_lexer_by_name('bsl')
        tokens = lexer.get_tokens(
            '''
            НовыйОбъект = Новый("ТаблицаЗначений");
            '''
        )

        self.assertEqual(
            filter_tokens(tokens),
            [
                (Token.Name.Variable, 'НовыйОбъект'),
                (Token.Operator, '='),
                (Token.Name.Builtin, 'Новый'),
                (Token.Punctuation, '('),
                (Token.Literal.String, '"'),
                (Token.Name.Class, 'ТаблицаЗначений'),
                (Token.Literal.String, '"'),
                (Token.Punctuation, ')'),
                (Token.Punctuation, ';'),
            ],
        )

    def test_lexing_internal_function_in_variable_name(self):
        lexer = lexers.get_lexer_by_name('bsl')
        tokens = lexer.get_tokens(
            '''
            ПрефиксЗначениеЗаполненоПостфикс = "";
            '''
        )

        self.assertEqual(
            filter_tokens(tokens),
            [
                (Token.Name.Variable, 'ПрефиксЗначениеЗаполненоПостфикс'),
                (Token.Operator, '='),
                (Token.Literal.String, '"'),
                (Token.Literal.String, '"'),
                (Token.Punctuation, ';'),
            ],
        )

    def test_lexing_internal_function_in_fluent_chain_call(self):
        lexer = lexers.get_lexer_by_name('bsl')
        tokens = lexer.get_tokens(
            '''
            Объект.Истина.Сообщить().Если().Цикл().Новый;
            '''
        )

        self.assertEqual(
            filter_tokens(tokens),
            [
                (Token.Name.Variable, 'Объект'),
                (Token.Operator, '.'),
                (Token.Name.Variable, 'Истина'),
                (Token.Operator, '.'),
                (Token.Name.Function, 'Сообщить'),
                (Token.Punctuation, '('),
                (Token.Punctuation, ')'),
                (Token.Operator, '.'),
                (Token.Name.Function, 'Если'),
                (Token.Punctuation, '('),
                (Token.Punctuation, ')'),
                (Token.Operator, '.'),
                (Token.Name.Function, 'Цикл'),
                (Token.Punctuation, '('),
                (Token.Punctuation, ')'),
                (Token.Operator, '.'),
                (Token.Name.Variable, 'Новый'),
                (Token.Punctuation, ';')
            ],
        )

    def test_lexing_internal_property_highlithing(self):
        lexer = lexers.get_lexer_by_name('bsl')
        tokens = lexer.get_tokens(
            '''
            Справочники.ИмяСправочника.СоздатьЭлемент();
            '''
        )

        self.assertEqual(
            filter_tokens(tokens),
            [
                (Token.Name.Namespace, 'Справочники'),
                (Token.Operator, '.'),
                (Token.Name.Class, 'ИмяСправочника'),
                (Token.Operator, '.'),
                (Token.Name.Function, 'СоздатьЭлемент'),
                (Token.Punctuation, '('),
                (Token.Punctuation, ')'),
                (Token.Punctuation, ';')
            ],
        )

    def test_lexing_internal_function_highlithing(self):
        lexer = lexers.get_lexer_by_name('bsl')
        tokens = lexer.get_tokens(
            '''
            А = ХранилищеПользовательскихНастроекДинамическихСписков.Сохранить();
            '''
        )

        self.assertEqual(
            filter_tokens(tokens),
            [
                (Token.Name.Variable, 'А'),
                (Token.Operator, '='),
                (Token.Name.Class, 'ХранилищеПользовательскихНастроекДинамическихСписков'),
                (Token.Operator, '.'),
                (Token.Name.Function, 'Сохранить'),
                (Token.Punctuation, '('),
                (Token.Punctuation, ')'),
                (Token.Punctuation, ';')
            ],
        )

    def test_lexing_variable_assignment_with_compare(self):
        lexer = lexers.get_lexer_by_name('bsl')
        tokens = lexer.get_tokens(
            '''
            Б = А = 0;
            '''
        )

        self.assertEqual(
            filter_tokens(tokens),
            [
                (Token.Name.Variable, 'Б'),
                (Token.Operator, '='),
                (Token.Name.Variable, 'А'),
                (Token.Operator, '='),
                (Token.Literal.Number, '0'),
                (Token.Punctuation, ';')
            ],
        )

    def test_lexing_label(self):
        lexer = lexers.get_lexer_by_name('bsl')
        tokens = lexer.get_tokens(
            '''
            ~Метка:
            Перейти ~Метка;
            '''
        )

        self.assertEqual(
            filter_tokens(tokens),
            [
                (Token.Name.Label, '~Метка'),
                (Token.Punctuation, ':'),
                (Token.Keyword, 'Перейти'),
                (Token.Name.Label, '~Метка'),
                (Token.Punctuation, ';')
            ],
        )

    def test_lexing_single_word_highlighting(self):
        lexer = lexers.get_lexer_by_name('bsl')
        tokens = lexer.get_tokens(
            '''
            НачатьТранзакцию
            '''
        )

        self.assertEqual(
            filter_tokens(tokens),
            [
                (Token.Name.Builtin, 'НачатьТранзакцию'),
            ],
        )


    def test_lexing_invalid_illegal(self):
        lexer = lexers.get_lexer_by_name('bsl')
        tokens = lexer.get_tokens(
            '''
            ПараметрСНекорректнымЗначением = Нелегальщина,
            ПараметрСНекорректнымЗначением =НелегальщинаБезПробела,
            '''
        )

        self.assertEqual(
            filter_tokens(tokens),
            [
                (Token.Name.Variable, 'ПараметрСНекорректнымЗначением'),
                (Token.Operator, '='),
                (Token.Name.Variable, 'Нелегальщина'),
                (Token.Punctuation, ','),
                (Token.Name.Variable, 'ПараметрСНекорректнымЗначением'),
                (Token.Operator, '='),
                (Token.Name.Variable, 'НелегальщинаБезПробела'),
                (Token.Punctuation, ',')
            ],
        )


    def test_lexing_async_await(self):
        lexer = lexers.get_lexer_by_name('bsl')
        tokens = lexer.get_tokens(
            '''
            Асинх Процедура П()
                Ждать НеNull(Null);
            КонецПроцедуры 
            '''
        )

        self.assertEqual(
            filter_tokens(tokens),
            [
                (Token.Keyword, 'Асинх'),
                (Token.Keyword, 'Процедура'),
                (Token.Name.Function, 'П'),
                (Token.Punctuation, '('),
                (Token.Punctuation, ')'),
                (Token.Keyword, 'Ждать'),
                (Token.Name.Function, 'НеNull'),
                (Token.Punctuation, '('),
                (Token.Keyword.Constant, 'Null'),
                (Token.Punctuation, ')'),
                (Token.Punctuation, ';'),
                (Token.Keyword, 'КонецПроцедуры')
            ],
        )

    def test_lexing_wait_and_identifier(self):
        lexer = lexers.get_lexer_by_name('bsl')
        tokens = lexer.get_tokens(
            '''
            Асинх Процедура Test(Ждать, wait)
                Ждать 1;
                Ждать (Ждать 1);
                Ждать Об;
                Если Ждать Тогда
                    Возврат;
                КонецЕсли;
            КонецПроцедуры
            '''
        )

        self.assertEqual(
            filter_tokens(tokens),
            [
                (Token.Keyword, 'Асинх'),
                (Token.Keyword, 'Процедура'),
                (Token.Name.Function, 'Test'),
                (Token.Punctuation, '('),
                (Token.Name.Variable, 'Ждать'),
                (Token.Punctuation, ','),
                (Token.Name.Variable, 'wait'),
                (Token.Punctuation, ')'),
                (Token.Keyword, 'Ждать'),
                (Token.Literal.Number, '1'),
                (Token.Punctuation, ';'),
                (Token.Keyword, 'Ждать'),
                (Token.Punctuation, '('),
                (Token.Keyword, 'Ждать'),
                (Token.Literal.Number, '1'),
                (Token.Punctuation, ')'),
                (Token.Punctuation, ';'),
                (Token.Keyword, 'Ждать'),
                (Token.Name.Variable, 'Об'),
                (Token.Punctuation, ';'),
                (Token.Keyword, 'Если'),
                (Token.Keyword, 'Ждать'),
                (Token.Keyword, 'Тогда'),
                (Token.Keyword, 'Возврат'),
                (Token.Punctuation, ';'),
                (Token.Keyword, 'КонецЕсли'),
                (Token.Punctuation, ';'),
                (Token.Keyword, 'КонецПроцедуры'),
            ],
        )

    def test_lexing_execute_algorithm(self):
        lexer = lexers.get_lexer_by_name('bsl')
        tokens = lexer.get_tokens(
            '''
            Выполнить Алгоритм;
            '''
        )

        self.assertEqual(
            filter_tokens(tokens),
            [
                (Token.Keyword, 'Выполнить'),
                (Token.Name.Variable, 'Алгоритм'),
                (Token.Punctuation, ';'),
            ],
        )

    def test_lexing_execute_method_call(self):
        lexer = lexers.get_lexer_by_name('bsl')
        tokens = lexer.get_tokens(
            '''
            Запрос = Новый Запрос();
            Результат = Запрос.Выполнить();
            '''
        )

        self.assertEqual(
            filter_tokens(tokens),
            [
                (Token.Name.Variable, 'Запрос'),
                (Token.Operator, '='),
                (Token.Keyword, 'Новый'),
                (Token.Name.Class, 'Запрос'),
                (Token.Punctuation, '('),
                (Token.Punctuation, ')'),
                (Token.Punctuation, ';'),
                (Token.Name.Variable, 'Результат'),
                (Token.Operator, '='),
                (Token.Name.Variable, 'Запрос'),
                (Token.Operator, '.'),
                (Token.Name.Function, 'Выполнить'),
                (Token.Punctuation, '('),
                (Token.Punctuation, ')'),
                (Token.Punctuation, ';'),
            ],
        )

    def test_lexing_execute_nested_string_call(self):
        lexer = lexers.get_lexer_by_name('bsl')
        tokens = lexer.get_tokens(
            '''
            Выполнить("ВыполнитьЗапрос()");
            '''
        )

        self.assertEqual(
            filter_tokens(tokens),
            [
                (Token.Name.Builtin, 'Выполнить'),
                (Token.Punctuation, '('),
                (Token.Literal.String, '"'),
                (Token.Literal.String, 'ВыполнитьЗапрос()'),
                (Token.Literal.String, '"'),
                (Token.Punctuation, ')'),
                (Token.Punctuation, ';'),
            ],
        )

    def test_lexing_execute_select_values(self):
        lexer = lexers.get_lexer_by_name('bsl')
        tokens = lexer.get_tokens(
            '''
            Выполнить("ВыбратьЗначения()");
            '''
        )

        self.assertEqual(
            filter_tokens(tokens),
            [
                (Token.Keyword, 'Выполнить'),
                (Token.Punctuation, '('),
                (Token.Literal.String, '"'),
                (Token.Literal.String, 'ВыбратьЗначения()'),
                (Token.Literal.String, '"'),
                (Token.Punctuation, ')'),
                (Token.Punctuation, ';'),
            ],
        )

    def test_types_from_json_are_builtins(self):
        lexer = lexers.get_lexer_by_name('bsl')
        tokens = lexer.get_tokens(
            '''
            ГруппаФормы = Новый ГруппаФормы;
            ДанныеФормыДерево = Неопределено;
            НастройкиКлиентскогоПриложения();
            '''
        )

        self.assertEqual(
            filter_tokens(tokens),
            [
                (Token.Name.Variable, 'ГруппаФормы'),
                (Token.Operator, '='),
                (Token.Keyword, 'Новый'),
                (Token.Name.Class, 'ГруппаФормы'),
                (Token.Punctuation, ';'),
                (Token.Name.Variable, 'ДанныеФормыДерево'),
                (Token.Operator, '='),
                (Token.Keyword.Constant, 'Неопределено'),
                (Token.Punctuation, ';'),
                (Token.Name.Function, 'НастройкиКлиентскогоПриложения'),
                (Token.Punctuation, '('),
                (Token.Punctuation, ')'),
                (Token.Punctuation, ';'),
            ],
        )

    def test_global_method_from_assets_is_builtin(self):
        lexer = lexers.get_lexer_by_name('bsl')
        tokens = lexer.get_tokens(
            '''
            ВопросАсинх();
            '''
        )

        self.assertEqual(
            filter_tokens(tokens),
            [
                (Token.Name.Builtin, 'ВопросАсинх'),
                (Token.Punctuation, '('),
                (Token.Punctuation, ')'),
                (Token.Punctuation, ';'),
            ],
        )

    def test_lexing_type_literal_and_function(self):
        lexer = lexers.get_lexer_by_name('bsl')

        tokens = lexer.get_tokens(
            '''
            Y = Тип(П);
            '''
        )

        self.assertEqual(
            filter_tokens(tokens),
            [
                (Token.Name.Variable, 'Y'),
                (Token.Operator, '='),
                (Token.Name.Builtin, 'Тип'),
                (Token.Punctuation, '('),
                (Token.Name.Variable, 'П'),
                (Token.Punctuation, ')'),
                (Token.Punctuation, ';'),
            ],
        )

    def test_lexing_logical_and_expression(self):
        lexer = lexers.get_lexer_by_name('bsl')
        tokens = lexer.get_tokens(
            '''
            Рез = (Цена > 0) И (Количество > 0);
            '''
        )

        self.assertEqual(
            filter_tokens(tokens),
            [
                (Token.Name.Variable, 'Рез'),
                (Token.Operator, '='),
                (Token.Punctuation, '('),
                (Token.Name.Variable, 'Цена'),
                (Token.Operator, '>'),
                (Token.Literal.Number, '0'),
                (Token.Punctuation, ')'),
                (Token.Keyword, 'И'),
                (Token.Punctuation, '('),
                (Token.Name.Variable, 'Количество'),
                (Token.Operator, '>'),
                (Token.Literal.Number, '0'),
                (Token.Punctuation, ')'),
                (Token.Punctuation, ';'),
            ],
        )

    def test_lexing_logical_or_expression(self):
        lexer = lexers.get_lexer_by_name('bsl')
        tokens = lexer.get_tokens(
            '''
            Рез = (ЭтоАдмин) Или (ЭтоМенеджер);
            '''
        )

        self.assertEqual(
            filter_tokens(tokens),
            [
                (Token.Name.Variable, 'Рез'),
                (Token.Operator, '='),
                (Token.Punctuation, '('),
                (Token.Name.Variable, 'ЭтоАдмин'),
                (Token.Punctuation, ')'),
                (Token.Keyword, 'Или'),
                (Token.Punctuation, '('),
                (Token.Name.Variable, 'ЭтоМенеджер'),
                (Token.Punctuation, ')'),
                (Token.Punctuation, ';'),
            ],
        )

    def test_lexing_logical_not_expression(self):
        lexer = lexers.get_lexer_by_name('bsl')
        tokens = lexer.get_tokens(
            '''
            Рез = Не (ЭтоАдмин);
            '''
        )

        self.assertEqual(
            filter_tokens(tokens),
            [
                (Token.Name.Variable, 'Рез'),
                (Token.Operator, '='),
                (Token.Keyword, 'Не'),
                (Token.Punctuation, '('),
                (Token.Name.Variable, 'ЭтоАдмин'),
                (Token.Punctuation, ')'),
                (Token.Punctuation, ';'),
            ],
        )

    def test_calling_undefined_is_error(self):
        lexer = lexers.get_lexer_by_name('bsl')
        tokens = lexer.get_tokens(
            '''
            Неопределено(123)
            '''
        )

        self.assertEqual(
            filter_tokens(tokens),
            [
                (Token.Generic.Error, 'Неопределено(123)'),
            ],
        )

    def test_calling_constant_is_error(self):
        lexer = lexers.get_lexer_by_name('bsl')
        tokens = lexer.get_tokens(
            '''
            X = Неопределено(123);
            '''
        )

        self.assertEqual(
            filter_tokens(tokens),
            [
                (Token.Name.Variable, 'X'),
                (Token.Operator, '='),
                (Token.Generic.Error, 'Неопределено(123)'),
                (Token.Punctuation, ';'),
            ],
        )

    def test_calling_null_is_error(self):
        lexer = lexers.get_lexer_by_name('bsl')
        tokens = lexer.get_tokens(
            '''
            X = Null(123);
            '''
        )

        self.assertEqual(
            filter_tokens(tokens),
            [
                (Token.Name.Variable, 'X'),
                (Token.Operator, '='),
                (Token.Generic.Error, 'Null(123)'),
                (Token.Punctuation, ';'),
            ],
        )

    def test_lexing_raise_exception_in_if(self):
        self.assertTokens(
            '''
            Если Сумма <= 0 Тогда
                ВызватьИсключение "Сумма должна быть больше 0";
            КонецЕсли;
            ''',
            [
                (Token.Keyword, 'Если'),
                (Token.Name.Variable, 'Сумма'),
                (Token.Operator, '<='),
                (Token.Literal.Number, '0'),
                (Token.Keyword, 'Тогда'),
                (Token.Name.Exception, 'ВызватьИсключение'),
                (Token.Literal.String, '"'),
                (Token.Literal.String, 'Сумма должна быть больше 0'),
                (Token.Literal.String, '"'),
                (Token.Punctuation, ';'),
                (Token.Keyword, 'КонецЕсли'),
                (Token.Punctuation, ';'),
            ],
        )

    def test_lexing_raise_exception_function_call(self):
        self.assertTokens(
            'ВызватьИсключение("Ошибка на клиенте с категорией", КатегорияОшибки.ОшибкаКонфигурации, "error.client.config", "error.client.config additional info");',
            [
                (Token.Name.Exception, 'ВызватьИсключение'),
                (Token.Punctuation, '('),
                (Token.Literal.String, '"'),
                (Token.Literal.String, 'Ошибка на клиенте с категорией'),
                (Token.Literal.String, '"'),
                (Token.Punctuation, ','),
                (Token.Name.Variable, 'КатегорияОшибки'),
                (Token.Operator, '.'),
                (Token.Name.Variable, 'ОшибкаКонфигурации'),
                (Token.Punctuation, ','),
                (Token.Literal.String, '"'),
                (Token.Literal.String, 'error.client.config'),
                (Token.Literal.String, '"'),
                (Token.Punctuation, ','),
                (Token.Literal.String, '"'),
                (Token.Literal.String, 'error.client.config additional info'),
                (Token.Literal.String, '"'),
                (Token.Punctuation, ')'),
                (Token.Punctuation, ';'),
            ],
        )

    def test_lexing_raise_exception_multiline(self):
        self.assertTokens(
            '''
            ВызватьИсключение(
                "Документ не может быть проведен",
                КатегорияОшибки.ОшибкаКонфигурации,
                "ERR.DOCS.0001",
                "Клиенту запрещена отгрузка"
            );
            ''',
            [
                (Token.Name.Exception, 'ВызватьИсключение'),
                (Token.Punctuation, '('),
                (Token.Literal.String, '"'),
                (Token.Literal.String, 'Документ не может быть проведен'),
                (Token.Literal.String, '"'),
                (Token.Punctuation, ','),
                (Token.Name.Variable, 'КатегорияОшибки'),
                (Token.Operator, '.'),
                (Token.Name.Variable, 'ОшибкаКонфигурации'),
                (Token.Punctuation, ','),
                (Token.Literal.String, '"'),
                (Token.Literal.String, 'ERR.DOCS.0001'),
                (Token.Literal.String, '"'),
                (Token.Punctuation, ','),
                (Token.Literal.String, '"'),
                (Token.Literal.String, 'Клиенту запрещена отгрузка'),
                (Token.Literal.String, '"'),
                (Token.Punctuation, ')'),
                (Token.Punctuation, ';'),
            ],
        )

    def test_lexing_delete_insert_in_code(self):
        self.assertTokens(
            '''
            #Удаление
            Если СтароеУсловие Тогда
            #КонецУдаления
            #Вставка
            НовоеУсловие = Выражение;
            #КонецВставки
            ''',
            [
                (Token.Comment.Preproc, '#Удаление'),
                (Token.Keyword, 'Если'),
                (Token.Name.Variable, 'СтароеУсловие'),
                (Token.Keyword, 'Тогда'),
                (Token.Comment.Preproc, '#КонецУдаления'),
                (Token.Comment.Preproc, '#Вставка'),
                (Token.Name.Variable, 'НовоеУсловие'),
                (Token.Operator, '='),
                (Token.Name.Variable, 'Выражение'),
                (Token.Punctuation, ';'),
                (Token.Comment.Preproc, '#КонецВставки'),
            ],
        )

class BslSdblIntegrationTestCase(LexerTestCase):

    maxDiff = None # if characters too more at assertEqual
    lexer_name = 'bsl'

    def test_sdbl_query_string_pipe_comment_with_quotes(self):
        self.assertTokens(
            '''
ТекстЗапроса =
    "ВЫБРАТЬ
    |// Закомметированная строка внутри запроса с кавычками ""ТЕКСТ""
            ''',
            [
                (Token.Name.Variable, 'ТекстЗапроса'),
                (Token.Operator, '='),
                (Token.Literal.String, '"'),
                (Token.Keyword.Declaration, 'ВЫБРАТЬ'),
                (Token.Literal.String, '|'),
                (Token.Comment.Single, '// Закомметированная строка внутри запроса с кавычками ""ТЕКСТ""'),
            ],
        )

    def test_sdbl_query_string_pipe_comment_with_autoselect(self):
        self.assertTokens(
            '''
ТекстЗапроса =
    "ВЫБРАТЬ
 |//АВТОУПОРЯДОЧИВАНИЕ";
            ''',
            [
                (Token.Name.Variable, 'ТекстЗапроса'),
                (Token.Operator, '='),
                (Token.Literal.String, '"'),
                (Token.Keyword.Declaration, 'ВЫБРАТЬ'),
                (Token.Literal.String, '|'),
                (Token.Comment.Single, '//АВТОУПОРЯДОЧИВАНИЕ'),
                (Token.Literal.String, '"'),
                (Token.Punctuation, ';'),
            ],
        )

    def test_sdbl_query_string_double_slash_literal(self):
        self.assertTokens(
            '''
ТекстЗапроса =
"ВЫБРАТЬ
| Поле
//|//АВТОУПОРЯДОЧИВАНИЕ";
|//АВТОУПОРЯДОЧИВАНИЕ";
            ''',
            [
                (Token.Name.Variable, 'ТекстЗапроса'),
                (Token.Operator, '='),
                (Token.Literal.String, '"'),
                (Token.Keyword.Declaration, 'ВЫБРАТЬ'),
                (Token.Literal.String, '|'),
                (Token.Name.Variable, 'Поле'),
                (Token.Comment.Single, '//|//АВТОУПОРЯДОЧИВАНИЕ";'),
                (Token.Literal.String, '|'),
                (Token.Comment.Single, '//АВТОУПОРЯДОЧИВАНИЕ'),
                (Token.Literal.String, '"'),
                (Token.Punctuation, ';'),
            ],
        )

    def test_constraint_logic_string(self):
        self.assertTokens(
            '''
Ограничение.Текст =
"РазрешитьЧтениеИзменение
|ГДЕ
| ЗначениеРазрешено(Организация)
|И ЗначениеРазрешено(Контрагент)";
            ''',
            [
                (Token.Name.Variable, 'Ограничение'),
                (Token.Operator, '.'),
                (Token.Name.Variable, 'Текст'),
                (Token.Operator, '='),
                (Token.Literal.String, '"'),
                (Token.Keyword.Declaration, 'РазрешитьЧтениеИзменение'),
                (Token.Literal.String, '|'),
                (Token.Keyword.Declaration, 'ГДЕ'),
                (Token.Literal.String, '|'),
                (Token.Name.Builtin, 'ЗначениеРазрешено'),
                (Token.Punctuation, '('),
                (Token.Name.Variable, 'Организация'),
                (Token.Punctuation, ')'),
                (Token.Literal.String, '|'),
                (Token.Operator.Word, 'И'),
                (Token.Name.Builtin, 'ЗначениеРазрешено'),
                (Token.Punctuation, '('),
                (Token.Name.Variable, 'Контрагент'),
                (Token.Punctuation, ')'),
                (Token.Literal.String, '"'),
                (Token.Punctuation, ';'),
            ],
        )


class SdblLexerTestCase(LexerTestCase):

    maxDiff = None # if characters too more at assertEqual
    lexer_name = 'sdbl'

    def test_guess_lexer_for_filename(self):
        with open(os.path.join(CURRENT_DIR, 'examplefiles', 'sdbl', 'samples.sdbl'), 'r', encoding='utf-8') as fh:
            text_sdbl = fh.read()
            guessed_lexer = lexers.guess_lexer_for_filename('samples.sdbl', text_sdbl)
            self.assertEqual(guessed_lexer.name, SdblLexer.name)

    def test_get_lexer_by_name(self):
        lexer = lexers.get_lexer_by_name('sdbl')
        self.assertEqual(lexer.name, SdblLexer.name)

    def test_sdbl_semicolon_is_punctuation(self):
        self.assertTokens(
            '''
ПОМЕСТИТЬ Классификатор
ИЗ
    &Классификатор КАК Параметр
;

////////////////////////////////////////////////////////////////////////////////
ВЫБРАТЬ
            ''',
            [
                (Token.Keyword.Declaration, 'ПОМЕСТИТЬ'),
                (Token.Name.Variable, 'Классификатор'),
                (Token.Keyword.Declaration, 'ИЗ'),
                (Token.Literal.String.Interpol, '&Классификатор'),
                (Token.Keyword.Declaration, 'КАК'),
                (Token.Name.Variable, 'Параметр'),
                (Token.Punctuation, ';'),
                (Token.Comment.Single, '////////////////////////////////////////////////////////////////////////////////'),
                (Token.Keyword.Declaration, 'ВЫБРАТЬ'),
            ],
        )

    def test_sdbl_keyword_of(self):
        self.assertTokens(
            'FOR UPDATE OF',
            [
                (Token.Keyword.Declaration, 'FOR UPDATE'),
                (Token.Keyword.Declaration, 'OF'),
            ],
        )

    def test_sdbl_english_function_aliases(self):
        self.assertTokens(
            '''
LOWER("a") UPPER("b") STRINGLENGTH("c")
TRIMALL("d") TRIML("e") TRIMR("f")
STRFIND("a", "b") STRREPLACE("a", "b", "c")
ROUND(1.2) INT(3.4)
            ''',
            [
                (Token.Name.Builtin, 'LOWER'),
                (Token.Punctuation, '('),
                (Token.Literal.String, '"'),
                (Token.Literal.String, 'a'),
                (Token.Literal.String, '"'),
                (Token.Punctuation, ')'),
                (Token.Name.Builtin, 'UPPER'),
                (Token.Punctuation, '('),
                (Token.Literal.String, '"'),
                (Token.Literal.String, 'b'),
                (Token.Literal.String, '"'),
                (Token.Punctuation, ')'),
                (Token.Name.Builtin, 'STRINGLENGTH'),
                (Token.Punctuation, '('),
                (Token.Literal.String, '"'),
                (Token.Literal.String, 'c'),
                (Token.Literal.String, '"'),
                (Token.Punctuation, ')'),
                (Token.Name.Builtin, 'TRIMALL'),
                (Token.Punctuation, '('),
                (Token.Literal.String, '"'),
                (Token.Literal.String, 'd'),
                (Token.Literal.String, '"'),
                (Token.Punctuation, ')'),
                (Token.Name.Builtin, 'TRIML'),
                (Token.Punctuation, '('),
                (Token.Literal.String, '"'),
                (Token.Literal.String, 'e'),
                (Token.Literal.String, '"'),
                (Token.Punctuation, ')'),
                (Token.Name.Builtin, 'TRIMR'),
                (Token.Punctuation, '('),
                (Token.Literal.String, '"'),
                (Token.Literal.String, 'f'),
                (Token.Literal.String, '"'),
                (Token.Punctuation, ')'),
                (Token.Name.Builtin, 'STRFIND'),
                (Token.Punctuation, '('),
                (Token.Literal.String, '"'),
                (Token.Literal.String, 'a'),
                (Token.Literal.String, '"'),
                (Token.Punctuation, ','),
                (Token.Literal.String, '"'),
                (Token.Literal.String, 'b'),
                (Token.Literal.String, '"'),
                (Token.Punctuation, ')'),
                (Token.Name.Builtin, 'STRREPLACE'),
                (Token.Punctuation, '('),
                (Token.Literal.String, '"'),
                (Token.Literal.String, 'a'),
                (Token.Literal.String, '"'),
                (Token.Punctuation, ','),
                (Token.Literal.String, '"'),
                (Token.Literal.String, 'b'),
                (Token.Literal.String, '"'),
                (Token.Punctuation, ','),
                (Token.Literal.String, '"'),
                (Token.Literal.String, 'c'),
                (Token.Literal.String, '"'),
                (Token.Punctuation, ')'),
                (Token.Name.Builtin, 'ROUND'),
                (Token.Punctuation, '('),
                (Token.Literal.Number, '1.2'),
                (Token.Punctuation, ')'),
                (Token.Name.Builtin, 'INT'),
                (Token.Punctuation, '('),
                (Token.Literal.Number, '3.4'),
                (Token.Punctuation, ')'),
            ],
        )

    def test_sdbl_metadata_roots_english(self):
        lexer = lexers.get_lexer_by_name('sdbl')
        tokens = lexer.get_tokens(
            '''
InformationRegister.Reg.Table
AccumulationRegister.Reg.Table
AccountingRegister.Reg.Table
CalculationRegister.Reg.Table
DocumentJournal.DocJ.Table
FilterCriterion.Crit.Table
Sequence.Seq.Table
Task.Task1.Table
Document.Doc.Table
            '''
        )

        self.assertEqual(
            filter_tokens(tokens),
            [
                (Token.Name.Namespace, 'InformationRegister'),
                (Token.Operator, '.'),
                (Token.Name.Class, 'Reg'),
                (Token.Operator, '.'),
                (Token.Name.Class, 'Table'),
                (Token.Name.Namespace, 'AccumulationRegister'),
                (Token.Operator, '.'),
                (Token.Name.Class, 'Reg'),
                (Token.Operator, '.'),
                (Token.Name.Class, 'Table'),
                (Token.Name.Namespace, 'AccountingRegister'),
                (Token.Operator, '.'),
                (Token.Name.Class, 'Reg'),
                (Token.Operator, '.'),
                (Token.Name.Class, 'Table'),
                (Token.Name.Namespace, 'CalculationRegister'),
                (Token.Operator, '.'),
                (Token.Name.Class, 'Reg'),
                (Token.Operator, '.'),
                (Token.Name.Class, 'Table'),
                (Token.Name.Namespace, 'DocumentJournal'),
                (Token.Operator, '.'),
                (Token.Name.Class, 'DocJ'),
                (Token.Operator, '.'),
                (Token.Name.Class, 'Table'),
                (Token.Name.Namespace, 'FilterCriterion'),
                (Token.Operator, '.'),
                (Token.Name.Class, 'Crit'),
                (Token.Operator, '.'),
                (Token.Name.Class, 'Table'),
                (Token.Name.Namespace, 'Sequence'),
                (Token.Operator, '.'),
                (Token.Name.Class, 'Seq'),
                (Token.Operator, '.'),
                (Token.Name.Class, 'Table'),
                (Token.Name.Namespace, 'Task'),
                (Token.Operator, '.'),
                (Token.Name.Class, 'Task1'),
                (Token.Operator, '.'),
                (Token.Name.Class, 'Table'),
                (Token.Name.Namespace, 'Document'),
                (Token.Operator, '.'),
                (Token.Name.Class, 'Doc'),
                (Token.Operator, '.'),
                (Token.Name.Class, 'Table'),
            ],
        )

    def test_sdbl_metadata_roots_russian(self):
        lexer = lexers.get_lexer_by_name('sdbl')
        tokens = lexer.get_tokens(
            '''
РегистрБухгалтерии.Рег.Таблица
РегистрРасчета.Рег.Таблица
Последовательность.Рег.Таблица
Задача.Рег.Таблица
            '''
        )

        self.assertEqual(
            filter_tokens(tokens),
            [
                (Token.Name.Namespace, 'РегистрБухгалтерии'),
                (Token.Operator, '.'),
                (Token.Name.Class, 'Рег'),
                (Token.Operator, '.'),
                (Token.Name.Class, 'Таблица'),
                (Token.Name.Namespace, 'РегистрРасчета'),
                (Token.Operator, '.'),
                (Token.Name.Class, 'Рег'),
                (Token.Operator, '.'),
                (Token.Name.Class, 'Таблица'),
                (Token.Name.Namespace, 'Последовательность'),
                (Token.Operator, '.'),
                (Token.Name.Class, 'Рег'),
                (Token.Operator, '.'),
                (Token.Name.Class, 'Таблица'),
                (Token.Name.Namespace, 'Задача'),
                (Token.Operator, '.'),
                (Token.Name.Class, 'Рег'),
                (Token.Operator, '.'),
                (Token.Name.Class, 'Таблица'),
            ],
        )

    def test_lexing_constant(self):
        lexer = lexers.get_lexer_by_name('sdbl')
        tokens = lexer.get_tokens(
            '''
    ВЫБРАТЬ
        Неопределено КАК Поле2
            '''
        )

        self.assertEqual(
            filter_tokens(tokens),
            [
                (Token.Keyword.Declaration, 'ВЫБРАТЬ'),
                (Token.Keyword.Constant, 'Неопределено'),
                (Token.Keyword.Declaration, 'КАК'),
                (Token.Name.Variable, 'Поле2'),
            ],
        )

    def test_lexing_multiline_string_with_comment(self):
        lexer = lexers.get_lexer_by_name('sdbl')
        tokens = lexer.get_tokens(
            '''
ВЫБРАТЬ
    "Многострочная
    // это Комментарий
    с экранированной "" кавычкой
    строка" КАК Поле,
            '''
        )

        self.assertEqual(
            filter_tokens(tokens),
            [
                (Token.Keyword.Declaration, 'ВЫБРАТЬ'),
                (Token.Literal.String, '"'),
                (Token.Literal.String, 'Многострочная'),
                (Token.Comment.Single, '// это Комментарий'),
                (Token.Literal.String, 'с экранированной '),
                (Token.Literal.String.Escape, '""'),
                (Token.Literal.String, ' кавычкой'),
                (Token.Literal.String, 'строка'),
                (Token.Literal.String, '"'),
                (Token.Keyword.Declaration, 'КАК'),
                (Token.Name.Variable, 'Поле'),
                (Token.Punctuation, ','),
            ],
        )

    def test_lexing_numbers_and_operators(self):
        lexer = lexers.get_lexer_by_name('sdbl')
        tokens = lexer.get_tokens(
            '''
ВЫБОР КОГДА НЕ 0 = 0 * 1 ТОГДА ИСТИНА ИНАЧЕ ЛОЖЬ КОНЕЦ КАК Условие,
            '''
        )

        self.assertEqual(
            filter_tokens(tokens),
            [
                (Token.Keyword.Declaration, 'ВЫБОР'),
                (Token.Keyword.Declaration, 'КОГДА'),
                (Token.Operator.Word, 'НЕ'),
                (Token.Literal.Number, '0'),
                (Token.Operator, '='),
                (Token.Literal.Number, '0'),
                (Token.Operator, '*'),
                (Token.Literal.Number, '1'),
                (Token.Keyword.Declaration, 'ТОГДА'),
                (Token.Keyword.Constant, 'ИСТИНА'),
                (Token.Keyword.Declaration, 'ИНАЧЕ'),
                (Token.Keyword.Constant, 'ЛОЖЬ'),
                (Token.Keyword.Declaration, 'КОНЕЦ'),
                (Token.Keyword.Declaration, 'КАК'),
                (Token.Name.Variable, 'Условие'),
                (Token.Punctuation, ','),
            ],
        )

    def test_sdbl_choice_operator(self):
        lexer = lexers.get_lexer_by_name('sdbl')
        tokens = lexer.get_tokens(
            '''
ВЫБОР
    КОГДА Поле = ИСТИНА ТОГДА "Это"
    ИНАЧЕ "Не Задана"
КОНЕЦ Цена
            '''
        )

        self.assertEqual(
            filter_tokens(tokens),
            [
                (Token.Keyword.Declaration, 'ВЫБОР'),
                (Token.Keyword.Declaration, 'КОГДА'),
                (Token.Name.Variable, 'Поле'),
                (Token.Operator, '='),
                (Token.Keyword.Constant, 'ИСТИНА'),
                (Token.Keyword.Declaration, 'ТОГДА'),
                (Token.Literal.String, '"'),
                (Token.Literal.String, 'Это'),
                (Token.Literal.String, '"'),
                (Token.Keyword.Declaration, 'ИНАЧЕ'),
                (Token.Literal.String, '"'),
                (Token.Literal.String, 'Не Задана'),
                (Token.Literal.String, '"'),
                (Token.Keyword.Declaration, 'КОНЕЦ'),
                (Token.Name.Variable, 'Цена'),
            ],
        )

    def test_sdbl_type_cast_operator(self):
        lexer = lexers.get_lexer_by_name('sdbl')
        tokens = lexer.get_tokens(
            '''
ВЫРАЗИТЬ(Поле КАК ЧИСЛО(10, 2)) КАК ЧислоПоля,
ВЫРАЗИТЬ(Поле КАК СТРОКА(20)) КАК СтрокаПоля,
ВЫРАЗИТЬ(Поле КАК БУЛЕВО) КАК БулевоПоля,
ВЫРАЗИТЬ(Поле КАК ДАТА) КАК ДатаПоля
            '''
        )

        self.assertEqual(
            filter_tokens(tokens),
            [
                (Token.Name.Builtin, 'ВЫРАЗИТЬ'),
                (Token.Punctuation, '('),
                (Token.Name.Variable, 'Поле'),
                (Token.Keyword.Declaration, 'КАК'),
                (Token.Name.Class, 'ЧИСЛО'),
                (Token.Punctuation, '('),
                (Token.Literal.Number, '10'),
                (Token.Punctuation, ','),
                (Token.Literal.Number, '2'),
                (Token.Punctuation, ')'),
                (Token.Punctuation, ')'),
                (Token.Keyword.Declaration, 'КАК'),
                (Token.Name.Variable, 'ЧислоПоля'),
                (Token.Punctuation, ','),
                (Token.Name.Builtin, 'ВЫРАЗИТЬ'),
                (Token.Punctuation, '('),
                (Token.Name.Variable, 'Поле'),
                (Token.Keyword.Declaration, 'КАК'),
                (Token.Name.Class, 'СТРОКА'),
                (Token.Punctuation, '('),
                (Token.Literal.Number, '20'),
                (Token.Punctuation, ')'),
                (Token.Punctuation, ')'),
                (Token.Keyword.Declaration, 'КАК'),
                (Token.Name.Variable, 'СтрокаПоля'),
                (Token.Punctuation, ','),
                (Token.Name.Builtin, 'ВЫРАЗИТЬ'),
                (Token.Punctuation, '('),
                (Token.Name.Variable, 'Поле'),
                (Token.Keyword.Declaration, 'КАК'),
                (Token.Name.Class, 'БУЛЕВО'),
                (Token.Punctuation, ')'),
                (Token.Keyword.Declaration, 'КАК'),
                (Token.Name.Variable, 'БулевоПоля'),
                (Token.Punctuation, ','),
                (Token.Name.Builtin, 'ВЫРАЗИТЬ'),
                (Token.Punctuation, '('),
                (Token.Name.Variable, 'Поле'),
                (Token.Keyword.Declaration, 'КАК'),
                (Token.Name.Class, 'ДАТА'),
                (Token.Punctuation, ')'),
                (Token.Keyword.Declaration, 'КАК'),
                (Token.Name.Variable, 'ДатаПоля'),
            ],
        )

    def test_lexing_functions_and_numbers(self):
        lexer = lexers.get_lexer_by_name('sdbl')
        tokens = lexer.get_tokens(
            '''
ГОД(ДАТАВРЕМЯ(1, 1, 1)) КАК Функция,
ВЫРАЗИТЬ(0 КАК Число) КАК Выражение,
            '''
        )

        self.assertEqual(
            filter_tokens(tokens),
            [
                (Token.Name.Builtin, 'ГОД'),
                (Token.Punctuation, '('),
                (Token.Name.Builtin, 'ДАТАВРЕМЯ'),
                (Token.Punctuation, '('),
                (Token.Literal.Number, '1'),
                (Token.Punctuation, ','),
                (Token.Literal.Number, '1'),
                (Token.Punctuation, ','),
                (Token.Literal.Number, '1'),
                (Token.Punctuation, ')'),
                (Token.Punctuation, ')'),
                (Token.Keyword.Declaration, 'КАК'),
                (Token.Name.Variable, 'Функция'),
                (Token.Punctuation, ','),
                (Token.Name.Builtin, 'ВЫРАЗИТЬ'),
                (Token.Punctuation, '('),
                (Token.Literal.Number, '0'),
                (Token.Keyword.Declaration, 'КАК'),
                (Token.Name.Class, 'Число'),
                (Token.Punctuation, ')'),
                (Token.Keyword.Declaration, 'КАК'),
                (Token.Name.Variable, 'Выражение'),
                (Token.Punctuation, ','),
            ],
        )

    def test_sdbl_functions_are_builtin(self):
        lexer = lexers.get_lexer_by_name('sdbl')
        tokens = lexer.get_tokens(
            '''
АВТОНОМЕРЗАПИСИ() РАЗНОСТЬДАТ(ДАТА(), ДАТАВРЕМЯ(1,1,1)) ИНДЕКСИРОВАТЬ ПО НАБОРАМ Таблица
INDEX BY SETS Table
ПОДСТРОКА("abc",1,2) СУММА(1) КОЛИЧЕСТВО(*) ОКР(1.23,2) ЕСТЬNULL(Поле,0) СГРУППИРОВАНОПО(Поле) РАЗМЕРХРАНИМЫХДАННЫХ(Поле) УНИКАЛЬНЫЙИДЕНТИФИКАТОР(Поле)
            '''
        )

        self.assertEqual(
            filter_tokens(tokens),
            [
                (Token.Name.Builtin, 'АВТОНОМЕРЗАПИСИ'),
                (Token.Punctuation, '('),
                (Token.Punctuation, ')'),
                (Token.Name.Builtin, 'РАЗНОСТЬДАТ'),
                (Token.Punctuation, '('),
                (Token.Name.Builtin, 'ДАТА'),
                (Token.Punctuation, '('),
                (Token.Punctuation, ')'),
                (Token.Punctuation, ','),
                (Token.Name.Builtin, 'ДАТАВРЕМЯ'),
                (Token.Punctuation, '('),
                (Token.Literal.Number, '1'),
                (Token.Punctuation, ','),
                (Token.Literal.Number, '1'),
                (Token.Punctuation, ','),
                (Token.Literal.Number, '1'),
                (Token.Punctuation, ')'),
                (Token.Punctuation, ')'),
                (Token.Keyword.Declaration, 'ИНДЕКСИРОВАТЬ ПО НАБОРАМ'),
                (Token.Name.Variable, 'Таблица'),
                (Token.Keyword.Declaration, 'INDEX BY SETS'),
                (Token.Name.Variable, 'Table'),
                (Token.Name.Builtin, 'ПОДСТРОКА'),
                (Token.Punctuation, '('),
                (Token.Literal.String, '"'),
                (Token.Literal.String, 'abc'),
                (Token.Literal.String, '"'),
                (Token.Punctuation, ','),
                (Token.Literal.Number, '1'),
                (Token.Punctuation, ','),
                (Token.Literal.Number, '2'),
                (Token.Punctuation, ')'),
                (Token.Name.Builtin, 'СУММА'),
                (Token.Punctuation, '('),
                (Token.Literal.Number, '1'),
                (Token.Punctuation, ')'),
                (Token.Name.Builtin, 'КОЛИЧЕСТВО'),
                (Token.Punctuation, '('),
                (Token.Operator, '*'),
                (Token.Punctuation, ')'),
                (Token.Name.Builtin, 'ОКР'),
                (Token.Punctuation, '('),
                (Token.Literal.Number, '1.23'),
                (Token.Punctuation, ','),
                (Token.Literal.Number, '2'),
                (Token.Punctuation, ')'),
                (Token.Name.Builtin, 'ЕСТЬNULL'),
                (Token.Punctuation, '('),
                (Token.Name.Variable, 'Поле'),
                (Token.Punctuation, ','),
                (Token.Literal.Number, '0'),
                (Token.Punctuation, ')'),
                (Token.Name.Builtin, 'СГРУППИРОВАНОПО'),
                (Token.Punctuation, '('),
                (Token.Name.Variable, 'Поле'),
                (Token.Punctuation, ')'),
                (Token.Name.Builtin, 'РАЗМЕРХРАНИМЫХДАННЫХ'),
                (Token.Punctuation, '('),
                (Token.Name.Variable, 'Поле'),
                (Token.Punctuation, ')'),
                (Token.Name.Builtin, 'УНИКАЛЬНЫЙИДЕНТИФИКАТОР'),
                (Token.Punctuation, '('),
                (Token.Name.Variable, 'Поле'),
                (Token.Punctuation, ')'),
            ],
        )

    def test_sdbl_aggregate_functions(self):
        lexer = lexers.get_lexer_by_name('sdbl')
        tokens = lexer.get_tokens(
            '''
ВЫБРАТЬ
   Накладная.Номенклатура.Наименование,
   СУММА (Накладная.Сумма) КАК Сумма,
   СРЕДНЕЕ (Накладная.Сумма) КАК Среднее,
   МАКСИМУМ (Накладная.Сумма) КАК Максимум,
   МИНИМУМ (Накладная.Сумма) КАК Минимум,
   КОЛИЧЕСТВО (Накладная.Сумма) КАК Колич,
   КОЛИЧЕСТВО (РАЗЛИЧНЫЕ Накладная.Сумма) КАК КоличРазл,
   КОЛИЧЕСТВО (*) КАК КоличВсе
ИЗ
   Документ.РасходнаяНакладная.Состав КАК Накладная
СГРУППИРОВАТЬ ПО
   Накладная.Номенклатура
ИТОГИ ОБЩИЕ
            '''
        )

        self.assertEqual(
            filter_tokens(tokens),
            [
                (Token.Keyword.Declaration, 'ВЫБРАТЬ'),
                (Token.Name.Variable, 'Накладная'),
                (Token.Operator, '.'),
                (Token.Name.Variable, 'Номенклатура'),
                (Token.Operator, '.'),
                (Token.Name.Variable, 'Наименование'),
                (Token.Punctuation, ','),
                (Token.Name.Builtin, 'СУММА'),
                (Token.Punctuation, '('),
                (Token.Name.Variable, 'Накладная'),
                (Token.Operator, '.'),
                (Token.Name.Variable, 'Сумма'),
                (Token.Punctuation, ')'),
                (Token.Keyword.Declaration, 'КАК'),
                (Token.Name.Variable, 'Сумма'),
                (Token.Punctuation, ','),
                (Token.Name.Builtin, 'СРЕДНЕЕ'),
                (Token.Punctuation, '('),
                (Token.Name.Variable, 'Накладная'),
                (Token.Operator, '.'),
                (Token.Name.Variable, 'Сумма'),
                (Token.Punctuation, ')'),
                (Token.Keyword.Declaration, 'КАК'),
                (Token.Name.Variable, 'Среднее'),
                (Token.Punctuation, ','),
                (Token.Name.Builtin, 'МАКСИМУМ'),
                (Token.Punctuation, '('),
                (Token.Name.Variable, 'Накладная'),
                (Token.Operator, '.'),
                (Token.Name.Variable, 'Сумма'),
                (Token.Punctuation, ')'),
                (Token.Keyword.Declaration, 'КАК'),
                (Token.Name.Variable, 'Максимум'),
                (Token.Punctuation, ','),
                (Token.Name.Builtin, 'МИНИМУМ'),
                (Token.Punctuation, '('),
                (Token.Name.Variable, 'Накладная'),
                (Token.Operator, '.'),
                (Token.Name.Variable, 'Сумма'),
                (Token.Punctuation, ')'),
                (Token.Keyword.Declaration, 'КАК'),
                (Token.Name.Variable, 'Минимум'),
                (Token.Punctuation, ','),
                (Token.Name.Builtin, 'КОЛИЧЕСТВО'),
                (Token.Punctuation, '('),
                (Token.Name.Variable, 'Накладная'),
                (Token.Operator, '.'),
                (Token.Name.Variable, 'Сумма'),
                (Token.Punctuation, ')'),
                (Token.Keyword.Declaration, 'КАК'),
                (Token.Name.Variable, 'Колич'),
                (Token.Punctuation, ','),
                (Token.Name.Builtin, 'КОЛИЧЕСТВО'),
                (Token.Punctuation, '('),
                (Token.Keyword.Declaration, 'РАЗЛИЧНЫЕ'),
                (Token.Name.Variable, 'Накладная'),
                (Token.Operator, '.'),
                (Token.Name.Variable, 'Сумма'),
                (Token.Punctuation, ')'),
                (Token.Keyword.Declaration, 'КАК'),
                (Token.Name.Variable, 'КоличРазл'),
                (Token.Punctuation, ','),
                (Token.Name.Builtin, 'КОЛИЧЕСТВО'),
                (Token.Punctuation, '('),
                (Token.Operator, '*'),
                (Token.Punctuation, ')'),
                (Token.Keyword.Declaration, 'КАК'),
                (Token.Name.Variable, 'КоличВсе'),
                (Token.Keyword.Declaration, 'ИЗ'),
                (Token.Name.Namespace, 'Документ'),
                (Token.Operator, '.'),
                (Token.Name.Class, 'РасходнаяНакладная'),
                (Token.Operator, '.'),
                (Token.Name.Class, 'Состав'),
                (Token.Keyword.Declaration, 'КАК'),
                (Token.Name.Variable, 'Накладная'),
                (Token.Keyword.Declaration, 'СГРУППИРОВАТЬ ПО'),
                (Token.Name.Variable, 'Накладная'),
                (Token.Operator, '.'),
                (Token.Name.Variable, 'Номенклатура'),
                (Token.Keyword.Declaration, 'ИТОГИ'),
                (Token.Keyword.Declaration, 'ОБЩИЕ'),
            ],
        )

    def test_sdbl_external_datasource_dimension_table(self):
        lexer = lexers.get_lexer_by_name('sdbl')
        tokens = lexer.get_tokens(
            '''
ВЫБРАТЬ * 
ИЗ ВнешнийИсточникДанных.MyDS.Куб.MyCube.ТаблицаИзмерения.MyTable
ИЗ ExternalDataSource.MyDS.Cube.MyCube.DimensionTable.MyTable
            '''
        )

        self.assertEqual(
            filter_tokens(tokens),
            [
                (Token.Keyword.Declaration, 'ВЫБРАТЬ'),
                (Token.Operator, '*'),
                (Token.Keyword.Declaration, 'ИЗ'),
                (Token.Name.Namespace, 'ВнешнийИсточникДанных'),
                (Token.Operator, '.'),
                (Token.Name.Class, 'MyDS'),
                (Token.Operator, '.'),
                (Token.Name.Class, 'Куб'),
                (Token.Operator, '.'),
                (Token.Name.Class, 'MyCube'),
                (Token.Operator, '.'),
                (Token.Name.Class, 'ТаблицаИзмерения'),
                (Token.Operator, '.'),
                (Token.Name.Class, 'MyTable'),
                (Token.Keyword.Declaration, 'ИЗ'),
                (Token.Name.Namespace, 'ExternalDataSource'),
                (Token.Operator, '.'),
                (Token.Name.Class, 'MyDS'),
                (Token.Operator, '.'),
                (Token.Name.Class, 'Cube'),
                (Token.Operator, '.'),
                (Token.Name.Class, 'MyCube'),
                (Token.Operator, '.'),
                (Token.Name.Class, 'DimensionTable'),
                (Token.Operator, '.'),
                (Token.Name.Class, 'MyTable'),
            ],
        )

    def test_sdbl_external_datasource_invalid_segments(self):
        lexer = lexers.get_lexer_by_name('sdbl')
        tokens = lexer.get_tokens(
            '''
ВЫБРАТЬ * 
ИЗ ВнешнийИсточникДанных.123.Куб.!bad.ТаблицаИзмерения.#badTable
ИЗ ExternalDataSource.123.Cube.!bad.DimensionTable.#badTable
            '''
        )

        self.assertEqual(
            filter_tokens(tokens),
            [
                (Token.Keyword.Declaration, 'ВЫБРАТЬ'),
                (Token.Operator, '*'),
                (Token.Keyword.Declaration, 'ИЗ'),
                (Token.Name.Namespace, 'ВнешнийИсточникДанных'),
                (Token.Operator, '.'),
                (Token.Generic.Error, '123'),
                (Token.Operator, '.'),
                (Token.Name.Variable, 'Куб'),
                (Token.Operator, '.'),
                (Token.Generic.Error, '!bad'),
                (Token.Operator, '.'),
                (Token.Name.Variable, 'ТаблицаИзмерения'),
                (Token.Operator, '.'),
                (Token.Generic.Error, '#badTable'),
                (Token.Keyword.Declaration, 'ИЗ'),
                (Token.Name.Namespace, 'ExternalDataSource'),
                (Token.Operator, '.'),
                (Token.Generic.Error, '123'),
                (Token.Operator, '.'),
                (Token.Name.Variable, 'Cube'),
                (Token.Operator, '.'),
                (Token.Generic.Error, '!bad'),
                (Token.Operator, '.'),
                (Token.Name.Variable, 'DimensionTable'),
                (Token.Operator, '.'),
                (Token.Generic.Error, '#badTable'),
            ],
        )

    def test_sdbl_hash_table_name_is_error(self):
        lexer = lexers.get_lexer_by_name('sdbl')
        tokens = lexer.get_tokens('ВЫБРАТЬ * ИЗ #ИмяТаблицыПланаОбмена')

        self.assertEqual(
            filter_tokens(tokens),
            [
                (Token.Keyword.Declaration, 'ВЫБРАТЬ'),
                (Token.Operator, '*'),
                (Token.Keyword.Declaration, 'ИЗ'),
                (Token.Generic.Error, '#ИмяТаблицыПланаОбмена'),
            ],
        )

    def test_sdbl_simple_catalog(self):
        lexer = lexers.get_lexer_by_name('sdbl')
        tokens = lexer.get_tokens('ВЫБРАТЬ * ИЗ Справочник.Номенклатура')

        self.assertEqual(
            filter_tokens(tokens),
            [
                (Token.Keyword.Declaration, 'ВЫБРАТЬ'),
                (Token.Operator, '*'),
                (Token.Keyword.Declaration, 'ИЗ'),
                (Token.Name.Namespace, 'Справочник'),
                (Token.Operator, '.'),
                (Token.Name.Class, 'Номенклатура'),
            ],
        )

    def test_sdbl_register_slice_first(self):
        lexer = lexers.get_lexer_by_name('sdbl')
        tokens = lexer.get_tokens(
            '''
ВЫБРАТЬ * ИЗ РегистрСведений.КурсВал.СрезПервых(&ПараметрДата, 
    Валюта = &ПараметрВалюта)
            '''
        )

        self.assertEqual(
            filter_tokens(tokens),
            [
                (Token.Keyword.Declaration, 'ВЫБРАТЬ'),
                (Token.Operator, '*'),
                (Token.Keyword.Declaration, 'ИЗ'),
                (Token.Name.Class, 'РегистрСведений'),
                (Token.Operator, '.'),
                (Token.Name.Class, 'КурсВал'),
                (Token.Operator, '.'),
                (Token.Name.Function, 'СрезПервых'),
                (Token.Punctuation, '('),
                (Token.Literal.String.Interpol, '&ПараметрДата'),
                (Token.Punctuation, ','),
                (Token.Name.Variable, 'Валюта'),
                (Token.Operator, '='),
                (Token.Literal.String.Interpol, '&ПараметрВалюта'),
                (Token.Punctuation, ')'),
            ],
        )

    def test_sdbl_accumulation_register_query(self):
        lexer = lexers.get_lexer_by_name('sdbl')
        tokens = lexer.get_tokens(
            '''
ВЫБРАТЬ * ИЗ РегистрНакопления.УчетНоменклатуры.ОстаткиИОбороты(&НачПериода, 
    &КонПериода, , Склад = &ПараметрСклад)
            '''
        )

        self.assertEqual(
            filter_tokens(tokens),
            [
                (Token.Keyword.Declaration, 'ВЫБРАТЬ'),
                (Token.Operator, '*'),
                (Token.Keyword.Declaration, 'ИЗ'),
                (Token.Name.Namespace, 'РегистрНакопления'),
                (Token.Operator, '.'),
                (Token.Name.Class, 'УчетНоменклатуры'),
                (Token.Operator, '.'),
                (Token.Name.Function, 'ОстаткиИОбороты'),
                (Token.Punctuation, '('),
                (Token.Literal.String.Interpol, '&НачПериода'),
                (Token.Punctuation, ','),
                (Token.Literal.String.Interpol, '&КонПериода'),
                (Token.Punctuation, ','),
                (Token.Punctuation, ','),
                (Token.Name.Variable, 'Склад'),
                (Token.Operator, '='),
                (Token.Literal.String.Interpol, '&ПараметрСклад'),
                (Token.Punctuation, ')'),
            ],
        )

    def test_sdbl_binary_and_logical_operators(self):
        lexer = lexers.get_lexer_by_name('sdbl')
        tokens = lexer.get_tokens(
            '''
ВЫБРАТЬ
    1 + 2 - 3 * 4 / 5 КАК Арифметика,
    "A" + "B" КАК Строки
ГДЕ
    Поле > 0
    И Поле < 10
    И Поле МЕЖДУ 1 И 5
    И Поле ПОДОБНО "%стр%"
    И Поле В ИЕРАРХИИ ДругаяТаблица
    И Поле В (1,2,3)
    И Поле = NULL
    И Поле ЕСТЬ NULL
    И Поле ССЫЛКА Справочник.Номенклатура
            '''
        )

        self.assertEqual(
            filter_tokens(tokens),
            [
                (Token.Keyword.Declaration, 'ВЫБРАТЬ'),
                (Token.Literal.Number, '1'),
                (Token.Operator, '+'),
                (Token.Literal.Number, '2'),
                (Token.Operator, '-'),
                (Token.Literal.Number, '3'),
                (Token.Operator, '*'),
                (Token.Literal.Number, '4'),
                (Token.Operator, '/'),
                (Token.Literal.Number, '5'),
                (Token.Keyword.Declaration, 'КАК'),
                (Token.Name.Variable, 'Арифметика'),
                (Token.Punctuation, ','),
                (Token.Literal.String, '"'),
                (Token.Literal.String, 'A'),
                (Token.Literal.String, '"'),
                (Token.Operator, '+'),
                (Token.Literal.String, '"'),
                (Token.Literal.String, 'B'),
                (Token.Literal.String, '"'),
                (Token.Keyword.Declaration, 'КАК'),
                (Token.Name.Variable, 'Строки'),
                (Token.Keyword.Declaration, 'ГДЕ'),
                (Token.Name.Variable, 'Поле'),
                (Token.Operator, '>'),
                (Token.Literal.Number, '0'),
                (Token.Operator.Word, 'И'),
                (Token.Name.Variable, 'Поле'),
                (Token.Operator, '<'),
                (Token.Literal.Number, '10'),
                (Token.Operator.Word, 'И'),
                (Token.Name.Variable, 'Поле'),
                (Token.Operator.Word, 'МЕЖДУ'),
                (Token.Literal.Number, '1'),
                (Token.Operator.Word, 'И'),
                (Token.Literal.Number, '5'),
                (Token.Operator.Word, 'И'),
                (Token.Name.Variable, 'Поле'),
                (Token.Operator.Word, 'ПОДОБНО'),
                (Token.Literal.String, '"'),
                (Token.Literal.String, '%стр%'),
                (Token.Literal.String, '"'),
                (Token.Operator.Word, 'И'),
                (Token.Name.Variable, 'Поле'),
                (Token.Operator.Word, 'В'),
                (Token.Operator.Word, 'ИЕРАРХИИ'),
                (Token.Name.Variable, 'ДругаяТаблица'),
                (Token.Operator.Word, 'И'),
                (Token.Name.Variable, 'Поле'),
                (Token.Operator.Word, 'В'),
                (Token.Punctuation, '('),
                (Token.Literal.Number, '1'),
                (Token.Punctuation, ','),
                (Token.Literal.Number, '2'),
                (Token.Punctuation, ','),
                (Token.Literal.Number, '3'),
                (Token.Punctuation, ')'),
                (Token.Operator.Word, 'И'),
                (Token.Name.Variable, 'Поле'),
                (Token.Operator, '='),
                (Token.Keyword.Constant, 'NULL'),
                (Token.Operator.Word, 'И'),
                (Token.Name.Variable, 'Поле'),
                (Token.Operator.Word, 'ЕСТЬ'),
                (Token.Keyword.Constant, 'NULL'),
                (Token.Operator.Word, 'И'),
                (Token.Name.Variable, 'Поле'),
                (Token.Name.Variable, 'ССЫЛКА'),
                (Token.Name.Namespace, 'Справочник'),
                (Token.Operator, '.'),
                (Token.Name.Class, 'Номенклатура'),
            ],
        )

    def test_sdbl_select03_sample(self):
        lexer = lexers.get_lexer_by_name('sdbl')
        tokens = lexer.get_tokens(
            '''
ВЫБРАТЬ
    Изменения.ВидСогласования,
    Изменения.КоличествоЧасовСогласования,
    Изменения.КоличествоДнейСогласования,
    ТИПЗНАЧЕНИЯ(Изменения.ПустаяСсылка) КАК ТипСсылки
ПОМЕСТИТЬ ВТСрокиСогласования
ИЗ
    РегистрСведений.успСрокиСогласования КАК Изменения
            '''
        )

        self.assertEqual(
            filter_tokens(tokens),
            [
                (Token.Keyword.Declaration, 'ВЫБРАТЬ'),
                (Token.Keyword.Declaration, 'Изменения'),
                (Token.Operator, '.'),
                (Token.Name.Variable, 'ВидСогласования'),
                (Token.Punctuation, ','),
                (Token.Keyword.Declaration, 'Изменения'),
                (Token.Operator, '.'),
                (Token.Name.Variable, 'КоличествоЧасовСогласования'),
                (Token.Punctuation, ','),
                (Token.Keyword.Declaration, 'Изменения'),
                (Token.Operator, '.'),
                (Token.Name.Variable, 'КоличествоДнейСогласования'),
                (Token.Punctuation, ','),
                (Token.Name.Builtin, 'ТИПЗНАЧЕНИЯ'),
                (Token.Punctuation, '('),
                (Token.Keyword.Declaration, 'Изменения'),
                (Token.Operator, '.'),
                (Token.Name.Variable, 'ПустаяСсылка'),
                (Token.Punctuation, ')'),
                (Token.Keyword.Declaration, 'КАК'),
                (Token.Name.Variable, 'ТипСсылки'),
                (Token.Keyword.Declaration, 'ПОМЕСТИТЬ'),
                (Token.Name.Variable, 'ВТСрокиСогласования'),
                (Token.Keyword.Declaration, 'ИЗ'),
                (Token.Name.Namespace, 'РегистрСведений'),
                (Token.Operator, '.'),
                (Token.Name.Class, 'успСрокиСогласования'),
                (Token.Keyword.Declaration, 'КАК'),
                (Token.Keyword.Declaration, 'Изменения'),
            ],
        )

    def test_sdbl_class_name_is_class(self):
        lexer = lexers.get_lexer_by_name('sdbl')
        tokens = lexer.get_tokens('ВЫБРАТЬ * ИЗ РегистрСведений.КурсВал.СрезПервых()')

        self.assertEqual(
            filter_tokens(tokens),
            [
                (Token.Keyword.Declaration, 'ВЫБРАТЬ'),
                (Token.Operator, '*'),
                (Token.Keyword.Declaration, 'ИЗ'),
                (Token.Name.Namespace, 'РегистрСведений'),
                (Token.Operator, '.'),
                (Token.Name.Class, 'КурсВал'),
                (Token.Operator, '.'),
                (Token.Name.Function, 'СрезПервых'),
                (Token.Punctuation, '('),
                (Token.Punctuation, ')'),
            ],
        )

    def test_sdbl_case_expression_and_cast(self):
        lexer = lexers.get_lexer_by_name('sdbl')
        tokens = lexer.get_tokens(
            '''
ВЫБРАТЬ
    ВЫБОР
       КОГДА Цена > 1000 ТОГДА "1000 -"
       КОГДА Цена > 100 ТОГДА "100 - 1000"
    ИНАЧЕ "Не Задана"
    КОНЕЦ КАК ЦенаКатегория,
    ВЫРАЗИТЬ(Поле КАК ЧИСЛО(10,2)) КАК ЧислоПоля
ИЗ Таблица
            '''
        )

        self.assertEqual(
            filter_tokens(tokens),
            [
                (Token.Keyword.Declaration, 'ВЫБРАТЬ'),
                (Token.Keyword.Declaration, 'ВЫБОР'),
                (Token.Keyword.Declaration, 'КОГДА'),
                (Token.Name.Variable, 'Цена'),
                (Token.Operator, '>'),
                (Token.Literal.Number, '1000'),
                (Token.Keyword.Declaration, 'ТОГДА'),
                (Token.Literal.String, '"'),
                (Token.Literal.String, '1000 -'),
                (Token.Literal.String, '"'),
                (Token.Keyword.Declaration, 'КОГДА'),
                (Token.Name.Variable, 'Цена'),
                (Token.Operator, '>'),
                (Token.Literal.Number, '100'),
                (Token.Keyword.Declaration, 'ТОГДА'),
                (Token.Literal.String, '"'),
                (Token.Literal.String, '100 - 1000'),
                (Token.Literal.String, '"'),
                (Token.Keyword.Declaration, 'ИНАЧЕ'),
                (Token.Literal.String, '"'),
                (Token.Literal.String, 'Не Задана'),
                (Token.Literal.String, '"'),
                (Token.Keyword.Declaration, 'КОНЕЦ'),
                (Token.Keyword.Declaration, 'КАК'),
                (Token.Name.Variable, 'ЦенаКатегория'),
                (Token.Punctuation, ','),
                (Token.Name.Builtin, 'ВЫРАЗИТЬ'),
                (Token.Punctuation, '('),
                (Token.Name.Variable, 'Поле'),
                (Token.Keyword.Declaration, 'КАК'),
                (Token.Name.Class, 'ЧИСЛО'),
                (Token.Punctuation, '('),
                (Token.Literal.Number, '10'),
                (Token.Punctuation, ','),
                (Token.Literal.Number, '2'),
                (Token.Punctuation, ')'),
                (Token.Punctuation, ')'),
                (Token.Keyword.Declaration, 'КАК'),
                (Token.Name.Variable, 'ЧислоПоля'),
                (Token.Keyword.Declaration, 'ИЗ'),
                (Token.Name.Variable, 'Таблица'),
            ],
        )

    def test_like_and_escape(self):
        lexer = lexers.get_lexer_by_name('sdbl')
        tokens = lexer.get_tokens(
            '''
Номенклатура.Наименование ПОДОБНО &Шаблон СПЕЦСИМВОЛ "~"
            '''
        )

        self.assertEqual(
            filter_tokens(tokens),
            [
                (Token.Name.Variable, 'Номенклатура'),
                (Token.Operator, '.'),
                (Token.Name.Variable, 'Наименование'),
                (Token.Operator.Word, 'ПОДОБНО'),
                (Token.Literal.String.Interpol, '&Шаблон'),
                (Token.Keyword.Declaration, 'СПЕЦСИМВОЛ'),
                (Token.Literal.String, '"'),
                (Token.Literal.String, '~'),
                (Token.Literal.String, '"'),
            ],
        )

    def test_line_continuation_pipe_in_sdbl(self):
        lexer = lexers.get_lexer_by_name('sdbl')
        tokens = lexer.get_tokens(
            '''
|   Таблица.Ссылка КАК Ссылка
|   Таблица.Контрагент КАК Контрагент
            '''
        )

        self.assertEqual(
            filter_tokens(tokens),
            [
                (Token.Generic.Error, '|'),
                (Token.Name.Variable, 'Таблица'),
                (Token.Operator, '.'),
                (Token.Name.Variable, 'Ссылка'),
                (Token.Keyword.Declaration, 'КАК'),
                (Token.Name.Variable, 'Ссылка'),
                (Token.Generic.Error, '|'),
                (Token.Name.Variable, 'Таблица'),
                (Token.Operator, '.'),
                (Token.Name.Variable, 'Контрагент'),
                (Token.Keyword.Declaration, 'КАК'),
                (Token.Name.Variable, 'Контрагент'),
            ],
        )

    def test_sdbl_pipe_comment_with_quotes(self):
        lexer = lexers.get_lexer_by_name('sdbl')
        tokens = lexer.get_tokens(
            '''
|// Закомметированная строка внутри запроса с кавычками ""ТЕКСТ""
            '''
        )

        self.assertEqual(
            filter_tokens(tokens),
            [
                (Token.Generic.Error, '|'),
                (Token.Comment.Single, '// Закомметированная строка внутри запроса с кавычками ""ТЕКСТ""'),
            ],
        )
