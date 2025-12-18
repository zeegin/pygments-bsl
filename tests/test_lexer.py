import os
import re
from unittest import TestCase

from pygments import lexers
from pygments.token import Token

# from pygments_bsl import lexer as lexer_mod
from pygments_bsl.lexer import BslLexer, SdblLexer

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))

class BslLexerTestCase(TestCase):

    maxDiff = None # if characters too more at assertEqual

    def __filter_tokens(self, tokens):
        space = re.compile('^[ \n]+$')
        return [i for i in tokens if not space.match(i[1]) and not i[1] == '']

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
        lexer = lexers.get_lexer_by_name('bsl')
        tokens = lexer.get_tokens(
            '''
            #Область ИмяОбласти
            // это комментарий
            #КонецОбласти
            '''
        )

        self.assertEqual(
            self.__filter_tokens(tokens),
            [
                (Token.Comment.Preproc, '#Область ИмяОбласти'),
                (Token.Comment.Single, '// это комментарий'),
                (Token.Comment.Preproc, '#КонецОбласти'),
            ],
        )

    def test_lexing_preproc_if_chain(self):
        lexer = lexers.get_lexer_by_name('bsl')
        tokens = lexer.get_tokens(
            '''
#Если Сервер Тогда
#ИначеЕсли Клиент Тогда
#Иначе
#КонецЕсли
            '''
        )

        self.assertEqual(
            self.__filter_tokens(tokens),
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
        lexer = lexers.get_lexer_by_name('bsl')
        tokens = lexer.get_tokens(
            '''
#Если Сервер Или ТолстыйКлиентОбычноеПриложение И НЕ ВнешнееСоединение Тогда
#КонецЕсли
            '''
        )

        self.assertEqual(
            self.__filter_tokens(tokens),
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

    def test_lexing_preproc_insert_and_delete_blocks(self):
        lexer = lexers.get_lexer_by_name('bsl')
        tokens = lexer.get_tokens(
            '''
#Вставка
Процедура ДобавитьКод() КонецПроцедуры
#КонецВставки
#Удаление
Функция Устаревшая() КонецФункции
#КонецУдаления
            '''
        )

        self.assertEqual(
            self.__filter_tokens(tokens),
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

    def test_lexing_variable_declaration(self):
        lexer = lexers.get_lexer_by_name('bsl')
        tokens = lexer.get_tokens(
            '''
            Перем А Экспорт;
            '''
        )

        self.assertEqual(
            self.__filter_tokens(tokens),
            [
                (Token.Keyword.Declaration, 'Перем'),
                (Token.Name.Variable, 'А'),
                (Token.Keyword, 'Экспорт'),
                (Token.Punctuation, ';'),
            ],
        )

    def test_lexing_variable_declaration_multi(self):
        lexer = lexers.get_lexer_by_name('bsl')
        tokens = lexer.get_tokens(
            '''
            Перем А, Б;
            '''
        )

        self.assertEqual(
            self.__filter_tokens(tokens),
            [
                (Token.Keyword.Declaration, 'Перем'),
                (Token.Name.Variable, 'А'),
                (Token.Punctuation, ','),
                (Token.Name.Variable, 'Б'),
                (Token.Punctuation, ';'),
            ],
        )

    def test_lexing_variable_declaration_multi_export_first(self):
        lexer = lexers.get_lexer_by_name('bsl')
        tokens = lexer.get_tokens(
            '''
            Перем А Экспорт, Б;
            '''
        )

        self.assertEqual(
            self.__filter_tokens(tokens),
            [
                (Token.Keyword.Declaration, 'Перем'),
                (Token.Name.Variable, 'А'),
                (Token.Keyword, 'Экспорт'),
                (Token.Punctuation, ','),
                (Token.Name.Variable, 'Б'),
                (Token.Punctuation, ';'),
            ],
        )
    
    def test_lexing_variable_declaration_multi_export_second(self):
        lexer = lexers.get_lexer_by_name('bsl')
        tokens = lexer.get_tokens(
            '''
            Перем А, Б Экспорт;
            '''
        )

        self.assertEqual(
            self.__filter_tokens(tokens),
            [
                (Token.Keyword.Declaration, 'Перем'),
                (Token.Name.Variable, 'А'),
                (Token.Punctuation, ','),
                (Token.Name.Variable, 'Б'),
                (Token.Keyword, 'Экспорт'),
                (Token.Punctuation, ';'),
            ],
        )

    def test_lexing_variable_declaration_multi_export_both(self):
        lexer = lexers.get_lexer_by_name('bsl')
        tokens = lexer.get_tokens(
            '''
            Перем А Экспорт, Б Экспорт;
            '''
        )

        self.assertEqual(
            self.__filter_tokens(tokens),
            [
                (Token.Keyword.Declaration, 'Перем'),
                (Token.Name.Variable, 'А'),
                (Token.Keyword, 'Экспорт'),
                (Token.Punctuation, ','),
                (Token.Name.Variable, 'Б'),
                (Token.Keyword, 'Экспорт'),
                (Token.Punctuation, ';'),
            ],
        )

    def test_lexing_inline_comment(self):
        lexer = lexers.get_lexer_by_name('bsl')
        tokens = lexer.get_tokens(
            '''
            Перем ДиалогРаботыСКаталогом;     // Диалог работы с каталогом
            '''
        )

        self.assertEqual(
            self.__filter_tokens(tokens),
            [
                (Token.Keyword.Declaration, 'Перем'),
                (Token.Name.Variable, 'ДиалогРаботыСКаталогом'),
                (Token.Punctuation, ';'),
                (Token.Comment.Single, '// Диалог работы с каталогом'),
            ],
        )

    def test_lexing_preprocessor(self):
        lexer = lexers.get_lexer_by_name('bsl')
        tokens = lexer.get_tokens(
            '''
            #Если Сервер Тогда
            // это комментарий
            #КонецЕсли
            '''
        )

        self.assertEqual(
            self.__filter_tokens(tokens),
            [
                (Token.Comment.Preproc, '#Если'),
                (Token.Keyword.Constant, 'Сервер'),
                (Token.Comment.Preproc, 'Тогда'),
                (Token.Comment.Single, '// это комментарий'),
                (Token.Comment.Preproc, '#КонецЕсли'),
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
            self.__filter_tokens(tokens),
            [
                (Token.Name.Decorator, '&НаСервере;'),
            ],
        )

    def test_decorator_split_name_inside(self):
        """Desired display: '&Перед' as Token.Name.Decorator, parentheses as punctuation,
        and the inner name as Token.Name.Function (no quotes)"""
        lexer = lexers.get_lexer_by_name('bsl')
        tokens = lexer.get_tokens('&Перед("НазваниеМетода");')

        self.assertEqual(
            self.__filter_tokens(tokens),
            [
                (Token.Name.Decorator, '&Перед'),
                (Token.Punctuation, '('),
                (Token.Name.Function, 'НазваниеМетода'),
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
            self.__filter_tokens(tokens),
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
            self.__filter_tokens(tokens),
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
            self.__filter_tokens(tokens),
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
            self.__filter_tokens(tokens),
            [
                (Token.Name.Decorator, '&Перед'),
                (Token.Punctuation, '('),
                (Token.Name.Function, 'ПередЗаписью'),
                (Token.Punctuation, ')'),
                (Token.Keyword, 'Процедура'),
                (Token.Name.Function, 'Расш1_ПередЗаписью'),
                (Token.Punctuation, '('),
                (Token.Punctuation, ')'),
                (Token.Keyword, 'КонецПроцедуры'),
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
            self.__filter_tokens(tokens),
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
                (Token.Generic.Error, 'Нелегальщина'), # Token.Generic.Error
                (Token.Punctuation, ','),
                (Token.Name.Variable, 'ПараметрСНекорректнымЗначением'),
                (Token.Operator, '='),
                (Token.Generic.Error, 'НелегальщинаБезПробела'), # Token.Generic.Error
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
            self.__filter_tokens(tokens),
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
            self.__filter_tokens(tokens),
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
            self.__filter_tokens(tokens),
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
            self.__filter_tokens(tokens),
            [
                (Token.Name.Variable, 'Строка'),
                (Token.Operator, '='),
                (Token.Literal.String, '"'),
                (Token.Literal.String, 'Кефир 15'),
                (Token.Literal.String, '%'),
                (Token.Literal.String, ' жирности'),
                (Token.Literal.String, '"'),
                (Token.Punctuation, ';')
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
            self.__filter_tokens(tokens),
            [
                (Token.Name.Variable, 'СтрокаСоСловомВыбрать'),
                (Token.Operator, '='),
                (Token.Literal.String, '"'),
                (Token.Literal.String, 'Some selected text'),
                (Token.Literal.String, '"'),
                (Token.Punctuation, ';'),
            ],
        )

    def test_lexing_number(self):
        lexer = lexers.get_lexer_by_name('bsl')
        tokens = lexer.get_tokens(
            '''
            Число = 0.0 * 100;
            '''
        )

        self.assertEqual(
            self.__filter_tokens(tokens),
            [
                (Token.Name.Variable, 'Число'),
                (Token.Operator, '='),
                (Token.Literal.Number, '0.0'),
                (Token.Operator, '*'),
                (Token.Literal.Number, '100'),
                (Token.Punctuation, ';'),
            ],
        )


    def test_lexing_date(self):
        lexer = lexers.get_lexer_by_name('bsl')
        tokens = lexer.get_tokens(
            '''
            Дата = '00010101000000';
            '''
        )

        self.assertEqual(
            self.__filter_tokens(tokens),
            [
                (Token.Name.Variable, 'Дата'),
                (Token.Operator, '='),
                (Token.Literal.Date, "'00010101000000'"),
                (Token.Punctuation, ';'),
            ],
        )


    def test_lexing_date_short(self):
        lexer = lexers.get_lexer_by_name('bsl')
        tokens = lexer.get_tokens(
            '''
            КороткаяДата = '00010101';
            '''
        )

        self.assertEqual(
            self.__filter_tokens(tokens),
            [
                (Token.Name.Variable, 'КороткаяДата'),
                (Token.Operator, '='),
                (Token.Literal.Date, "'00010101'"),
                (Token.Punctuation, ';'),
            ],
        )

    def test_lexing_date_with_separators(self):
        lexer = lexers.get_lexer_by_name('bsl')
        tokens = lexer.get_tokens(
            '''
            ДатаСРазделителями = '0001-01-01T00:00:00';
            '''
        )

        self.assertEqual(
            self.__filter_tokens(tokens),
            [
                (Token.Name.Variable, 'ДатаСРазделителями'),
                (Token.Operator, '='),
                (Token.Literal.Date, "'0001-01-01T00:00:00'"),
                (Token.Punctuation, ';'),
            ],
        )

    def test_lexing_date_short_with_separators(self):
        lexer = lexers.get_lexer_by_name('bsl')
        tokens = lexer.get_tokens(
            '''
            КороткаяДатаСРазделителями = '0001/01/01';
            '''
        )

        self.assertEqual(
            self.__filter_tokens(tokens),
            [
                (Token.Name.Variable, 'КороткаяДатаСРазделителями'),
                (Token.Operator, '='),
                (Token.Literal.Date, "'0001/01/01'"),
                (Token.Punctuation, ';'),
            ],
        )


    def test_lexing_date_in_string(self):
        lexer = lexers.get_lexer_by_name('bsl')
        tokens = lexer.get_tokens(
            '''
            СтрокаСДатойВнутри = "Литерал типа Дата: '00010101'";
            '''
        )

        self.assertEqual(
            self.__filter_tokens(tokens),
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
            self.__filter_tokens(tokens),
            [
                (Token.Keyword, 'Если'),
                (Token.Name.Variable, 'А'),
                (Token.Operator, '='),
                (Token.Literal.Number, '0'),
                (Token.Keyword, 'И'), # <- Error? Token.Operator.Word
                (Token.Keyword, 'НЕ'), # <- Error? Token.Operator.Word
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
            self.__filter_tokens(tokens),
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
            self.__filter_tokens(tokens),
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
            self.__filter_tokens(tokens),
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
        lexer = lexers.get_lexer_by_name('bsl')
        tokens = lexer.get_tokens(
            '''
            СтрДлина();
            СтрДлина ();
            '''
        )

        self.assertEqual(
            self.__filter_tokens(tokens),
            [
                (Token.Name.Builtin, 'СтрДлина'),
                (Token.Punctuation, '('),
                (Token.Punctuation, ')'),
                (Token.Punctuation, ';'),
                (Token.Name.Builtin, 'СтрДлина'),
                (Token.Punctuation, '('),
                (Token.Punctuation, ')'),
                (Token.Punctuation, ';'),
            ],
        )

    def test_lexing_call_new(self):
        lexer = lexers.get_lexer_by_name('bsl')
        tokens = lexer.get_tokens(
            '''
            НовыйОбъект = Новый ТаблицаЗначений;
            '''
        )

        self.assertEqual(
            self.__filter_tokens(tokens),
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
            self.__filter_tokens(tokens),
            [
                (Token.Name.Variable, 'НовыйОбъект'),
                (Token.Operator, '='),
                (Token.Name.Builtin, 'Новый'),
                (Token.Punctuation, '('),
                (Token.Literal.String, '"'),
                (Token.Literal.String, 'ТаблицаЗначений'),
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
            self.__filter_tokens(tokens),
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
            self.__filter_tokens(tokens),
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
            self.__filter_tokens(tokens),
            [
                (Token.Name.Class, 'Справочники'),
                (Token.Operator, '.'),
                (Token.Name.Variable, 'ИмяСправочника'),
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
            self.__filter_tokens(tokens),
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
            self.__filter_tokens(tokens),
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
            self.__filter_tokens(tokens),
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
            self.__filter_tokens(tokens),
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
            self.__filter_tokens(tokens),
            [
                (Token.Name.Variable, 'ПараметрСНекорректнымЗначением'),
                (Token.Operator, '='),
                (Token.Name.Variable, 'Нелегальщина'), # Token.Generic.Error
                (Token.Punctuation, ','),
                (Token.Name.Variable, 'ПараметрСНекорректнымЗначением'),
                (Token.Operator, '='),
                (Token.Name.Variable, 'НелегальщинаБезПробела'), # Token.Generic.Error
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
            self.__filter_tokens(tokens),
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

    def test_lexing_execute_algorithm(self):
        lexer = lexers.get_lexer_by_name('bsl')
        tokens = lexer.get_tokens(
            '''
            Выполнить Алгоритм;
            '''
        )

        self.assertEqual(
            self.__filter_tokens(tokens),
            [
                (Token.Keyword, 'Выполнить'),
                (Token.Name.Variable, 'Алгоритм'),
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
            self.__filter_tokens(tokens),
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
            self.__filter_tokens(tokens),
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
            self.__filter_tokens(tokens),
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
            self.__filter_tokens(tokens),
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
            self.__filter_tokens(tokens),
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
            self.__filter_tokens(tokens),
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
            self.__filter_tokens(tokens),
            [
                (Token.Name.Variable, 'X'),
                (Token.Operator, '='),
                (Token.Generic.Error, 'Null(123)'),
                (Token.Punctuation, ';'),
            ],
        )

    def test_lexing_raise_exception_in_if(self):
        lexer = lexers.get_lexer_by_name('bsl')
        tokens = lexer.get_tokens(
            '''
            Если Сумма <= 0 Тогда
                ВызватьИсключение "Сумма должна быть больше 0";
            КонецЕсли;
            '''
        )
    def test_lexing_raise_exception_function_call(self):
        self.assertEqual(
            self.__filter_tokens(tokens),
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
        lexer = lexers.get_lexer_by_name('bsl')
        tokens = lexer.get_tokens('ВызватьИсключение("Ошибка на клиенте с категорией", КатегорияОшибки.ОшибкаКонфигурации, "error.client.config", "error.client.config additional info");')

        self.assertEqual(
            self.__filter_tokens(tokens),
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
        


class SdblLexerTestCase(TestCase):

    maxDiff = None # if characters too more at assertEqual

    def __filter_tokens(self, tokens):
        space = re.compile('^[ \n]+$')
        return [i for i in tokens if not space.match(i[1]) and not i[1] == '']


    def test_guess_lexer_for_filename(self):
        with open(os.path.join(CURRENT_DIR, 'examplefiles', 'sdbl', 'samples.sdbl'), 'r', encoding='utf-8') as fh:
            text_sdbl = fh.read()
            guessed_lexer = lexers.guess_lexer_for_filename('samples.sdbl', text_sdbl)
            self.assertEqual(guessed_lexer.name, SdblLexer.name)

    def test_get_lexer_by_name(self):
        lexer = lexers.get_lexer_by_name('sdbl')
        self.assertEqual(lexer.name, SdblLexer.name)


    def test_lexing_constant(self):
        lexer = lexers.get_lexer_by_name('sdbl')
        tokens = lexer.get_tokens(
            '''
    ВЫБРАТЬ
        Неопределено КАК Поле2
            '''
        )

        self.assertEqual(
            self.__filter_tokens(tokens),
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
            self.__filter_tokens(tokens),
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
