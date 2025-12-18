# Большой тест

## BSL

```bsl
// SYNTAX TEST "source.bsl"
#Область ИмяОбласти
// <- Token.Comment.Preproc
// ^ Token.Comment.Preproc
//       ^ Token.Comment.Preproc

Перем А Экспорт;
// <- Token.Keyword.Declaration
//    ^ Token.Name.Variable
//      ^ Token.Keyword

Перем А, Б;
//     ^ Token.Operator
//       ^ Token.Name.Variable

Перем А Экспорт, Б;
//    ^ Token.Name.Variable
//       ^ Token.Keyword
//             ^ Token.Operator
//               ^ Token.Name.Variable

Перем А, Б Экспорт;
//    ^ Token.Name.Variable
//     ^ Token.Operator
//       ^ Token.Name.Variable
//         ^ Token.Keyword

Перем А Экспорт, Б Экспорт;
//    ^ Token.Name.Variable
//       ^ Token.Keyword
//             ^ Token.Operator
//               ^ Token.Name.Variable
//                 ^ Token.Keyword

#Если Сервер Тогда
// <- Token.Comment.Preproc
//    ^^^^^^ Token.Comment.Preproc

// Комментарий процедуры
// <- Token.Comment.Single
&НаСервере
// <- Token.Name.Decorator
// ^ Token.Name.Decorator
Процедура ИмяПроцедуры(
// <- Token.Keyword
//        ^ Token.Name.Function
//                    ^ Token.Punctuation
    Знач ПараметрСКонстантой,
//  ^ Token.Keyword
//       ^ Token.Name.Variable
//                          ^ Token.Operator
    ОбычныйПараметр,
//  ^ Token.Name.Variable
    ПараметрСНекорректнымЗначением = Нелегальщина,
//                                  ^ Token.Generic.Error
    ПараметрСНекорректнымЗначением =НелегальщинаБезПробела,
//                                  ^ Token.Generic.Error
//                                                        ^ Token.Operator
    ПараметрСДефолтнымЧисловымЗначением = 0) Экспорт
//                                      ^ Token.Operator
//                                        ^ Token.Literal.Number
//                                         ^ Token.Punctuation
//                                           ^ Token.Keyword
    Б = "текст с экраннированной "" кавычкой" + "и конкатенаций""";
//       ^ Token.String
//                               ^^ Token.String.Escape
//                                              ^ Token.String
//                                                             ^^ Token.String.Escape
//                                                                ^ Token.Operator

    В = "многострочная
//      ^ Token.Literal.String
    |строка
//  ^ Token.Literal.String
    //|это комментарий
//      ^ Token.Comment.Single
    |// а это нет
//      ^ Token.Literal.String
    |";
//   ^ Token.Literal.String
//    ^ Token.Punctuation

    Г = "";
//      ^^ Token.Literal.String

    ТекстЗапроса =
    "ВЫБРАТЬ
//  ^^ Token.Literal.String
//   ^ Token.Keyword
    |	Таблица.Поле КАК Поле,
    |	МАКСИМУМ(Таблица.Поле2) КАК Поле2
    |ИЗ
    |	Таблица КАК Таблица
    |ГДЕ
    |	Таблица.Поле = 0
    |	И Таблица.Поле <> ""Строка""
    |	И ВЫРАЗИТЬ(Таблица.Поле КАК СТРОКА) <> """"
    |	И Таблица.Поле <> ""Строка с экраннированной """" кавычкой""
    //|Закомментированная строка
//  ^ Token.Literal.String Token.Comment.Single
    |// Закомметированная строка внутри запроса с кавычками ""ТЕКСТ""
//  ^ Token.Literal.String
//  ^ not:Token.Comment.Single
//   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ Token.Comment.Single
    |СГРУППИРОВАТЬ ПО
    |	Поле
    //|//АВТОУПОРЯДОЧИВАНИЕ";
//  ^^^^^^^^^^^^^^^^^^^^^^^^^ Token.Comment.Single
    |//АВТОУПОРЯДОЧИВАНИЕ";
//  ^^^^^^^^^^^^^^^^^^^^^^ Token.Literal.String
//  ^ not:Token.Comment.Single
//   ^^^^^^^^^^^^^^^^^^^^ Token.Comment.Single
//                       ^ not:Token.Comment.Single
//                        ^ Token.Operator

    // Проверка на корректность обработки FirstLineMatch и #include: source.sdbl
    СтрокаСоСловомВыбрать = "Some selected text";
//                                ^^^^^^ not:Token.Keyword

    Число = 0.0 * 100;
//  ^ Token.Name.Variable
//          ^^^ Token.Number
//              ^ Token.Operator

    Дата = '00010101000000';
//         ^^^^^^^^^^^^^^^^ Token.Literal.Date
    КороткаяДата = '00010101';
//                 ^^^^^^^^^^ Token.Literal.Date
    ДатаСРазделителями = '0001-01-01T00:00:00';
//                       ^^^^^^^^^^^^^^^^^^^^^ Token.Literal.Date
    КороткаяДатаСРазделителями = '0001/01/01';
//                               ^^^^^^^^^^^^ Token.Literal.Date
    СтрокаСДатойВнутри = "Литерал типа Дата: '00010101'";
//                                          ^^^^^^^^^^^^ Token.Literal.String
//                                           ^^^^^^^^^^ not:Token.Literal.Date

    Если А = 0 И НЕ Число <= 0 Тогда
//  ^ Token.Keyword
//         ^ Token.Operator
//           ^ Token.Literal.Number
//             ^ Token.Keyword
//               ^^ Token.Keyword
//                        ^^ Token.Operator
//                             ^ Token.Keyword

        ОбычныйПараметр = Истина;
//                        ^ Token.Keyword.Constant
    Иначе
//  ^ Token.Keyword
        ОбычныйПараметр = Ложь
    КонецЕсли;
//  ^ Token.Keyword

    Пока ЗначениеЗаполнено(Б) Цикл
//  ^ Token.Keyword
//       ^ Token.Name.Builtin
//                        ^ Token.Punctuation
//                          ^ Token.Name.Variable
//                           ^ Token.Punctuation
//                             ^ Token.Keyword
        Прервать;
//      ^ Token.Keyword
    КонецЦикла;
//  ^ Token.Keyword

    НевстроеннаяПроцедура();
//  ^ Token.Name.Function

    НовыйОбъект = Новый ТаблицаЗначений;
//                ^^^^^ Token.Keyword
//                     ^ Token.Name.Class
    НовыйОбъектСкобка = Новый("ТаблицаЗначений");
//                      ^^^^^ Token.Name.Function
//                           ^ Token.Punctuation

    ПрефиксЗначениеЗаполненоПостфикс = "";
//  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ Token.Name.Variable
//                                  ^ Token.Operator
//                                    ^ Token.Literal.String
//                                     ^ Token.Literal.String
//                                      ^ Token.Punctuation

    // Проверка на корректность обработки начала и конца слова
    Объект.Сообщить().Если().Цикл().Новый;
//         ^^^^^^^^                 ^^^^^ Token.Name.Function
//                    ^^^^ Token.Name.Function
//                           ^^^^ Token.Name.Function

    // Проверка подсветки глобальных свойств с точкой
    Справочники.ИмяСправочника.СоздатьЭлемент();
//  ^ Token.Name.Class
    А = ХранилищеПользовательскихНастроекДинамическихСписков.Сохранить();
//      ^ Token.Name.Class

    А = 0;
//  ^ Token.Name.Variable
//    ^ Token.Operator

    Б = А = 0;
//  ^ Token.Name.Variable
//    ^ Token.Operator
//        ^ Token.Operator

    Если А = Б Тогда
//       ^ Token.Name.Variable
//         ^ Token.Operator
    ИначеЕсли ЗначениеЗаполнено(А) = ЗначениеЗаполнено(Б) Тогда
//            ^ Token.Name.Builtin
//                                 ^ Token.Operator
    КонецЕсли;

    // TODO:
//     ^^^^ Token.Comment.Single

    Если А И
//       ^ Token.Name.Variable
        Б = В Тогда
//      ^ Token.Name.Variable       
        Б = 0;
//      ^ Token.Name.Variable
    КонецЕсли;

КонецПроцедуры
// <- Token.Keyword

Процедура НевстроеннаяПроцедура()
    Возврат;
//  ^ Token.Keyword
КонецПроцедуры

&Перед("ПередЗаписью")
// <- Token.Name.Decorator
// ^^^ Token.Name.Decorator
//     ^ Token.Punctuation
//      ^^^^^^^^^^^^^ Token.Name.Function
//                   ^ Token.Punctuation
Процедура Расш1_ПередЗаписью()

КонецПроцедуры

#КонецЕсли
// <- Token.Comment.Preproc
// ^ Token.Comment.Preproc

#КонецОбласти
// <- Token.Comment.Preproc
// ^ Token.Comment.Preproc

~Метка:
Перейти ~Метка;

Рез = Ждать Об; // Об имеет тип Обещание

Асинх Функция КопироватьФайлыАсинх(ИсхКаталог, ЦелКаталог)

Асинх Функция КопироватьФайлыАсинх(Знач ИсхКаталог, Знач ЦелКаталог)

Асинх Процедура П()

    Попытка
        Ждать НеNull(Null); 
    Исключение
        // Исключение из НеNull() будет перехвачено здесь
        Сообщить("Передали Null"); 
    КонецПопытки

КонецПроцедуры

Файлы = Ждать НайтиФайлыАсинх(ИсхКаталог, "*", Ложь); //2

СтрШаблон("Товар: %1, %2 не найден!", Номенклатура, Характеристика);
СтрШаблон("Скидка составила %1%%", 10);

ТекстЗапроса = "ВЫБРАТЬ
|   Контрагенты.Ссылка КАК Ссылка
|// ПОМЕСТИТЬ Контрагенты
|ИЗ
|   Справочник.Контрагенты КАК Контрагенты";

Если ВыгрузитьВоВременнуюТаблицу Тогда
    ТекстЗапроса = СтрЗаменить(ТекстЗапроса, "// ПОМЕСТИТЬ", "ПОМЕСТИТЬ");
КонецЕсли;

Результат = СтрЗаменить(Результат, "%", "~%");


Выполнить Алгоритм;

Х = Неопределено(123);
Х = Null(123);

Рез = (Цена > 0) И (Количество > 0);

Рез = (Цена > 0) И (Количество > 0);

Рез = Не (ЭтоАдмин);

Если Сумма <= 0 Тогда
    ВызватьИсключение "Сумма должна быть больше 0";
КонецЕсли;

#Если Сервер Или ТолстыйКлиентОбычноеПриложение И НЕ ВнешнееСоединение Тогда
#КонецЕсли

#Если Сервер Тогда
#ИначеЕсли Клиент Тогда
#Иначе
#КонецЕсли

```

## SDBL

```sdbl
// SYNTAX TEST "source.sdbl"
ВЫБРАТЬ
// <- Token.Keyword.Declaration
// Комментарий запроса
// <- Token.Comment.Single
    "Многострочная
//  ^ Token.String
    // это Комментарий
//  ^ Token.Comment.Single
    с экранированной "" кавычкой
//                   ^^ Token.String.Escape
    строка" КАК Поле,
//  ^^^^^^^ Token.String
//  ^ Token.String
//          ^^^ Token.Keyword.Declaration
//              ^ not:Token.Keyword.Declaration
//                  ^ Token.Operator
    Неопределено КАК Поле2,
//  ^ Token.Keyword.Constant
    0.0 КАК ДробноеЧисло,
//  ^^^ Token.Literal.Number
    0 КАК ЦелоеЧисло,
//  ^ Token.Literal.Number
    ВЫБОР КОГДА НЕ 0 = 0 * 1 ТОГДА ИСТИНА ИНАЧЕ ЛОЖЬ КОНЕЦ КАК Условие,
//  ^^^^^ Token.Keyword.Declaration
//        ^^^^^ Token.Keyword.Declaration
//              ^^ Token.Keyword.Declaration
//                   ^ Token.Operator
//                       ^ Token.Operator
//                           ^^^^^ Token.Keyword.Declaration
//                                        ^^^^^ Token.Keyword.Declaration
//                                                   ^^^^^ Token.Keyword.Declaration
    ГОД(ДАТАВРЕМЯ(1, 1, 1)) КАК Функция,
//  ^^^ Token.Keyword.Declaration
//     ^ not:Token.Keyword.Declaration
//      ^ Token.Keyword.Declaration
    ВЫРАЗИТЬ(0 КАК Число) КАК Выражение,
//  ^ Token.Keyword.Declaration
//                 ^^^^^ Token.Keyword.Declaration
    ВЫБОР КОГДА Неопределено ССЫЛКА Справочник.Справочник1 ТОГДА ИСТИНА КОНЕЦ КАК Ссылка,
//                           ^^^^^^ Token.Keyword.Declaration
//                                                                                ^^^^^^ not:Token.Keyword.Declaration
    ВЫБОР КОГДА Справочник.Справочник2 Есть NULL ТОГДА 0 ИНАЧЕ Справочник.Количество КОНЕЦ КАК Количество,
//                                     ^^^^^^^^^ Token.Keyword.Declaration
    ВЫБОР КОГДА Справочник.Справочник2 Есть НЕ NULL ТОГДА Справочник.Количество ИНАЧЕ 0 КОНЕЦ КАК Количество1,
//                                     ^^^^^^^^^^^^ Token.Keyword.Declaration
    ВЫБОР КОГДА Справочник.Справочник2 Is NULL ТОГДА 0 ИНАЧЕ Справочник.Количество КОНЕЦ КАК kolvo,
//                                     ^^^^^^^ Token.Keyword.Declaration
    ВЫБОР КОГДА Справочник.Справочник2 Is NOT NULL ТОГДА Справочник.Количество ИНАЧЕ 0 КОНЕЦ КАК kolvo1,
//                                     ^^^^^^^^^^^ Token.Keyword.Declaration   

    &Параметр КАК Параметр
//  ^^^^^^^^^ Token.Name.Variable


ПОДОБНО
Реквизит ПОДОБНО "123%"
Реквизит ПОДОБНО &Шаблон


Реквизит ПОДОБНО "123" + "%"
Реквизит ПОДОБНО &Шаблон + "%"
Реквизит ПОДОБНО Таблица.Шаблон

%
_
[…]
[^…]
_%[]^)

СПЕЦСИМВОЛ

    ВЫБРАТЬ
        Номенклатура.Ссылка КАК Ссылка 
    ИЗ
        Справочник.Номенклатура КАК Номенклатура
    ГДЕ
        Номенклатура.Наименование ПОДОБНО &Шаблон СПЕЦСИМВОЛ "~"

"Шуруп~_10~[21~] медь~~4~%" СПЕЦСИМВОЛ "~"
```
