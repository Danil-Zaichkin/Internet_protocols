## Заичкин Данил КН-201



## Задача 1. Трассировка автономных систем
- Пользователь вводит ip-адрес или доменное имя
- происходит трассировка до указанного узла с помощью утилиты traceroute
- программа выводит для каждого узла ip-адрес, номер автономной системы, страна, провайдер  

## tracer.py 
![help](https://github.com/Danil-Zaichkin/Internet_protocols/raw/main/img/tracer_help.jpg)
![output](https://github.com/Danil-Zaichkin/Internet_protocols/raw/main/img/tracer_output_example.jpg)

## Задача 2. Кеширующий DNS сервер
- Сервер прослушивает 53 порт
- При появлении запроса сервер проверят наличие ответа в кэше, если в кэше ответа нет, то запрос отправляется авторитетному dns серверу
- Кэш представлен в виде хеш-таблицы, где ключами являются пары `доменное имя, тип запроса`, 
значениями являются все ресурсные записи по этой паре, полученные из ответов авторитетного dns сервера
- Для парсинга dns записей используется библиотека `dnslib`
- Поддерживаются запросы `A`, `AAAA`, `NS`, `SOA`
- по истечении TTL DNS запроса, он удаляется из кеша. При десериализации кеша все записи с просроченным TTL также удаляются

## dns_server.py

![help](https://github.com/Danil-Zaichkin/Internet_protocols/raw/main/img/dns_server_help.jpg)
![help](https://github.com/Danil-Zaichkin/Internet_protocols/raw/main/img/dns_server_example.jpg)

## Задача 3. Использование API
- Использование API ВКонтакте для получения списка друзей заданного пользователя
- Скрипт принимает user_id пользователя ВКонтакте

## vk_parser.py

https://github.com/Danil-Zaichkin/Internet_protocols/assets/91212875/20d11d69-2dab-4799-b852-21325bee5d46
