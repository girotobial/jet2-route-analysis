import abc
from io import BytesIO
import json
import logging
from pathlib import Path
from random import randint
from time import sleep
from typing import Dict
from zipfile import ZipFile

from bs4 import BeautifulSoup
import pandas as pd
import requests


class ABCScraper(abc.ABC):
    @abc.abstractmethod
    def download(self):
        pass

    @abc.abstractmethod
    def save(self):
        pass

    @abc.abstractproperty
    def dataframe(self):
        pass


class Jet2(ABCScraper):
    def __init__(self):
        """Handles the download and saving of route data from the Jet2 API
        """
        self.url = (
            r'https://www.jet2.com'
            r'/api/search/airportinformation/allairportinformation'
        )
        self.data = None

    def download(self):
        self.data = requests.get(self.url).json()
        return self

    def save(self, file_path: Path, file_name: str = 'jet2_data.json'):
        with open(file_path / file_name, 'w') as file:
            json.dump(self.data, file)
        return self

    @property
    def dataframe(self) -> pd.DataFrame:
        try:
            df = pd.DataFrame(self.data['Data'])
        except ValueError:
            pd.DataFrame(self.data)
        return df


class AirportDatabase(ABCScraper):
    def __init__(self) -> None:
        self._zip_url = (
            'https://www.partow.net/downloads/'
            'GlobalAirportDatabase.zip'
        )
        self._column_url = (
            'https://www.partow.net/miscellaneous/airportdatabase'
            '/index.html#Downloads'
        )
        self._rows = None
        self._column_data = None
        self._column_names = None

    def _download_rows(self) -> str:
        r = requests.get(self._zip_url, stream=True)
        zip_ = ZipFile(BytesIO(r.content))
        self._rows = zip_.read('GlobalAirportDatabase.txt')
        return self._rows

    def _scrape_column_headers(self) -> pd.DataFrame:
        response = requests.get(self._column_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find_all(
            'table',
            {'class': 'tg'}
        )
        data = pd.read_html(
            io=str(table),
        )[0]
        self._column_data = data
        self._column_names = data['Name'].to_list()
        return data

    def download(self):
        self._download_rows()
        self._scrape_column_headers()
        return self

    def save(
        self,
        file_path: Path,
        file_names: Dict[str, str] = dict(
            rows='airport_database',
            column_headers='airport_database_headers'
        )
    ):
        with open(file_path / file_names['rows'], 'wb') as row_file:
            row_file.write(self._rows)

        column_data = self._column_data
        column_data.to_csv(
            file_path / file_names['column_headers'],
            index=False
        )

    @property
    def dataframe(self) -> pd.DataFrame:
        data = pd.read_table(
            BytesIO(self._rows),
            sep=':',
        )
        data.columns = self._column_names
        return data


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
