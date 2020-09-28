import pandas as pd
import plotly.graph_objects as go


def plotly_route_map(
    route_data: pd.DataFrame,
    title: str = 'Jet2 Routes',
    projection: str = 'orthographic',
    height: float = None,
    width: float = None,
    landcolor: str = None,
    oceancolor: str = None,
) -> go.Figure:
    """Creates routemap using plotly

    Parameters
    ----------
    route_data : pd.DataFrame
        Long form dataframe of routes with columns:
            - Departure Airport Name
            - Destination Airport Name
            - Departure Longitude
            - Destination Longitude
            - Departure Latitude
            - Destination Latitude
    title : str, optional
        Title of the figure, by default 'Jet2 Routes'
    projection : str, optional
        plotly Scattergeo projection, by default 'orthographic'
        accepts:
            - equirectangular
            - mercator
            - orthographic
            - natural earth
            - kavrayskiy7
            - miller
            - robinson
            - eckert4
            - azimuthal equal area
            - azimuthal equidistant
            - conic equal area
            - conic conformal
            - conic equidistant
            - gnomonic
            - stereographic
            - mollweide
            - hammer
            - transverse mercator
            - albers usa
            - winkel tripel
            - aitoff
            - sinusoidal
    height : float, optional
        height of the figure, by default 600
    width : float, optional
        width of the figure, by default 600

    Returns
    -------
    go.Figure
        World map with route pairings identified.
    """
    fig = go.Figure()
    for i in range(len(route_data)):
        fig.add_trace(
            go.Scattergeo(
                text=(
                    f'{route_data["Departure Airport Name"][i]}'
                    f' to {route_data["Destination Airport Name"][i]}'
                ),
                lon=[
                    route_data['Departure Longitude'][i],
                    route_data['Destination Longitude'][i]
                ],
                lat=[
                    route_data['Departure Latitude'][i],
                    route_data['Destination Latitude'][i]
                ],
                mode='lines',
                line=dict(color='red'),
                opacity=0.6,
            )
        )
    fig.update_layout(
        title_text=title,
        showlegend=False,
        height=height,
        width=width,
        geo=dict(
            projection_type=projection,
            showland=True,
            showocean=True,
            fitbounds='locations',
            landcolor=landcolor,
            oceancolor=oceancolor,
            lakecolor=oceancolor,
        ),
    )
    return fig
