from typing import Dict

import pandas as pd
import streamlit as st

import src.data.scraper as scraper
import src.data.make_dataset as dataset
import src.visualization.visualize as viz


@st.cache
def load_data():
    jet2 = scraper.Jet2().download().dataframe
    air_db = scraper.AirportDatabase().download().dataframe
    data = dataset.build_dataset(jet2, air_db)
    data = data.dropna().reset_index()
    return data


def filter_mask(
    data: pd.DataFrame,
    column: str,
    values: list = [],
):
    if values == []:
        return pd.Series([True]*len(data))
    else:
        return data[column].isin(values)


def filter_data(data: pd.DataFrame, parameters: Dict[str, list]) -> pd.DataFrame:
    """Selects rows based on passed parameters

    Parameters
    ----------
    data : pd.DataFrame
        Un Filtered dataset
    parameters : Dict[list]
        dictionary of lists with keys:
        * destination_airport
        * destination_country
        * departure_airport
        * departure_country

    Returns
    -------
    pd.DataFrame
        Filtered dataset
    """
    COLUMNS = dict(
        destination_airport='Destination Airport Name',
        destination_country='Destination Country',
        departure_airport='Departure Airport Name',
        departure_country='Departure Country',
    )
    mask = pd.Series([True] * len(data))
    for param, column in COLUMNS.items():
        mask = mask & filter_mask(data, column, parameters.get(param))

    return data[mask].reset_index()


def main():
    st.title('Jet2 Route Map')
    with st.spinner('Loading Data'):
        data = load_data()

    departures = data[
        data['isDepartureAirport']
    ]['Departure Airport Name'].sort_values().unique().tolist()
    destinations = data[
        data['isDestinationAirport']
    ]['Departure Airport Name'].sort_values().unique().tolist()
    countries = data['Departure Country']\
        .sort_values()\
        .append(data['Destination Country'])\
        .unique()

    st.sidebar.title('Departure')
    departure_airport = st.sidebar.multiselect('Departure Airport', departures)
    departure_country = st.sidebar.multiselect('Departure Country', countries)

    st.sidebar.title('Destination')
    dest_airport = st.sidebar.multiselect('Destination Airport', destinations)
    dest_country = st.sidebar.multiselect('Destination Country', countries)

    parameters = dict(
        departure_airport=departure_airport,
        destination_airport=dest_airport,
        departure_country=departure_country,
        destination_country=dest_country,
    )
    filtered_data = filter_data(data, parameters)

    st.plotly_chart(viz.plotly_route_map(filtered_data, title=None))


if __name__ == '__main__':
    main()
