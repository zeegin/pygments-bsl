// SYNTAX TEST "source.os"
#Использовать cmdline
// <- Token.Keyword

Процедура САннотированнымиПараметрами(

  	&АннотацияДляПараметра
//  ^^^ Token.Name.Decorator
  	Знач Парам1,
//  ^ Token.Keyword
//       ^ Token.Name.Variable
    &АннотацияДляПараметра
//  ^^^ Token.Name.Decorator
    &АннотацияДляПараметра1
//  ^^^ Token.Name.Decorator
    &АннотацияДляПараметра2(СПараметрами = 3, 4, 5)
//  ^^^ Token.Name.Decorator
//                         ^ Token.Punctuation
//                          ^^^ Token.Name.Variable
//                                       ^ Token.Operator
//                                         ^ Token.Literal.Number
//                                          ^ Token.Operator
//                                            ^ Token.Literal.Number
//                                                ^ Token.Punctuation
    Знач Парам2,
//  ^ Token.Keyword
//       ^ Token.Name.Variable
    Парам3,
//  ^ Token.Name.Variable
    Парам4 = Неопределено
//  ^ Token.Name.Variable
) Экспорт
// <- Token.Punctuation
// ^ Token.Keyword
КонецПроцедуры
// <- Token.Keyword

&НаСервере
// <- Token.Name.Decorator
// ^ Token.Name.Decorator
&НаКлиентеНаСервереБезКонтекста
// <- Token.Name.Decorator
// ^ Token.Name.Decorator
&НаЧемУгодно(ДажеСПараметром = "Да", СПараметромБезЗначения, "Значение без параметра")
// <- Token.Name.Decorator
// ^ Token.Name.Decorator
//          ^ Token.Punctuation
//           ^^^ Token.Name.Variable
//                           ^ Token.Operator
//                             ^^^^ Token.Literal.String
//                                 ^ Token.Operator
//                                   ^^^ Token.Name.Variable
//                                                         ^ Token.Operator
//                                                           ^^^^ Token.Literal.String
&НаЧемУгодно(ДажеДважды = Истина)
// <- Token.Name.Decorator
// ^ Token.Name.Decorator
//          ^ Token.Punctuation
//           ^^^ Token.Name.Variable
//                      ^ Token.Operator
//                        ^ Token.Keyword.Constant
Процедура ТестДолжен_ПроверитьПолучениеАннотацийМетода() Экспорт

КонецПроцедуры
