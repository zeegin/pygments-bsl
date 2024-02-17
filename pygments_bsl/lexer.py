from pygments.lexer import RegexLexer, words
from pygments.token import Token

import re

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
        'КонецПопытки','EndTry','ВызватьИсключение','Raise',
        # keyword.control.repeat.bsl
        'Пока','While','Для','For','Каждого','Each',
        'Из','In','По','To','Цикл','Do','КонецЦикла', 'EndDo',
        # keyword.operator.logical.bsl
        'НЕ','NOT','И','AND','ИЛИ','OR',
        # support.function.bsl
        'Новый','New',
        # storage.modifier.bsl
        'Знач', 'Val',
        # 
        'Перейти', 'Goto',
        'Асинх', 'Async',
        'Ждать', 'Await',
    ), prefix='(?<!\.)', suffix=r'\b')

    NAME_BUILTIN = words((
        # support.function.bsl
        # Глобальный контекст - функции работы со значениями типа Строка
        'Новый','New','СтрДлина','StrLen',
        'СокрЛ','TrimL','СокрП','TrimR','СокрЛП','TrimAll',
        'Лев','Left','Прав','Right','Сред','Mid',
        'СтрНайти','StrFind',
        'ВРег','Upper','НРег','Lower','ТРег','Title',
        'Символ','Char','КодСимвола','CharCode',
        'ПустаяСтрока','IsBlankString',
        'СтрЗаменить','StrReplace',
        'СтрЧислоСтрок','StrLineCount',
        'СтрПолучитьСтроку','StrGetLine',
        'СтрЧислоВхождений','StrOccurrenceCount',
        'СтрСравнить','StrCompare',
        'СтрНачинаетсяС','StrStartWith',
        'СтрЗаканчиваетсяНа','StrEndsWith',
        'СтрРазделить','StrSplit',
        'СтрСоединить','StrConcat',
        # Глобальный контекст - функции работы со значениями типа Число
        'Цел','Int','Окр','Round',
        'ACos','ACos','ASin','ASin','ATan','ATan',
        'Cos','Cos','Exp','Exp','Log','Log','Log10','Log10',
        'Pow','Pow','Sin','Sin','Sqrt','Sqrt','Tan','Tan',
        # Глобальный контекст - функции работы со значениями типа Дата
        'Год','Year','Месяц','Month','День','Day',
        'Час','Hour','Минута','Minute','Секунда','Second',
        'НачалоГода','BegOfYear',
        'НачалоДня','BegOfDay',
        'НачалоКвартала','BegOfQuarter',
        'НачалоМесяца','BegOfMonth',
        'НачалоМинуты','BegOfMinute',
        'НачалоНедели','BegOfWeek',
        'НачалоЧаса','BegOfHour',
        'КонецГода','EndOfYear',
        'КонецДня','EndOfDay',
        'КонецКвартала','EndOfQuarter',
        'КонецМесяца','EndOfMonth',
        'КонецМинуты','EndOfMinute',
        'КонецНедели','EndOfWeek',
        'КонецЧаса','EndOfHour',
        'НеделяГода','WeekOfYear',
        'ДеньГода','DayOfYear',
        'ДеньНедели','WeekDay',
        'ТекущаяДата','CurrentDate',
        'ДобавитьМесяц','AddMonth',
        # Глобальный контекст - функции работы со значениями типа Тип
        'Тип','Type','ТипЗнч','TypeOf',
        # Глобальный контекст - функции преобразования значений
        'Булево','Boolean','Число','Number',
        'Строка','String','Дата','Date',
        # Глобальный контекст - процедуры и функции интерактивной работы
        'ПоказатьВопрос','ShowQueryBox',
        'Вопрос','DoQueryBox',
        'ПоказатьПредупреждение','ShowMessageBox',
        'Предупреждение','DoMessageBox',
        'Сообщить','Message',
        'ОчиститьСообщения','ClearMessages',
        'ОповеститьОбИзменении','NotifyChanged',
        'Состояние','Status',
        'Сигнал','Beep',
        'ПоказатьЗначение','ShowValue',
        'ОткрытьЗначение','OpenValue',
        'Оповестить','Notify',
        'ОбработкаПрерыванияПользователя','UserInterruptProcessing',
        'ОткрытьСодержаниеСправки','OpenHelpContent',
        'ОткрытьИндексСправки','OpenHelpIndex',
        'ОткрытьСправку','OpenHelp',
        'ПоказатьИнформациюОбОшибке','ShowErrorInfo',
        'КраткоеПредставлениеОшибки','BriefErrorDescription',
        'ПодробноеПредставлениеОшибки','DetailErrorDescription',
        'ПолучитьФорму','GetForm',
        'ЗакрытьСправку','CloseHelp',
        'ПоказатьОповещениеПользователя','ShowUserNotification',
        'ОткрытьФорму','OpenForm',
        'ОткрытьФормуМодально','OpenFormModal',
        'АктивноеОкно','ActiveWindow',
        'ВыполнитьОбработкуОповещения','ExecuteNotifyProcessing',
        # Глобальный контекст - функции для вызова диалога ввода данных
        'ПоказатьВводЗначения','ShowInputValue',
        'ВвестиЗначение','InputValue',
        'ПоказатьВводЧисла','ShowInputNumber',
        'ВвестиЧисло','InputNumber',
        'ПоказатьВводСтроки','ShowInputString',
        'ВвестиСтроку','InputString',
        'ПоказатьВводДаты','ShowInputDate',
        'ВвестиДату','InputDate',
        # Глобальный контекст - функции форматирования
        'Формат','Format',
        'ЧислоПрописью','NumberInWords',
        'НСтр','NStr',
        'ПредставлениеПериода','PeriodPresentation',
        'СтрШаблон','StrTemplate',
        # Глобальный контекст - функции обращения к конфигурации
        'ПолучитьОбщийМакет','GetCommonTemplate',
        'ПолучитьОбщуюФорму','GetCommonForm',
        'ПредопределенноеЗначение','PredefinedValue',
        'ПолучитьПолноеИмяПредопределенногоЗначения','GetPredefinedValueFullName',
        # Глобальный контекст - процедуры и функции сеанса работы
        'ПолучитьЗаголовокСистемы','GetCaption',
        'ПолучитьСкоростьКлиентскогоСоединения','GetClientConnectionSpeed',
        'ПодключитьОбработчикОжидания','AttachIdleHandler',
        'УстановитьЗаголовокСистемы','SetCaption',
        'ОтключитьОбработчикОжидания','DetachIdleHandler',
        'ИмяКомпьютера','ComputerName',
        'ЗавершитьРаботуСистемы','Exit',
        'ИмяПользователя','UserName',
        'ПрекратитьРаботуСистемы','Terminate',
        'ПолноеИмяПользователя','UserFullName',
        'ЗаблокироватьРаботуПользователя','LockApplication',
        'КаталогПрограммы','BinDir',
        'КаталогВременныхФайлов','TempFilesDir',
        'ПравоДоступа','AccessRight',
        'РольДоступна','IsInRole',
        'ТекущийЯзык','CurrentLanguage',
        'ТекущийКодЛокализации','CurrentLocaleCode',
        'СтрокаСоединенияИнформационнойБазы','InfoBaseConnectionString',
        'ПодключитьОбработчикОповещения','AttachNotificationHandler',
        'ОтключитьОбработчикОповещения','DetachNotificationHandler',
        'ПолучитьСообщенияПользователю','GetUserMessages',
        'ПараметрыДоступа','AccessParameters',
        'ПредставлениеПриложения','ApplicationPresentation',
        'ТекущийЯзыкСистемы','CurrentSystemLanguage',
        'ЗапуститьСистему','RunSystem',
        'ТекущийРежимЗапуска','CurrentRunMode',
        'УстановитьЧасовойПоясСеанса','SetSessionTimeZone',
        'ЧасовойПоясСеанса','SessionTimeZone',
        'ТекущаяДатаСеанса','CurrentSessionDate',
        'УстановитьКраткийЗаголовокПриложения','SetShortApplicationCaption',
        'ПолучитьКраткийЗаголовокПриложения','GetShortApplicationCaption',
        'ПредставлениеПрава','RightPresentation',
        'ВыполнитьПроверкуПравДоступа','VerifyAccessRights',
        'РабочийКаталогДанныхПользователя','UserDataWorkDir',
        'КаталогДокументов','DocumentsDir',
        'ПолучитьИнформациюЭкрановКлиента','GetClientDisplaysInformation',
        'ТекущийВариантОсновногоШрифтаКлиентскогоПриложения','ClientApplicationBaseFontCurrentVariant',
        'ТекущийВариантИнтерфейсаКлиентскогоПриложения','ClientApplicationInterfaceCurrentVariant',
        'УстановитьЗаголовокКлиентскогоПриложения','SetClientApplicationCaption',
        'ПолучитьЗаголовокКлиентскогоПриложения','GetClientApplicationCaption',
        'НачатьПолучениеКаталогаВременныхФайлов','BeginGettingTempFilesDir',
        'НачатьПолучениеКаталогаДокументов','BeginGettingDocumentsDir',
        'НачатьПолучениеРабочегоКаталогаДанныхПользователя','BeginGettingUserDataWorkDir',
        'ПодключитьОбработчикЗапросаНастроекКлиентаЛицензирования','AttachLicensingClientParametersRequestHandler',
        'ОтключитьОбработчикЗапросаНастроекКлиентаЛицензирования','DetachLicensingClientParametersRequestHandler',
        # Глобальный контекст - процедуры и функции сохранения значений
        'ЗначениеВСтрокуВнутр','ValueToStringInternal',
        'ЗначениеИзСтрокиВнутр','ValueFromStringInternal',
        'ЗначениеВФайл','ValueToFile',
        'ЗначениеИзФайла','ValueFromFile',
        # Глобальный контекст - Процедуры и функции работы с операционной системой
        'КомандаСистемы','System',
        'ЗапуститьПриложение','RunApp',
        'ПолучитьCOMОбъект','GetCOMObject',
        'ПользователиОС','OSUsers',
        'НачатьЗапускПриложения','BeginRunningApplication',
        # Глобальный контекст - Процедуры и функции работы с внешними компонентами
        'ПодключитьВнешнююКомпоненту','AttachAddIn',
        'НачатьУстановкуВнешнейКомпоненты','BeginInstallAddIn',
        'УстановитьВнешнююКомпоненту','InstallAddIn',
        'НачатьПодключениеВнешнейКомпоненты','BeginAttachingAddIn',
        # Глобальный контекст - Процедуры и функции работы с файлами
        'КопироватьФайл','FileCopy',
        'ПереместитьФайл','MoveFile',
        'УдалитьФайлы','DeleteFiles',
        'НайтиФайлы','FindFiles',
        'СоздатьКаталог','CreateDirectory',
        'ПолучитьИмяВременногоФайла','GetTempFileName',
        'РазделитьФайл','SplitFile',
        'ОбъединитьФайлы','MergeFiles',
        'ПолучитьФайл','GetFile',
        'НачатьПомещениеФайла','BeginPutFile',
        'ПоместитьФайл','PutFile',
        'ЭтоАдресВременногоХранилища','IsTempStorageURL',
        'УдалитьИзВременногоХранилища','DeleteFromTempStorage',
        'ПолучитьИзВременногоХранилища','GetFromTempStorage',
        'ПоместитьВоВременноеХранилище','PutToTempStorage',
        'ПодключитьРасширениеРаботыСФайлами','AttachFileSystemExtension',
        'НачатьУстановкуРасширенияРаботыСФайлами','BeginInstallFileSystemExtension',
        'УстановитьРасширениеРаботыСФайлами','InstallFileSystemExtension',
        'ПолучитьФайлы','GetFiles',
        'ПоместитьФайлы','PutFiles',
        'ЗапроситьРазрешениеПользователя','RequestUserPermission',
        'ПолучитьМаскуВсеФайлы','GetAllFilesMask',
        'ПолучитьМаскуВсеФайлыКлиента','GetClientAllFilesMask',
        'ПолучитьМаскуВсеФайлыСервера','GetServerAllFilesMask',
        'ПолучитьРазделительПути','GetPathSeparator',
        'ПолучитьРазделительПутиКлиента','GetClientPathSeparator',
        'ПолучитьРазделительПутиСервера','GetServerPathSeparator',
        'НачатьПодключениеРасширенияРаботыСФайлами','BeginAttachingFileSystemExtension',
        'НачатьЗапросРазрешенияПользователя','BeginRequestingUserPermission',
        'НачатьПоискФайлов','BeginFindingFiles',
        'НачатьСозданиеКаталога','BeginCreatingDirectory',
        'НачатьКопированиеФайла','BeginCopyingFile',
        'НачатьПеремещениеФайла','BeginMovingFile',
        'НачатьУдалениеФайлов','BeginDeletingFiles',
        'НачатьПолучениеФайлов','BeginGettingFiles',
        'НачатьПомещениеФайлов','BeginPuttingFiles',
        # Глобальный контекст - Процедуры и функции работы с информационной базой
        'НачатьТранзакцию','BeginTransaction',
        'ЗафиксироватьТранзакцию','CommitTransaction',
        'ОтменитьТранзакцию','RollbackTransaction',
        'УстановитьМонопольныйРежим','SetExclusiveMode',
        'МонопольныйРежим','ExclusiveMode',
        'ПолучитьОперативнуюОтметкуВремени','GetRealTimeTimestamp',
        'ПолучитьСоединенияИнформационнойБазы','GetInfoBaseConnections',
        'НомерСоединенияИнформационнойБазы','InfoBaseConnectionNumber',
        'КонфигурацияИзменена','ConfigurationChanged',
        'КонфигурацияБазыДанныхИзмененаДинамически','DataBaseConfigurationChangedDynamically',
        'УстановитьВремяОжиданияБлокировкиДанных','SetLockWaitTime',
        'ОбновитьНумерациюОбъектов','RefreshObjectsNumbering',
        'ПолучитьВремяОжиданияБлокировкиДанных','GetLockWaitTime',
        'КодЛокализацииИнформационнойБазы','InfoBaseLocaleCode',
        'УстановитьМинимальнуюДлинуПаролейПользователей','SetUserPasswordMinLength',
        'ПолучитьМинимальнуюДлинуПаролейПользователей','GetUserPasswordMinLength',
        'ИнициализироватьПредопределенныеДанные','InitializePredefinedData',
        'УдалитьДанныеИнформационнойБазы','EraseInfoBaseData',
        'УстановитьПроверкуСложностиПаролейПользователей','SetUserPasswordStrengthCheck',
        'ПолучитьПроверкуСложностиПаролейПользователей','GetUserPasswordStrengthCheck',
        'ПолучитьСтруктуруХраненияБазыДанных','GetDBStorageStructureInfo',
        'УстановитьПривилегированныйРежим','SetPrivilegedMode',
        'ПривилегированныйРежим','PrivilegedMode',
        'ТранзакцияАктивна','TransactionActive',
        'НеобходимостьЗавершенияСоединения','ConnectionStopRequest',
        'НомерСеансаИнформационнойБазы','InfoBaseSessionNumber',
        'ПолучитьСеансыИнформационнойБазы','GetInfoBaseSessions',
        'ЗаблокироватьДанныеДляРедактирования','LockDataForEdit',
        'УстановитьСоединениеСВнешнимИсточникомДанных','ConnectExternalDataSource',
        'РазблокироватьДанныеДляРедактирования','UnlockDataForEdit',
        'РазорватьСоединениеСВнешнимИсточникомДанных','DisconnectExternalDataSource',
        'ПолучитьБлокировкуСеансов','GetSessionsLock',
        'УстановитьБлокировкуСеансов','SetSessionsLock',
        'ОбновитьПовторноИспользуемыеЗначения','RefreshReusableValues',
        'УстановитьБезопасныйРежим','SetSafeMode',
        'БезопасныйРежим','SafeMode',
        'ПолучитьДанныеВыбора','GetChoiceData',
        'УстановитьЧасовойПоясИнформационнойБазы','SetInfoBaseTimeZone',
        'ПолучитьЧасовойПоясИнформационнойБазы','GetInfoBaseTimeZone',
        'ПолучитьОбновлениеКонфигурацииБазыДанных','GetDataBaseConfigurationUpdate',
        'УстановитьБезопасныйРежимРазделенияДанных','SetDataSeparationSafeMode',
        'БезопасныйРежимРазделенияДанных','DataSeparationSafeMode',
        'УстановитьВремяЗасыпанияПассивногоСеанса','SetPassiveSessionHibernateTime',
        'ПолучитьВремяЗасыпанияПассивногоСеанса','GetPassiveSessionHibernateTime',
        'УстановитьВремяЗавершенияСпящегоСеанса','SetHibernateSessionTerminateTime',
        'ПолучитьВремяЗавершенияСпящегоСеанса','GetHibernateSessionTerminateTime',
        'ПолучитьТекущийСеансИнформационнойБазы','GetCurrentInfoBaseSession',
        'ПолучитьИдентификаторКонфигурации','GetConfigurationID',
        'УстановитьНастройкиКлиентаЛицензирования','SetLicensingClientParameters',
        'ПолучитьИмяКлиентаЛицензирования','GetLicensingClientName',
        'ПолучитьДополнительныйПараметрКлиентаЛицензирования','GetLicensingClientAdditionalParameter',
        # Глобальный контекст - Процедуры и функции работы с данными информационной базы
        'НайтиПомеченныеНаУдаление','FindMarkedForDeletion',
        'НайтиПоСсылкам','FindByRef',
        'УдалитьОбъекты','DeleteObjects',
        'УстановитьОбновлениеПредопределенныхДанныхИнформационнойБазы','SetInfoBasePredefinedDataUpdate',
        'ПолучитьОбновлениеПредопределенныхДанныхИнформационнойБазы','GetInfoBasePredefinedData',
        # Глобальный контекст - Процедуры и функции работы с XML
        'XMLСтрока','XMLString',
        'XMLЗначение','XMLValue',
        'XMLТип','XMLType',
        'XMLТипЗнч','XMLTypeOf',
        'ИзXMLТипа','FromXMLType',
        'ВозможностьЧтенияXML','CanReadXML',
        'ПолучитьXMLТип','GetXMLType',
        'ПрочитатьXML','ReadXML',
        'ЗаписатьXML','WriteXML',
        'НайтиНедопустимыеСимволыXML','FindDisallowedXMLCharacters',
        'ИмпортМоделиXDTO','ImportXDTOModel',
        'СоздатьФабрикуXDTO','CreateXDTOFactory',
        # Глобальный контекст - Процедуры и функции работы с JSON
        'ЗаписатьJSON','WriteJSON',
        'ПрочитатьJSON','ReadJSON',
        'ПрочитатьДатуJSON','ReadJSONDate',
        'ЗаписатьДатуJSON','WriteJSONDate',
        # Глобальный контекст - Процедуры и функции работы с журналом регистрации
        'ЗаписьЖурналаРегистрации','WriteLogEvent',
        'ПолучитьИспользованиеЖурналаРегистрации','GetEventLogUsing',
        'УстановитьИспользованиеЖурналаРегистрации','SetEventLogUsing',
        'ПредставлениеСобытияЖурналаРегистрации','EventLogEventPresentation',
        'ВыгрузитьЖурналРегистрации','UnloadEventLog',
        'ПолучитьЗначенияОтбораЖурналаРегистрации','GetEventLogFilterValues',
        'УстановитьИспользованиеСобытияЖурналаРегистрации','SetEventLogEventUse',
        'ПолучитьИспользованиеСобытияЖурналаРегистрации','GetEventLogEventUse',
        'СкопироватьЖурналРегистрации','CopyEventLog',
        'ОчиститьЖурналРегистрации','ClearEventLog',
        # Глобальный контекст - Процедуры и функции работы с универсальными объектами
        'ЗначениеВДанныеФормы','ValueToFormData',
        'ДанныеФормыВЗначение','FormDataToValue',
        'КопироватьДанныеФормы','CopyFormData',
        'УстановитьСоответствиеОбъектаИФормы','SetObjectAndFormConformity',
        'ПолучитьСоответствиеОбъектаИФормы','GetObjectAndFormConformity',
        # Глобальный контекст - Процедуры и функции работы с функциональными опциями
        'ПолучитьФункциональнуюОпцию','GetFunctionalOption',
        'ПолучитьФункциональнуюОпциюИнтерфейса','GetInterfaceFunctionalOption',
        'УстановитьПараметрыФункциональныхОпцийИнтерфейса','SetInterfaceFunctionalOptionParameters',
        'ПолучитьПараметрыФункциональныхОпцийИнтерфейса','GetInterfaceFunctionalOptionParameters',
        'ОбновитьИнтерфейс','RefreshInterface',
        # Глобальный контекст - Процедуры и функции работы с криптографией
        'УстановитьРасширениеРаботыСКриптографией','InstallCryptoExtension',
        'НачатьУстановкуРасширенияРаботыСКриптографией','BeginInstallCryptoExtension',
        'ПодключитьРасширениеРаботыСКриптографией','AttachCryptoExtension',
        'НачатьПодключениеРасширенияРаботыСКриптографией','BeginAttachingCryptoExtension',
        # Глобальный контекст - Процедуры и функции работы со стандартным интерфейсом OData
        'УстановитьСоставСтандартногоИнтерфейсаOData','SetStandardODataInterfaceContent',
        'ПолучитьСоставСтандартногоИнтерфейсаOData','GetStandardODataInterfaceContent',
        # Глобальный контекст - Процедуры и функции работы с двоичными данными
        'СоединитьБуферыДвоичныхДанных','ConcatBinaryDataBuffers'
        # Глобальный контекст - Прочие процедуры и функции
        'Мин','Min',
        'Макс','Max',
        'ОписаниеОшибки','ErrorDescription',
        'Вычислить','Eval',
        'ИнформацияОбОшибке','ErrorInfo',
        'Base64Значение','Base64Value',
        'Base64Строка','Base64String',
        'ЗаполнитьЗначенияСвойств','FillPropertyValues',
        'ЗначениеЗаполнено','ValueIsFilled',
        'ПолучитьПредставленияНавигационныхСсылок','GetURLsPresentations',
        'НайтиОкноПоНавигационнойСсылке','FindWindowByURL',
        'ПолучитьОкна','GetWindows',
        'ПерейтиПоНавигационнойСсылке','GotoURL',
        'ПолучитьНавигационнуюСсылку','GetURL',
        'ПолучитьДопустимыеКодыЛокализации','GetAvailableLocaleCodes',
        'ПолучитьНавигационнуюСсылкуИнформационнойБазы','GetInfoBaseURL',
        'ПредставлениеКодаЛокализации','LocaleCodePresentation',
        'ПолучитьДопустимыеЧасовыеПояса','GetAvailableTimeZones',
        'ПредставлениеЧасовогоПояса','TimeZonePresentation',
        'ТекущаяУниверсальнаяДата','CurrentUniversalDate',
        'ТекущаяУниверсальнаяДатаВМиллисекундах','CurrentUniversalDateInMilliseconds',
        'МестноеВремя','ToLocalTime',
        'УниверсальноеВремя','ToUniversalTime',
        'ЧасовойПояс','TimeZone',
        'СмещениеЛетнегоВремени','DaylightTimeOffset',
        'СмещениеСтандартногоВремени','StandardTimeOffset',
        'КодироватьСтроку','EncodeString',
        'РаскодироватьСтроку','DecodeString',
        'Найти','Find',
        # Глобальный контекст - События приложения и сеанса
        'ПередНачаломРаботыСистемы','BeforeStart',
        'ПриНачалеРаботыСистемы','OnStart',
        'ПередЗавершениемРаботыСистемы','BeforeExit',
        'ПриЗавершенииРаботыСистемы','OnExit',
        'ОбработкаВнешнегоСобытия','ExternEventProcessing',
        'УстановкаПараметровСеанса','SessionParametersSetting',
        'ПриИзмененииПараметровЭкрана','OnChangeDisplaySettings',
    ), prefix='(?<!\.)', suffix=r'(?=(\s?[\(])|$)(?=[^\wа-яё]|$)')

    NAME_CLASS = words((
        # support.class.bsl
        # Глобальный контекст - Свойства (классы)
        'WSСсылки','WSReferences',
        'БиблиотекаКартинок','PictureLib',
        'БиблиотекаМакетовОформленияКомпоновкиДанных','DataCompositionAppearanceTemplateLib',
        'БиблиотекаСтилей','StyleLib',
        'БизнесПроцессы','BusinessProcesses',
        'ВнешниеИсточникиДанных','ExternalDataSources',
        'ВнешниеОбработки','ExternalDataProcessors',
        'ВнешниеОтчеты','ExternalReports',
        'Документы','Documents',
        'ДоставляемыеУведомления','DeliverableNotifications',
        'ЖурналыДокументов','DocumentJournals',
        'Задачи','Tasks',
        'ИспользованиеРабочейДаты','WorkingDateUse',
        'ИсторияРаботыПользователя','UserWorkHistory',
        'Константы','Constants',
        'КритерииОтбора','FilterCriteria',
        'Метаданные','Metadata',
        'Обработки','DataProcessors',
        'ОтправкаДоставляемыхУведомлений','DeliverableNotificationSend',
        'Отчеты','Reports',
        'ПараметрыСеанса','SessionParameters',
        'Перечисления','Enums',
        'ПланыВидовРасчета','ChartsOfCalculationTypes',
        'ПланыВидовХарактеристик','ChartsOfCharacteristicTypes',
        'ПланыОбмена','ExchangePlans',
        'ПланыСчетов','ChartsOfAccounts',
        'ПолнотекстовыйПоиск','FullTextSearch',
        'ПользователиИнформационнойБазы','InfoBaseUsers',
        'Последовательности','Sequences',
        'РасширенияКонфигурации','ConfigurationExtensions',
        'РегистрыБухгалтерии','AccountingRegisters',
        'РегистрыНакопления','AccumulationRegisters',
        'РегистрыРасчета','CalculationRegisters',
        'РегистрыСведений','InformationRegisters',
        'РегламентныеЗадания','ScheduledJobs',
        'СериализаторXDTO','XDTOSerializer',
        'Справочники','Catalogs',
        'СредстваГеопозиционирования','LocationTools',
        'СредстваКриптографии','CryptoToolsManager',
        'СредстваМультимедиа','MultimediaTools',
        'СредстваПочты','MailTools',
        'СредстваТелефонии','TelephonyTools',
        'ФабрикаXDTO','XDTOFactory',
        'ФоновыеЗадания','BackgroundJobs',
        'ХранилищаНастроек','SettingsStorages',
        'ВстроенныеПокупки','InAppPurchases',
        'ОтображениеРекламы','AdRepresentation',
        'ПанельЗадачОС','OSTaskbar',
        'ПроверкаВстроенныхПокупок','InAppPurchasesValidation'
        # support.variable.bsl
        # Глобальный контекст - Свойства (переменные)
        'ГлавныйИнтерфейс','MainInterface',
        'ГлавныйСтиль','MainStyle',
        'ПараметрЗапуска','LaunchParameter',
        'РабочаяДата','WorkingDate',
        'ХранилищеВариантовОтчетов','ReportsVariantsStorage',
        'ХранилищеНастроекДанныхФорм','FormDataSettingsStorage',
        'ХранилищеОбщихНастроек','CommonSettingsStorage',
        'ХранилищеПользовательскихНастроекДинамическихСписков','DynamicListsUserSettingsStorage',
        'ХранилищеПользовательскихНастроекОтчетов','ReportsUserSettingsStorage',
        'ХранилищеСистемныхНастроек','SystemSettingsStorage'
    ), prefix='(?<!\.)', suffix=r'\b')

    KEYWORD_CONSTANT = words((
        # constant.language.bsl
        'Неопределено','Undefined','Истина','True','Ложь','False','NULL'
    ), prefix='(?<!\.)', suffix=r'\b')

    OPERATORS = words((
        '=','<=','>=','<>','<','>','+','-','*','/','%','.'
    ))

    # see https://pygments.org/docs/tokens
    tokens = {
        'root': [
            (r'\n', Token.Text),
            (r'[^\S\n]+', Token.Text),
            (r'\/\/.*?(?=\n)', Token.Comment.Single),
            (r'[\[\]:(),;]', Token.Punctuation),
            (r'\&.*$', Token.Name.Decorator),
            (OPERATORS, Token.Operator),
            (r'\#.*$', Token.Comment.Preproc),
            (NAME_BUILTIN, Token.Name.Builtin),
            (r'[\wа-яё_][\wа-яё0-9_]*(?=(\s?[\(]))', Token.Name.Function),
            (KEYWORD_DECLARATION, Token.Keyword.Declaration),
            (KEYWORD, Token.Keyword),
            (NAME_CLASS, Token.Name.Class),
            (KEYWORD_CONSTANT, Token.Keyword.Constant),
            (r'\b\d+\.?\d*\b', Token.Number),
            (r'[\wа-яё_][\wа-яё0-9_]*', Token.Name.Variable),
            ('\"', Token.String, 'string'),
            (r'\'.*?\'', Token.Literal.Date),
            (r'~.*?(?=[:;])', Token.Name.Label),
        ],
        'string': [
            ('\"(?![\"])', Token.String, '#pop'),            
            (r'\n', Token.Text),
            (r'(?<=\n)[^\S\n]+', Token.Text),
            (r'(?<=[^\S\n])\/\/.*?(?=\n)', Token.Comment.Single),
            (r'(?<=^)\/\/.*?(?=\n)', Token.Comment.Single),
            (r'[^\"\|\n%]+', Token.String),
            (r'\"\"', Token.String.Escape),
            (r'\|', Token.String),
            (r'%\d', Token.String.Interpol),
            (r'%%', Token.String.Escape),
        ],
        # String.Regex
    }




class SdblLexer(RegexLexer):
    name = '1C (SDBL) Lexer'
    aliases = ['sdbl']
    filenames = ['*.sdbl']

    flags = re.MULTILINE | re.IGNORECASE | re.VERBOSE

    KEYWORD_DECLARATION = words((
        # keyword.control.sdbl
        'Выбрать','Select','Разрешенные','Allowed','Различные','Distinct',
        'Первые','Top','Как','As','ПустаяТаблица','EpmtyTable',
        'Поместить','Into','Уничтожить','Drop','Из','From',


        # ((Левое|Left|Правое|Right|Полное|Full)\s+(Внешнее\s+|Outer\s+)?Соединение|Join)
        # ((Внутреннее|Inner)\s+Соединение|Join)
        # Где|Where|(Сгруппировать\s+По)|(Group\s+By)
        # Имеющие|Having|Объединить(\s+Все)?|Union(\s+All)?
        # (Упорядочить\s+По)|(Order\s+By)
        # Автоупорядочивание|Autoorder|Итоги|Totals
        # По(\s+Общие)?|By(\s+Overall)?|(Только\s+)?Иерархия|(Only\s+)?Hierarchy
        # Периодами|Periods|Индексировать|Index|Выразить|Cast
        # |Возр|Asc|Убыв|Desc
        # Для\s+Изменения|(For\s+Update(\s+Of)?)
        # Спецсимвол|Escape
    ), prefix='(?<!\.)', suffix=r'\b')
    
    KEYWORD_CONSTANT = words((
        # constant.language.sdbl
        'Неопределено','Undefined','Истина','True','Ложь','False','NULL'
    ), prefix='(?<!\.)', suffix=r'\b')

    tokens = {
        'root': [
            (r'\n', Token.Text),
            (r'[^\S\n]+', Token.Text),
            (r'\/\/.*?(?=\n)', Token.Comment.Single),
            (r'[\[\]:(),;]', Token.Punctuation),
            (KEYWORD_DECLARATION, Token.Keyword.Declaration),
            (KEYWORD_CONSTANT, Token.Keyword.Constant),
            (r'[\wа-яё_][\wа-яё0-9_]*', Token.Name.Variable),
        ]
    }