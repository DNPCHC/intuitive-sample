import psycopg2
import urllib.request
import json
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
import plotly.express as px

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# Instantiates server
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server=app.server

# Goes to the indicated url, parses through the json and stores into a dictionary and additionally a data frame
with urllib.request.urlopen("http://api.worldbank.org/v2/countries/USA/indicators/NY.GDP.MKTP.CD?per_page=5000&format=json") as url:
    data = json.loads(url.read().decode())
    print(json.dumps(data, indent=2, sort_keys=True))
    # Excludes the title of the json when copying the dictionary into the dataframe
    dfUS = pd.DataFrame.from_dict(data[1])


# Reverses the indexes of the dataframe
dfUS = dfUS.iloc[::-1]


# Establishes connection with the database
con = psycopg2.connect(
    host="ec2-52-6-77-239.compute-1.amazonaws.com",
    database="d2bo0a226irnot",
    user="lghdwoxqblmbcc",
    password="2e79c2ca9ef38dd79d8569c53112ecb42e1bdc35bd44a74723915bc0eed755b5",
    port="5432"
)

# cursor
cur = con.cursor()

# execute query
cur.execute("select country, date, value from china_gdp")

# Fetches all of the gdp values and prints them
rows = cur.fetchall()
for r in rows:
    print(f"country {r[0]} date {r[1]} value {r[2]}")

# Creates new dataframe for values pulled from database
dfCombined = pd.DataFrame(rows, columns=['country', 'date', 'value'])

# Creates an intermediary dataframe and adds it to data pulled from database
dfIntermediary = dfUS[['countryiso3code', 'date', 'value']]
dfIntermediary = dfIntermediary.rename(columns={"countryiso3code": "country"})
dfCombined = dfCombined.append(dfIntermediary, ignore_index=True)
cur.close()
# close the connection
con.close()

# creates the figure for the line plot based on the US and China GDP
fig = px.line(dfCombined, x="date", y="value", color="country")

# displays figures and html
app.layout = html.Div(children=[
    html.H1(children='US v China GDP', style={"text-align": "center"}),

    html.Div(children=[dcc.Graph(
        id='example-graph',
        figure=fig
    ), dash_table.DataTable(
        data=dfCombined.to_dict('records'),
        columns=[{'id': c, 'name': c} for c in dfCombined.columns],
        page_action='none',
        style_table={'height': '300px', 'overflowY': 'auto',
                     'width': '95%', "margin-left": "30px"},
    ), html.Div([html.H5("Source:"),
                 html.A(
                     href="http://api.worldbank.org/v2/countries/USA/indicators/NY.GDP.MKTP.CD?per_page=5000&format=json", children=("USA")), html.Br(),
                 html.A(href="http://api.worldbank.org/v2/countries/CHN/indicators/NY.GDP.MKTP.CD?per_page=5000&format=json", children=("China"))])]),

])

# runs server
if __name__ == '__main__':
    app.run_server(debug=True)
