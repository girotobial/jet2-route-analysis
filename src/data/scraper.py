import abc
from io import BytesIO
import json
from pathlib import Path
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
