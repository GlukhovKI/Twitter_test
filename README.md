## Схема работы скрипта:
  * Подключение к twitter api
  * Подписка на указанные аккаунты  
  * "Прослушка" аккаунтов с получения данных о твитах
***
## Для работы скрипта необходим модуль python-twitter:
  $ pip install python-twitter
***
## Так же вам нужно знать.
  * consumer_key
  * consumer_secret 
  * access_token_key
  * access_token_secret 

***Их нужно вписать в файл config.ini***
***
## Другие данные необходимые для заполнения файла конфигурации:

Перечисление аккаунтов, на которые хотите подписаться. Перечесление через ***запятую***.

#### аккаунты
friendships = accaunt1 accaunt2

Включение и выключения работы лога и лога ошибок. По умолчанию значение ***False***.

#### логирование в файле True/False
file_logging = False
#### сохранение ошибок в файле True/False
file_errors = False

Возможность задать название файлов для вашего удобства.

#### название файла для хранения получаемых данных
main_file_name = Twitts.txt
#### * для хранения id последних сообщений
last_ids_file_name = Last_ids.txt
#### * для логирования
logs_file_name = Logs.txt
#### * для логирования ошибок
errors_file_name = Errors.txt
