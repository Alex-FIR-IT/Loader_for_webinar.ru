import os
import re
from typing import List, AnyStr

from moviepy.editor import VideoFileClip, concatenate_videoclips

from support.decorators import print_execution_time


def get_merge_files_or_not_from_user() -> bool:
    """
    Asks user whether he needs to merge videos or not
    :return: True or None
    """
    user_response = None

    while not user_response:
        user_response = re.fullmatch(pattern=r'да|нет',
                                     string=input("Запустить процесс слияния файлов? (да или нет)\n> "),
                                     flags=re.IGNORECASE
                                     )

    if re.fullmatch(pattern=r'да', string=user_response.group(), flags=re.IGNORECASE):
        return True


def get_webinar_filename_from_user() -> AnyStr:
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


def get_chunks_filepaths(directory: AnyStr) -> List:
    """
    Create a chunks list, sorts it and then returns it
    :param directory: directory with chunks
    :return: sorted list with filepath for each chunk
    :raise ValueError if there are no chunks in directory
    """
    try:
        chunks_filenames = sorted(os.listdir(path=directory), key=lambda x: int(x[0]))
    except ValueError as error:
        raise ValueError(f'В указанной директории присутствуют файлы, помимо чанков!\nТело ошибки: {error}')

    chunks_filepaths = [os.path.join(directory, chunk_filename) for chunk_filename in chunks_filenames]
    return chunks_filepaths


@print_execution_time(action='слияние чанков')
def merge_files(*, video_filenames: List, filename: AnyStr):
    videos = [VideoFileClip(filename=filename) for filename in video_filenames]

    if len(videos) > 1:
        final_video = concatenate_videoclips(clips=videos,
                                             method='compose')

        final_video.write_videofile(filename)
        delete_chunks(chunks=video_filenames)
    else:
        print('Найден всего 1 чанк! Слияние не требуется')


def delete_chunks(chunks: List):
    """
    Takes list with filepaths to chunks and then delete them all
    :param chunks: List with all filepaths to chunks
    """
    for chunk in chunks:
        os.remove(chunk)


if __name__ == '__main__':
    webinar_filename = get_webinar_filename_from_user()

    directory_with_chunks = get_directory_from_user()
    chunks_filenames = get_chunks_filepaths(directory=directory_with_chunks)

    merge_files(video_filenames=chunks_filenames,
                filename=os.path.join(directory_with_chunks, webinar_filename))
