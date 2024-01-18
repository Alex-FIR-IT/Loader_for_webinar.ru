import os
import re
from typing import List
from moviepy.editor import VideoFileClip, concatenate_videoclips
from support.decorators import print_execution_time, chime_when_is_done, retry_execution_if_exception_is_raised


def merging_files_is_needed_from_user() -> bool:
    """
    Asks user whether he needs to merge videos or not
    :return: True or None
    """
    user_response = None

    while not user_response:
        user_response = re.fullmatch(pattern=r'да|нет',
                                     string=input("Нужно ли будет запустить процесс слияния чанков? (да или нет)\n> "),
                                     flags=re.IGNORECASE
                                     )

    if re.fullmatch(pattern=r'да', string=user_response.group(), flags=re.IGNORECASE):
        return True


def get_webinar_filename_from_user() -> str:
    """
    Get webinar filename from user. If filename does not have extension '.mp4', then add it by itself
    :return: webinar_filename
    """
    filename = None

    while not filename:
        filename = re.fullmatch(pattern=r'.+',
                                string=input("Введите имя для итогового файла:\n> "),
                                flags=re.DOTALL
                                ).group()

    if not filename.endswith('.mp4'):
        filename += '.mp4'

    return filename


def get_directory_from_user():
    """
    Get directory path from user and then returns sorted list with them all
    :return: directory
    """
    directory = None

    while not directory:
        directory = input('Вставьте директорию с файлами, которые нужно соединить в один: \n> ')

        if not os.path.isdir(s=directory):
            print('Указанные путь должен быть директорией!')
            directory = None

    return directory


def get_chunks_filepaths(directory: str) -> List:
    """
    Create a chunks list, sorts it and then returns it
    :param directory: directory with chunks
    :return: sorted list with filepath for each chunk
    :raise ValueError if there are no chunks in directory
    """
    try:
        chunks_filepaths = sorted(os.listdir(path=directory), key=lambda x: int(x[0]))
    except ValueError as error:
        raise ValueError(f'В указанной директории присутствуют файлы, помимо чанков!\nТело ошибки: {error}')

    chunks_filepaths = [os.path.join(directory, chunk_filename) for chunk_filename in chunks_filepaths]
    return chunks_filepaths


@chime_when_is_done(chime_level='info')
@print_execution_time(action='слияние чанков')
def merge_files(*, chunks_filepaths: List, filepath: str, remove_mp3: bool):
    """
    Merge given chunks into one mp3 and then mp4 file
    :param chunks_filepaths: filepaths to all chunks
    :param filepath: filepath for mp3 and mp4 files (directory + filename)
    :param remove_mp3: remove mp3 file, if True
    """
    videos = [VideoFileClip(filename=chunks_filepath) for chunks_filepath in chunks_filepaths]

    if len(videos) > 1:
        final_video = concatenate_videoclips(clips=videos,
                                             method='compose')

        final_video.write_videofile(filename=filepath,
                                    remove_temp=remove_mp3,
                                    temp_audiofile=f'{filepath[:-1]}3'
                                    )
        delete_chunks(chunks=chunks_filepaths)
    else:
        print('Найден всего 1 чанк! Слияние не требуется')


@retry_execution_if_exception_is_raised(retries=5, delay=5)
def delete_chunk(*, chunk_name: str) -> None:
    """
    Delete chunk using its filepath
    :param chunk_name: filepath to chunk
    """
    os.remove(chunk_name)


def delete_chunks(*, chunks: List):
    """
    Takes list with filepaths to chunks and then delete them all
    :param chunks: List with all filepaths to chunks
    """
    for chunk in chunks:
        delete_chunk(chunk_name=chunk)


def main_merge_files(*, remove_mp3: bool):
    """
    Used when user needs only to merge already existent chunks
    :param remove_mp3: remove mp3 file, if True
    """
    webinar_filename = get_webinar_filename_from_user()

    directory_with_chunks = get_directory_from_user()
    chunks_filepaths = get_chunks_filepaths(directory=directory_with_chunks)

    merge_files(chunks_filepaths=chunks_filepaths,
                filepath=os.path.join(directory_with_chunks, webinar_filename),
                remove_mp3=remove_mp3,
                )
