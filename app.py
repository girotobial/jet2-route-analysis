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


def main():
    st.title('Jet2 Route Map')
    with st.spinner('Loading Data'):
        data = load_data()

    departure_to_filter = st.sidebar.multiselect(
        "Departure Airport",
        data[
            data['isDepartureAirport']
        ]['Departure Airport Name'].unique().tolist()
    )

    departure_mask = filter_mask(
        data=data,
        column='Departure Airport Name',
        values=departure_to_filter
    )

    destination_to_filter = st.sidebar.multiselect(
        "Destination Airport",
        data[
            data['isDestinationAirport']
        ]['Departure Airport Name'].unique().tolist()
    )
    destination_mask = filter_mask(
        data=data,
        column='Destination Airport Name',
        values=destination_to_filter
    )

    filtered_data = data[
        (departure_mask) & (destination_mask)
    ].reset_index()
    st.plotly_chart(viz.plotly_route_map(filtered_data, title=None))


if __name__ == '__main__':
    main()
