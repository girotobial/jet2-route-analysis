import abc
import json
from io import BytesIO
from pathlib import Path
from typing import List
from zipfile import ZipFile

import pandas as pd
import requests
from bs4 import BeautifulSoup


class ABCScraper(abc.ABC):
    @abc.abstractmethod
    def download(self):
        pass

    @abc.abstractmethod
    def save(self):
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
        self.data = None

    def _download_rows(self) -> str:
        r = requests.get(self._zip_url, stream=True)
        zip_ = ZipFile(BytesIO(r.content))
        self.rows = zip_.read('GlobalAirportDatabase.txt')
        return self.rows

    def _scrape_column_headers(self) -> pd.DataFrame:
        response = requests.get(self._column_url)
        soup = BeautifulSoup(response.text)
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

    def save(self, file_path: Path, file_name: str):
        pass
        # TODO
