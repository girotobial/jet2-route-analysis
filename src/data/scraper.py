import abc
import json
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

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

    def save(self, file_path: Path):
        with open(file_path / 'jet2_data.json', 'w') as file:
            json.dump(self.data, file)
        return self


class AirportDatabase(ABCScraper):
    def __init__(self):
        self._zip_url = (
            'https://www.partow.net/downloads/'
            'GlobalAirportDatabase.zip'
        )
        self._column_url = (
            'https://www.partow.net/miscellaneous/airportdatabase'
            '/index.html#Downloads'
        )

    def download(self):
        # TODO

    def save(self):
        # TODO
