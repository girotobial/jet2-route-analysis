import requests
import json
from pathlib import Path


class Jet2:
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
            json.dump(self.data['Data'], file)
        return self
