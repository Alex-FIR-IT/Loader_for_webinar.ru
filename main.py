import json
import os.path
import re
from typing import Dict, AnyStr, List
import chime
from scripts.download import download_webinar
from scripts.files_merging import merge_files, merging_files_is_needed_from_user, main_merge_files
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


def choose_option_one_out_of_three_from_user() -> AnyStr:
    """
    get from user '1', '2', '3' and then returns is
    :return: '1' or '2' or '3'
    """
    option_number = None

    while not option_number:
        option_number = re.fullmatch(pattern=r'1|2|3',
                                     string=input("Что необходимо сделать? \n"
                                                  "1. Выгрузить запись вебинара;\n"
                                                  "2. Запустить процесс слияние чанков.\n"
                                                  "3. Выгрузить несколько вебинаров, используя пакетную загрузку\n"
                                                  "> ")
                                     )

    return option_number.group()


def get_filename_from_user() -> AnyStr:
    """
    Get filename from user, then check whether this file exists and file's extension is '.txt
    :return: filename
    """
    while True:
        filename = input('Вставьте путь до файла с ссылками:\n> ')

        if os.path.isfile(filename) and os.path.splitext(p=filename)[-1] == '.txt':
            break

    return filename


def unload_links_from_file(*, filename: AnyStr) -> List[AnyStr]:
    """
    Open file, read likks to webinars from it and then returns it as a list
    :param filename: file which contains links to webinars
    :return: list with links to webinars
    """
    with open(file=filename, mode='r') as file:
        links = file.readlines()

    if links:
        return links


@chime_when_is_done(chime_level='success')
def main() -> None:
    """
    Main function which starts script
    :return: None
    """
    user_option = choose_option_one_out_of_three_from_user()

    if user_option == '1':
        links_from_user = (get_link_from_user(),)
    elif user_option == '2':
        main_merge_files()
        return
    elif user_option == '3':
        filename = get_filename_from_user()
        links_from_user = unload_links_from_file(filename=filename)
    else:
        raise NotImplementedError('Эта ошибка не должна была возникнуть'
                                  ' - ошибка выбора в функции choose_option_one_out_of_three_from_user')

    script_settings = load_from_json()

    if script_settings.get('auto_files_merging') or merging_files_is_needed_from_user():
        file_merging_will_be_performed = True
    else:
        file_merging_will_be_performed = False

    for link_from_user in links_from_user:
        try:
            filenames_dict = download_webinar(link_from_user=link_from_user)

            if file_merging_will_be_performed:
                merge_files(video_filenames=filenames_dict.get('chunks_filenames'),
                            filename=filenames_dict.get('webinar_filename'))

        except Exception as error:
            print(error)
            chime.error()


if __name__ == '__main__':
    chime.theme('pokemon')
    chime.notify_exceptions()

    main()
