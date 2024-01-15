from scripts.download import download_webinar, load_from_json
from scripts.files_merging import merge_files, get_merge_files_or_not_from_user


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