import json
import os.path
import re
from typing import Dict, List
import chime
from scripts.download import download_webinar
from scripts.files_merging import merge_files, merging_files_is_needed_from_user, main_merge_files
from support.decorators import chime_when_is_done
import logging


def get_record_id_if_link_is_correct(*, link: str) -> str:
    """
    if link matches the correct link pattern, then returns record_id
    :param link: link to webinar
    :return: webinar's record_id
    """
    link = re.fullmatch(pattern=r'https://'
                                r'(?:my.mts-link.ru|events.webinar.ru)'
                                r'/.+/(?P<record_id>[0-9]+)$',
                        string=link.strip(),
                        flags=re.MULTILINE
                        )
    if link:
        return link.group('record_id')


def get_record_id_out_of_link_from_user() -> str:
    """
    Requests a link to webinar from user
    :return: webinar's record_id
    """
    record_id = None

    while not record_id:
        record_id = get_record_id_if_link_is_correct(
            link=input("Вставьте, пожалуйста, ссылку на страницу с вебинаром: \n> "))

        if not record_id:
            print('Ссылка не соответствует паттерну \'https://my.mts-link.ru/.+/(?P<record_id>[0-9]+)$\'!\n')

    return record_id


def get_record_ids_from_links(*, links: List[str]) -> List[str]:
    """
    Check whether links are correct and then returns list which contains record_ids for each webinar
    :param links: list with links to webinars
    :return: list which contains record_ids for each webinar
    :raise ValueError: if any link is incorrect
    """
    record_ids = []
    for link in links:
        record_id = get_record_id_if_link_is_correct(link=link)

        if not record_id:
            raise ValueError(fr'Ссылка - <{link.__repr__()}> не соответствует паттерну \'https://my.mts-link.ru/.+/(?P<record_id>[0-9]+)$\'!\n')

        record_ids.append(record_id)

    return record_ids


def load_from_json() -> Dict:
    """
    Loads script settings from settings.json and then convert it into dict to return it
    :return: dict with script settings
    """
    with open(file='settings.json', mode='r') as file:
        return json.load(fp=file)


def choose_option_one_out_of_three_from_user() -> str:
    """
    get from user '1', '2', '3' and then returns is
    :return: '1' or '2' or '3'
    """
    option_number = None

    while not option_number:
        option_number = re.fullmatch(pattern=r'1|2|3',
                                     string=input("Что необходимо сделать? \n"
                                                  "1. Выгрузить запись вебинара;\n"
                                                  "2. Запустить процесс слияние чанков;\n"
                                                  "3. Выгрузить несколько вебинаров, используя пакетную загрузку.\n"
                                                  "> ")
                                     )

    return option_number.group()


def get_filename_from_user() -> str:
    """
    Get filename from user, then check whether this file exists and file's extension is '.txt
    :return: filename with links to webinar.ru
    """
    while True:
        filename = input('Вставьте путь до файла с ссылками:\n> ')

        if os.path.isfile(filename) and os.path.splitext(p=filename)[-1] == '.txt':
            break

    return filename


def unload_links_from_file(*, filename: str) -> List[str]:
    """
    Open file, read links to webinars from it and then returns it as a list
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
    script_settings = load_from_json()
    remove_mp3 = script_settings.get('remove_mp3_after_merging_chunks')

    if user_option == '1':
        record_ids_tpl = (get_record_id_out_of_link_from_user(),)
    elif user_option == '2':
        main_merge_files(remove_mp3=remove_mp3)
        return
    elif user_option == '3':
        filename = get_filename_from_user()
        links = unload_links_from_file(filename=filename)
        record_ids_tpl = get_record_ids_from_links(links=links)
    else:
        raise NotImplementedError('Эта ошибка не должна была возникнуть'
                                  ' - ошибка выбора в функции choose_option_one_out_of_three_from_user')

    if script_settings.get('auto_files_merging') or merging_files_is_needed_from_user():
        file_merging_will_be_performed = True
    else:
        file_merging_will_be_performed = False

    #    # webinars_infos = [threading.Thread(target=download_webinar,
    #                                    kwargs={'record_id': record_id})
    #                   for record_id in record_id_tpl]
    #
    # for thread in webinars_infos:
    #     thread.start()
    # for thread in webinars_infos:
    #     thread.join()
    #
    # print(webinars_infos)

    for record_id in record_ids_tpl:
        try:
            webinar_info = download_webinar(record_id=record_id)

            if file_merging_will_be_performed:
                merge_files(video_filenames=webinar_info.get('chunks_filenames'),
                            filename=webinar_info.get('webinar_filename'),
                            remove_mp3=remove_mp3,
                            )

        except Exception as error:
            print(error)
            chime.error()


if __name__ == '__main__':
    chime.theme('pokemon')
    chime.notify_exceptions()

    main()
