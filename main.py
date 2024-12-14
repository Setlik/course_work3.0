import os


def main():
    api_key = os.getenv('YT_API_KEY')
    channel_ids = [
        'UC-OVMPlMA3-YCIeg4z5z23A',
        'UCwHL6WHUarjGfUM_586me8w',

    ]
    params = config()

    data = get_youtube_data(api_key, channel_ids)
    create_database('youtube', params)
    save_data_to_database(data, 'youtube', params)


if __name__ == '__main__':
    main()