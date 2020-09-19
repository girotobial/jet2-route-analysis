import logging
from pathlib import Path
from random import randint
from time import sleep

from bs4 import BeautifulSoup
import click
import pandas as pd
import requests

import src.data.scraper as scraper


def iata_location_table_parser(html_response: str) -> pd.DataFrame:
    """Reads IATA webpage and returns location data

    Args:
        html_response (str): html code from IATA website

    Returns:
        pd.DataFrame: dataframe of rows from the webpage
    """
    soup = BeautifulSoup(
        html_response,
        'html.parser'
    )
    table = soup.find_all(
        'table',
        {'class': "datatable"}
    )[-1]
    return pd.concat(
        pd.read_html(str(table))
    )


def scrape_iata_code_row(code: str) -> pd.DataFrame:
    """Scrapes the IATA website for location data for a certain code

    Args:
        code (str): IATA location code or airfield name

    Returns:
        pd.DataFrame: Single row of data.
    """
    logger = logging.getLogger(__name__)
    logger.info(f'Scraping IATA code:{code}')
    url = (
            f'https://www.iata.org/en/publications/directories/'
            f'code-search/?airport.search={code}'
    )
    response = requests.get(url)
    for tries in range(2):
        if 'error' in BeautifulSoup(response.text, 'html.parser').head:
            response = requests.get(url)
            sleep(5)
        else:
            break
    return iata_location_table_parser(response.text)


def scrape_iata_codes(jet2_data: str) -> pd.DataFrame:
    codes = pd.DataFrame(jet2_data['Data'])['code'].unique()
    dataframes = []
    for code in codes:
        dataframes.append(scrape_iata_code_row(code))
        sleep(randint(2, 5))
    return pd.concat(dataframes)


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
