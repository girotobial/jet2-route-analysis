import click
import logging
import requests
import json


def download_data():
    url = (
        r'https://www.jet2.com'
        r'/api/search/airportinformation/allairportinformation'
    )
    data = requests.get(url).json
    return data


@click.command()
@click.argument('output_filepath', type=click.Path())
def main(output_filepath):
    """Downloads the data from the jet2 api and saves it into the external folder
    """

    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)
    logger = logging.getLogger(__name__)
    logger.info('downloading data')

    data = download_data()
    with open(output_filepath, 'w') as file:
        json.dump(data, file)


if __name__ == '__main__':
    main()
