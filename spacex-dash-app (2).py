# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv",index_col=0)
print(spacex_df.columns.tolist())
spacex_df.rename(columns={'class':'Launch_result'},inplace=True)
print(spacex_df.columns.tolist())

max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                                dcc.Dropdown(id='site-dropdown',
                                                options=[
                                                {'label': 'All Sites', 'value': 'ALL'}] +
                                                [{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()
                                                ],
                                                value='ALL',
                                                placeholder="Select a Launch Site here",
                                                    searchable=True
                                                ),                                
                                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),
                                # Function decorator to specify function input and output
                                

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                                min=0, max=10000, step=1000,
                                                marks={i: str(i) for i in range(0, 10001, 2500)},
                                                value=[min_payload, max_payload]),
                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
                                Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    print("Callback triggered")
    filtered_df = spacex_df
    if entered_site == 'ALL':
        df_grouped = spacex_df[spacex_df['Launch_result'] == 1].groupby('Launch Site').size().reset_index(name='counts')
        fig = px.pie(df_grouped, values='counts', 
        names='Launch Site', 
        title='Total successful launches by site')
        return fig
    else:
        # return the outcomes piechart for a selected site
        # Filter data for selected site
        site_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        df_counts = site_df['Launch_result'].value_counts().reset_index()
        df_counts.columns = ['Launch_result', 'counts']
        df_counts['Launch_result'] = df_counts['Launch_result'].map({1: 'Success', 0: 'Failure'})
        fig = px.pie(df_counts,
        values='counts',
        names='Launch_result',
        title=f'Success vs Failure for site {entered_site}')
        print(spacex_df.shape)
        return fig
# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [
        Input(component_id='site-dropdown', component_property='value'),
        Input(component_id='payload-slider', component_property='value')
    ]
)
def get_scatter_plot(selected_site, payload_range):
    # Filter data by payload range
    low, high = payload_range
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)]

    # Filter by site
    if selected_site == 'ALL':
        title = 'Correlation between Payload and Outcome for All Sites'
    else:
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]
        title = f'Correlation between Payload and Outcome for {selected_site}'
    print("Selected site:", selected_site)
    print("Payload range:", payload_range)
    print("Filtered DataFrame shape:", filtered_df.shape)

    # Create scatter plot
    fig = px.scatter(
        filtered_df,
        x='Payload Mass (kg)',
        y='Launch_result',
        color='Booster Version Category',
        title=title,
        hover_data=['Launch Site']
    )
    return fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
