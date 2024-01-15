import os
import re
import ssl
import urllib.request
from typing import List, Dict, AnyStr
import requests
from support import kwargs_for_request
from support.decorators import print_execution_time


def mkdir_if_not_exists(*, filename: AnyStr) -> AnyStr:
    """
    If directory does not exist, then create it and returns its path,
    otherwise just returns its path
    :param filename: filename for which the directory will be created
    :return: directory path
    """
    filename_without_extension = re.match(pattern=r'.+(?=.mp4)',
                                          string=filename
                                          )

    directory = os.path.join(os.getcwd(), filename_without_extension.group())
    if not os.path.exists(path=directory):
        os.mkdir(path=directory)

    return directory


def set_context_for_urllib() -> ssl.SSLContext:
    """
    Sets context for urllib: disables checking for certificate
    :return: ssl.SSLContext
    """
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    return context


def get_link_from_user() -> re.Match:
    """
    Requests a link to webinar from user
    :return: Match object with group named <record_id>
    """
    link = None

    while not link:
        link = re.fullmatch(pattern=r'https://my.mts-link.ru/.+/(?P<record_id>[0-9]+)$',
                            string=input("Вставьте, пожалуйста, ссылку на страницу с вебинаром: \n> "))

        if not link:
            print('Ссылка не соответствует паттерну \'https://my.mts-link.ru/.+/(?P<record_id>[0-9]+)$\'!\n')

    return link


def get_json_data_link(*, link: re.Match) -> AnyStr:
    """
    Create url path for json file with data
    :param link: Match object with group named <record_id>
    :return: url to json_data
    :raise ConnectionRefusedError if there is no record_id
    """

    if not link.group('record_id'):
        raise ConnectionRefusedError("Отсутствует id вебинара")

    return fr"https://my.mts-link.ru/api/eventsessions/{link.group('record_id')}/record?withoutCuts=false"


def get_json_data_from_link(*, link_to_json: AnyStr) -> Dict:
    """
    Passes link_to_json into requests.get and returns json
    :param link_to_json: url which is required to download json
    :return: dict with json_data
    """
    json_data = requests.get(url=link_to_json,
                             params=kwargs_for_request.params,
                             headers=kwargs_for_request.headers
                             )

    return json_data.json()


def get_filename(*, json_data: Dict) -> AnyStr:
    """
    If there is webinar filename in dict, then returns it,
    otherwise returns 'Name_is_not_found.mp4'
    :param json_data: dict which contains all needed information about webinar
    :return: webinar_filename
    """
    filename = json_data.get('name') if json_data.get('name') else 'Name_is_not_found'

    if not filename.endswith('.mp4'):
        filename += '.mp4'

    return filename


def get_video_urls(*, json_data: Dict) -> List:
    """
    Search for urls to webinar chunks and then returns list with them all
    :param json_data: dict which contains all needed information about webinar
    :return: chunks list
    :raise ValueError if there are no videos in the directory
    """
    urls = []

    for element in json_data.get('eventLogs'):

        if type(element) is dict:
            dc = element.get('data')
            if type(dc) is dict and dc.get('url'):
                urls.append(dc.get('url'))

    if not urls:
        raise ValueError('Не найдено ни одного видео!')

    return urls


def download_video_chunk(*, video_chunk_url: AnyStr, filename: AnyStr, directory: AnyStr) -> bool:
    """
    Download webinar chunk and write it into file
    :param video_chunk_url: url to chunk
    :param filename: chunk filename
    :param directory: directory defines into which directory the downloaded_video_chunk will be installed
    :return: True if any exception is not raised
    """
    content = urllib.request.urlopen(url=video_chunk_url,
                                     context=set_context_for_urllib(),
                                     ).read()

    with open(f'{os.path.join(directory, filename)}', 'ab') as output_file:
        output_file.write(content)

    return True


@print_execution_time(action="скачивание")
def download_webinar() -> Dict:
    set_context_for_urllib()
    link_from_user = get_link_from_user()
    link_to_json_data = get_json_data_link(link=link_from_user)

    json_data = get_json_data_from_link(link_to_json=link_to_json_data)

    video_chunks_urls = get_video_urls(json_data=json_data)

    video_chunks_urls_length = len(video_chunks_urls)
    print(f'Количество видео-роликов: {video_chunks_urls_length}: \n{"\n".join(video_chunks_urls)}')
    print('Загрузка началась!')

    webinar_filename = re.sub(pattern=r'[\s\/:*?"<>|+]+',
                              repl=r'_',
                              string=get_filename(json_data=json_data)
                              )

    directory = mkdir_if_not_exists(filename=webinar_filename)
    chunks_filenames = []
    for index, video_chunk_url in enumerate(video_chunks_urls):
        filename = os.path.join(directory, f'{index + 1}) {webinar_filename}')
        chunks_filenames.append(filename)
        download_video_chunk(video_chunk_url=video_chunk_url,
                             filename=filename,
                             directory=directory
                             )
        print(f'{index + 1}/{video_chunks_urls_length} выполнено!')

    print('Готово!')

    return {'chunks_filenames': chunks_filenames,
            'webinar_filename': f'{os.path.join(directory, webinar_filename)}'
            }
