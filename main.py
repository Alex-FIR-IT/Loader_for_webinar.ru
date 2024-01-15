import json
from typing import Dict
from scripts.download import download_webinar
from scripts.files_merging import merge_files, get_merge_files_or_not_from_user


def load_from_json() -> Dict:
    """
    Loads script settings from settings.json and then convert it into dict to return it
    :return: dict with script settings
    """
    with open(file='settings.json', mode='r') as file:
        return json.load(fp=file)


def main():
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
    main()