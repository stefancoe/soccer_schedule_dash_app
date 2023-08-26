from dash import Dash, html, dcc, callback, Output, Input, dash_table, State
import plotly.express as px
import pandas as pd
from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
from dateutil.parser import parse
import numpy as np



app = Dash(__name__)
server = app.server

app.layout = html.Div([
    html.Div([
    html.H1(children='Title of Dash App', style={'textAlign':'center'}),
    html.H2(children='Paste in Schedule URL:', style={'textAlign':'left'}),
    dcc.Textarea(
        id='textarea-url',
        value='',
        style={'width': '25%', 'height': 50},
    ),
    html.H2(children='Type Team Name as it Appears in Schedule:', style={'textAlign':'left'}),
    dcc.Textarea(
        id='textarea-team-name',
        value='',
        style={'width': '25%', 'height': 50},
    ),
    html.H2(children='Number of Minutes to Arrive Before Start Time:', style={'textAlign':'left'}),
    dcc.Textarea(
        id='textarea-arrival-time',
        value='',
        style={'width': '25%', 'height': 50},
    ),
    html.H2(children='Home Uniform Color:', style={'textAlign':'left'}),
    dcc.Textarea(
        id='textarea-home-uniform',
        value='',
        style={'width': '25%', 'height': 50},
    ),
    html.H2(children='Away Uniform Color:', style={'textAlign':'left'}),
    dcc.Textarea(
        id='textarea-away-uniform',
        value='',
        style={'width': '25%', 'height': 50},
    ),
]),
    html.Div([
    html.Button('Submit', id='generate-schedule-button', n_clicks=0, style={'left' : 0}),
    dash_table.DataTable(
          id="table_infos",
          columns=[{'id': "Date", 'name': "Date"}, {'id': "Name", 'name': "Name"}, {'id': "Time", 'name': "Time"}, 
                   {'id': "Opponent Name", 'name': "Opponent Name"}, 
                   {'id': "Arrival Time", 'name': "Arrival Time"}, 
                   {'id': "Home or Away", 'name': "Home or Away"}, {'id': "Uniform", 'name': "Uniform"},
                   {'id': "Location Name", 'name': "Location Name"}],
    style_as_list_view=True,
    style_cell={'padding': '5px'},
    style_header={
        'backgroundColor': 'white',
        'fontWeight': 'bold'},
          export_format="csv"),

]),
])
def is_date(string, fuzzy=False):
    """
    Return whether the string can be interpreted as a date.

    :param string: str, string to check for date
    :param fuzzy: bool, ignore unknown tokens in string if True
    """
    try: 
        parse(string, fuzzy=fuzzy)
        return True

    except ValueError:
        return False
    
def f7(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]

@callback(
    Output('table_infos', 'data'),
    Input('generate-schedule-button', 'n_clicks'),
    State('textarea-url', 'value'),
    State('textarea-team-name', 'value'),
    State('textarea-arrival-time', 'value'),
    State('textarea-home-uniform', 'value'),
    State('textarea-away-uniform', 'value'),
)

def update_output(n_clicks, value, value1, value2, value3, value4):
    
    if n_clicks > 0:
        page = urlopen(value)
        html = page.read().decode("utf-8")
        soup = BeautifulSoup(html, "html.parser")
        
        # get dates
        test = soup.find_all("h4")
        date_list = []
        for item in test:
            if is_date(item.text):
                date_list.append(item.text)

        date_list = f7(date_list)

        df_list = pd.read_html(value, flavor='html5lib')
        keep_list = []
        for df in df_list:
            if 'Home Team' in df.columns:
                df['Date'] = date_list[0]
                date_list.pop(0)
                keep_list.append(df)
        
        

        df = pd.concat(keep_list)
        df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%m/%d/%Y')
        df = df[(df['Home Team']==value1) | (df['Away Team']==value1)]
        df['Home or Away'] = np.where(df['Home Team']==value1, 'Home', 'Away')
        df['Name'] = value1
        df['Opponent Name'] = np.where(df['Home or Away']=='Home', df['Away Team'], df['Home Team'])
        df['Uniform'] = np.where(df['Home or Away']=='Home', value3, value4)


        #df['Time'] = ''
        df['Arrival Time'] = value2
        df['Location Name'] = np.where(df['Location'].isnull(), 'TBD', df['Location'])
        #df['Location Details'] = 'TBD'

        print(df)
        return df.to_dict(orient = "records")



if __name__ == '__main__':
    app.run(debug=True)
