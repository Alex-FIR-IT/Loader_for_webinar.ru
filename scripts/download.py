import os
import re
from typing import List, Dict
import requests
import tqdm
from utils import kwargs_for_request
from utils.decorators import print_execution_time, chime_when_is_done


def mkdir_if_not_exists(*, filename: str) -> str:
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


def get_json_data_link(*, record_id: str) -> str:
    """
    Create url path for remote json file with data
    :param record_id: string value of record_id
    :return: url to json_data
    :raise ConnectionRefusedError if there is no record_id
    """

    if not record_id:
        raise ConnectionRefusedError("Отсутствует id вебинара")

    return fr"https://my.mts-link.ru/api/eventsessions/{record_id}/record?withoutCuts=false"


def get_json_data_from_link(*, link_to_json: str) -> Dict:
    """
    Passes link_to_json into function requests.get() and returns json
    :param link_to_json: url which is required to download json
    :return: dict with json_data
    """
    json_data = requests.get(url=link_to_json,
                             params=kwargs_for_request.params,
                             headers=kwargs_for_request.headers
                             )

    return json_data.json()


def get_filename(*, json_data: Dict) -> str:
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


def download_video_chunk(*, video_chunk_url: str, filepath: str) -> bool:
    """
    Download webinar chunk and write it into file
    :param video_chunk_url: url to chunk
    :param filepath: chunk filepath
    :return: True if any exception is not raised
    """

    with open(filepath, 'wb') as output_chunk_file:
        with requests.get(url=video_chunk_url, stream=True) as request_obj:
            request_obj.raise_for_status()
            total = int(request_obj.headers.get('content-length', 0))

            tqdm_params = {
                'desc': video_chunk_url,
                'total': total,
                'miniters': 1,
                'unit': 'it',
                'unit_scale': True,
                'unit_divisor': 1024,
            }

            with tqdm.tqdm(**tqdm_params) as tqdm_obj:
                for sub_chunk in request_obj.iter_content(chunk_size=8192):
                    tqdm_obj.update(len(sub_chunk))
                    output_chunk_file.write(sub_chunk)

    return True


@chime_when_is_done(chime_level='info')
@print_execution_time(action="скачивание")
def download_webinar(*, record_id: str) -> Dict:
    """
    Download webinar using link and then returns dict{chunks_filepaths, webinar_filename}
    :param record_id: webinar's record_id
    :return: dict{chunks_filepaths, webinar_filepath}
    """

    link_to_json_data = get_json_data_link(record_id=record_id)

    json_data = get_json_data_from_link(link_to_json=link_to_json_data)

    video_chunks_urls = get_video_urls(json_data=json_data)

    video_chunks_urls_with_numeration_for_output = [f"{index + 1}) {video}"
                                                    for index, video in enumerate(video_chunks_urls)
                                                    ]

    video_chunks_urls_length = len(video_chunks_urls)
    print(f'Количество видео-роликов: {video_chunks_urls_length}: \n'
          f'{"\n".join(video_chunks_urls_with_numeration_for_output)}'
          )

    print('Загрузка началась!')

    webinar_filename = re.sub(pattern=r'[\s\/:*?"<>|+]+',
                              repl=r'_',
                              string=get_filename(json_data=json_data)
                              )

    directory = mkdir_if_not_exists(filename=webinar_filename)
    chunks_filepaths = []
    for index, video_chunk_url in enumerate(video_chunks_urls):
        filepath = os.path.join(directory, f'{index + 1}) {webinar_filename}')
        chunks_filepaths.append(filepath)
        download_video_chunk(video_chunk_url=video_chunk_url,
                             filepath=filepath
                             )
        print(f'{index + 1}/{video_chunks_urls_length} выполнено!')

    print('Готово!')

    return {'chunks_filepaths': chunks_filepaths,
            'webinar_filepath': f'{os.path.join(directory, webinar_filename)}'
            }
