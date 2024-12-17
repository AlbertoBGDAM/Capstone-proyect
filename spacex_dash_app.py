# Import required libraries
import pandas as pd
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX data into pandas dataframe
spacex_df = pd.read_csv("https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/dataset_part_2.csv")

# Verificar las primeras filas y las columnas
print(spacex_df.head())
print(spacex_df.columns)

# Eliminar filas con valores nulos en columnas críticas
spacex_df = spacex_df.dropna(subset=['PayloadMass', 'LaunchSite', 'Class'])

# Rango de Payload
max_payload = spacex_df['PayloadMass'].max()
min_payload = spacex_df['PayloadMass'].min()

# Crear la aplicación Dash
app = dash.Dash(__name__)

# Crear el layout de la aplicación
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    # Dropdown para seleccionar el Launch Site
    dcc.Dropdown(id='site-dropdown',
                 options=[
                     {'label': 'All Sites', 'value': 'ALL'},
                     {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                     {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                     {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                     {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'}
                 ],
                 value='ALL',
                 placeholder="Select a Launch Site here",
                 searchable=True),
    html.Br(),

    # Gráfico de Pie
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    # Slider para seleccionar el rango de Payload
    html.P("Payload range (Kg):"),
    dcc.RangeSlider(id='payload-slider',
                    min=min_payload, max=max_payload, step=1000,
                    marks={int(min_payload): f'{int(min_payload)}',
                           int(max_payload): f'{int(max_payload)}'},
                    value=[min_payload, max_payload]),
    html.Br(),

    # Gráfico de Scatter
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# Callback para actualizar el gráfico de pie
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        fig = px.pie(spacex_df,
                     values='Class',
                     names='LaunchSite',
                     title='Total Success Launches By Site')
    else:
        filtered_df = spacex_df[spacex_df['LaunchSite'] == selected_site]
        success_counts = filtered_df['Class'].value_counts().reset_index()
        success_counts.columns = ['Outcome', 'Count']
        fig = px.pie(success_counts,
                     values='Count',
                     names='Outcome',
                     title=f'Success vs. Failed Launches for {selected_site}')
    return fig

# Callback para actualizar el gráfico de scatter
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def update_scatter_chart(selected_site, payload_range):
    filtered_df = spacex_df[(spacex_df['PayloadMass'] >= payload_range[0]) &
                            (spacex_df['PayloadMass'] <= payload_range[1])]
    if selected_site == 'ALL':
        fig = px.scatter(filtered_df,
                         x='PayloadMass',
                         y='Class',
                         color='BoosterVersion',
                         title='Correlation Between Payload and Success for All Sites')
    else:
        filtered_df = filtered_df[filtered_df['LaunchSite'] == selected_site]
        fig = px.scatter(filtered_df,
                         x='PayloadMass',
                         y='Class',
                         color='BoosterVersion',
                         title=f'Correlation Between Payload and Success for {selected_site}')
    return fig

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run_server(debug=True)
