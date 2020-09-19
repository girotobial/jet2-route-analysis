import logging
from pathlib import Path

import click

import src.data.scraper as scraper


@click.command()
@click.argument('input_filepath', type=click.Path())
@click.argument('output_filepath', type=click.Path())
def main(input_filepath: str, output_filepath: str):
    """Downloads the raw data into the input filepath,
    processes the data and saves it in the output filepath

    Args:
        input_filepath (str): folder to save raw data to
        output_filepath (str): folder to save processed data to.
    """

    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)
    logger = logging.getLogger(__name__)

    input_filepath = Path().cwd() / input_filepath
    output_filepath = Path().cwd() / output_filepath

    logger.info('Downloading Jet2 data from Jet2 API')

    jet2 = scraper.Jet2()
    jet2.download().save(input_filepath)

    logger.info('Scraping Global Aiport Database')
    airport_database = scraper.AirportDatabase()
    airport_database.download().save(input_filepath)


if __name__ == '__main__':
    main()
