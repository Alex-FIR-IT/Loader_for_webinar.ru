import json
import re
from typing import Dict
import chime
from scripts.download import download_webinar
from scripts.files_merging import merge_files, get_merge_files_or_not_from_user, main_merge_files
from support.decorators import chime_when_is_done


def get_link_from_user() -> re.Match:
    """
    Requests a link to webinar from user
    :return: Match object with group named <record_id>
    """
    link = None

    while not link:
        link = re.fullmatch(pattern=r'https://'
                                    r'(?:my.mts-link.ru|events.webinar.ru)'
                                    r'/.+/(?P<record_id>[0-9]+)$',
                            string=input("Вставьте, пожалуйста, ссылку на страницу с вебинаром: \n> "))

        if not link:
            print('Ссылка не соответствует паттерну \'https://my.mts-link.ru/.+/(?P<record_id>[0-9]+)$\'!\n')

    return link


def load_from_json() -> Dict:
    """
    Loads script settings from settings.json and then convert it into dict to return it
    :return: dict with script settings
    """
    with open(file='settings.json', mode='r') as file:
        return json.load(fp=file)


def use_only_merging_from_user():
    option_number = None

    while not option_number:
        option_number = re.fullmatch(pattern=r'1|2',
                                     string=input("Что необходимо сделать? \n"
                                                  "1. Выгрузить запись вебинара;"
                                                  "2. Запустить процесс слияние файлов.\n"
                                                  "> ")
                                     )

    if re.fullmatch(pattern=r'1', string=option_number.group()):
        return True


@chime_when_is_done(chime_level='success')
def main():
    if use_only_merging_from_user():
        main_merge_files()
    else:
        filenames_dict = download_webinar()

        script_settings = load_from_json()

        if script_settings.get('auto_files_merging'):
            merge_files(video_filenames=filenames_dict.get('chunks_filenames'),
                        filename=filenames_dict.get('webinar_filename'))
        else:
            if get_merge_files_or_not_from_user():
                merge_files(video_filenames=filenames_dict.get('chunks_filenames'),
                            filename=filenames_dict.get('webinar_filename'))


if __name__ == '__main__':
    chime.theme('pokemon')
    chime.notify_exceptions()

    main()
