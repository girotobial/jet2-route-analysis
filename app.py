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


def main():
    st.title('Jet2 Route Map')
    with st.spinner('Loading Data'):
        data = load_data()

    departure_to_filter = st.sidebar.multiselect(
        "Departure Airport",
        [
            *data[
                data['isDepartureAirport']
            ]['Departure Airport Name'].unique()
        ]
    )
    if departure_to_filter == []:
        departure_mask = pd.Series([True]*len(data))
    else:
        departure_mask = (
            data['Departure Airport Name'].isin(departure_to_filter)
        )

    destination_to_filter = st.sidebar.multiselect(
        "Destination Airport",
        [
            *data[
                data['isDestinationAirport']
            ]['Departure Airport Name'].unique()
        ]
    )
    if destination_to_filter == []:
        destination_mask = pd.Series([True]*len(data))
    else:
        destination_mask = (
            data['Destination Airport Name'].isin(destination_to_filter)
        )

    filtered_data = data[
        (departure_mask) & (destination_mask)
    ].reset_index()
    st.plotly_chart(viz.plotly_route_map(filtered_data, title=None))


if __name__ == '__main__':
    main()
