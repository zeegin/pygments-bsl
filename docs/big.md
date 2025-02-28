# Большой тест

## BSL

```bsl
// SYNTAX TEST "source.bsl"
#Область ИмяОбласти
// <- keyword.other.section.bsl
// ^ keyword.other.section.bsl
//       ^ entity.name.section.bsl

Перем А Экспорт;
// <- storage.type.var.bsl
//    ^ variable.bsl
//      ^ storage.modifier.bsl

Перем А, Б;
//     ^ keyword.operator.bsl
//       ^ variable.bsl

Перем А Экспорт, Б;
//    ^ variable.bsl
//       ^ storage.modifier.bsl
//             ^ keyword.operator.bsl
//               ^ variable.bsl

Перем А, Б Экспорт;
//    ^ variable.bsl
//     ^ keyword.operator.bsl
//       ^ variable.bsl
//         ^ storage.modifier.bsl

Перем А Экспорт, Б Экспорт;
//    ^ variable.bsl
//       ^ storage.modifier.bsl
//             ^ keyword.operator.bsl
//               ^ variable.bsl
//                 ^ storage.modifier.bsl

#Если Сервер Тогда
// <- keyword.other.preprocessor.bsl
//    ^^^^^^ keyword.other.preprocessor.bsl

// Комментарий процедуры
// <- comment.line.double-slash.bsl
&НаСервере
// <- storage.modifier.directive.bsl
// ^ storage.modifier.directive.bsl
Процедура ИмяПроцедуры(
// <- storage.type.bsl
//        ^ entity.name.function.bsl
//                    ^ punctuation.bracket.begin.bsl
    Знач ПараметрСКонстантой,
//  ^ storage.modifier.bsl
//       ^ variable.parameter.bsl
//                          ^ keyword.operator.bsl
    ОбычныйПараметр,
//  ^ variable.parameter.bsl
    ПараметрСНекорректнымЗначением = Нелегальщина,
//                                  ^ not:invalid.illegal.bsl
//                                   ^ invalid.illegal.bsl
    ПараметрСНекорректнымЗначением =НелегальщинаБезПробела,
//                                  ^ invalid.illegal.bsl
//                                                        ^ keyword.operator.bsl
    ПараметрСДефолтнымЧисловымЗначением = 0) Экспорт
//                                      ^ keyword.operator.assignment.bsl
//                                        ^ constant.numeric.bsl
//                                         ^ punctuation.bracket.end.bsl
//                                           ^ storage.modifier.bsl
    Б = "текст с экраннированной "" кавычкой" + "и конкатенаций""";
//       ^ string.quoted.double.bsl
//                               ^^ constant.character.escape.bsl
//                                 ^ not:constant.character.escape.bsl
//                                              ^ string.quoted.double.bsl
//                                                             ^^ constant.character.escape.bsl
//                                                               ^ not:constant.character.escape.bsl
//                                                                ^ keyword.operator.bsl

    В = "многострочная
//      ^ string.quoted.double.bsl
    |строка
//  ^ string.quoted.double.bsl
    //|это комментарий
//      ^ comment.line.double-slash.bsl
    |// а это нет
//      ^ string.quoted.double.bsl
    |";
//   ^ string.quoted.double.bsl
//    ^ keyword.operator.bsl

    Г = "";
//      ^^ string.quoted.double.bsl

    ТекстЗапроса =
    "ВЫБРАТЬ
//  ^^ string.quoted.double.bsl
//   ^ keyword.control.sdbl
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
//  ^ string.quoted.double.bsl comment.line.double-slash.bsl
    |// Закомметированная строка внутри запроса с кавычками ""ТЕКСТ""
//  ^ string.quoted.double.bsl
//  ^ not:comment.line.double-slash.sdbl
//   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ comment.line.double-slash.sdbl
    |СГРУППИРОВАТЬ ПО
    |	Поле
    //|//АВТОУПОРЯДОЧИВАНИЕ";
//  ^^^^^^^^^^^^^^^^^^^^^^^^^ comment.line.double-slash.bsl
    |//АВТОУПОРЯДОЧИВАНИЕ";
//  ^^^^^^^^^^^^^^^^^^^^^^ string.quoted.double.bsl
//  ^ not:comment.line.double-slash.sdbl
//   ^^^^^^^^^^^^^^^^^^^^ comment.line.double-slash.sdbl
//                       ^ not:comment.line.double-slash.sdbl
//                        ^ keyword.operator.bsl

    // Проверка на корректность обработки FirstLineMatch и #include: source.sdbl
    СтрокаСоСловомВыбрать = "Some selected text";
//                                ^^^^^^ not:keyword.control.sdbl

    Число = 0.0 * 100;
//  ^ not:support.function.bsl
//          ^^^ constant.numeric.bsl
//              ^ keyword.operator.arithmetic.bsl

    Дата = '00010101000000';
//         ^^^^^^^^^^^^^^^^ constant.other.date.bsl
    КороткаяДата = '00010101';
//                 ^^^^^^^^^^ constant.other.date.bsl
    ДатаСРазделителями = '0001-01-01T00:00:00';
//                       ^^^^^^^^^^^^^^^^^^^^^ constant.other.date.bsl
    КороткаяДатаСРазделителями = '0001/01/01';
//                               ^^^^^^^^^^^^ constant.other.date.bsl
    СтрокаСДатойВнутри = "Литерал типа Дата: '00010101'";
//                                          ^^^^^^^^^^^^ string.quoted.double.bsl
//                                           ^^^^^^^^^^ not:constant.other.date.bsl

    Если А = 0 И НЕ Число <= 0 Тогда
//  ^ keyword.control.conditional.bsl
//         ^ keyword.operator.comparison.bsl
//           ^ constant.numeric.bsl
//             ^ keyword.operator.logical.bsl
//               ^^ keyword.operator.logical.bsl
//                        ^^ keyword.operator.comparison.bsl
//                             ^ keyword.control.conditional.bsl

        ОбычныйПараметр = Истина;
//                        ^ constant.language.bsl
    Иначе
//  ^ keyword.control.conditional.bsl
        ОбычныйПараметр = Ложь
    КонецЕсли;
//  ^ keyword.control.conditional.bsl

    Пока ЗначениеЗаполнено(Б) Цикл
//  ^ keyword.control.repeat.bsl
//       ^ support.function.bsl
//                        ^ punctuation.bracket.begin.bsl
//                         ^ not:punctuation.bracket.begin.bsl
//                          ^ punctuation.bracket.end.bsl
        Прервать;
//      ^ keyword.control.bsl
    КонецЦикла;
//  ^ keyword.control.repeat.bsl

    НевстроеннаяПроцедура();
//  ^ not:support.function.bsl

    НовыйОбъект = Новый ТаблицаЗначений;
//                ^^^^^ support.function.bsl
//                     ^ not:support.function.bsl
    НовыйОбъектСкобка = Новый("ТаблицаЗначений");
//                      ^^^^^ support.function.bsl
//                           ^ not:support.function.bsl

    ПрефиксЗначениеЗаполненоПостфикс = "";
//  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ not:support.function.bsl

    // Проверка на корректность обработки начала и конца слова
    Объект.Сообщить().Если().Цикл().Новый;
//         ^^^^^^^^                 ^^^^^ not:support.function.bsl
//                    ^^^^ not:keyword.control.conditional.bsl
//                           ^^^^ not:keyword.control.repeat.bsl

    // Проверка подсветки глобальных свойств с точкой
    Справочники.ИмяСправочника.СоздатьЭлемент();
//  ^ support.class.bsl
    А = ХранилищеПользовательскихНастроекДинамическихСписков.Сохранить();
//      ^ support.variable.bsl

    А = 0;
//  ^ variable.assignment.bsl
//    ^ keyword.operator.assignment.bsl

    Б = А = 0;
//  ^ variable.assignment.bsl
//    ^ keyword.operator.assignment.bsl
//        ^ keyword.operator.comparison.bsl

    Если А = Б Тогда
//       ^ not:variable.assignment.bsl
//         ^ keyword.operator.comparison.bsl
    ИначеЕсли ЗначениеЗаполнено(А) = ЗначениеЗаполнено(Б) Тогда
//            ^ not:variable.assignment.bsl
//                                 ^ keyword.operator.comparison.bsl
    КонецЕсли;

    // TODO:
//     ^^^^	storage.type.class.todo

    Если А И
//       ^ not:variable.assignment.bsl
        Б = В Тогда
//      ^ not:variable.assignment.bsl       
        Б = 0;
//      ^ variable.assignment.bsl
    КонецЕсли;

КонецПроцедуры
// <- storage.type.bsl

Процедура НевстроеннаяПроцедура()
    Возврат;
//  ^ keyword.control.bsl
КонецПроцедуры

&Перед("ПередЗаписью")
// <- storage.type.annotation.bsl
// ^^^ storage.type.annotation.bsl
//     ^^^^^^^^^^^^^^ string.quoted.double.bsl
Процедура Расш1_ПередЗаписью()

КонецПроцедуры

#КонецЕсли
// <- keyword.other.preprocessor.bsl
// ^ keyword.other.preprocessor.bsl

#КонецОбласти
// <- keyword.other.section.bsl
// ^ keyword.other.section.bsl

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

```

## SDBL

```sdbl
// SYNTAX TEST "source.sdbl"
ВЫБРАТЬ
// <- keyword.control.sdbl
// Комментарий запроса
// <- comment.line.double-slash.sdbl
    "Многострочная
//  ^ string.quoted.double.sdbl
    // это Комментарий
//  ^ comment.line.double-slash.sdbl
    с экранированной "" кавычкой
//                   ^^ constant.character.escape.sdbl
    строка" КАК Поле,
//  ^^^^^^^ string.quoted.double.sdbl
//  ^ string.quoted.double.sdbl
//          ^^^ keyword.control.sdbl
//              ^ not:keyword.control.sdbl
//                  ^ keyword.operator.sdbl
    Неопределено КАК Поле2,
//  ^ constant.language.sdbl
    0.0 КАК ДробноеЧисло,
//  ^^^ constant.numeric.sdbl
    0 КАК ЦелоеЧисло,
//  ^ constant.numeric.sdbl
    ВЫБОР КОГДА НЕ 0 = 0 * 1 ТОГДА ИСТИНА ИНАЧЕ ЛОЖЬ КОНЕЦ КАК Условие,
//  ^^^^^ keyword.control.conditional.sdbl
//        ^^^^^ keyword.control.conditional.sdbl
//              ^^ keyword.operator.logical.sdbl
//                   ^ keyword.operator.comparison.sdbl
//                       ^ keyword.operator.arithmetic.sdbl
//                           ^^^^^ keyword.control.conditional.sdbl
//                                        ^^^^^ keyword.control.conditional.sdbl
//                                                   ^^^^^ keyword.control.conditional.sdbl
    ГОД(ДАТАВРЕМЯ(1, 1, 1)) КАК Функция,
//  ^^^ support.function.sdbl
//     ^ not:support.function.sdbl
//      ^ support.function.sdbl
    ВЫРАЗИТЬ(0 КАК Число) КАК Выражение,
//  ^ keyword.control.sdbl
//                 ^^^^^ support.type.sdbl
    ВЫБОР КОГДА Неопределено ССЫЛКА Справочник.Справочник1 ТОГДА ИСТИНА КОНЕЦ КАК Ссылка,
//                           ^^^^^^ keyword.operator.logical.sdbl
//                                                                                ^^^^^^ not:keyword.operator.logical.sdbl
    ВЫБОР КОГДА Справочник.Справочник2 Есть NULL ТОГДА 0 ИНАЧЕ Справочник.Количество КОНЕЦ КАК Количество,
//                                     ^^^^^^^^^ keyword.operator.logical.sdbl
    ВЫБОР КОГДА Справочник.Справочник2 Есть НЕ NULL ТОГДА Справочник.Количество ИНАЧЕ 0 КОНЕЦ КАК Количество1,
//                                     ^^^^^^^^^^^^ keyword.operator.logical.sdbl
    ВЫБОР КОГДА Справочник.Справочник2 Is NULL ТОГДА 0 ИНАЧЕ Справочник.Количество КОНЕЦ КАК kolvo,
//                                     ^^^^^^^ keyword.operator.logical.sdbl
    ВЫБОР КОГДА Справочник.Справочник2 Is NOT NULL ТОГДА Справочник.Количество ИНАЧЕ 0 КОНЕЦ КАК kolvo1,
//                                     ^^^^^^^^^^^ keyword.operator.logical.sdbl   

    &Параметр КАК Параметр
//  ^^^^^^^^^ variable.parameter.sdbl


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