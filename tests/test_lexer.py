import os
import re
from unittest import TestCase

from pygments import lexers
from pygments.token import Token

from pygments_bsl import lexer as lexer_mod
from pygments_bsl.lexer import BSLLexer

# from tokens_bsl import TOKENS as expected_tokens_bsl
# from tokens_os import TOKENS as expected_tokens_os

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))

lexer = lexers.load_lexer_from_file(lexer_mod.__file__, "BSLLexer")

with open(os.path.join(CURRENT_DIR, "samples.bsl"), "r") as fh:
    text_bsl = fh.read()

with open(os.path.join(CURRENT_DIR, "samples.os"), "r") as fh:
    text_os = fh.read()

class BslLexerTestCase(TestCase):

    maxDiff = None # if characters too more at assertEqual

    def __filter_tokens(self, tokens):
        space = re.compile("[ \n]+")
        return [i for i in tokens if not space.match(i[1]) and not i[1] == ""]

    def test_guess_lexer_for_filename(self):
        guessed_lexer = lexers.guess_lexer_for_filename("samples.bsl", text_bsl)
        self.assertEqual(guessed_lexer.name, BSLLexer.name)

        guessed_lexer = lexers.guess_lexer_for_filename("samples.os", text_os)
        self.assertEqual(guessed_lexer.name, BSLLexer.name)

    def test_get_lexer_by_name(self):
        lexer = lexers.get_lexer_by_name("bsl")
        self.assertEqual(lexer.name, BSLLexer.name)

        lexer = lexers.get_lexer_by_name("os")
        self.assertEqual(lexer.name, BSLLexer.name)

    # TODO Global test for samples
    # disabled because too difficult to support
    
    # def test_get_tokens_one(self):
    #     lexer = lexers.get_lexer_by_name("bsl")
    #     tokens = lexer.get_tokens(text_bsl)
    #     self.assertEqual([i for i in tokens], expected_tokens_bsl)
    
    # def test_get_tokens_one(self):
    #     lexer = lexers.get_lexer_by_name("os")
    #     tokens = lexer.get_tokens(text_os)
    #     self.assertEqual([i for i in tokens], expected_tokens_os)
    
    def test_lexing_region(self):
        lexer = lexers.get_lexer_by_name("bsl")
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
                (Token.Keyword.Declaration, "#Область ИмяОбласти"),
                (Token.Comment.Singleline, '// это комментарий\n'),
                (Token.Keyword.Declaration, "#КонецОбласти"),
            ],
        )
    
    def test_lexing_variable_declaration(self):
        lexer = lexers.get_lexer_by_name("bsl")
        tokens = lexer.get_tokens(
            '''
            Перем А Экспорт;
            '''
        )

        self.assertEqual(
            self.__filter_tokens(tokens),
            [
                (Token.Keyword, "Перем"),
                (Token.Name.Variable, "А"),
                (Token.Keyword, "Экспорт"),
                (Token.Punctuation, ";"),
            ],
        )

    def test_lexing_variable_declaration_multi(self):
        lexer = lexers.get_lexer_by_name("bsl")
        tokens = lexer.get_tokens(
            '''
            Перем А, Б;
            '''
        )

        self.assertEqual(
            self.__filter_tokens(tokens),
            [
                (Token.Keyword, "Перем"),
                (Token.Name.Variable, "А"),
                (Token.Punctuation, ','),
                (Token.Name.Variable, 'Б'),
                (Token.Punctuation, ";"),
            ],
        )

    def test_lexing_variable_declaration_multi_export_first(self):
        lexer = lexers.get_lexer_by_name("bsl")
        tokens = lexer.get_tokens(
            '''
            Перем А Экспорт, Б;
            '''
        )

        self.assertEqual(
            self.__filter_tokens(tokens),
            [
                (Token.Keyword, "Перем"),
                (Token.Name.Variable, "А"),
                (Token.Keyword, "Экспорт"),
                (Token.Punctuation, ','),
                (Token.Name.Variable, 'Б'),
                (Token.Punctuation, ";"),
            ],
        )
    
    def test_lexing_variable_declaration_multi_export_second(self):
        lexer = lexers.get_lexer_by_name("bsl")
        tokens = lexer.get_tokens(
            '''
            Перем А, Б Экспорт;
            '''
        )

        self.assertEqual(
            self.__filter_tokens(tokens),
            [
                (Token.Keyword, "Перем"),
                (Token.Name.Variable, "А"),
                (Token.Punctuation, ','),
                (Token.Name.Variable, 'Б'),
                (Token.Keyword, "Экспорт"),
                (Token.Punctuation, ";"),
            ],
        )

    def test_lexing_variable_declaration_multi_export_both(self):
        lexer = lexers.get_lexer_by_name("bsl")
        tokens = lexer.get_tokens(
            '''
            Перем А Экспорт, Б Экспорт;
            '''
        )

        self.assertEqual(
            self.__filter_tokens(tokens),
            [
                (Token.Keyword, "Перем"),
                (Token.Name.Variable, "А"),
                (Token.Keyword, "Экспорт"),
                (Token.Punctuation, ','),
                (Token.Name.Variable, 'Б'),
                (Token.Keyword, "Экспорт"),
                (Token.Punctuation, ";"),
            ],
        )

    def test_lexing_inline_comment(self):
        lexer = lexers.get_lexer_by_name("bsl")
        tokens = lexer.get_tokens(
            '''
            Перем ДиалогРаботыСКаталогом;     // Диалог работы с каталогом
            '''
        )

        self.assertEqual(
            self.__filter_tokens(tokens),
            [
                (Token.Keyword, "Перем"),
                (Token.Name.Variable, "ДиалогРаботыСКаталогом"),
                (Token.Punctuation, ";"),
                (Token.Comment.Singleline, '// Диалог работы с каталогом\n'),
            ],
        )

    def test_lexing_preprocessor(self):
        lexer = lexers.get_lexer_by_name("bsl")
        tokens = lexer.get_tokens(
            '''
            #Если Сервер Тогда;
            // это комментарий
            #КонецЕсли
            '''
        )

        self.assertEqual(
            self.__filter_tokens(tokens),
            [
                (Token.Keyword.Declaration, "#Если Сервер Тогда;"),
                (Token.Comment.Singleline, '// это комментарий\n'),
                (Token.Keyword.Declaration, "#КонецЕсли"),
            ],
        )

    def test_lexing_annotation(self):
        lexer = lexers.get_lexer_by_name("bsl")
        tokens = lexer.get_tokens(
            '''
            &НаСервере;
            '''
        )

        self.assertEqual(
            self.__filter_tokens(tokens),
            [
                (Token.Keyword.Declaration, "&НаСервере;"),
            ],
        )

    def test_lexing_procedure_declaration(self):
        lexer = lexers.get_lexer_by_name("bsl")
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
                (Token.Keyword, "Процедура"),
                (Token.Name.Function, "НевстроеннаяПроцедура"),
                (Token.Punctuation, '('),
                (Token.Punctuation, ')'),
                (Token.Keyword, "Возврат"),
                (Token.Punctuation, ';'),
                (Token.Keyword, "КонецПроцедуры"),
            ],
        )

    def test_lexing_procedure_declaration_with_annotation(self):
        lexer = lexers.get_lexer_by_name("bsl")
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
                (Token.Keyword.Declaration, '&Перед("ПередЗаписью")'),
                (Token.Keyword, "Процедура"),
                (Token.Name.Function, "Расш1_ПередЗаписью"),
                (Token.Punctuation, '('),
                (Token.Punctuation, ')'),
                (Token.Keyword, "КонецПроцедуры"),
            ],
        )

    def test_lexing_procedure_declaration_with_param(self):
        lexer = lexers.get_lexer_by_name("bsl")
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
                (Token.Keyword, "Процедура"),
                (Token.Name.Function, "ИмяПроцедуры"),
                (Token.Punctuation, '('),
                (Token.Keyword, 'Знач'),
                (Token.Name.Variable, 'ПараметрСКонстантой'), # <- Error? Token.Name.Variable.Instance
                (Token.Punctuation, ','),
                (Token.Name.Variable, 'ОбычныйПараметр'), # <- Error? Token.Name.Variable.Instance
                (Token.Punctuation, ','),
                (Token.Name.Variable, 'ПараметрСНекорректнымЗначением'), # <- Error? Token.Name.Variable.Instance
                (Token.Operator, '='),
                (Token.Name.Variable, 'Нелегальщина'), # <- Error? Token.Error
                (Token.Punctuation, ','),
                (Token.Name.Variable, 'ПараметрСНекорректнымЗначением'), # <- Error? Token.Name.Variable.Instance
                (Token.Operator, '='),
                (Token.Name.Variable, 'НелегальщинаБезПробела'), # <- Error? Token.Error
                (Token.Punctuation, ','),
                (Token.Name.Variable, 'ПараметрСДефолтнымЧисловымЗначением'), # <- Error? Token.Name.Variable.Instance
                (Token.Operator, '='),
                (Token.Literal.Number, '0'),
                (Token.Punctuation, ')'),
                (Token.Keyword, 'Экспорт'),
            ],
        )

    def test_lexing_text_with_quoted(self):
        lexer = lexers.get_lexer_by_name("bsl")
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
                (Token.Literal.String, '"текст с экраннированной "'),
                (Token.Literal.String, '" кавычкой"'), # <- Error?
                (Token.Operator, '+'),
                (Token.Literal.String, '"и конкатенаций"'),
                (Token.Literal.String, '""'), # <- Error?
                (Token.Punctuation, ';'),
            ],
        )

    def test_lexing_text_multiline(self):
        lexer = lexers.get_lexer_by_name("bsl")
        tokens = lexer.get_tokens(
            '''
            В = "многострочная
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
                (Token.Literal.String, '"многострочная'),
                (Token.Literal.String, '|строка'),
                (Token.Comment.Singleline, '//|это комментарий\n'),
                (Token.Literal.String, '|// а это нет'),
                (Token.Literal.String, '|"'),
                (Token.Punctuation, ';'),
            ],
        )

    def test_lexing_text_with_keyword(self):
        lexer = lexers.get_lexer_by_name("bsl")
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
                (Token.Literal.String, '"Some selected text"'),
                (Token.Punctuation, ';'),
            ],
        )

    def test_lexing_number(self):
        lexer = lexers.get_lexer_by_name("bsl")
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
                (Token.Literal.Number, '0.0'), # <- Error? Token.Name.Float
                (Token.Operator, '*'),
                (Token.Literal.Number, '100'), # <- Error? Token.Name.Integer
                (Token.Punctuation, ';'),
            ],
        )


    def test_lexing_date(self):
        lexer = lexers.get_lexer_by_name("bsl")
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
        lexer = lexers.get_lexer_by_name("bsl")
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
        lexer = lexers.get_lexer_by_name("bsl")
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
        lexer = lexers.get_lexer_by_name("bsl")
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
        lexer = lexers.get_lexer_by_name("bsl")
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
                (Token.Literal.String, '''"Литерал типа Дата: '00010101'"'''),
                (Token.Punctuation, ';'),
            ],
        )

    def test_lexing_if_else(self):
        lexer = lexers.get_lexer_by_name("bsl")
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
                (Token.Operator, '<'), # <- Error! Should be '<='
                (Token.Operator, '='), # <- But don`t metter for highliting
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
        lexer = lexers.get_lexer_by_name("bsl")
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
        lexer = lexers.get_lexer_by_name("bsl")
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
        lexer = lexers.get_lexer_by_name("bsl")
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
        lexer = lexers.get_lexer_by_name("bsl")
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
        lexer = lexers.get_lexer_by_name("bsl")
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
                (Token.Name.Variable, 'ТаблицаЗначений'), # <- Error? Token.Keyword.Type
                (Token.Punctuation, ';'),
            ],
        )

    def test_lexing_call_new_function(self):
        lexer = lexers.get_lexer_by_name("bsl")
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
                (Token.Literal.String, '"ТаблицаЗначений"'),
                (Token.Punctuation, ')'),
                (Token.Punctuation, ';'),
            ],
        )

    def test_lexing_internal_function_in_variable_name(self):
        lexer = lexers.get_lexer_by_name("bsl")
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
                (Token.Literal.String, '""'),
                (Token.Punctuation, ';'),
            ],
        )

    def test_lexing_internal_function_in_fluent_chain_call(self):
        lexer = lexers.get_lexer_by_name("bsl")
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
        lexer = lexers.get_lexer_by_name("bsl")
        tokens = lexer.get_tokens(
            '''
            Справочники.ИмяСправочника.СоздатьЭлемент();
            '''
        )

        self.assertEqual(
            self.__filter_tokens(tokens),
            [
                (Token.Class, 'Справочники'),
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
        lexer = lexers.get_lexer_by_name("bsl")
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
                (Token.Class, 'ХранилищеПользовательскихНастроекДинамическихСписков'),
                (Token.Operator, '.'),
                (Token.Name.Function, 'Сохранить'),
                (Token.Punctuation, '('),
                (Token.Punctuation, ')'),
                (Token.Punctuation, ';')
            ],
        )

    def test_lexing_variable_assignment_with_compare(self):
        lexer = lexers.get_lexer_by_name("bsl")
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
        lexer = lexers.get_lexer_by_name("bsl")
        tokens = lexer.get_tokens(
            '''
            ~Метка:
            Перейти ~Метка;
            '''
        )

        self.assertEqual(
            self.__filter_tokens(tokens),
            [
                (Token.Token.Label, '~Метка:'),
                (Token.Keyword, 'Перейти'),
                (Token.Label, '~Метка;')
            ],
        )

    def test_lexing_single_word_highlighting(self):
        lexer = lexers.get_lexer_by_name("bsl")
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