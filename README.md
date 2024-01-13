# Загрузчик для webinar.ru

Позволяет скачать запись вебинара и сохранить его в формате ".mp4"

## Общая информация

1) Скрипт выгружает вебинары с webinar.ru, если ссылка подходит под паттерн "https://my.mts-link.ru/*";
2) Скрипт создает папку для вебинара, (ВНИНИЕ! )выгружает туда все чанки (у каждого чанка будет свой индикс в названии) и после этого создает новый файл, который состоит из всех скаченных чанков (он будет без индекса);
3) Скрипт самостоятельно обращается к сайту, следовательно, не имеет смысла параллельно запускать видео вручную из браузера. Это только замедлить скорость выгрузки вебинара!
4) В файле settings.json указаны настройки для скрипта, значения там принимают значения True или False. Можно изменить поведение скрипта, поменяв значение настроек в фале settings.json


## Для подготовки к запуску необходимо:

1) Перетащить скрипт в любую локальную папку и распаковать;
2) Открыть терминал в директории скрипта;
3) Прописать следующую команду:

```commandline
  pip install -r requirements.txt
```

## Для запуска скрипта необходимо:

1) Открыть терминал в директории скрипта;
2) Прописать следующую команду:

```commandline
  python scripts/main_script.py
```
ИЛИ

```commandline
  python3 scripts/main_script.py
```
## Альтернативные возможности:
-----------------
Можно также отдельно запустить слияние файлов. Для этого нужно:

1) Открыть терминал в директории скрипта;
2) Прописать следующую команду:

```commandline
  python scripts/files_merging.py
```

ИЛИ 

```commandline
  python3 scripts/files_merging.py
```

   