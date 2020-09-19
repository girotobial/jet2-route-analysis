# Default libraries
import logging
from pathlib import Path

# Third party libraries
import click
import pandas as pd

# Custom code
import src.data.scraper as scraper


def build_dataset(
    jet2_data: pd.DataFrame,
    airport_database: pd.DataFrame
) -> pd.DataFrame:
    """Takes raw datasets and constructs dataframe for analysis.

    Parameters
    ----------
    jet2_data : pd.DataFrame
        Raw Jet2 route data
    airport_database : pd.DataFrame
        Raw airport database data

    Returns
    -------
    pd.DataFrame
        Dataset for analysis
    """
    # Remove routes not available for booking or without destinations
    jet2_data = jet2_data[
        (jet2_data['isEnabledForBooking'] is True)
        & (jet2_data['destinationIataCodes'] != '')
    ]

    # The dataset is focused on lat/long in decimal and standardised location
    # names so the following columns are not needed.
    jet2_data.drop(
        columns=[
            'searchTerms',
            'airportUrlKey',
            'isEnabledForBooking',
            'country',
            'label'
        ],
        inplace=True
    )
    airport_sub_titles = ['Degrees', 'Minutes', 'Seconds', 'Direction']
    airport_database.drop(
        columns=[
            *[f'Latitude {sub}' for sub in airport_sub_titles],
            *[f'Longitude {sub}' for sub in airport_sub_titles],
            'ICAO Code',
            'Airport Name',
        ],
        inplace=True
    )
    airport_database.rename(
        columns={
            'Latitude Decimal Degrees': 'Latitude',
            'Longitude Decimal Degrees': 'Longitude'
        },
        inplace=True
    )

    jet2_data['destinationIataCodes'] = jet2_data['destinationIataCodes']\
        .apply(lambda x: x.split('|'))
    jet2_data = jet2_data.explode('destinationIataCodes')

    # TODO Merge
    
    # FIXME
    data = None
    return data


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

    logger.info('Building dataset')
    build_dataset(
        jet2_data=jet2.dataframe,
        airport_database=airport_database.dataframe
    )

    



if __name__ == '__main__':
    main()
