import streamlit as st

import src.data.scraper as scraper
import src.data.make_dataset as dataset
import src.visualization.visualize as viz


@st.cache
def load_data():
    jet2 = scraper.Jet2().download().dataframe
    air_db = scraper.AirportDatabase().download().dataframe
    data = dataset.build_dataset(jet2, air_db)
    return data


def main():
    st.title('Jet2 Route Map')
    data_load_state = st.text('Loading Data')
    data = load_data()
    data_load_state.text('Done!')
    st.plotly_chart(viz.plotly_route_map(data))


if __name__ == '__main__':
    main()
