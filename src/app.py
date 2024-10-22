import plotly.offline as pyo
import plotly.graph_objs as go
import pandas as pd
from dash import Dash, Input, Output, html, dcc

df = pd.read_csv('NYC_Baby_Names_2012-2021.csv')

app = Dash(__name__)

server = app.server

gender_marker = {'MALE':'circle',
                 'FEMALE':'diamond'}

gender_color = {'MALE':'blue',
                 'FEMALE':'magenta'}

gender_size = {'MALE':14,
                 'FEMALE':9}

gender_opacity = {'MALE':0.7,
                 'FEMALE':1}

line_style = {'MALE':'solid',
              'FEMALE':'dot'}

app.layout = html.Div([html.H1('Top Ranked Baby Names in New York City (NYC)'),
                      html.A("Click to return to Data Insights Journal", href="https://joash.pages.dev/posts/baby-names/",
                             style={'color': 'blue', 'text-decoration': 'none'}),
                        html.Br(),
                        html.Br(),
                        html.Div([html.H4('Select the Year:'),
                                dcc.Dropdown(id='xaxis-dropdown',
                                             options=[{'label':i,'value':i} for i in df['Year'].unique()],
                                             value=df['Year'].unique().tolist(),
                                             multi=True)],
                                             style={'width':'30%','display':'inline-block'}),
                        html.Div([],style={'width':'2%','display':'inline-block'}),
                      html.Div([html.H4('Select the Ranking to display:'),
                                dcc.Dropdown(id='yaxis-dropdown',
                                             options=[{'label':i,'value':i} for i in range(1,11)],
                                             value=[1,2,3],
                                             multi=True)],
                                             style={'width':'20%','display':'inline-block'}),
                        html.Div([],style={'width':'2%','display':'inline-block'}),
                        html.Div([html.H4('Select Gender:'),
                                  dcc.Dropdown(id='gender-dropdown',
                                               options=[{'label':i,'value':i} for i in df['Gender'].unique()],
                                               value=['FEMALE'],
                                               multi=True)],
                                               style={'width':'15%','display':'inline-block'}),
                        html.Div([],style={'width':'2%','display':'inline-block'}),
                        html.Div([html.H4('Select Ethnicity Group*:'),
                                  dcc.Dropdown(id='ethnicity-dropdown',
                                               options=[{'label':i,'value':i} for i in df['Ethnicity-Short'].unique()],
                                               value=['AAPI','BLACK (NH)','WHITE (NH)','HISPANIC'],
                                               multi=True)],
                                               style={'width':'25%','display':'inline-block'}),                                                  
                      html.Div([dcc.Graph(id='graph')]),
                      html.Div([html.P('*AAPI: ASIAN AND PACIFIC ISLANDER; BLACK (NH): BLACK NON HISPANIC; WHITE (NH): WHITE NON HISPANIC')],
                               style={'fontSize':10})
                      ],style={'fontFamily':'helvetica','fontsize':12})

@app.callback(Output(component_id='graph',component_property='figure'),
              [Input(component_id='xaxis-dropdown',component_property='value'),
               Input(component_id='yaxis-dropdown',component_property='value'),
               Input(component_id='gender-dropdown',component_property='value'),
               Input(component_id='ethnicity-dropdown',component_property='value')])
def update_graph(xaxis_value,yaxis_value,gender_value,ethnicity_value):
        data = []

        filtered_df = df[(df['Year'].isin(xaxis_value)) & 
                         (df['Ethnicity-Short'].isin(ethnicity_value)) &
                         (df['Gender'].isin(gender_value))
                         ]
        # Aggregate scores by name
        aggregated_df = filtered_df.groupby(['Year','Name','Gender'], as_index=False)['Count'].sum()

        # Step 3: Rank the aggregated scores
        aggregated_df['Rank'] = aggregated_df.groupby(['Year','Gender'])['Count'].rank(ascending=False, method='dense')

        matching_names = aggregated_df[aggregated_df['Rank'].isin(yaxis_value)]['Name'].unique()

        ranked_aggregated_df = aggregated_df[aggregated_df['Name'].isin(matching_names)]


        for name in matching_names:
              for gender in ranked_aggregated_df['Gender'].unique():
                    subset = ranked_aggregated_df[(ranked_aggregated_df['Name']==name) &
                                         (ranked_aggregated_df['Gender']==gender)]
                    
                    if not subset.empty:
                          trace = go.Scatter(x=subset['Year'],
                                             y=subset['Rank'],
                                             mode='lines+markers',
                                             marker={'symbol':gender_marker[gender],
                                                     'size':gender_size[gender],
                                                     'opacity':gender_opacity[gender]
                                                     },
                                                line={'dash':line_style[gender]
                                                           },
                                                opacity=gender_opacity[gender],
                                                name=f"{name} ({gender})")
                          data.append(trace)


        layout = go.Layout(title=f"Rankings for: {', '.join(ranked_aggregated_df['Name'].unique())}",
                   xaxis={'title':'Year','dtick':1},
                   yaxis={'title':'Ranking','autorange':'reversed','zeroline':False},
                   hovermode='closest')
        
        return {'data':data,'layout':layout}

if __name__ == '__main__':
    app.run_server(debug=True)